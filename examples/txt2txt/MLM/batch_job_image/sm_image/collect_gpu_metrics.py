import boto3
import subprocess
import time

cloudwatch = boto3.client('cloudwatch')

while True:
    # Get GPU utilization
    gpu_util = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,nounits,noheader'])
    gpu_util = int(gpu_util.decode().strip())
     
    # Get GPU memory utilization
    gpu_mem_util = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.memory', '--format=csv,nounits,noheader'])  
    gpu_mem_util = int(gpu_mem_util.decode().strip())

    # Put metrics into CloudWatch
    cloudwatch.put_metric_data(
        Namespace='AWS/SageMaker',
        MetricData=[
            {
                'MetricName': 'GPUUtilization',
                'Dimensions': [
                    {
                        'Name': 'EndpointName',
                        'Value': 'my-endpoint'
                    },
                ],
                'Unit': 'Percent',
                'Value': gpu_util
            },
            {
                'MetricName': 'GPUMemoryUtilization',
                'Dimensions': [
                    {
                        'Name': 'EndpointName',
                        'Value': 'my-endpoint'  
                    },
                ],
                'Unit': 'Percent',
                'Value': gpu_mem_util
            },
        ]
    )
    
    time.sleep(60) # Wait 1 minute before collecting next metrics