import os
import json
import base64
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging to output to current stdout for debugging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Create console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler)

# Initialize the Amazon Bedrock boto3 client
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")
# aws bedrock list-foundation-models --region us-east-1 | jq '.modelSummaries[] | {modelId, modelName, providerName}'
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"

orignal_template = """
You are given an image containing a workflow diagram. Your task is to:
1. Identify the content of the image and describe the workflow in detail.
2. Extract the objects and their relationships.
3. Transform the extracted workflow into Mermaid chart code.

Here is the image data (in base64 format): {image_data}

Please provide the detailed description first, followed by the Mermaid chart code.
"""

"""
revise the prompt using claude prompt generator: https://github.com/aws-samples/claude-prompt-generator
TODO: 
(1) More example on the mermaid template as few shots for model to choose the optimzed schema according to the description;
(2) PE to obtain the more accurate description for the workflow diagram;
"""
prompt_template = """
<instruction_guide>
# Instruction Guide

## Be clear & direct

Your task is to analyze a workflow diagram in an image and provide a detailed description of the workflow. Additionally, you need to:

1. Extract the objects and their relationships from the image.
2. Transform the extracted workflow into Mermaid chart code.

Follow these steps:

1. Identify the content of the given image uploaded {placeholder}.
2. Describe the workflow in detail, including all the steps and their relationships.
3. Extract the objects (steps, decisions, etc.) and their relationships from the workflow.
4. Use the extracted information to generate Mermaid chart code representing the workflow.

Your response should be structured as follows:

<description>
[Detailed description of the workflow]
</description>

<mermaid>
[Mermaid chart code representing the workflow]
</mermaid>

## Use examples

Here is an example of how your response should be formatted:

<example>
<description>
This workflow diagram represents the process of ordering food at a restaurant. It starts with a customer entering the restaurant and being seated by the host. The server then takes the customer's order and passes it to the kitchen. The kitchen prepares the food and sends it back to the server, who delivers it to the customer. After the customer finishes their meal, they pay the bill and leave the restaurant.
</description>

<mermaid>
graph TD
    A[Customer enters restaurant] --> B[Seated by host]
    B --> C[Server takes order]
    C --> D[Order passed to kitchen]
    D --> E[Kitchen prepares food]
    E --> F[Food sent back to server]
    F --> G[Server delivers food to customer]
    G --> H[Customer finishes meal]
    H --> I[Customer pays bill]
    I --> J[Customer leaves restaurant]
</mermaid>
</example>

</instruction_guide>
"""

def encode_image(image_path):
    logger.info(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens):
    """
    Invokes a model with a multimodal prompt.
    Args:
        bedrock_runtime: The Amazon Bedrock boto3 client.
        model_id (str): The model ID to use.
        messages (JSON): The messages to send to the model.
        max_tokens (int): The maximum number of tokens to generate.
    Returns:
        The response from the model.
    """
    logger.info(f"Running multimodal prompt with model ID: {model_id}")
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages
    })

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())
    logger.info(f"Response: {response_body}")
    return response_body

def extract_workflow_to_mermaid(response):
    logger.info(f"Extracting workflow details from response")
    workflow_details = response['content'][0]['text']  # Adjust based on actual response structure
    # extract the detailed description according to the prompt template
    detailed_description = workflow_details.split("<description>")[1].split("</description>")[0].strip()
    logger.info(f"Extracted detailed description: {detailed_description}")
    # extract the mermaid chart code according to the prompt template
    mermaid_code = workflow_details.split("<mermaid>")[1].split("</mermaid>")[0].strip()
    logger.info(f"Extracted Mermaid code: {mermaid_code}")
    return mermaid_code

if __name__ == "__main__":
    image_path = "Web-Crawler.png"
    try:
        encoded_image = encode_image(image_path)
        message = {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encoded_image}},
                {"type": "text", "text": prompt_template.format(placeholder="")}
            ]
        }
        messages = [message]
        response = run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens=4096)
        if response and 'text' in response['content'][0]:
            mermaid_code = extract_workflow_to_mermaid(response)
    except ClientError as e:
        logger.error(e)