"""
DynamoDB Table Creation Script for Noisemaker
Creates tables with proper schemas for user_id based partitioning
"""

import boto3
from botocore.exceptions import ClientError
import sys

def create_tables():
    """Create all required DynamoDB tables with correct schemas"""
    
    dynamodb = boto3.client('dynamodb', region_name='us-east-2')
    
    # Define proper table schemas
    tables_config = {
        # CRITICAL TABLES - User and Song Data
        'noisemaker-email-reservations': {
            'KeySchema': [
                {'AttributeName': 'email', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-users': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            'GlobalSecondaryIndexes': [
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }
            ]
        },
        'noisemaker-songs': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'song_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'song_id', 'AttributeType': 'S'}
            ]
        },
        
        # POSTING AND CONTENT TABLES
        'noisemaker-posting-history': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'post_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'post_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-content-generation': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'content_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'content_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-content-tasks': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'task_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'task_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-scheduled-posts': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'scheduled_time', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'scheduled_time', 'AttributeType': 'S'}
            ]
        },
        
        # ANALYTICS TABLES
        'noisemaker-artwork-analytics': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'artwork_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'artwork_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-user-behavior': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'timestamp', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'timestamp', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-milestones': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'milestone_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'milestone_id', 'AttributeType': 'S'}
            ]
        },
        
        # COMMUNITY ENGAGEMENT TABLES
        'noisemaker-reddit-engagement': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'post_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'post_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-discord-engagement': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'message_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'message_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-discord-servers': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'server_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'server_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-engagement-history': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'engagement_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'engagement_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-community-analytics': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'metric_id', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'metric_id', 'AttributeType': 'S'}
            ]
        },
        
        # SPOTIFY OAUTH AND METRICS TABLES
        'noisemaker-oauth-tokens': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-baselines': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'calculation_date', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'calculation_date', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-track-metrics': {
            'KeySchema': [
                {'AttributeName': 'track_id', 'KeyType': 'HASH'},
                {'AttributeName': 'poll_date', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'track_id', 'AttributeType': 'S'},
                {'AttributeName': 'poll_date', 'AttributeType': 'S'}
            ]
        },

        # SYSTEM TABLES
        'noisemaker-artwork-cleanup': {
            'KeySchema': [
                {'AttributeName': 'cleanup_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'cleanup_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-system-alerts': {
            'KeySchema': [
                {'AttributeName': 'alert_id', 'KeyType': 'HASH'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'alert_id', 'AttributeType': 'S'}
            ]
        },
        'noisemaker-platform-connections': {
            'KeySchema': [
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'platform', 'KeyType': 'RANGE'}
            ],
            'AttributeDefinitions': [
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'platform', 'AttributeType': 'S'}
            ]
        }
    }
    
    created = 0
    exists = 0
    errors = 0
    
    print("🚀 Creating DynamoDB Tables...\n")
    
    for table_name, config in tables_config.items():
        try:
            # Build create_table params
            create_params = {
                'TableName': table_name,
                'KeySchema': config['KeySchema'],
                'AttributeDefinitions': config['AttributeDefinitions'],
                'BillingMode': 'PAY_PER_REQUEST'
            }

            # Add GSI if defined
            if 'GlobalSecondaryIndexes' in config:
                create_params['GlobalSecondaryIndexes'] = config['GlobalSecondaryIndexes']

            dynamodb.create_table(**create_params)

            gsi_count = len(config.get('GlobalSecondaryIndexes', []))
            gsi_info = f" (with {gsi_count} GSI)" if gsi_count > 0 else ""
            print(f"✅ Created: {table_name}{gsi_info}")
            created += 1
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceInUseException':
                print(f"⚠️  Already exists: {table_name}")
                exists += 1
            else:
                print(f"❌ Error creating {table_name}: {e.response['Error']['Message']}")
                errors += 1
        except Exception as e:
            print(f"❌ Unexpected error with {table_name}: {str(e)}")
            errors += 1
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created}")
    print(f"   Already existed: {exists}")
    print(f"   Errors: {errors}")
    print(f"   Total tables: {len(tables_config)}")
    
    if errors > 0:
        sys.exit(1)
    
    return True

if __name__ == '__main__':
    print("Noisemaker DynamoDB Table Creation")
    print("=" * 50)
    create_tables()
    print("\n✅ All tables processed successfully!")
