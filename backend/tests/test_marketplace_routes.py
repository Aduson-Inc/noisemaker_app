"""
Tests for Marketplace API Routes
Basic smoke tests to verify marketplace endpoints are functioning
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)


class TestMarketplaceRoutes:
    """Test suite for marketplace API endpoints"""

    @patch('marketplace.artwork_manager')
    def test_get_artwork_all_filter(self, mock_manager):
        """Test GET /api/marketplace/artwork with 'all' filter"""
        # Mock response
        mock_manager.get_artwork_pool.return_value = [
            {
                'artwork_id': 'art-1',
                'filename': 'test.jpg',
                'upload_date': '2025-01-01T00:00:00',
                'download_count': 5,
                'is_on_hold': False,
                'can_purchase': True
            }
        ]

        response = client.get('/api/marketplace/artwork?filter=all')

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['filter'] == 'all'
        assert isinstance(data['artworks'], list)

    @patch('marketplace.artwork_manager')
    def test_get_user_credits(self, mock_manager):
        """Test GET /api/marketplace/credits"""
        # Mock response
        mock_manager.get_user_credits.return_value = {
            'success': True,
            'available_downloads': 3,
            'total_downloads_used': 2,
            'total_purchases': 1
        }

        response = client.get('/api/marketplace/credits?user_id=test-user-123')

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['available_downloads'] == 3

    @patch('marketplace.album_artwork_integration')
    def test_download_artwork_success(self, mock_integration):
        """Test POST /api/marketplace/download - successful download"""
        # Mock successful download
        mock_integration.handle_artwork_download.return_value = {
            'success': True,
            'download_url': 'https://s3.amazonaws.com/test/artwork.jpg',
            'remaining_credits': 2
        }

        response = client.post('/api/marketplace/download', json={
            'user_id': 'test-user-123',
            'artwork_id': 'art-1'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'download_url' in data
        assert data['remaining_credits'] == 2

    @patch('marketplace.album_artwork_integration')
    def test_download_artwork_no_credits(self, mock_integration):
        """Test POST /api/marketplace/download - no credits"""
        # Mock failed download
        mock_integration.handle_artwork_download.return_value = {
            'success': False,
            'error': 'No download credits available'
        }

        response = client.post('/api/marketplace/download', json={
            'user_id': 'test-user-123',
            'artwork_id': 'art-1'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is False
        assert 'error' in data

    @patch('marketplace.artwork_manager')
    def test_place_hold_success(self, mock_manager):
        """Test POST /api/marketplace/hold - successful hold"""
        # Mock successful hold
        mock_manager.place_artwork_hold.return_value = {
            'success': True,
            'session_id': 'session-123',
            'hold_expires': '2025-01-01T12:05:00'
        }

        response = client.post('/api/marketplace/hold', json={
            'user_id': 'test-user-123',
            'artwork_id': 'art-1'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'session_id' in data

    @patch('marketplace.album_artwork_integration')
    def test_purchase_artwork_success(self, mock_integration):
        """Test POST /api/marketplace/purchase - successful purchase"""
        # Mock successful purchase
        mock_integration.handle_artwork_purchase.return_value = {
            'success': True,
            'download_urls': ['https://s3.amazonaws.com/test/purchased1.jpg'],
            'amount_paid': 2.99,
            'tokens_used': 1
        }

        response = client.post('/api/marketplace/purchase', json={
            'user_id': 'test-user-123',
            'artwork_ids': ['art-1'],
            'purchase_type': 'single'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['amount_paid'] == 2.99

    @patch('marketplace.artwork_manager')
    def test_get_artwork_filters(self, mock_manager):
        """Test all filter types for artwork listing"""
        filters = ['all', 'new', 'popular', 'exclusive']

        for filter_type in filters:
            mock_manager.get_artwork_pool.return_value = []

            response = client.get(f'/api/marketplace/artwork?filter={filter_type}')

            assert response.status_code == 200
            data = response.json()
            assert data['filter'] == filter_type

    @patch('marketplace.album_artwork_integration')
    def test_marketplace_health_check(self, mock_integration):
        """Test GET /api/marketplace/health"""
        # Mock health check
        mock_integration.get_integration_health.return_value = {
            'success': True,
            'overall_health': 'healthy'
        }

        response = client.get('/api/marketplace/health')

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    @patch('marketplace.artwork_manager')
    def test_get_analytics(self, mock_manager):
        """Test GET /api/marketplace/analytics"""
        # Mock analytics
        mock_manager.get_marketplace_analytics.return_value = {
            'pool_status': {
                'current_count': 200,
                'max_capacity': 250
            }
        }

        response = client.get('/api/marketplace/analytics')

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'analytics' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
