"""
Add Email Global Secondary Index (GSI) to noisemaker-users table.

This script adds an email-index GSI to enable efficient email lookups
instead of using full table scans.

Run this ONCE on the production database to add the index.
The index creation is asynchronous - it may take a few minutes to complete.

Usage:
    python scripts/add_email_gsi.py
"""

import boto3
from botocore.exceptions import ClientError
import time
import sys


def add_email_gsi():
    """Add email-index GSI to noisemaker-users table."""

    dynamodb = boto3.client('dynamodb', region_name='us-east-2')
    table_name = 'noisemaker-users'
    index_name = 'email-index'

    print(f"🔧 Adding GSI '{index_name}' to table '{table_name}'...")
    print()

    try:
        # Check if table exists and get current state
        response = dynamodb.describe_table(TableName=table_name)
        table_status = response['Table']['TableStatus']

        if table_status != 'ACTIVE':
            print(f"❌ Table is not active (status: {table_status}). Wait and try again.")
            sys.exit(1)

        # Check if GSI already exists
        existing_gsis = response['Table'].get('GlobalSecondaryIndexes', [])
        for gsi in existing_gsis:
            if gsi['IndexName'] == index_name:
                gsi_status = gsi['IndexStatus']
                if gsi_status == 'ACTIVE':
                    print(f"✅ GSI '{index_name}' already exists and is ACTIVE.")
                    return True
                else:
                    print(f"⏳ GSI '{index_name}' exists but status is: {gsi_status}")
                    print("   Wait for it to become ACTIVE.")
                    return False

        # Add the GSI
        print(f"📝 Creating GSI '{index_name}'...")
        print("   Partition Key: email (String)")
        print("   Projection: ALL (includes all attributes)")
        print()

        dynamodb.update_table(
            TableName=table_name,
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexUpdates=[
                {
                    'Create': {
                        'IndexName': index_name,
                        'KeySchema': [
                            {'AttributeName': 'email', 'KeyType': 'HASH'}
                        ],
                        'Projection': {
                            'ProjectionType': 'ALL'
                        }
                    }
                }
            ]
        )

        print("✅ GSI creation initiated!")
        print()
        print("⏳ Waiting for GSI to become ACTIVE...")
        print("   (This may take a few minutes depending on table size)")
        print()

        # Poll for completion
        while True:
            response = dynamodb.describe_table(TableName=table_name)
            gsis = response['Table'].get('GlobalSecondaryIndexes', [])

            for gsi in gsis:
                if gsi['IndexName'] == index_name:
                    status = gsi['IndexStatus']
                    if status == 'ACTIVE':
                        print(f"✅ GSI '{index_name}' is now ACTIVE!")
                        print()
                        print("📊 Index Details:")
                        print(f"   Item Count: {gsi.get('ItemCount', 'N/A')}")
                        print(f"   Size Bytes: {gsi.get('IndexSizeBytes', 'N/A')}")
                        return True
                    else:
                        print(f"   Status: {status}...")
                        time.sleep(10)
                        break
            else:
                print("   GSI not found in table description yet...")
                time.sleep(5)

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']

        if error_code == 'ResourceNotFoundException':
            print(f"❌ Table '{table_name}' does not exist!")
        elif error_code == 'ValidationException' and 'already exists' in error_msg.lower():
            print(f"✅ GSI '{index_name}' already exists.")
            return True
        else:
            print(f"❌ AWS Error: {error_code} - {error_msg}")

        sys.exit(1)

    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)


def verify_gsi():
    """Verify the GSI works by doing a test query."""

    dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
    table = dynamodb.Table('noisemaker-users')

    print()
    print("🧪 Testing GSI query...")

    try:
        # Do a test query (won't find anything, but proves GSI works)
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression='email = :email',
            ExpressionAttributeValues={':email': 'test@example.com'},
            Limit=1
        )

        print("✅ GSI query works correctly!")
        print(f"   Scanned Count: {response.get('ScannedCount', 0)}")
        print(f"   Items Returned: {len(response.get('Items', []))}")
        return True

    except ClientError as e:
        print(f"❌ GSI query failed: {e.response['Error']['Message']}")
        return False


if __name__ == '__main__':
    print("=" * 60)
    print("NOiSEMaKER - Add Email GSI to Users Table")
    print("=" * 60)
    print()

    success = add_email_gsi()

    if success:
        verify_gsi()
        print()
        print("=" * 60)
        print("✅ GSI setup complete!")
        print()
        print("Next step: Deploy the updated user_auth.py that uses")
        print("           query() instead of scan() for email lookups.")
        print("=" * 60)
