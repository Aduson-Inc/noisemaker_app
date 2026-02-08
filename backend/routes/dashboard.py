"""
Dashboard API Routes
Handles user dashboard data: songs, posts, stats
"""

import logging
from fastapi import APIRouter, HTTPException, status, Depends, Path
from typing import List, Dict, Any

from models.schemas import (
    SongInfo,
    PostInfo,
    DashboardResponse,
    DashboardStats,
    UserStatsResponse,
    PlatformStats,
    UpdateCaptionRequest,
    PostActionResponse,
    AddSongRequest,
    AddSongResponse
)
from middleware.auth import get_current_user_id
from data.song_manager import song_manager
from data.user_manager import user_manager
from data.dynamodb_client import dynamodb_client

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/user", tags=["Dashboard"])



@router.get("/{user_id}/songs", response_model=List[SongInfo])
async def get_user_songs(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> List[SongInfo]:
    """
    Get all active songs for a user.

    Returns list of songs with their current status and metrics.
    """
    try:
        # Verify user can only access their own songs
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's songs"
            )

        logger.info(f"Fetching songs for user: {user_id}")

        # Get active songs from song manager
        active_songs = song_manager.get_user_active_songs(user_id)

        # Convert to response format
        songs_list = []
        for song in active_songs:
            song_info = SongInfo(
                id=song.get('song_id', ''),
                spotify_track_id=song.get('spotify_track_id', ''),
                name=song.get('song', 'Unknown'),
                artist=song.get('artist_title', 'Unknown Artist'),
                album_art=song.get('art_url', ''),
                fire_mode=song.get('fire_mode', False),
                fire_mode_triggered=song.get('fire_mode_triggered', False),
                baseline_streams=song.get('baseline_streams', 0),
                current_streams=song.get('current_streams', 0),
                added_at=song.get('created_at', '')
            )
            songs_list.append(song_info)

        return songs_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching songs for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch songs"
        )


@router.get("/{user_id}/songs/{song_id}/upcoming-post")
async def get_upcoming_post(
    user_id: str,
    song_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get the next upcoming post for a specific song.

    Returns the next scheduled post with caption and image preview.
    """
    try:
        # Verify user authorization
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's posts"
            )

        logger.info(f"Fetching upcoming post for song {song_id}, user {user_id}")

        # Query scheduled posts table
        # Filter by user_id and song_id, get the next pending post
        try:
            response = dynamodb_client.query_table(
                table_name='noisemaker-scheduled-posts',
                key_condition='user_id = :uid',
                expression_values={':uid': user_id},
                filter_expression='song_id = :sid AND post_status = :status',
                filter_values={':sid': song_id, ':status': 'pending'}
            )
        except:
            # If query fails, return None (no upcoming post)
            return {"upcoming_post": None}

        if not response or len(response) == 0:
            return {"upcoming_post": None}

        # Get the first upcoming post (sorted by scheduled_time)
        upcoming = sorted(response, key=lambda x: x.get('scheduled_time', ''))[0]

        post_data = {
            "id": upcoming.get('post_id', ''),
            "song_id": upcoming.get('song_id', ''),
            "platform": upcoming.get('platform', ''),
            "scheduled_time": upcoming.get('scheduled_time', ''),
            "caption": upcoming.get('caption', ''),
            "image_url": upcoming.get('image_url', ''),
            "status": upcoming.get('post_status', 'pending')
        }

        return {"upcoming_post": post_data}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching upcoming post for song {song_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch upcoming post"
        )


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> UserStatsResponse:
    """
    Get user's performance statistics.

    Returns metrics like monthly listeners, follower growth, streams, engagement.
    """
    try:
        # Verify authorization
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's stats"
            )

        logger.info(f"Fetching stats for user: {user_id}")

        # Get user profile for baseline and stats
        user_profile = user_manager.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get stats from user profile
        # These would be populated by daily Spotify API polling
        stats = UserStatsResponse(
            monthly_listeners=user_profile.get('monthly_listeners', 0),
            follower_growth=user_profile.get('follower_growth', 0),
            total_streams=user_profile.get('total_streams', 0),
            engagement_rate=user_profile.get('engagement_rate', 0.0)
        )

        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user stats"
        )


# ============================================================================
# MILESTONE ENDPOINTS
# Milestones are shared videos stored in S3. Each user has their own history
# tracking which milestone videos they've seen. Once a user views a milestone
# video, it's marked as played and won't show for that user again.
# ============================================================================

@router.get("/{user_id}/milestones")
async def get_pending_milestone(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Get pending milestone for user (if any).
    Returns milestone type, video URL, and artist name for display.
    """
    try:
        # Verify user is requesting their own milestone history
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's milestone history"
            )

        # Get pending milestone from user's history
        pending = user_manager.get_pending_milestone(user_id)

        # Get artist name from user profile for "LET'S GO!!!" display
        user_profile = user_manager.get_user_profile(user_id) or {}
        artist_name = user_profile.get('spotify_artist_name', user_profile.get('name', 'Artist'))

        if pending.get('has_pending'):
            return {
                'has_pending': True,
                'milestone_type': pending.get('milestone_type'),
                'video_url': pending.get('video_url'),
                'description': pending.get('description'),
                'artist_name': artist_name
            }
        else:
            return {
                'has_pending': False,
                'milestone_type': None,
                'video_url': None,
                'artist_name': artist_name
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting milestones for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch milestones"
        )


