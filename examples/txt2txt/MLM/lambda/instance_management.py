# lambda/instance_management.py

import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sm_client = boto3.client('sagemaker')

def handler(event, context):
    logger.info("raw event: {} and event body {}".format(event, json.loads(event['body'])))
    http_method = event['httpMethod']
    if http_method == 'POST':
        payload = json.loads(event['body'])
        instance_name = payload['instanceName']
        instance_type = payload['instanceType']
        model_name = payload['modelName']
        # Call SageMaker API to create instance
        response = sm_client.create_endpoint(
            EndpointName=instance_name,
            EndpointConfigName=f'{instance_name}-config',
            ProductionVariants=[{
                'VariantName': 'AllTraffic',
                'ModelName': model_name,  
                'InitialInstanceCount': 1,
                'InstanceType': instance_type
            }]
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'GET':
        # Call SageMaker API to list instances  
        response = sm_client.list_endpoints()
        return {
            'statusCode': 200, 
            'body': json.dumps(response['Endpoints'])
        }
    elif http_method == 'PUT':
        instance_name = event['pathParameters']['instanceName']
        payload = json.loads(event['body'])
        # Call SageMaker API to update instance
        response = sm_client.update_endpoint(
            EndpointName=instance_name,
            EndpointConfigName=payload['endpointConfigName']  
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'DELETE':
        instance_name = event['pathParameters']['instanceName']
        # Call SageMaker API to delete instance
        response = sm_client.delete_endpoint(EndpointName=instance_name)
        return {
            'statusCode': 200,
            'body': json.dumps(response) 
        }