import { App, Stack, StackProps, CfnOutput, Duration } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as iam from 'aws-cdk-lib/aws-iam';

import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as ecrdeploy from 'cdk-ecr-deployment';

export class MLMStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Create S3 bucket to hold the model.tar.gz
    const bucket = new s3.Bucket(this, 'ModelBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create SagemMaker image in ECR from local Dockerfile and pass the inference_image_uri to the Lambda function as environment variable to create the SageMaker model
    const ecrImage = new ecr.Repository(this, 'BYOCImage', {
      repositoryName: 'ecr-byoc-image',
    });
    
    const dockerImageAsset = new ecr_assets.DockerImageAsset(this, 'BYOCAsset', {
      directory: 'ecr-byoc-assets',
    });

    // Complete the dirty job of commands below:
    // # aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <your account id>.dkr.ecr.us-east-1.amazonaws.com
    // # docker build -t byoc-image .
    // # docker tag byoc-image:latest <your account id>.dkr.ecr.us-east-1.amazonaws.com/byoc-image:latest
    // # docker push <your account id>.dkr.ecr.us-east-1.amazonaws.com/byoc-image:latest

    // new ecrdeploy.ECRDeployment(this, 'DeployDockerImage', {
    //   src: new ecrdeploy.DockerImageName(dockerImageAsset.imageUri),
    //   dest: new ecrdeploy.DockerImageName(`${ecrImage.repositoryUri}:latest`),
    // });

    // Create SageMaker execution role with permission to access S3 bucket and full SageMaker access
    const sagemakerRole = new iam.Role(this, 'SageMakerRole', {
      assumedBy: new iam.ServicePrincipal('sagemaker.amazonaws.com'),
    });

    bucket.grantReadWrite(sagemakerRole);
    sagemakerRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonSageMakerFullAccess'));

    // Create the Lambda functions for each submodule
    const instanceManagementLambda = new lambda.Function(this, 'InstanceManagementFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'instance_management.handler',
      code: lambda.Code.fromAsset('lambda'),
      timeout: Duration.minutes(15),
    });

    const modelManagementLambda = new lambda.Function(this, 'ModelManagementFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,  
      handler: 'model_management.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        model_bucket: bucket.bucketName,
        // Fix for now
        model_prefix: 'model',
        role_name: sagemakerRole.roleName,
        inference_image_uri: ecrImage.repositoryUri,
      },
      timeout: Duration.minutes(15),
    });

    const observabilityLambda = new lambda.Function(this, 'ObservabilityFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'observability.handler',  
      code: lambda.Code.fromAsset('lambda'),
      timeout: Duration.minutes(15),
    });

    // Grant the Lambda functions access to the IAM to get the execution role, iam:GetRole action
    instanceManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['iam:GetRole', 'iam:PassRole'],
      resources: ['*'],
    }));

    modelManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['iam:GetRole', 'iam:PassRole'],
      resources: ['*'],
    }));

    // Grant the Lambda functions full access to the SageMaker
    instanceManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['sagemaker:*'],
      resources: ['*'],
    }));

    modelManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['sagemaker:*'],
      resources: ['*'],
    }));

    // Grant the Lambda functions full access to ECR to get the inference image
    instanceManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ecr:*'],
      resources: ['*'],
    }));

    modelManagementLambda.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['ecr:*'],
      resources: ['*'],
    }));

    // Grant the Lambda functions full access to CloudWatch Logs to get the SageMaker metrics
    observabilityLambda.addToRolePolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['cloudwatch:*'],
      resources: ['*'],
    }));

    // Create the API Gateway REST API
    const api = new apigw.RestApi(this, 'MLM-API', {
      restApiName: 'MLM Service',
      description: 'This service serve as entrypont of the model lifecycle management',
      endpointConfiguration: {
        types: [apigw.EndpointType.REGIONAL],
      },
      defaultCorsPreflightOptions: {
        allowHeaders: [
          "Content-Type",
          "X-Amz-Date",
          "Authorization",
          "X-Api-Key",
          "X-Amz-Security-Token",
        ],
        allowMethods: apigw.Cors.ALL_METHODS,
        allowCredentials: true,
        allowOrigins: apigw.Cors.ALL_ORIGINS,
      },
      deployOptions: {
        stageName: "v1",
        metricsEnabled: true,
        loggingLevel: apigw.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
        tracingEnabled: true,
      },
    });

    // Create API resources and methods
    const instancesResource = api.root.addResource('instances');
    instancesResource.addMethod('POST', new apigw.LambdaIntegration(instanceManagementLambda)); // Create instance
    instancesResource.addMethod('GET', new apigw.LambdaIntegration(instanceManagementLambda)); // List instances
    
    const instanceResource = instancesResource.addResource('{instanceName}');
    instanceResource.addMethod('GET', new apigw.LambdaIntegration(instanceManagementLambda)); // Describe instance
    instanceResource.addMethod('PUT', new apigw.LambdaIntegration(instanceManagementLambda)); // Update instance  
    instanceResource.addMethod('DELETE', new apigw.LambdaIntegration(instanceManagementLambda)); // Delete instance

    const modelsResource = api.root.addResource('models');  
    modelsResource.addMethod('POST', new apigw.LambdaIntegration(modelManagementLambda)); // Create model
    modelsResource.addMethod('GET', new apigw.LambdaIntegration(modelManagementLambda)); // List models
    
    const modelResource = modelsResource.addResource('{modelName}');
    modelResource.addMethod('GET', new apigw.LambdaIntegration(modelManagementLambda)); // Describe model  
    modelResource.addMethod('PUT', new apigw.LambdaIntegration(modelManagementLambda)); // Update model
    modelResource.addMethod('DELETE', new apigw.LambdaIntegration(modelManagementLambda)); // Delete model

    const metricsResource = api.root.addResource('metrics');
    metricsResource.addMethod('GET', new apigw.LambdaIntegration(observabilityLambda)); // Get instance metrics

    // Output the API Gateway URL and prefix
    new CfnOutput(this, 'API URL', {
      value: api.url ?? 'Something went wrong with the deploy',
    });
    new CfnOutput(this, 'API URL for instance management', {
      value: `${api.url}/instances`,
    });
    new CfnOutput(this, 'API URL for model management', {
      value: `${api.url}/models`,
    });
    new CfnOutput(this, 'API URL for observability', {
      value: `${api.url}/metrics`,
    });
    new CfnOutput(this, 'Inference Image URI', {
      value: ecrImage.repositoryUri,
    });
  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

new MLMStack(app, 'MLM-dev', { env: devEnv });
// new MyStack(app, 'MLM-prod', { env: prodEnv });

app.synth();