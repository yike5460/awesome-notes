# History

Quadrant division in LLM to performant in downstream tasks:

* Prompt Engineering: This is crucial for guiding the model's behavior through well-crafted prompts, ensuring the responses are aligned with user intent.
* Fine-tuning: Fine-tuning allows the model to specialize in specific tasks or domains, enhancing its effectiveness and accuracy.
* RAG: This involves the model retrieving relevant data from external sources and using it to generate informed responses, ensuring accuracy and relevance.
* All of Above: The model should have a holistic understanding, incorporating diverse techniques to handle various scenarios.

Orchestration of Information and Decision Making:

* Chat: The model engages in dialogues, providing coherent and contextually aware responses.
* Agent: It acts as an autonomous entity, making decisions and performing tasks based on the information it processes.
* RAG: The integration of retrieval mechanisms ensures the model's responses are informed and accurate, combining the strengths of both retrieval and generation.

![History](./img/history.png)

Model as a Service (MaaS) is an AI method hosted in the cloud that offers developers and businesses the ability to utilize pre-built, pre-trained or customized machine learning models. These models encompass a diverse array of AI functions, such as natural language processing (NLP), computer vision, recommendation systems etc.. MaaS streamlines the incorporation of AI capabilities into applications, without constructing & maintain the whole workflow including data preparation, model training & tuning and infrastructure operation from scratch, allowing businesses to concentrate on addressing practical challenges.

![MaaS](./img/maas.png)


summarize the core function provided by Azure AI studio categorized into classes below: Data management, Model fine-tune, Prompt management, Inference acceleration, Model evaluation, Tracing and debugging, API/SDK support, Other

# Markteting Analyze
Overall, we observe that most of the MaaS providers are focusing on the following aspects beside the managed foundation model:
- Data management, including data pre-processing (ETL), labeling and augmentation, data compression for network transmission, etc.
- Prompt management: including built-in prompt templates for different tasks, few shot management, etc.
- Model fine-tune, including post-training optimization, SFT/SFT-LORA, RLHF, incremental training, etc.
- Inference acceleration, including hardware acceleration (e.g. custom chip, heterogeneous gpu for decoupled prefill & decode), software optimization (flashAttension, quantization, cache etc.) without aware of the underlying infrastructure
- Model evaluation, including model comparison, auto/manual evaluation, etc.
- Data privacy, including multi-tenancy, model encryption, sandbox isolation, etc.
- Tracing and debugging, full path observability from data pre-processing, intention detection, knowledge retrieval to llm output with metrics including extracted knowledge metadata, identified intention, tools used, llm inference latency and token output, etc.
- API/SDK support, including RESTful API, multi-language SDK, etc.

Some of the MaaS providers been observed are:
- Azure: Azure AI Studio
- 阿里云: Dash Scope
- 腾讯云
- 百度千帆: Model Builder
- 字节跳动: 火山方舟
- 商汤: SensorCore
- 第四范式: Model Hub 
- 智谱AI

# System Overview
* Model Lifecycle Management, CRUD operation on model, dataset and associate infrastructure (SageMaker Endpoint)
* Model Efficiency, accelerate inference with hardware (customized chip) and software (optimized operator, LMI, model quantization, hosted fine tuning etc.)
    * do we know top 3 techniques are used in consideration for its maturity, performance and eco-system?
    * can we implement the top 3 techniques prototype and commercialization with automation, low code etc.
* Intention Management, allow user to inject their application specific prompt template along with tools involved to customize the  intention detection, besides the built-in prompt templates and tools
* Model Evaluation, explainable AI with objective metric and evaluation method (e.g. RAGAS) 
* Tracing, debugging and visualization of the stats from PE, embedding, retrieval
* Filter & particularize content restrictions using AWS Guardrails
* Full fledge RESTful API and multi-language SDK
* Data Privacy, multi-tenancy with least privilege 

## Model Lifecycle Management

Model lifecycle management module including instance resource CRUD operations (create, update, delete), model resource management (model create, update, delete, list), instance resource observability (instance number, instance status, GPU usage, in-flight request number), backed by AWS SageMaker endpoint, with OpenAPI conformed RESTful API expose to client for further UI integration.

### Core Submodules
- Model Preparation and Packaging: Handles the process of preparing models for deployment using AWS Batch, including:
    - Accepting user-specified model ID and platform (e.g., "THUDM/glm-4-9b-chat" on Hugging Face)
    - Creating and submitting AWS Batch jobs for model container building
    - Packaging models per series
    - Uploading packaged models to specific S3 buckets for SageMaker Endpoint creation
