import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
user_id = 'NjEtnuD9dx5ywxLWwmVOqw'

# Get all tables that start with noisemaker
client = boto3.client('dynamodb', region_name='us-east-2')
tables = [t for t in client.list_tables()['TableNames'] if t.startswith('noisemaker')]

print(f"Scanning {len(tables)} tables for user: {user_id}\n")

for table_name in sorted(tables):
    table = dynamodb.Table(table_name)
    try:
        # Try query with user_id as partition key
        response = table.query(KeyConditionExpression=Key('user_id').eq(user_id))
        if response['Items']:
            print(f"=== {table_name} ({len(response['Items'])} items) ===")
            for item in response['Items']:
                for k, v in item.items():
                    print(f"  {k}: {v}")
                print()
    except:
        try:
            # Try scan for tables with different key structure
            response = table.scan(FilterExpression=Key('user_id').eq(user_id))
            if response['Items']:
                print(f"=== {table_name} ({len(response['Items'])} items) ===")
                for item in response['Items']:
                    for k, v in item.items():
                        print(f"  {k}: {v}")
                    print()
        except:
            pass

print("--- DONE ---")