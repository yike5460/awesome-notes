import boto3
import json
import os
# load environment variables
from dotenv import load_dotenv
load_dotenv()

bedrock = boto3.client(service_name="bedrock", region_name="us-east-1")
bedrock_runtime = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")

# Select the foundation model you want to customize
base_model_id = "cohere.command-light-text-v14:7:4k"
model_name = "finetune-model-qs"
# use fixed role for debugging purposes
role = os.getenv("SM_EXE_ROLE")

s3 = boto3.client("s3")

def validate_models():
    # list all models with fine tuning customizations
    for model in bedrock.list_foundation_models(
        byCustomizationType="FINE_TUNING")["modelSummaries"]:
        for key, value in model.items():
            # print only model arn, id, name and if customizationsSupported
            if key in ["modelArn", "modelId", "modelName", "customizationsSupported"]:
                print(f"{key}: {value}")
        print("-----\n")

def load_and_transform_dataset():
    """
    Before: schema of the dataset
    "rows":[
    {"row_idx":0,"row":{"id":"train_0","dialogue":"#Person1#: Hi, Mr. Smith. I'm Doctor Hawkins. Why are you here today?\n#Person2#: I found it would be a good idea to get a check-up.\n#Person1#: Yes, well, you haven't had one for 5 years. You should have one every year.\n#Person2#: I know. I figure as long as there is nothing wrong, why go see the doctor?\n#Person1#: Well, the best way to avoid serious illnesses is to find out about them early. So try to come at least once a year for your own good.\n#Person2#: Ok.\n#Person1#: Let me see here. Your eyes and ears look fine. Take a deep breath, please. Do you smoke, Mr. Smith?\n#Person2#: Yes.\n#Person1#: Smoking is the leading cause of lung cancer and heart disease, you know. You really should quit.\n#Person2#: I've tried hundreds of times, but I just can't seem to kick the habit.\n#Person1#: Well, we have classes and some medications that might help. I'll give you more information before you leave.\n#Person2#: Ok, thanks doctor.","summary":"Mr. Smith's getting a check-up, and Doctor Hawkins advises him to have one every year. Hawkins'll give some information about their classes and medications to help Mr. Smith quit smoking.","topic":"get a check-up"},"truncated_cells":[]},
    {...},
    ]

    After: schema of the dataset
    {"completion": "Mr. Smith's getting a check-up, and Doctor Haw...", "prompt": Summarize the following conversation.\n\n#Pers..."}
    {...}
    """
    transformed_data = []

    # Attempt to read the file as a whole JSON array first
    try:
        with open("train.txt", "r") as file:
            data = json.load(file)  # Attempt to parse the entire file content as JSON
        # If successful, process each row in the 'rows' key
        for row in data['rows']:
            transformed_data.append(transform_row(row))
    except json.JSONDecodeError:
        # If the file doesn't contain a single valid JSON object/array,
        # fall back to processing line by line or another strategy
        print("The file doesn't contain a single valid JSON object. Please check the format.")

    # Write transformed dataset to local directory with name train-summarization.jsonl
    with open("train-summarization.jsonl", "w") as file:
        for row in transformed_data:
            file.write(f"{row}\n")

def upload_dataset_to_s3(file_name = "train-summarization.jsonl", bucket = "your_bucket", name = "your_file_prefix"):
    # Upload the transformed dataset to S3
    s3.upload_file(file_name, bucket, name)

def transform_row(row):
    dialogue = row['row']['dialogue']
    summary = row['row']['summary']
    # Format according to the target schema
    transformed_row = {
        "prompt": f"Summarize the following conversation.\n\n{dialogue}",
        "completion": summary
    }
    return json.dumps(transformed_row)

def create_customization_job(job_name, train_data_uri, output_data_uri):
    # Create a model customization job
    bedrock.create_model_customization_job(
        customizationType="FINE_TUNING",
        jobName=job_name,
        customModelName=model_name,
        roleArn=role,
        baseModelIdentifier=base_model_id,
        hyperParameters = {
            "epochCount": "1",
            "batchSize": "8",
            "learningRate": "0.00001",
        },
        trainingDataConfig={"s3Uri": train_data_uri},
        outputDataConfig={"s3Uri": output_data_uri},
    )

    # Check for the job status
    status = bedrock.get_model_customization_job(jobIdentifier=job_name)["status"]
    print(f"Job status: {status}")

# Main entry point:
if __name__ == "__main__":
    # load and transform dataset
    # load_and_transform_dataset()
    
    # upload dataset to s3
    upload_dataset_to_s3("train-summarization.jsonl", "delete-me-jack-us-east-1", "fine-tune/train-summarization.jsonl")

    # validate available models
    # validate_models()

    # create customization job
    create_customization_job("fine-tune-05028-03","s3://delete-me-jack-us-east-1/fine-tune/train-summarization.jsonl", "s3://delete-me-jack-us-east-1/fine-tune/output")