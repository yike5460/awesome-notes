# lambda/model_management.py

import boto3
from botocore.exceptions import ClientError

import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

region = boto3.session.Session().region_name
sm_client = boto3.client('sagemaker')
smr_client = boto3.client('sagemaker-runtime')
iam_client = boto3.client('iam')

# Get environment variables
model_bucket = os.environ['model_bucket']
model_prefix = os.environ['model_prefix']

# Fix the image url for now
inference_image_uri = (
    f"763104351884.dkr.ecr.{region}.amazonaws.com/djl-inference:0.23.0-deepspeed0.9.5-cu118"
)

def get_endpoint_execution_role(role_name='AmazonSageMaker-ExecutionRole'):
    """
    Retrieves the AWS SageMaker execution role ARN from IAM.

    Parameters:
    role_name (str): The name of the SageMaker execution role to retrieve.

    Returns:
    str: The ARN of the SageMaker execution role.
    """    
    try:
        # Get the IAM role
        response = iam_client.get_role(RoleName=role_name)
        # Extract the role ARN
        role_arn = response['Role']['Arn']
        logger.info(f"Successfully retrieved role ARN: {role_arn}")
        return role_arn
    except ClientError as error:
        error_code = error.response['Error']['Code']
        if error_code == 'NoSuchEntity':
            logger.info(f"The role {role_name} does not exist.")
        else:
            logger.info(f"Unexpected error occurred: {error}")
        return None

def create_model(model_name, role, s3_code_artifact):
    """
    Creates a SageMaker model.

    Parameters:
    model_name (str): The name of the model.
    role (str): The ARN of the SageMaker execution role.
    inference_image_uri (str): The URI of the Docker image for the inference container.
    s3_code_artifact (str): The S3 URI of the model artifact.

    Returns: 
    dict: The response from the SageMaker `create_model` API call.    
    """
    try:
        create_model_response = sm_client.create_model(
            ModelName=model_name,
            ExecutionRoleArn=role,
            PrimaryContainer={
                "Image": inference_image_uri,
                "ModelDataUrl": s3_code_artifact
            }
        )
        logger.info("Model created successfully:", create_model_response)
        return create_model_response
    except ClientError as e:
        logger.info("Failed to create model:", e)
        return None

def handler(event, context):
    logger.info("raw event: {} and event body {}".format(event, json.loads(event['body'])))
    http_method = event['httpMethod']
    if http_method == 'POST':
        # Create new SageMaker model
        payload = json.loads(event['body'])
        model_name = payload['modelName']
        
        # Get the SageMaker execution role ARN
        role = get_endpoint_execution_role()
        if role is None:
            return {
                'statusCode': 500,
                'body': json.dumps("Failed to create model. Execution role not found.")
            }

        # Create the SageMaker model
        response = create_model(
            model_name=model_name,
            role=role,
            inference_image_uri=inference_image_uri,
            # assemble the s3 path using passing env variable bucket and prefix, 's3://bucket/prefix/model.tar.gz'
            s3_code_artifact="s3://" + model_bucket + "/" + model_prefix + "/" + model_name + ".tar.gz"
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'GET':
        # Call SageMaker API to list models
        response = sm_client.list_models()
        return {
            'statusCode': 200,
            'body': json.dumps(response['Models'])
        }
    elif http_method == 'PUT':
        model_name = event['pathParameters']['modelName']
        payload = json.loads(event['body'])
        # Consider to update the endpoint config that takes the new model and update the endpoint afterwward, no operation to update model for now, give such hint directly for now
        response = {
            'message': 'Model update is not supported. Consider updating the endpoint configuration instead.'
        }
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'DELETE':
        model_name = event['pathParameters']['modelName']
        # Call SageMaker API to delete model
        try:
            response = sm_client.delete_model(ModelName=model_name)
            return {
                'statusCode': 200,
                'body': json.dumps(response)
            }
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to delete model: {e}")
            }