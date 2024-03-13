# Lambda to get GitHub PR content
import os
import boto3
import requests
import json
import logging
from dotenv import load_dotenv

# Set up logging to output to current stdout for debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
load_dotenv()

# get the repo name from the environment variables, OWNER/REPO
# repo_name_list = os.environ['RepoNameList']
repo_name_list = [os.getenv('RepoNameList')]

# get the GitHub access token from the environment variables
access_token = os.getenv('GITHUB_PAT')

GITHUB_API_ROOT = 'https://api.github.com/repos/'

# Initialize the LLM client
bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

prompt_template = """
Below are PR content with format of a list, each item include PR title, description and link:
```
{_pr_list}
```
Please categorize the GitHub PR contents with the following categories: New Features, Bug Fixes, Enhancements, and Others.
Then, analyze the GitHub PR contents with each category and summarize their common requirements into bullet points.
1. DO NOT make up any information, only summarize the common requirements from the PRs, 
2. The bullet points should be concise and capture the essence of the PRs,
3. The number of bullet point within each category should not exceed 5, the length of each bullet point should not exceed 500 characters, the total length of the bullet points should not exceed 10,
4. Try to include all the related PR links in the summary for reference if such PR is contributing to the bullet point,
5. The output format should be in markdown which can be paste for preview directly without any beginning or ending words, the expected output format and result are as follows:

- New Features:
    - Summary 1, possibly PR link1, PR link2
    - Summary 2, possibly PR link3, PR link4
- Bug Fixes:
    - Summary 3, possibly PR link5, PR link6
    - Summary 4, possibly PR link7, PR link8
- Enhancements:
    - Summary 5, possibly PR link9, PR link10
    - Summary 6, possibly PR link11, PR link12
- Others:
    - Summary 7, possibly PR link13, PR link14
    - Summary 8, possibly PR link15, PR link16
"""

# Function to fetch PRs from GitHub
def fetch_prs(repo_name):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    # PR content with format of a list, each item include PR title, description and link, e.g., [{PR title: xx,}, 'PR2']
    prs = []
    """
    Refer to https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28
    curl -L \
        -H "Accept: application/vnd.github+json" \
        -H "Authorization: Bearer <YOUR-TOKEN>" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        https://api.github.com/repos/OWNER/REPO/pulls
    """
    page_rage = 50
    # Fetch closed PRs only
    for state in ['closed']:
        url = f'{GITHUB_API_ROOT}{repo_name}/pulls?state={state}&per_page={page_rage}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logger.info(f'Fetched PRs from {repo_name} with state {state}')
        pr_data = response.json()
        for pr in pr_data:
            # Create a dictionary with the PR title, description (body), and link
            pr_details = {
                'title': pr['title'],
                'description': pr['body'],
                'link': pr['html_url']
            }
            prs.append(pr_details)
    return prs

# Function to invoke AWS Bedrock LLM (Claude2/3)
def summarize_prs(pr_list):
    prompt = prompt_template.format(
        _pr_list=pr_list
    )

    accept = "*/*"
    contentType = "application/json"
    # uncomment below code to see the difference between claude2 and claude3
    # modelId = "anthropic.claude-v2"
    # prompt = "\n\nHuman:{}".format(prompt) + "\n\nAssistant:"
    # body = json.dumps(
    #     {
    #         "prompt": prompt,
    #         "temperature": 0.1,
    #         "top_p": 1,
    #         "top_k": 0,
    #         "max_tokens_to_sample": 500,
    #         "stop_sequences": ["\n\nHuman:"],
    #     }
    # )

    """ 
    For multi-modal models, the "messages" field schema is as follows:
    "messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "mediaType": "image/jpeg",
                        "data": "base64_encoded_image"
                    }
                }
                {
                    "type": "text",
                    "text": "what is this image about?"
                }
            ]
        }
    ]
    refer to https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-anthropic-claude-messages.html for more details
    """
    modelId = "anthropic.claude-3-sonnet-20240229-v1:0"
    body = json.dumps(
        {
            "max_tokens": 1024,
            "system": "You are an experience solution architect & developer in AWS offering customer professional boilerplate solution to help on actual project landing, especially in DevOps field.",
            "messages": [{"role": "user", "content": prompt}],
            "anthropic_version": "bedrock-2023-05-31",
            "temperature": 0.1,
            "top_p": 1,
            "top_k": 0,
            # "stop_sequences": ["\n\nHuman:"],
        }
    )
    response = bedrock_client.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())

    # Extract the text content from the response
    message_content = response_body.get('content')
    if message_content and isinstance(message_content, list):
        # Assuming the first item in the list is the one with the 'text' type
        text_content = next((item for item in message_content if item['type'] == 'text'), {}).get('text', '')
    else:
        text_content = ''

    # Split the text content into lines and remove empty lines
    completion = [line for line in text_content.split("\n") if line.strip()]
    return completion

# Entry point for the Lambda function
def handler(_event, _context):
    all_prs = []
    for repo_name in repo_name_list:
        prs = fetch_prs(repo_name)
        all_prs.extend(prs)
    # Convert the list of PR details into a format suitable for summarization
    pr_list = [f"Title: {pr['title']}\nDescription: {pr['description']}\nLink: {pr['link']}\n" for pr in all_prs]
    
    # logger.info('All PRs: {pr_list}')
    summarization = summarize_prs(pr_list)
    print(f'Summarization: {summarization}')
    # Do something with the summarization, e.g., store in a database or send it somewhere
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'PR summarization completed',
            'summarization': summarization
        })
    }

# main entry point for debugging
if __name__ == '__main__':
    handler({}, {})