## Why Using Finetune?

## How to Use Finetune?

## Implementation Theory & Technical Stack

## Quick Start with AWS Bedrock
Basic steps according to video [here](https://www.youtube.com/watch?v=SdTWlQPy1jE) and [here](https://aws.amazon.com/blogs/aws/customize-models-in-amazon-bedrock-with-your-own-data-using-fine-tuning-and-continued-pre-training/):
- Select Your Base Model: Choose a base model provided by Amazon, such as Lama 2 or Titan. This model will serve as the foundation for your custom model.
- Provide Your Dataset: Supply your own dataset to the chosen base model. This dataset can contain specific information relevant to your needs, such as company data or personal data.
- Fine-Tune the Model: Use Amazon Bedrock to train the base model on your dataset. This process adapts the model to better understand and generate outputs based on your specific data.
- Access the Custom Model through AWS Console or SDK: After fine-tuning, your custom model is accessible for use. You can interact with it either through the AWS Console or programmatically via the AWS SDK (Boto3).
- Provision Throughputs: Before using your custom model, you need to purchase provision throughputs. This step is necessary for deploying your model for actual use.