- Instance Resource Management: Handles CRUD operations for SageMaker endpoint instances. Key functionalities:
    - Create new endpoint instances
    - Update existing endpoint instances (e.g. scale up/down, change instance type)
    - Delete endpoint instances
    - List and describe endpoint instances
- Model Resource Management: Manages the ML models deployed to SageMaker endpoints. Key functionalities:
    - Create new model versions
    - Update existing models (e.g. change model artifacts, containers)
    - Delete model versions
    - List and describe models and their versions
- Instance Observability: Provides visibility into the runtime metrics and status of SageMaker endpoint instances. Key metrics:
    - Number of instances per endpoint
    - Instance status (InService, Updating, Failed, etc.)
    - GPU utilization per instance
    - Number of in-flight inference requests per instance
- Model version management: Manages the versions of the models deployed to SageMaker endpoints along with their metadata, including training data/code, evaluation metrics/dataset and model artifacts itself.
- RESTful API Layer: Exposes the functionalities of the above submodules through a set of OpenAPI compliant RESTful APIs. The APIs will be used by client applications and UI for integration.

### Brief workflow

* Client applications/UI will send requests to the exposed APIs in API Gateway to perform model lifecycle management operations.
* API Gateway will route the requests to the appropriate Lambda functions based on the API path and HTTP method.
    * For model preparation and packaging: The Lambda function will submit a job to AWS Batch. AWS Batch will handle the container building, model packaging, and S3 upload processes. Upon job completion, AWS Batch will notify the Lambda function of the operation status.
    * For model and endpoint management: The Lambda functions will call the necessary SageMaker APIs to perform operations like creating/updating/deleting endpoint instances and models.
    * For observability: The Lambda function will call CloudWatch APIs to fetch metrics for the endpoint instances. The Lambda functions will return the API response to API Gateway, which will send it back to the client.

Consider the technical feasibility, e.g. can we execute docker build command inside AWS Lambda, potential service limitation, e.g. the hard limit 15 minutes of AWS Lambda processing time lead incomplete packaging job if the model size was large, or the base image pulling time longer than expected due to unstable network quality, service availability, e.g. Code Build service is not available in certain AWS regions, cost implication, e.g. the AWS EC2 can be idle since the model packaging job is not frequent thus incur unnecessary cost, we remove the AWS Lambda, EC2 and CodeBuild from the architecture and use AWS Batch to handle the model packaging job.

Below are the Mermaid code and the corresponding diagram for the overall workflow of the MLM module:

```mermaid
sequenceDiagram
    participant Client as Client App/UI
    participant APIGateway as API Gateway
    participant Lambda as Lambda Functions
    participant Batch as AWS Batch
    participant SageMaker as Amazon SageMaker
    participant CloudWatch as Amazon CloudWatch
    participant S3 as Amazon S3
    participant ECR as Amazon ECR
    
    Client->>APIGateway: Send API request
    APIGateway->>Lambda: Route request based on path/method
    
    rect rgb(255, 240, 245)
    note right of Lambda: Model Preparation and Packaging
    Lambda->>Batch: Submit job for container build and model packaging
    Batch->>ECR: Build and push model container
    ECR-->>Batch: Return container build status
    Batch->>S3: Package and upload model to S3
    S3-->>Batch: Return upload status
    Batch-->>Lambda: Return job completion status
    end

    rect rgb(240, 248, 255)
    note right of Lambda: Model Management
    Lambda->>SageMaker: Call SageMaker APIs for model CRUD  
    SageMaker-->>Lambda: Return model op response   
    end

    rect rgb(245, 255, 250)
    note right of Lambda: Endpoint Management
    Lambda->>SageMaker: Call SageMaker APIs for endpoint CRUD
    SageMaker-->>Lambda: Return endpoint op response
    end

    rect rgb(255, 250, 240)
    note right of Lambda: Endpoint Observability
    Lambda->>CloudWatch: Call CloudWatch APIs for metrics
    CloudWatch-->>Lambda: Return metrics
    end

    Lambda-->>APIGateway: Return API response
    APIGateway-->>Client: Return API response to client
```

And below are the UML diagrams for model version management in consideration of fine-tuning, evaluation and registry:
    
