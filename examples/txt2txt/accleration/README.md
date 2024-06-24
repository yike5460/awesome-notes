## Quick Start

### LLAMA.CPP
```
git clone https://github.com/ggerganov/llama.cpp && cd llama.cpp && make -j4 && cd models/ && wget https://huggingface.co/TheBloke/vicuna-7B-v1.5-GGUF/resolve/main/vicuna-7b-v1.5.Q5_0.gguf && cd .. && ./main -m models/vicuna-7b-v1.5.Q5_0.gguf && ./server -m models/vicuna-7b-v1.5.Q5_0.gguf
```

Login to http://127.0.0.1:8080/ and start your conversation with LLM running locally.

### vLLM