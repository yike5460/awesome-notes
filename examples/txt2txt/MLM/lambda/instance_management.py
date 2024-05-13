# lambda/instance_management.py

import boto3
from botocore.exceptions import ClientError
from urllib.parse import unquote

import os
import re
import json
import logging
import time

import datetime
from json import JSONEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sm_client = boto3.client('sagemaker')

class DateTimeEncoder(JSONEncoder):
    """ Custom encoder for datetime objects """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # Format datetime object to ISO 8601 string (YYYY-MM-DDTHH:MM:SS)
            return obj.isoformat()
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)

def model_name_validation(model_name):
    # Member must satisfy regular expression pattern: ^[a-zA-Z0-9]([\-a-zA-Z0-9]*[a-zA-Z0-9])?
    if not re.match(r'^[a-zA-Z0-9]([\-a-zA-Z0-9]*[a-zA-Z0-9])?', model_name):
        return False
    return True

def create_endpoint_config(model_name, endpoint_name, instance_type):
    """
    Creates a SageMaker endpoint configuration.

    Parameters:
    endpoint_name (str): The name of the endpoint.
    instance_type (str): The type of instance to use for the endpoint.

    Returns:
    dict: The SageMaker endpoint configuration.
    """
    endpoint_config_name = f'{endpoint_name}-config'
    # skip the creation if the endpoint configuration already exists
    if endpoint_config_name in [config['EndpointConfigName'] for config in sm_client.list_endpoint_configs()['EndpointConfigs']]:
        logger.info(f"Endpoint configuration {endpoint_config_name} already exists.")
        return None
    # Validate the model name
    if not model_name_validation(model_name):
        return {
            'statusCode': 400,
            'body': json.dumps(f"Invalid model name: {model_name} accepted pattern: ^[a-zA-Z0-9]([\-a-zA-Z0-9]*[a-zA-Z0-9])?")
        }
    try:
        response = sm_client.create_endpoint_config(
            EndpointConfigName=endpoint_config_name,
            ProductionVariants=[{
                'VariantName': 'AllTraffic',
                'ModelName': model_name,
                # The initial instance count is set to 1
                'InitialInstanceCount': 1,
                'InstanceType': instance_type,
                'ContainerStartupHealthCheckTimeoutInSeconds': 15*60,
            }]
        )
        # wait for the endpoint configuration to be created, endpoint is not supported by waiter according to https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sagemaker.html, use describe loop instead
        while True:
            response = sm_client.describe_endpoint_config(EndpointConfigName=endpoint_config_name)
            if response['EndpointConfigName'] == endpoint_config_name:
                break
            # wait for 5 seconds before checking again
            time.sleep(5)
            logger.info(f"Waiting for endpoint configuration {endpoint_config_name} to be created.")
        
        logger.info(f"Endpoint configuration {endpoint_config_name} created successfully.")
        return response
    except ClientError as e:
        logger.error(f"Failed to create endpoint configuration: {e}")
        return None

def handler(event, context):
    logger.info("raw event: {} and context {}".format(event, context))
    http_method = event['httpMethod']
    # In consideration the body part can be None
    payload = json.loads(event['body']) if event['body'] else {}
    if http_method == 'POST':
        model_name = payload['modelName']
        endpoint_name = payload['endpointName']
        instance_type = payload['instanceType']
        # Create the endpoint configuration
        try:
            response = create_endpoint_config(model_name, endpoint_name, instance_type)
            # Call SageMaker API to create instance
            try:
                response = sm_client.create_endpoint(
                    EndpointName=f"{endpoint_name}",
                    # Member must satisfy regular expression pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
                    EndpointConfigName=f'{endpoint_name}-config'
                )
                return {
                    'statusCode': 200,
                    'body': json.dumps(response)
                }
            except ClientError as e:
                logger.error(f"Failed to create endpoint: {e}")
                return {
                    'statusCode': 500,
                    'body': json.dumps(f"Failed to create endpoint: {e}")
                }
        except ClientError as e:
            logger.error(f"Failed to create endpoint configuration: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to create endpoint configuration: {e}")
            }
    elif http_method == 'GET':
        # Check if endpoint name is provided, if yes return the endpoint details using describe_endpoint API otherwise list all endpoints
        if 'endpointName' not in payload:
            try:
                response = sm_client.list_endpoints()
            except ClientError as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps(f"Failed to list endpoints: {e}")
                }
            # Assemble the endpoint details
            endpoint_list = []
            if 'Endpoints' in response and response['Endpoints']:
                for endpoint in response['Endpoints']:
                    endpointName = endpoint['EndpointName']
                    endpointArn = endpoint['EndpointArn']
                    creationTime = endpoint['CreationTime']
                    lastModifiedTime = endpoint['LastModifiedTime']
                    endpointStatus = endpoint['EndpointStatus']
                    endpoint_list.append({
                        'EndpointName': endpointName,
                        'EndpointArn': endpointArn,
                        'CreationTime': creationTime.strftime('%Y-%m-%d %H:%M:%S'),
                        'LastModifiedTime': lastModifiedTime,
                        'EndpointStatus': endpointStatus
                    })
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f"No endpoint found in response: {response}")
                }
            return {
                'statusCode': 200,
                'body': json.dumps(endpoint_list, cls=DateTimeEncoder)
            }

        # Decode the URL-encoded endpoint name, only operate in describe_endpoint for now
        endpoint_name = unquote(payload['endpointName'])
        try:
            response = sm_client.describe_endpoint(EndpointName=endpoint_name)
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to get endpoint: {e}")
            }
        return {
            'statusCode': 200,
            'body': json.dumps(response, cls=DateTimeEncoder)
        }
    elif http_method == 'PUT':
        endpoint_name = payload['endpointName']
        # Call SageMaker API to update instance
        response = sm_client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=payload['endpointConfigName']
            # RetainAllVariantProperties
            # ExcludeRetainedVariantProperties
            # DeploymentConfig
            # RetainDeploymentConfig
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'DELETE':
        endpoint_name = payload['endpointName']
        # Call SageMaker API to delete instance
        try:
            response = sm_client.delete_endpoint(EndpointName=endpoint_name)
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to delete endpoint: {e}")
            }