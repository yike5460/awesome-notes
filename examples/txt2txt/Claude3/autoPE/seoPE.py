import base64
import json
import boto3

bedrock_runtime = boto3.client('bedrock-runtime')
default_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
bedrock_default_system = 'You are an AI assistant that generates SEO-optimized product descriptions.'

def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens):
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "messages": messages
    })

    response = bedrock_runtime.invoke_model(
        body=body, modelId=model_id)
    response_body = json.loads(response.get('body').read())

    return response_body

def generate_bedrock_response(prompt):
    message = {
        "role": "user",
        "content": [
            {"type": "text", "text": prompt}
        ]
    }
    messages = [message]
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4000,
        "messages": messages,
        "system": bedrock_default_system,
    })
    response = bedrock_runtime.invoke_model(body=body, modelId=default_model_id)
    response_body = json.loads(response.get('body').read())
    return response_body['content'][0]['text']

def main():
    # Step 1: Ask user for input
    product_category = input("Please provide the product category: ")
    brand_name = input("Please provide the brand name: ")
    usage_description = input("Please provide the usage description: ")
    target_customer = input("Please provide the target customer: ")
    image_path = input("Please provide the path to the product image (optional): ")

    # Step 2: Create prompt template
    prompt_template = f"""
    Generate an SEO-optimized product description for a {product_category} from {brand_name}. 
    Usage: {usage_description}
    Target customer: {target_customer}
    """

    if image_path:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        message = {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": encoded_image}},
                {"type": "text", "text": prompt_template}
            ]
        }
        messages = [message]
        response = run_multi_modal_prompt(bedrock_runtime, bedrock_model_id, messages, max_tokens=4000)
        image_description = response['content'][0]['text']
        prompt_template += f"\nImage description: {image_description}"

    # Step 3: Generate SEO-optimized product description
    product_description = generate_bedrock_response(prompt_template)
    print("Generated Product Description:")
    print(product_description)

if __name__ == "__main__":
    main()