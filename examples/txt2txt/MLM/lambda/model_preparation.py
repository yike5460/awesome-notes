import os
import boto3
import json

def handler(event, context):
    batch_client = boto3.client('batch')
    
    # Extract model information from the event
    model_info = json.loads(event['body'])
    model_id = model_info['model_id']
    platform = model_info['platform']
    
    # Submit a Batch job for model preparation and packaging
    response = batch_client.submit_job(
        jobName=f'prepare-model-{model_id}',
        jobQueue=os.environ['JOB_QUEUE'],
        jobDefinition=os.environ['JOB_DEFINITION'],
        containerOverrides={
            'environment': [
                {'name': 'MODEL_ID', 'value': model_id},
                {'name': 'PLATFORM', 'value': platform},
                {'name': 'ECR_REPO', 'value': os.environ['ECR_REPO']},
                {'name': 'MODEL_BUCKET', 'value': os.environ['MODEL_BUCKET']},
            ]
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Model preparation job submitted successfully',
            'jobId': response['jobId']
        })
    }