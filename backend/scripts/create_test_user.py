"""
Create test user in DynamoDB
Email: treschmusic@gmail.com
Password: noise1Scotian
Tier: Legend
"""

import hashlib
import secrets
import time
import uuid
import boto3
from botocore.exceptions import ClientError

def hash_password(password: str, salt: str = None):
    """Hash password using PBKDF2-SHA256 (same as UserAuth)"""
    if salt is None:
        salt = secrets.token_hex(32)

    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100k iterations - matches UserAuth
    )

    return hashed.hex(), salt

def create_test_user():
    """Create test user with Legend tier"""

    # User details
    user_id = str(uuid.uuid4())
    email = "treschmusic@gmail.com"
    password = "noise1Scotian"
    full_name = "Trevor Schaump"
    artist_name = "Tresch"

    # Hash password
    password_hash, password_salt = hash_password(password)

    # Create DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('noisemaker-users')

    # Check if user already exists
    try:
        response = table.scan(
            FilterExpression='email = :email',
            ExpressionAttributeValues={':email': email.lower()},
            Limit=1
        )

        if response.get('Items'):
            print(f"❌ User with email {email} already exists!")
            print(f"   User ID: {response['Items'][0]['user_id']}")
            return
    except ClientError as e:
        print(f"Error checking existing user: {e}")
        return

    # Create user item
    timestamp = int(time.time())
    user_item = {
        'user_id': user_id,
        'email': email.lower(),
        'password_hash': password_hash,
        'password_salt': password_salt,
        'artist_name': artist_name,  # "Tresch"
        'name': full_name,  # "Trevor Schaump"
        'created_at': timestamp,
        'last_login': 0,
        'login_attempts': 0,
        'account_status': 'active',
        'subscription_tier': 'legend',  # Highest tier
        'gender': 'male',
        'session_token': None,
        'session_expires': 0,
        'payment_verified': True,  # Skip payment verification
        'stripe_customer_id': 'test_customer',
        'subscription_status': 'active'
    }

    # Insert into DynamoDB
    try:
        table.put_item(Item=user_item)
        print("✅ Test user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   User ID: {user_id}")
        print(f"   Tier: legend")
        print(f"   Payment Verified: True")
    except ClientError as e:
        print(f"❌ Error creating user: {e}")

if __name__ == "__main__":
    create_test_user()
