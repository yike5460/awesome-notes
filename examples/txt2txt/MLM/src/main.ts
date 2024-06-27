import { App, Stack, StackProps, CfnOutput, Duration, Size } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as iam from 'aws-cdk-lib/aws-iam';

import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as ecr_assets from 'aws-cdk-lib/aws-ecr-assets';
import * as ecrdeploy from 'cdk-ecr-deployment';
import * as batch from "aws-cdk-lib/aws-batch";
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from "aws-cdk-lib/aws-ecs";

export class MLMStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Create S3 bucket to hold the model.tar.gz
    const bucket = new s3.Bucket(this, 'ModelBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create SagemMaker image in ECR from local Dockerfile and pass the inference_image_uri to the Lambda function as environment variable to create the SageMaker model
    const ecrRepo = new ecr.Repository(this, 'BYOCImage', {
      repositoryName: 'ecr-byoc-image',
    });
    
    const dockerImageAsset = new ecr_assets.DockerImageAsset(this, 'BYOCAsset', {
      directory: 'ecr-byoc-assets',
    });

    // Find default VPC
    const connectorVpc = ec2.Vpc.fromLookup(this, 'ConnectorVPC', {
      isDefault: true,
    });

    // Find default security group attached to the VPC
    const securityGroup = ec2.SecurityGroup.fromLookupByName(this, 'DefaultSecurityGroup', 'default', connectorVpc);

    // Define batch compute environment with fargate
    const computeEnvironment = new batch.FargateComputeEnvironment(
      this,
      "ComputeEnvironment",
      {
        computeEnvironmentName: "batch-compute-environment",
        vpc: connectorVpc,
        vpcSubnets: {
          subnets: connectorVpc.privateSubnets,
        },
        securityGroups: [securityGroup],
        maxvCpus: 256,
        spot: false,
      },
    );
  
    // Define job queue
    const jobQueue = new batch.JobQueue(this, "JobQueue", {
      jobQueueName: "batch-job-queue",
      computeEnvironments: [
        {
          computeEnvironment: computeEnvironment,
          order: 1,
        },
      ],
    });

    // Create Batch Job Definition
    const jobDefinition = new batch.EcsJobDefinition(this, 'ModelPackagingJobDef', {
      container: new batch.EcsFargateContainerDefinition(
        this,
        "containerDefn",
        {
          // This container will be first used as batch container to package the model then as SageMaker inference image
          image: ecs.ContainerImage.fromAsset('./ecr-byoc-assets'),
          command: ['echo', 'This is a placeholder. Replace with actual model packaging logic.'],
          memory: Size.mebibytes(2048),
          cpu: 1,
          environment: {
            PLACEHOLDER: 'This is a placeholder. Replace with actual environment variables.',
          },
        },
      ),
      jobDefinitionName: 'model-packaging-job-definition',
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
    const modelPreparationLambda = new lambda.Function(this, 'ModelPreparationFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'model_preparation.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        JOB_QUEUE: jobQueue.jobQueueName,
        JOB_DEFINITION: jobDefinition.jobDefinitionName,
        ECR_REPO: ecrRepo.repositoryUri,
        MODEL_BUCKET: bucket.bucketName,
      },
      timeout: Duration.minutes(15),
    });
    
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
        inference_image_uri: ecrRepo.repositoryUri,
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
    modelPreparationLambda.addToRolePolicy(new iam.PolicyStatement({
      actions: ['batch:SubmitJob', 'batch:DescribeJobs'],
      resources: ['*'],
    }));
    
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
    const preparationResource = api.root.addResource('preparation');
    preparationResource.addMethod('POST', new apigw.LambdaIntegration(modelPreparationLambda));

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

    // Output the API Gateway URL and other important information
    new CfnOutput(this, 'API URL', { value: api.url ?? 'Something went wrong with the deploy' });
    new CfnOutput(this, 'API URL for model preparation', { value: `${api.url}/preparation` });
    new CfnOutput(this, 'API URL for instance management', { value: `${api.url}/instances` });
    new CfnOutput(this, 'API URL for model management', { value: `${api.url}/models` });
    new CfnOutput(this, 'API URL for observability', { value: `${api.url}/metrics` });
    new CfnOutput(this, 'ECR Repository URI', { value: ecrRepo.repositoryUri });
    new CfnOutput(this, 'Model S3 Bucket', { value: bucket.bucketName });
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