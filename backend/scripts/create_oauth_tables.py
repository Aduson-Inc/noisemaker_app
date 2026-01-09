"""
Create DynamoDB tables for OAuth system.

This script creates the necessary tables for the Noisemaker OAuth system:
1. noisemaker-oauth-states - For CSRF state validation
2. noisemaker-platform-connections - For user OAuth tokens (if not exists)

Author: Senior Python Backend Engineer
Version: 1.0
"""

import boto3
import sys

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb', region_name='us-east-2')

def create_oauth_states_table():
    """Create table for OAuth CSRF state validation."""
    try:
        table_name = 'noisemaker-oauth-states'

        dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'state', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'state', 'KeyType': 'HASH'}
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'Application', 'Value': 'Noisemaker'},
                {'Key': 'Purpose', 'Value': 'OAuth CSRF Protection'}
            ]
        )

        print(f"✅ Created table: {table_name}")
        return True

    except dynamodb.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return True

    except Exception as e:
        print(f"❌ Error creating {table_name}: {e}")
        return False


def create_platform_connections_table():
    """Create table for user platform OAuth connections."""
    try:
        table_name = 'noisemaker-platform-connections'

        dynamodb.create_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'platform', 'AttributeType': 'S'}
            ],
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},   # Partition key
                {'AttributeName': 'platform', 'KeyType': 'RANGE'}  # Sort key
            ],
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'Application', 'Value': 'Noisemaker'},
                {'Key': 'Purpose', 'Value': 'User Platform Connections'}
            ]
        )

        print(f"✅ Created table: {table_name}")
        return True

    except dynamodb.exceptions.ResourceInUseException:
        print(f"⚠️  Table {table_name} already exists")
        return True

    except Exception as e:
        print(f"❌ Error creating {table_name}: {e}")
        return False


def main():
    """Create all OAuth-related tables."""
    print("🚀 Creating DynamoDB tables for OAuth system...\n")

    results = []

    # Create OAuth states table
    print("Creating OAuth states table...")
    results.append(create_oauth_states_table())

    # Create platform connections table
    print("\nCreating platform connections table...")
    results.append(create_platform_connections_table())

    # Summary
    print("\n" + "="*60)
    if all(results):
        print("✅ All OAuth tables created successfully!")
        print("\nNext steps:")
        print("1. Configure OAuth app credentials in AWS Parameter Store")
        print("2. Set OAUTH_ENCRYPTION_KEY environment variable")
        print("3. Deploy OAuth API routes")
        return 0
    else:
        print("❌ Some tables failed to create. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