```mermaid
classDiagram
    class FoundationModel {
        version 1
    }
    class FineTuningDataAndCode {
        version 1
    }
    class PullFoundationModelMetadata {
        version 1
    }
    class FineTuneAdapterWeights {
        version 1
    }
    class AdaptedModel {
        version 1
    }
    class MergedModelVersion1 {
        version 1
    }
    class EvaluationDataAndCode {
        version 1
    }
    class ModelEvaluation {
        version 1
    }
    class EvaluationDatastore {
        version 1
    }
    class ModelRegistry {
        metadata for:
        - Foundation model
        - Adapted model
        - Merged model
    }

    FoundationModel --> PullFoundationModelMetadata : captures
    FineTuningDataAndCode --> FineTuneAdapterWeights : generates
    FineTuneAdapterWeights --> AdaptedModel : produces
    PullFoundationModelMetadata --> MergedModelVersion1 : integrates
    AdaptedModel --> MergedModelVersion1 : integrates
    EvaluationDataAndCode --> ModelEvaluation : inputs
    MergedModelVersion1 --> ModelEvaluation : evaluates
    ModelEvaluation --> EvaluationDatastore : stores
    FoundationModel --> ModelRegistry : registers
    AdaptedModel --> ModelRegistry : registers
    MergedModelVersion1 --> ModelRegistry : registers 
```

The MLM module will expose a set of RESTful APIs conforming to the OpenAPI specification. The OpenAPI specification will define the API paths, methods, request/response schemas, and security requirements. The OpenAPI specification will be used to generate client SDKs and server stubs for easy integration with client applications and UI. Refer to the [OpenAPI Specification](docs/OpenAPI_v1.1.yaml) for the detailed API definitions and Postman compatible [collection](docs/postman_collection_v1.1.json) to import and test the APIs directly.

## Model Efficiency

### acceleration with software

#### LMI with SageMaker
LMI DLCs offer a low-code interface that simplifies using state-of-the-art inference optimization techniques and hardware. LMI privide features some of the core features:
- Tensor Parallelism: Distributes the computational workload across multiple processing units, significantly speeding up model training and inference times.
- Efficient Attention: Optimizes attention mechanisms in models to enhance performance and reduce computational overhead.
- Batching: Aggregates multiple inference requests into a single batch to improve throughput and efficiency.
- Quantization: Reduces the precision of model weights and activations, leading to faster computation and reduced memory usage without significantly impacting accuracy.
- Memory Management: Efficiently allocates and manages memory resources to optimize performance and minimize bottlenecks.

Backend selection:
```mermaid
flowchart TD
    Start["Start"] --> HardwareSupport{"HardwareSupport"} & WorkloadSupport{"WorkloadSupport"}
    HardwareSupport -- Inf2 --> NeuronX["NeuronX SageMaker container"]
    HardwareSupport -- GPU --> ModelSelection{"Model Selection"}
    ModelSelection --> FalconLlama["Falcon, Llama2, Code Llama"] & T5Models["T5, MPT, GPT-NeoX, StarCoder"] & BaichuanMistral["Baichuan, Mistral"]
    WorkloadSupport -- Open-ended generation --> GenAITask["GenAITask"]
    GenAITask -- e.g. chatbots, code gen --> vLLM["vLLM DeepSpeed container"]
    WorkloadSupport -- Predictable input/output length --> PredictableIO["PredictableIO"]
    PredictableIO -- e.g. summarization --> TensorRT-LLM["TensorRT-LLM TRT-LLM container"]
    FalconLlama --> TokenLength{"Output Token length > 1024?"}
    TokenLength -- Yes --> LMI-Dist["LMI-Dist"]
    TokenLength -- No --> TensorRT-LLM
    T5Models --> LMI-Dist
    BaichuanMistral --> vLLM
    LMI-Dist -- Serving properties --> LMI-DistProps["engine=MPI, option.tensor_parallel_degree=max, option.model_id=, option.rolling_batch=lmi-dist"]
    TensorRT-LLM -- Serving properties --> TRT-LLMProps["engine=MPI, option.model_id="]
    vLLM -- Serving properties --> vLLMProps["engine=Python, option.tensor_parallel_degree=max, option.model_id=, option.rolling_batch=vllm"]
    style NeuronX fill:#FF6D00
    style vLLM fill:#FF6D00
    style TensorRT-LLM fill:#FF6D00
    style LMI-Dist fill:#FF6D00
```

* other accelerate framework

