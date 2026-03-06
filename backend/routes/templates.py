"""
Admin Template Management API Routes
Handles template upload, analysis, listing, and management.

Admin-only endpoints for the template ingestion system (Spec Section 5).
Templates are analyzed by a vision model (or use defaults when PLACEHOLDER)
and stored as JSON presets in the noisemaker-templates DynamoDB table.
"""

import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, status
from pydantic import BaseModel, Field

from middleware.auth import get_current_user_id
from content.template_engine import (
    ingest_template,
    select_template,
    render_static,
    DEFAULT_PRESETS,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/templates", tags=["Admin Templates"])

# Hardcoded admin user IDs — extend or replace with role-based check
ADMIN_USER_IDS = set()


# =============================================================================
# AUTH HELPER
# =============================================================================

def _require_admin(user_id: str) -> None:
    """Check if user is an admin. Raises 403 if not."""
    if ADMIN_USER_IDS and user_id not in ADMIN_USER_IDS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class TemplateResponse(BaseModel):
    template_id: str
    name: str = ""
    platform: str = "all"
    aspect_ratio: str = "1:1"
    is_active: bool = True
    layout_json: Optional[dict] = None
    created_at: str = ""


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    is_active: Optional[bool] = None
    layout_json: Optional[dict] = None


class TemplateListResponse(BaseModel):
    templates: list[TemplateResponse]
    default_presets: list[str]


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/upload", response_model=TemplateResponse)
async def upload_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    platform: str = Form(default="all"),
    aspect_ratio: str = Form(default="1:1"),
    current_user_id: str = Depends(get_current_user_id),
):
    """Upload a master PNG/SVG design and auto-analyze into a JSON preset.

    The vision model extracts bounding boxes for album art, song title,
    and artist name. If the vision model is PLACEHOLDER, uses default
    layout matching the specified aspect ratio.
    """
    _require_admin(current_user_id)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded",
        )

    result = ingest_template(image_bytes, name, platform, aspect_ratio)

    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("error", "Template ingestion failed"),
        )

    return TemplateResponse(
        template_id=result["template_id"],
        name=name,
        platform=platform,
        aspect_ratio=aspect_ratio,
    )


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    current_user_id: str = Depends(get_current_user_id),
):
    """List all custom templates plus available default presets."""
    _require_admin(current_user_id)

    import boto3
    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    custom_templates = []
    try:
        table = dynamodb.Table("noisemaker-templates")
        response = table.scan(Limit=50)
        for item in response.get("Items", []):
            custom_templates.append(TemplateResponse(
                template_id=item["template_id"],
                name=item.get("name", ""),
                platform=item.get("platform", "all"),
                aspect_ratio=item.get("aspect_ratio", "1:1"),
                is_active=item.get("is_active", True),
                created_at=item.get("created_at", ""),
            ))
    except Exception as e:
        logger.debug(f"Custom templates fetch failed (table may not exist): {e}")

    return TemplateListResponse(
        templates=custom_templates,
        default_presets=list(DEFAULT_PRESETS.keys()),
    )


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Get a template's full JSON preset by ID."""
    _require_admin(current_user_id)

    # Check default presets first
    for preset in DEFAULT_PRESETS.values():
        if preset["template_id"] == template_id:
            return TemplateResponse(
                template_id=template_id,
                name=preset.get("name", ""),
                platform=preset.get("platform", "all"),
                aspect_ratio=preset.get("aspect_ratio", "1:1"),
                layout_json=preset,
            )

    # Check DynamoDB
    import boto3
    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
    try:
        table = dynamodb.Table("noisemaker-templates")
        response = table.get_item(Key={"template_id": template_id})
        item = response.get("Item")
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found",
            )

        layout = json.loads(item.get("layout_json", "{}"))
        return TemplateResponse(
            template_id=template_id,
            name=item.get("name", ""),
            platform=item.get("platform", "all"),
            aspect_ratio=item.get("aspect_ratio", "1:1"),
            is_active=item.get("is_active", True),
            layout_json=layout,
            created_at=item.get("created_at", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template fetch failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch template",
        )


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    update: TemplateUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
):
    """Update a custom template's metadata or layout JSON."""
    _require_admin(current_user_id)

    import boto3
    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    update_expr_parts = []
    expr_values = {}
    expr_names = {}

    if update.name is not None:
        update_expr_parts.append("#n = :n")
        expr_names["#n"] = "name"
        expr_values[":n"] = update.name

    if update.platform is not None:
        update_expr_parts.append("platform = :p")
        expr_values[":p"] = update.platform

    if update.is_active is not None:
        update_expr_parts.append("is_active = :a")
        expr_values[":a"] = update.is_active

    if update.layout_json is not None:
        update_expr_parts.append("layout_json = :l")
        expr_values[":l"] = json.dumps(update.layout_json)

    if not update_expr_parts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    try:
        table = dynamodb.Table("noisemaker-templates")
        kwargs = {
            "Key": {"template_id": template_id},
            "UpdateExpression": "SET " + ", ".join(update_expr_parts),
            "ExpressionAttributeValues": expr_values,
        }
        if expr_names:
            kwargs["ExpressionAttributeNames"] = expr_names

        table.update_item(**kwargs)
        return {"status": "updated", "template_id": template_id}
    except Exception as e:
        logger.error(f"Template update failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update template",
        )


@router.delete("/{template_id}")
async def deactivate_template(
    template_id: str,
    current_user_id: str = Depends(get_current_user_id),
):
    """Deactivate a template (soft delete — sets is_active=False)."""
    _require_admin(current_user_id)

    import boto3
    dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

    try:
        table = dynamodb.Table("noisemaker-templates")
        table.update_item(
            Key={"template_id": template_id},
            UpdateExpression="SET is_active = :a",
            ExpressionAttributeValues={":a": False},
        )
        return {"status": "deactivated", "template_id": template_id}
    except Exception as e:
        logger.error(f"Template deactivation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate template",
        )
