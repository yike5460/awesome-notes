# lambda/observability.py

import boto3
import json
import logging

from datetime import datetime, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)

cloudwatch_client = boto3.client('cloudwatch', region_name='us-east-1')

def get_metric_statistics(namespace, metric_name, dimensions, start_time, end_time, period, statistics, unit):
    try:
        response = cloudwatch_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=statistics,
            Unit=unit
        )
        logging.info(f"Successfully retrieved metric statistics: {response}")
    except Exception as e:
        logger.error(f"Failed to get metric statistics: {e}")
        return None
    return response['Datapoints']

def handler(event, context):
    logger.info("raw event: {} and context {}".format(event, context))
    http_method = event['httpMethod']
    payload = json.loads(event['body'])
    endpoint_name = payload['endpointName']

    if http_method == 'GET':
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=30)
        # Check if the metric name if provided, if yes return the metric data otherwise scan all the metrics
        if 'metricName' not in payload:
            metric_data = {
                "SageMakerEndpointInvocationMetrics": {
                    "Invocation4XXErrors": get_metric_statistics('AWS/SageMaker', 'Invocation4XXErrors', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "Invocation5XXErrors": get_metric_statistics('AWS/SageMaker', 'Invocation5XXErrors', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "InvocationModelErrors": get_metric_statistics('AWS/SageMaker', 'InvocationModelErrors', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "Invocations": get_metric_statistics('AWS/SageMaker', 'Invocations', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "InvocationsPerCopy": get_metric_statistics('AWS/SageMaker', 'InvocationsPerCopy', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "InvocationsPerInstance": get_metric_statistics('AWS/SageMaker', 'InvocationsPerInstance', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum'], 'Count'),
                    "ModelLatency": get_metric_statistics('AWS/SageMaker', 'ModelLatency', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "ModelSetupTime": get_metric_statistics('AWS/SageMaker', 'ModelSetupTime', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "OverheadLatency": get_metric_statistics('AWS/SageMaker', 'OverheadLatency', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds')
                },
                # TODO: adjust the metrics below to match the actual metrics with the correct dimensions
                "SageMakerInferenceComponentMetrics": {
                    "CPUUtilizationNormalized": get_metric_statistics('AWS/SageMaker/InferenceComponents', 'CPUUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUMemoryUtilizationNormalized": get_metric_statistics('AWS/SageMaker/InferenceComponents', 'GPUMemoryUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUUtilizationNormalized": get_metric_statistics('AWS/SageMaker/InferenceComponents', 'GPUUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "MemoryUtilizationNormalized": get_metric_statistics('AWS/SageMaker/InferenceComponents', 'MemoryUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent')
                },
                "SageMakerEndpointMetrics": {
                    "CPUReservation": get_metric_statistics('AWS/SageMaker/Endpoints', 'CPUReservation', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Count'),
                    "CPUUtilization": get_metric_statistics('AWS/SageMaker/Endpoints', 'CPUUtilization', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "CPUUtilizationNormalized": get_metric_statistics('AWS/SageMaker/Endpoints', 'CPUUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "DiskUtilization": get_metric_statistics('AWS/SageMaker/Endpoints', 'DiskUtilization', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUMemoryUtilization": get_metric_statistics('AWS/SageMaker/Endpoints', 'GPUMemoryUtilization', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUMemoryUtilizationNormalized": get_metric_statistics('AWS/SageMaker/Endpoints', 'GPUMemoryUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUReservation": get_metric_statistics('AWS/SageMaker/Endpoints', 'GPUReservation', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Count'),
                    "GPUUtilization": get_metric_statistics('AWS/SageMaker/Endpoints', 'GPUUtilization', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "GPUUtilizationNormalized": get_metric_statistics('AWS/SageMaker/Endpoints', 'GPUUtilizationNormalized', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent'),
                    "MemoryReservation": get_metric_statistics('AWS/SageMaker/Endpoints', 'MemoryReservation', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Bytes'),
                    "MemoryUtilization": get_metric_statistics('AWS/SageMaker/Endpoints', 'MemoryUtilization', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Percent')
                },
                "SageMakerMultiModelEndpointMetrics": {
                    "ModelLoadingWaitTime": get_metric_statistics('AWS/SageMaker', 'ModelLoadingWaitTime', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "ModelUnloadingTime": get_metric_statistics('AWS/SageMaker', 'ModelUnloadingTime', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "ModelDownloadingTime": get_metric_statistics('AWS/SageMaker', 'ModelDownloadingTime', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "ModelLoadingTime": get_metric_statistics('AWS/SageMaker', 'ModelLoadingTime', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Microseconds'),
                    "ModelCacheHit": get_metric_statistics('AWS/SageMaker', 'ModelCacheHit', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'SampleCount'], 'None'),
                    "LoadedModelCount": get_metric_statistics('AWS/SageMaker', 'LoadedModelCount', [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'None')
                }
            }
            return {
                'statusCode': 200,
                'body': json.dumps(metric_data)
            }

        metric_name = payload['metricName']
        # Call CloudWatch API to get metrics
        try:
            # Fix to namespace AWS/SageMaker for now
            response = get_metric_statistics('AWS/SageMaker', metric_name, [{'Name': 'EndpointName', 'Value': endpoint_name}], start_time, end_time, 60, ['Average', 'Sum', 'Minimum', 'Maximum', 'SampleCount'], 'Count')
        except Exception as e:
            return {
                'statusCode': 500,
                'body': json.dumps(f"Failed to get metric statistics: {e}")
            }
        # print("response: ", response)
        metric_data = response['Datapoints']
        return {
            'statusCode': 200,
            'body': json.dumps(metric_data)
        }

# # Main entry point for debugging purposes
# if __name__ == "__main__":
#     event = {
#         "httpMethod": "GET",
#         "body": json.dumps({
#             "endpointName": "etl-endpoint",
#             "metricName": "Invocation4XXErrors"
#         })
#     }
#     context = {}
#     print(handler(event, context))