@router.post("/{user_id}/milestones/{milestone_id}/claim")
async def claim_milestone(
    user_id: str,
    milestone_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> Dict[str, Any]:
    """
    Mark a milestone video as played in user's history.
    Called when video finishes - updates THIS user's history so they
    won't see this milestone video again. Other users are unaffected.
    """
    try:
        # Verify user is updating their own milestone history
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot update other user's milestone history"
            )

        # Mark milestone video as played in user's history
        result = user_manager.mark_milestone_video_played(user_id, milestone_id)

        if result.get('success'):
            logger.info(f"Milestone {milestone_id} marked as viewed for user {user_id}")
            return {
                'success': True,
                'message': f'Milestone {milestone_id} marked as viewed'
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to mark milestone as viewed')
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking milestone {milestone_id} for {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update milestone history"
        )


# Post management endpoints
posts_router = APIRouter(prefix="/api/posts", tags=["Posts"])


@posts_router.patch("/{post_id}/caption", response_model=PostActionResponse)
async def update_post_caption(
    post_id: str,
    request: UpdateCaptionRequest,
    current_user_id: str = Depends(get_current_user_id)
) -> PostActionResponse:
    """
    Update caption for a scheduled post.

    Allows user to customize AI-generated captions before posting.
    """
    try:
        logger.info(f"Updating caption for post {post_id}")

        # Get post to verify ownership
        post_key = {'post_id': post_id}
        post_data = dynamodb_client.get_item('noisemaker-scheduled-posts', post_key)

        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Verify user owns this post
        if post_data.get('user_id') != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify other user's posts"
            )

        # Update caption
        updates = {'caption': request.caption}
        success = dynamodb_client.update_item(
            'noisemaker-scheduled-posts',
            post_key,
            updates
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update caption"
            )

        return PostActionResponse(
            success=True,
            message="Caption updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating caption for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update caption"
        )


@posts_router.post("/{post_id}/approve", response_model=PostActionResponse)
async def approve_post(
    post_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> PostActionResponse:
    """
    Approve a scheduled post for publishing.

    Marks post as ready to be posted at scheduled time.
    """
    try:
        logger.info(f"Approving post {post_id}")

        # Get post to verify ownership
        post_key = {'post_id': post_id}
        post_data = dynamodb_client.get_item('noisemaker-scheduled-posts', post_key)

        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Verify user owns this post
        if post_data.get('user_id') != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot approve other user's posts"
            )

        # Update status to approved
        updates = {'post_status': 'approved'}
        success = dynamodb_client.update_item(
            'noisemaker-scheduled-posts',
            post_key,
            updates
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to approve post"
            )

        return PostActionResponse(
            success=True,
            message="Post approved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve post"
        )


@posts_router.post("/{post_id}/reject", response_model=PostActionResponse)
async def reject_post(
    post_id: str,
    current_user_id: str = Depends(get_current_user_id)
) -> PostActionResponse:
    """
    Reject a scheduled post.

    Marks post as rejected and removes from schedule.
    """
    try:
        logger.info(f"Rejecting post {post_id}")

        # Get post to verify ownership
        post_key = {'post_id': post_id}
        post_data = dynamodb_client.get_item('noisemaker-scheduled-posts', post_key)

        if not post_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )

        # Verify user owns this post
        if post_data.get('user_id') != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot reject other user's posts"
            )

        # Update status to rejected
        updates = {'post_status': 'rejected'}
        success = dynamodb_client.update_item(
            'noisemaker-scheduled-posts',
            post_key,
            updates
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to reject post"
            )

        return PostActionResponse(
            success=True,
            message="Post rejected successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reject post"
        )


# Return both routers
def get_routers():
    """Return both dashboard and posts routers."""
    return [router, posts_router]
