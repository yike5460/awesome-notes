# Background

## Table of Contents
- [Introduction](#introduction)
- [Infrastructure](#infrastructure)
  - [UT Pipeline](#ut-pipeline)
  - [API Design](#api-design)
  - [Container](#container)
  - [GPU](#gpu)
  - [RUST](#rust)
  - [MAD](#mad)
- [GeneativeAI](#geneativeai)
  - [txt2txt](#txt2txt)
    - [Agent](#agent)
    - [Claude3](#claude3)
    - [Finetune](#finetune)
    - [LCEL](#lcel)
    - [MLM](#mlm)
    - [RAG](#rag)
    - [Web Integration](#web-integration)
  - [txt2img2vid](#txt2img2vid)
    - [CatScradle](#catscradle)
    - [CompyUI](#compyui)
    - [LoRA](#lora)
    - [sd3dalle](#sd3dalle)
- [DevOps](#devops)
  - [Constructor](#constructor)
  - [Container](#container)
  - [Math](#math)
- [Contributing](#contributing)
- [License](#license)

## Introduction
"The best way to learn something is to build it." someone might said it...

## Infrastructure

### UT Pipeline
Example implementation of unit testing pipeline with Selenium and Poetry:
- [UT Pipeline Example](examples/ut_pipeline)

### GPU
- [CUDA Programming](examples/GPU/CUDA)
  - LIFE Game implementation using CUDA
  - RDMA implementation
- [Parallel Processing](examples/GPU/parallel_processing)
  - Process lifecycle management
  - Threading and locking examples
  - Parallel processing patterns

### RUST
- [Rust Tutorial](examples/RUST/rust_tutorial)
  - Comprehensive examples covering Rust fundamentals
  - Advanced Rust features and patterns

### MAD (Modern Application Development)
- [Buttonize App Example](examples/MAD/my-buttonize-app)
  - AWS CDK implementation
  - Discount code generator application

## GeneativeAI

### txt2txt

#### Agent
- [Web Agent implementation with PyAutoGUI](examples/txt2txt/Agent/webAgent)
- [Triton acceleration examples](examples/txt2txt/Agent/AgentWeb/tritonSample.py)

#### Claude3
- [Claude3 integration examples](examples/txt2txt/Claude3)

#### Finetune
- [Model fine-tuning examples](examples/txt2txt/Finetune)

#### LCEL
- [LangChain Expression Language examples](examples/txt2txt/LCEL)

#### MLM
- [Masked Language Model implementations](examples/txt2txt/MLM)

#### RAG
- [Retrieval Augmented Generation examples](examples/txt2txt/RAG)
- [Role Play examples](examples/txt2txt/rolePlay)

#### Web Integration
- [Web crawler implementation](examples/txt2txt/webCrawler)
- [Web search integration](examples/txt2txt/webSearch)

### txt2img2vid

#### CatScradle
- [Image generation examples](examples/txt2img2vid/CatScradle)

#### CompyUI
- [ComfyUI integration](examples/txt2img2vid/CompyUI)

#### LoRA
- [Low-Rank Adaptation training examples](examples/txt2img2vid/LoRA)

#### sd3dalle
- [Stable Diffusion and DALL-E integration](examples/txt2img2vid/sd3dalle)

## DevOps

### Constructor
- [API implementation examples](examples/constructor/src)
- [Lambda function examples](examples/constructor/lambda)
- [API Documentation](examples/constructor/API.md)

### Container
- [Kubernetes deployment examples](examples/container/k8s)
- [Container management utilities](examples/container/depot)
- [Encryption utilities](examples/container/encrypt)

### Math
- [Mathematical computation examples](examples/math/math.ipynb)

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
This project is licensed under the terms specified in the LICENSE file.
