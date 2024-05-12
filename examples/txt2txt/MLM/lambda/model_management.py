# lambda/model_management.py

import boto3
from botocore.exceptions import ClientError
from urllib.parse import unquote

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
_model_bucket = os.environ['model_bucket']
_model_prefix = os.environ['model_prefix']
_role_name = os.environ['role_name']

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
            logger.info(f"Failed to retrieve role: {error}")
        return None

def create_model(model_name, role, s3_code_artifact):
    """
    Creates a SageMaker model.

    Parameters:
    model_name (str): The name of the model.
    role (str): The ARN of the SageMaker execution role, NOT required in RESTful API.
    inference_image_uri (str): The URI of the Docker image for the inference container, NOT required in RESTful API.
    s3_code_artifact (str): The S3 URI of the model artifact, NOT required in RESTful API.

    Returns: 
    dict: The response from the SageMaker `create_model` API call.    
    """
    logger.info(f"Creating model payload: {model_name}, {role}, {s3_code_artifact}")
    try:
        create_model_response = sm_client.create_model(
            ModelName=model_name,
            ExecutionRoleArn=role,
            PrimaryContainer={
                "Image": inference_image_uri,
                "ModelDataUrl": s3_code_artifact
            }
        )
        logger.info(f"Model created successfully: {create_model_response}")
        return create_model_response
    except ClientError as e:
        logger.error(f"Failed to create model: {e}")
        return e.response

def handler(event, context):
    logger.info("raw event: {} and context {}".format(event, context))
    http_method = event['httpMethod']
    payload = json.loads(event['body'])
    if http_method == 'POST':
        model_name = payload['modelName']
        # Get the SageMaker execution role ARN
        role = get_endpoint_execution_role(role_name=_role_name)
        if role is None:
            return {
                'statusCode': 500,
                'body': json.dumps("Failed to create model. Execution role not found.")
            }

        # Create the SageMaker model
        response = create_model(
            model_name=model_name,
            role=role,
            # inference_image_uri=inference_image_uri,
             # assemble the s3 path using passing env variable bucket and prefix, 's3://bucket/prefix/model.tar.gz'
            s3_code_artifact="s3://" + _model_bucket + "/" + _model_prefix + "/" + model_name + ".tar.gz"
        )
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'GET':
        # Check if the model name exists, if yes return the model details using describe_model API otherwise scan all models and return the list
        if 'modelName' not in payload:
            try:
                response = sm_client.list_models()
            except ClientError as e:
                return {
                    'statusCode': 500,
                    'body': json.dumps(f"Failed to list models: {e}")
                }
            # Assemble the model details
            model_list = []
            if 'Models' in response and response['Models']:
                for model in response['Models']:
                    model_name = model['ModelName']
                    model_arn = model['ModelArn']
                    creation_time = model['CreationTime']  # This is a datetime object
                    model_list.append({
                        'ModelName': model_name,
                        'ModelArn': model_arn,
                        'CreationTime': creation_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps(f"No model found in response: {response}")
                }

            return {
                'statusCode': 200,
                'body': json.dumps(model_list)
            }
        # Decode the URL-encoded model name, only operate in describe_model for now
        model_name = unquote(payload['modelName'])
        try:
            response = sm_client.describe_model(ModelName=model_name)
        except ClientError as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to get model: {e}")
            }
    elif http_method == 'PUT':
        model_name = payload['modelName']
        # Consider to update the endpoint config that takes the new model and update the endpoint afterwward, no operation to update model for now, give such hint directly for now
        response = {
            'message': 'Model update is not supported. Consider updating the endpoint configuration instead.'
        }
        return {
            'statusCode': 200,
            'body': json.dumps(response)
        }
    elif http_method == 'DELETE':
        model_name = payload['modelName']
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