# Web Agent

Tools to automate the human operation in web pages, e.g. search the information per query, record the notes to specific application, etc. Powered by Large Language Model, agent framework and model to recognize detailed layout in web pages.

## Core module

### Web page parser

Refer to [WebPageParser](https://github.com/microsoft/OmniParser) to start the tutuial.

1. Download the weight from [Hugging Face](https://huggingface.co/microsoft/OmniParser/tree/main) using HF CLI.

Install HF CLI if not installed:

```bash
pip install -U "huggingface_hub[cli]"
```

Make sure you have enough space to download the weight, remove unused weights if necessary, check the disk usage to find the largest folder in maximum 2 level start with home user folder:

```bash
du -h --max-depth=2 <your folder path> | sort -rh | head -n 10
e.g. du -ah --max-depth=2 /home/ubuntu/.cache/huggingface | sort -rh | head -n 10
```

Download the weight from the entire repo:

```bash
huggingface-cli download microsoft/OmniParser
```

Or specific weight:

```bash
cd weights
huggingface-cli download microsoft/OmniParser icon_detect/model.safetensors --local-dir .
huggingface-cli download microsoft/OmniParser icon_detect/model.yaml --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_florence/config.json --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_florence/generation_config.json --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_florence/model.safetensors --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/config.json --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/generation_config.json --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/pytorch_model-00001-of-00002.bin --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/pytorch_model-00002-of-00002.bin --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/pytorch_model-00001-of-00002.safetensors --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/pytorch_model-00002-of-00002.safetensors --local-dir .
huggingface-cli download microsoft/OmniParser icon_caption_blip2/pytorch_model.bin.index.json --local-dir .
```

2. Run the parser to parse the web page.

To find specific characters in a specific folder and show the line numbers, you can use the following command:

```bash
find . -type f -exec grep -Hn "best.pt" {} +
```

