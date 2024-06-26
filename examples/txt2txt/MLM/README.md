# Model Lifecycle Management (MLM)
model lifecycle management module including instance resource CRUD operations (create, update, delete), model resource management (model create, update, delete, list),  instance resource observability (instance number, instance status, GPU usage, in-flight request number), backed by AWS SageMaker endpoint, with OpenAPI conformed RESTful API expose to client for further UI integration.

## Core Submodules
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
- RESTful API Layer: Exposes the functionalities of the above submodules through a set of OpenAPI compliant RESTful APIs. The APIs will be used by client applications and UI for integration.

## Overall Workflow
Brief workflow of the MLM module:
- Client applications/UI will send requests to the exposed APIs in API Gateway to perform model lifecycle management operations.
- API Gateway will route the requests to the appropriate Lambda functions based on the API path and HTTP method.
    - For model preparation and packaging: The Lambda function will submit a job to AWS Batch. AWS Batch will handle the container building, model packaging, and S3 upload processes. Upon job completion, AWS Batch will notify the Lambda function of the operation status.
    - For model and endpoint management: The Lambda functions will call the necessary SageMaker APIs to perform operations like creating/updating/deleting endpoint instances and models.
    - For observability: The Lambda function will call CloudWatch APIs to fetch metrics for the endpoint instances.
The Lambda functions will return the API response to API Gateway, which will send it back to the client.

Consider the **technical feasibility**, e.g. can we execute docker build command inside AWS Lambda,
**potential service limitation**, e.g. the hard limit 15 minutes of AWS Lambda processing time lead uncomplete packaging job if the model size was large, or the base image pulling time longer than expected due to unstable network quality, 
**service availability**, e.g. Code Build service is not available in certain AWS regions,
**cost implication**, e.g. the AWS EC2 can be idle since the model packaging job is not frequent thus incur unnecessary cost, we remove the AWS Lambda, EC2 and CodeBuild from the architecture and use AWS Batch to handle the model packaging job.

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

## OpenAPI Specification
The MLM module will expose a set of RESTful APIs conforming to the OpenAPI specification. The OpenAPI specification will define the API paths, methods, request/response schemas, and security requirements. The OpenAPI specification will be used to generate client SDKs and server stubs for easy integration with client applications and UI.

Refer to the [OpenAPI Specification](docs/OpenAPI_v1.1.yaml) for the detailed API definitions and Postman compatible [collection](docs/postman_collection_v1.1.json) to import and test the APIs directly.

## Extent to MaaS (Model as a Service)
Refer to MLM considering model registry, and consider the possibility to evolve to MaaS (Model as a Service), core features should be included:
* Model Efficiency, accelerate inference with hardware (customized chip) and software (optimized operator, model quantisation etc.)
    * do we know top 3 techniques are used in consideration for its maturity, performance and eco-system?
    * can we implement the top 3 techniques prototype and commercialization with automation, low code etc.
* Data Privacy, multi-tenancy with least privilege 
* Model Lifecycle Management, CRUD operation on model, dataset and associate infrastructure (SageMaker Endpoint)
* Model Evaluation, explainable AI with objective metric and evaluation method (e.g. RAGAS) 
* Full fledge RESTful API and multi-language SDK

