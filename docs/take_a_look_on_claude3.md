
# Labeling data using Claude3 in Amazon Bedrock

## LoRA model training in Stable Diffusion
### Automatic image caption with Claude3
Refer the code in examples/LoRA/imageCaption.py to use the Claude3 to automatically caption the images in the image folder. The code will generate the caption file with the same name as the image file. Also we also provide the sample code using CSE (Custom Search Engine) to download the images from the internet and store them in the image folder automatically.

## Intention identification in LLM RAG
### Automatic corpus labeling with Claude3

## OpenAI API proxy to redirect from GPT request to Claude

The implementation theory of an API proxy for OpenAI revolves around creating a middleware layer that intercepts API requests from clients and forwards them to the OpenAI API or other LLM API, handling additional operations such as request transforming, billing, and parsing before returning the response to the client. This setup allows users to interact with the OpenAI API through the proxy by simply changing the base URL in their requests to point to the proxy server instead of directly to OpenAI.

There are the [post implementation](https://github.dev/openai/openai-python/blob/5cfb125acce0e8304d12bdd39b405071021db658/src/openai/_base_client.py#L1194) and [base_url assignment](https://github.dev/openai/openai-python/blob/5cfb125acce0e8304d12bdd39b405071021db658/src/openai/_client.py#L305) inside OpenAI Python client code, that original OpenAI client will redirect the request to the URL assigned in OPENAI_BASE_URL, we can just start a local(FLASK e.g.)/remote API server(API Gateway & Lambda or use Application Load Balancer in consideration of Lambda code start) to listen to the request, transform the request schema and redirect to Claude3 API and vice versa.
