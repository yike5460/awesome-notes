import { App, Stack, StackProps, CfnOutput } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as apigw from "aws-cdk-lib/aws-apigateway";
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3'
// import * as sagemaker from 'aws-cdk-lib/aws-sagemaker';

export class MLMStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Create S3 bucket to hold the model.tar.gz
    const bucket = new s3.Bucket(this, 'ModelBucket', {
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    });

    // Create the Lambda functions for each submodule
    const instanceManagementLambda = new lambda.Function(this, 'InstanceManagementFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'instance_management.handler',
      code: lambda.Code.fromAsset('lambda'),
    });

    const modelManagementLambda = new lambda.Function(this, 'ModelManagementFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,  
      handler: 'model_management.handler',
      code: lambda.Code.fromAsset('lambda'),
      environment: {
        model_bucket: bucket.bucketName,
        // Fix for now
        model_prefix: 'model'
      },
    });

    const observabilityLambda = new lambda.Function(this, 'ObservabilityFunction', {
      runtime: lambda.Runtime.PYTHON_3_10,
      handler: 'observability.handler',  
      code: lambda.Code.fromAsset('lambda'),
    });

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