# lambda/observability.py

import boto3
import json
from datetime import datetime, timedelta

cloudwatch_client = boto3.client('cloudwatch')

def handler(event, context):
    http_method = event['httpMethod']
    if http_method == 'GET':
        instance_name = event['queryStringParameters']['instanceName']
        metric_name = event['queryStringParameters']['metricName']
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        
        # Call CloudWatch API to get metrics
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/SageMaker',
            MetricName=metric_name,
            Dimensions=[
                {
                    'Name': 'EndpointName',
                    'Value': instance_name
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,
            Statistics=[
                'Average',
            ],
            Unit='Count'
        )
        
        metric_data = response['Datapoints']
        
        return {
            'statusCode': 200,
            'body': json.dumps(metric_data)
        }