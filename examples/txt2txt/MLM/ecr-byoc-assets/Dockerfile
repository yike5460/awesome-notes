# Make sure to login to public ECR before building the image: aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 763104351884.dkr.ecr.us-west-2.amazonaws.com

# Refer the official documentation for the base image at https://github.com/aws/deep-learning-containers/blob/master/available_images.md
FROM 763104351884.dkr.ecr.us-west-2.amazonaws.com/djl-inference:0.27.0-deepspeed0.12.6-cu121

# RUN pip install --no-cache-dir boto3

# Copy model files
COPY model.py requirements.txt /opt/ml/code/

# Copy custom metric collection script 
COPY collect_gpu_metrics.py /opt/ml/code/

# Copy shell script to launch Python metric collection
COPY start.sh /opt/ml/code/
RUN chmod +x /opt/ml/code/start.sh

# Set the entrypoint to the shell script
ENTRYPOINT ["/opt/ml/code/start.sh"]
