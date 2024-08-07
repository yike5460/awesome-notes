
# Labeling data using Claude3 in Amazon Bedrock

## LoRA model training in Stable Diffusion
### Automatic image caption with Claude3
Refer the [sample code](../examples/txt2img2vid/LoRA/imageCaption.py) to use the Claude3 to automatically caption the images in the image folder. The code will generate the caption file with the same name as the image file. Also we also provide the sample code using CSE (Custom Search Engine) to download the images from the internet and store them in the image folder automatically.

## Intention identification in LLM RAG
### Automatic corpus labeling with Claude3

# OpenAI API proxy to redirect from GPT request to Claude
The implementation theory of an API proxy for OpenAI revolves around creating a middleware layer that intercepts API requests from clients and forwards them to the OpenAI API or other LLM API, handling additional operations such as request transforming, billing, and parsing before returning the response to the client. This setup allows users to interact with the OpenAI API through the proxy by simply changing the base URL in their requests to point to the proxy server instead of directly to OpenAI.

There are the [post implementation](https://github.dev/openai/openai-python/blob/5cfb125acce0e8304d12bdd39b405071021db658/src/openai/_base_client.py#L1194) and [base_url assignment](https://github.dev/openai/openai-python/blob/5cfb125acce0e8304d12bdd39b405071021db658/src/openai/_client.py#L305) inside OpenAI Python client code, that original OpenAI client will redirect the request to the URL assigned in OPENAI_BASE_URL, we can just start a local(FLASK e.g.)/remote API server(API Gateway & Lambda or use Application Load Balancer in consideration of Lambda code start) to listen to the request, transform the request schema and redirect to Claude3 API and vice versa.

# Auto Prompt Engineering

## Prompt Enhancement for existing Claude user
Brief introduction of the auto prompt engineering in Claude3, the auto prompt engineering is a process of revising the prompt automatically based on the feedback from the test cases. The process is as follows:
+ Input your original promote to generate a dataset of test cases 
+ Annotate generations with human feedback or do nothing if no
+ Input the feedback to Claude3 to re-write the prompt
+ Do the process iteratively until the prompt is satisfactory
![image](https://github.com/yike5460/justNotes/assets/23544182/ef25c044-4512-4953-8eef-dce4aedaff48)

Run the [sample code](../examples/txt2txt/Claude3/autoPE/autoPE.py) in to see the auto prompt engineering enhancement in action.
![image](https://github.com/yike5460/justNotes/assets/23544182/96425b74-8791-49b7-9c6d-cfc3d606b41c)
![image](https://github.com/yike5460/justNotes/assets/23544182/e24c86ef-4c42-4797-a956-38dd78e09f30)

## Prompt Transform for existing OpenAI user
Migrating Excellence from OpenAI to Claude, to not just match but surpass the output quality you've come to expect from OpenAI. The idea is similar that involving user to compare the outputs of both OpenAI and Bedrock, input the feedback on the differences or precedence for the outputs, such iteration process will end until user feel confident that the response generated from Bedrock with revised prompt is align or superior than the response generated from OpenAI.
Run the [sample code](../examples/txt2txt/Claude3/autoPE/compPE.py) in to see how such alignment can be achived using evloved prompt.
![image](https://github.com/yike5460/justNotes/assets/23544182/64709c33-bff7-4ccc-a48b-fee402dc9aeb)