#### Multi-tier cache in web & backend
Using multi-tier cache to reduce the load on the backend and improve the response time of the system. The multi-tier cache can be implemented in web using local storage, browser cache, and CDN, and in backend using Redis, Memcached, and database cache.

web cache implementation sample using js:
```javascript
// Check if the data is present in the local storage
if (localStorage.getItem('data')) {
    // Use the data from the local storage
    const data = JSON.parse(localStorage.getItem('data'));
    console.log('Data from local storage:', data);
} else {
    // Fetch the data from the server
    fetch('https://api.example.com/data')
        .then(response => response.json())
        .then(data => {
            // Store the data in the local storage
            localStorage.setItem('data', JSON.stringify(data));
            console.log('Data from server:', data);
        });
}
```

backend cache implementation sample using Redis, e.g. managed by AWS Elasticache, implemented by AWS CDK:
```typescript
import * as elasticache from '@aws-cdk/aws-elasticache';

// Create a Redis cluster
const redisCluster = new elasticache.CfnCacheCluster(this, 'RedisCluster', {
    cacheNodeType: 'cache.t3.micro',
    engine: 'redis',
    numCacheNodes: 1,
    cacheSubnetGroupName: 'my-cache-subnet-group',
    vpcSecurityGroupIds: ['sg-12345678'],
});

// Create a cache policy
const cachePolicy = new elasticache.CfnParameterGroup(this, 'CachePolicy', {
    cacheParameterGroupFamily: 'redis6.x',
    description: 'Cache policy for Redis cluster',
    parameters: {
        'maxmemory-policy': 'allkeys-lru',
    },
});

// Associate the cache policy with the Redis cluster
redisCluster.addDependsOn(cachePolicy);
```

## Model Evaluation

LangSmith evaluators newly feature “self-improvement” whereby human corrections to [LLM-as-a-Judge](https://blog.langchain.dev/aligning-llm-as-a-judge-with-human-preferences/) outputs are stored as few-shot examples, which are then fed back into the prompt in future iterations. Inspired by the [paper](https://arxiv.org/pdf/2404.12272), it mentioned an EvalGen Interface which designed to assist users in generating evaluation criteria and implementing assertions for evaluating LLM outputs:
- Provides automated assistance in generating evaluation criteria and implementing assertions.
- Generates candidate implementations (Python functions, LLM grader prompts) and asks humans to grade a subset of LLM outputs.
- Uses human feedback to select implementations that align better with user grades.
The sample code for the EvalGen Interface can be refered to /test/Evalgen.py.
Either the EvalGen Interface or the LangSmith evaluators are just a few examples of how to evaluate LLM outputs, while the dataset prepared and annotated by human-in-the-loop can be further used to train the reward model for RLHF, e.g. use a BERT classifier to predict the probability distribution accross the positive and negative examples for given prompt completion pairs. For example:
The original pairwise of prompt-completion pairs are:
```mermaid
graph LR
    A[Prompt] --> B[Completions]
    B --> |Rank 1| C[A]
    B --> |Rank 2| D[B]
    B --> |Rank 3| E[C]
    C --> F[B]
    C --> G[C]
    D --> H[A]
    D --> I[C]
    E --> J[A]
    E --> K[B]
    F --> L([1,0])
    G --> M([1,0])
    H --> N([0,1])
    I --> O([1,0])
    J --> P([0,1])
    K --> Q([0,1])
```
And the transformed dataset for training the reward model is shown below:
| Prompt | Completion y_j (preferred) | Completion y_k (nonpreferred) | Rewards [r_j, r_k] |
|--------|-----------------------------|-------------------------------|--------------------|
| **Chris:** Hey Antje, do you like cats? <br> **Antje:** I hate cats. I'm allergic to them. | Chris asks Antje if she likes cats. <br> Antje does not like cats because she is allergic to them. | Chris asks Antje if she likes cats. <br> Antje hates cats. | [1, 0] |
| **Chris:** Hey Antje, do you like cats? <br> **Antje:** I hate cats. I'm allergic to them. | Chris asks Antje if she likes cats. <br> Antje hates cats. | Antje asks Chris if he likes cats. <br> Chris loves cats because they are fluffy, cute, and cuddly. | [1, 0] |
| **Chris:** Hey Antje, do you like cats? <br> **Antje:** I hate cats. I'm allergic to them. | Chris asks Antje if she likes cats. <br> Antje does not like cats because she is allergic to them. | Antje asks Chris if he likes cats. <br> Chris loves cats because they are fluffy, cute, and cuddly. | [1, 0] |





