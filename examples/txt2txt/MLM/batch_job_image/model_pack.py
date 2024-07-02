import os
import boto3
import tarfile
import shutil
from transformers import AutoTokenizer, AutoModel

s3 = boto3.client('s3')

def download_and_package_model(model_id, platform, ecr_repo, model_bucket):
    # Download the model from the specified platform (e.g., Hugging Face)
    if platform.lower() == 'huggingface':
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)
        
        # Save the model and tokenizer
        os.makedirs('model', exist_ok=True)
        tokenizer.save_pretrained('model')
        model.save_pretrained('model')
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # Create a tarball of the model
    with tarfile.open('model.tar.gz', 'w:gz') as tar:
        tar.add('model', arcname='.')

    # TODO, other customizations to package the model

    # Upload the tarball to S3
    s3.upload_file('model.tar.gz', model_bucket, f'{model_id}/model.tar.gz')

    # Clean up
    shutil.rmtree('model')
    os.remove('model.tar.gz')

    # Update the Dockerfile to construct the SageMaker image with new customized model
    with open('Dockerfile_sm', 'a') as f:
        f.write(f"\nCOPY --from=763104351884.dkr.ecr.us-west-2.amazonaws.com/djl-inference:0.27.0-deepspeed0.12.6-cu121 /opt/conda/lib/python3.10/site-packages/deepspeed /opt/conda/lib/python3.10/site-packages/deepspeed\n")
        f.write(f"ENV MODEL_S3_BUCKET={model_bucket}\n")
        f.write(f"ENV MODEL_S3_KEY={model_id}/model.tar.gz\n")
        # the sm_image folder is copied in the batch container beforehead
        f.write(f"COPY ./sm_image/model.py requirements.txt /opt/ml/code/\n")
        f.write(f"COPY ./sm_image/collect_gpu_metrics.py /opt/ml/code/\n")
        f.write(f"COPY ./sm_image/start_sm.sh /opt/ml/code/\n")

    # Build and push the Docker image using the updated Dockerfile Dockerfile_sm
    os.system(f"docker build -t {ecr_repo}:latest -f Dockerfile_sm .")
    os.system(f"docker push {ecr_repo}:latest")
    
    # Return the ECR repository URI that is ready to be deployed to SageMaker
    return f"{ecr_repo}:latest"

if __name__ == "__main__":
    model_id = os.environ['MODEL_ID']
    platform = os.environ['PLATFORM']
    ecr_repo = os.environ['ECR_REPO']
    model_bucket = os.environ['MODEL_BUCKET']

    res = download_and_package_model(model_id, platform, ecr_repo, model_bucket)

    