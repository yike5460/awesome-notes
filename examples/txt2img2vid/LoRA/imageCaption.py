import os
import json
import base64
import boto3
import logging
from botocore.exceptions import ClientError

# Set up logging to output to current stdout for debugging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

downloaded_images_path = 'downloaded_images'
caption_keyword = 'jeff bezos'

# Initialize the Amazon Bedrock boto3 client
bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name="us-east-1")

prompt_template = """
You have profound knowledge and hands-on experience in LoRA model training, especially in the field of dataset preparation including image captioning.
You are required to describe the content of images with {_style} style. The output should be: 
(1) a sentence no more than 100 words, describing the image content, such as the objects, actions, and scenes in the image;
(2) without any subjective opinions or emotionsm, without any beginning or ending words just the sentence;
(3) append special symbol <placehoder> in the very beginning of the sentence.
The sample output should be:
- <placehoder>, A person is riding a bike on the street.
- <placehoder>, A cat is sitting on the sofa.
- <placehoder>, A dog is running on the grass.
"""

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
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages
    })

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())

    return response_body

def add_image_captions(image_directory, model_id, max_tokens=1000):
    """
    Iterates over all images in a directory, sends them to Claude3 via Amazon Bedrock for
    captioning, and writes the captions to corresponding text files.
    Args:
        image_directory (str): The directory containing the images to process.
        model_id (str): The model ID to use with Claude3.
        max_tokens (int): The maximum number of tokens to generate.
    Returns:
        None.
    """
    for image_filename in os.listdir(image_directory):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            image_path = os.path.join(image_directory, image_filename)
            try:
                with open(image_path, "rb") as image_file:
                    content_image = base64.b64encode(image_file.read()).decode('utf8')

                message = {
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": content_image}},
                        {"type": "text", "text": prompt_template.format(_style="photorealism")}
                    ]
                }

                messages = [message]
                response = run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens)
                logger.info("run_multi_modal_prompt response: ", response)
                # Assuming the response contains a 'text' field with the caption.
                if response and 'text' in response['content'][0]:
                    caption = response['content'][0]['text']
                    caption_filename = os.path.splitext(image_path)[0] + '.txt'
                    with open(caption_filename, 'w') as f:
                        # relace the <placehoder> with caption_keyword
                        caption = caption.replace('<placehoder>', caption_keyword)
                        f.write(caption)
                    logger.info(f"Caption added for {image_filename}")
                else:
                    logger.info(f"Failed to add caption for {image_filename}")

            except IOError as e:
                logger.info(f"Error processing image {image_path}: {e}")
            except ClientError as err:
                message = err.response["Error"]["Message"]
                logger.info(f"A client error occurred: {message}")

# Example usage:
model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
add_image_captions(downloaded_images_path, model_id, max_tokens=1000)
