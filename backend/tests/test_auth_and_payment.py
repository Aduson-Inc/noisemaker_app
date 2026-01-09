"""
Tests for Authentication and Payment API Routes
Comprehensive tests for signup, signin, and payment flows
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


class TestAuthRoutes:
    """Test suite for authentication endpoints"""

    @patch('routes.auth.user_auth')
    @patch('routes.auth.user_manager')
    @patch('routes.auth.create_jwt_token')
    def test_signup_success(self, mock_jwt, mock_user_manager, mock_user_auth):
        """Test POST /api/auth/signup - successful signup"""
        # Mock successful user creation
        mock_user_auth.create_user.return_value = True
        mock_user_manager.update_user_profile.return_value = True
        mock_user_manager.initialize_baseline_collection.return_value = True
        mock_jwt.return_value = 'test-jwt-token-123'

        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'tier': 'talent',
            'gender': 'male'
        })

        assert response.status_code == 201
        data = response.json()
        assert 'user_id' in data
        assert data['token'] == 'test-jwt-token-123'
        assert data['message'] == 'Account created successfully'

    @patch('routes.auth.user_auth')
    def test_signup_duplicate_email(self, mock_user_auth):
        """Test POST /api/auth/signup - duplicate email"""
        # Mock user already exists
        mock_user_auth.create_user.return_value = False

        response = client.post('/api/auth/signup', json={
            'email': 'existing@example.com',
            'password': 'password123',
            'name': 'Test User',
            'tier': 'talent',
            'gender': 'male'
        })

        assert response.status_code == 400
        data = response.json()
        assert 'detail' in data

    def test_signup_weak_password(self):
        """Test POST /api/auth/signup - weak password"""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'short',  # Less than 8 characters
            'name': 'Test User',
            'tier': 'talent',
            'gender': 'male'
        })

        # Pydantic validation should catch this
        assert response.status_code == 422

    def test_signup_invalid_tier(self):
        """Test POST /api/auth/signup - invalid tier"""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'password123',
            'name': 'Test User',
            'tier': 'invalid_tier',
            'gender': 'male'
        })

        # Pydantic validation should catch this
        assert response.status_code == 422

    @patch('routes.auth.user_auth')
    @patch('routes.auth.create_jwt_token')
    def test_signin_success(self, mock_jwt, mock_user_auth):
        """Test POST /api/auth/signin - successful signin"""
        # Mock successful email lookup and authentication
        mock_user_auth.get_user_id_by_email.return_value = 'user-123'
        mock_user_auth.authenticate_user.return_value = 'session-token-123'
        mock_jwt.return_value = 'test-jwt-token-123'

        response = client.post('/api/auth/signin', json={
            'email': 'test@example.com',
            'password': 'password123'
        })

        assert response.status_code == 200
        data = response.json()
        assert data['user_id'] == 'user-123'
        assert data['token'] == 'test-jwt-token-123'
        assert data['message'] == 'Signed in successfully'

    @patch('routes.auth.user_auth')
    def test_signin_user_not_found(self, mock_user_auth):
        """Test POST /api/auth/signin - user not found"""
        # Mock email lookup returns None
        mock_user_auth.get_user_id_by_email.return_value = None

        response = client.post('/api/auth/signin', json={
            'email': 'nonexistent@example.com',
            'password': 'password123'
        })

        assert response.status_code == 401
        data = response.json()
        assert data['detail'] == 'Invalid email or password'

    @patch('routes.auth.user_auth')
    def test_signin_wrong_password(self, mock_user_auth):
        """Test POST /api/auth/signin - wrong password"""
        # Mock email lookup succeeds but authentication fails
        mock_user_auth.get_user_id_by_email.return_value = 'user-123'
        mock_user_auth.authenticate_user.return_value = None

        response = client.post('/api/auth/signin', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })

        assert response.status_code == 401
        data = response.json()
        assert data['detail'] == 'Invalid email or password'


class TestPaymentRoutes:
    """Test suite for payment endpoints"""

    @patch('routes.payment.user_manager')
    @patch('routes.payment.stripe.checkout.Session.create')
    @patch('routes.payment.get_current_user_id')
    def test_create_checkout_success(self, mock_auth, mock_stripe, mock_user_manager):
        """Test POST /api/payment/create-checkout - successful checkout creation"""
        # Mock authentication
        mock_auth.return_value = 'user-123'

        # Mock user profile
        mock_user_manager.get_user_profile.return_value = {
            'user_id': 'user-123',
            'email': 'test@example.com'
        }

        # Mock Stripe session creation
        mock_stripe.return_value = Mock(
            id='session-123',
            url='https://checkout.stripe.com/session-123'
        )

        response = client.post('/api/payment/create-checkout',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'user_id': 'user-123',
                'tier': 'talent'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['session_id'] == 'session-123'
        assert 'checkout.stripe.com' in data['url']

    @patch('routes.payment.get_current_user_id')
    def test_create_checkout_invalid_tier(self, mock_auth):
        """Test POST /api/payment/create-checkout - invalid tier"""
        mock_auth.return_value = 'user-123'

        response = client.post('/api/payment/create-checkout',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'user_id': 'user-123',
                'tier': 'invalid_tier'
            }
        )

        # Pydantic should catch this
        assert response.status_code == 422

    @patch('routes.payment.get_current_user_id')
    @patch('routes.payment.user_manager')
    def test_create_checkout_user_not_found(self, mock_user_manager, mock_auth):
        """Test POST /api/payment/create-checkout - user not found"""
        mock_auth.return_value = 'user-123'
        mock_user_manager.get_user_profile.return_value = None

        response = client.post('/api/payment/create-checkout',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'user_id': 'user-123',
                'tier': 'talent'
            }
        )

        assert response.status_code == 404
        data = response.json()
        assert 'User not found' in data['detail']

    @patch('routes.payment.stripe.checkout.Session.retrieve')
    @patch('routes.payment.user_manager')
    @patch('routes.payment.get_current_user_id')
    def test_confirm_payment_success(self, mock_auth, mock_user_manager, mock_stripe):
        """Test POST /api/payment/confirm - successful payment confirmation"""
        mock_auth.return_value = 'user-123'

        # Mock Stripe session retrieval
        mock_stripe.return_value = Mock(
            payment_status='paid',
            metadata={'user_id': 'user-123', 'tier': 'talent'}
        )

        # Mock subscription update
        mock_user_manager.update_subscription_tier.return_value = True

        response = client.post('/api/payment/confirm',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'session_id': 'session-123'
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'talent' in data['message']

    @patch('routes.payment.stripe.checkout.Session.retrieve')
    @patch('routes.payment.get_current_user_id')
    def test_confirm_payment_not_paid(self, mock_auth, mock_stripe):
        """Test POST /api/payment/confirm - payment not completed"""
        mock_auth.return_value = 'user-123'

        # Mock Stripe session with unpaid status
        mock_stripe.return_value = Mock(
            payment_status='unpaid',
            metadata={'user_id': 'user-123', 'tier': 'talent'}
        )

        response = client.post('/api/payment/confirm',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'session_id': 'session-123'
            }
        )

        assert response.status_code == 400
        data = response.json()
        assert 'not completed' in data['detail']

    @patch('routes.payment.stripe.checkout.Session.retrieve')
    @patch('routes.payment.get_current_user_id')
    def test_confirm_payment_wrong_user(self, mock_auth, mock_stripe):
        """Test POST /api/payment/confirm - session belongs to different user"""
        mock_auth.return_value = 'user-123'

        # Mock Stripe session with different user_id
        mock_stripe.return_value = Mock(
            payment_status='paid',
            metadata={'user_id': 'user-456', 'tier': 'talent'}
        )

        response = client.post('/api/payment/confirm',
            headers={'Authorization': 'Bearer test-token'},
            json={
                'session_id': 'session-123'
            }
        )

        assert response.status_code == 403
        data = response.json()
        assert 'does not belong' in data['detail']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
