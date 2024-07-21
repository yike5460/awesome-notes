// import * as cdk from 'aws-cdk-lib';
import * as path from 'path';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import { Construct } from 'constructs';

export interface AIAgentProps {
  /**
   * The name of the AI agent
   */
  readonly agentName: string;

  /**
   * The runtime for the Lambda function
   * @default lambda.Runtime.NODEJS_18_X
   */
  readonly runtime?: lambda.Runtime;

  /**
   * The memory size for the Lambda function
   * @default 128
   */
  readonly memorySize?: number;
}

export class AIAgent extends Construct {
  /**
   * The Lambda function for the AI agent
   */
  public readonly lambdaFunction: lambda.Function;

  /**
   * The API Gateway for the AI agent
   */
  public readonly api: apigateway.RestApi;

  constructor(scope: Construct, id: string, props: AIAgentProps) {
    super(scope, id);

    // Create the Lambda function
    this.lambdaFunction = new lambda.Function(this, 'AIAgentFunction', {
      runtime: props.runtime || lambda.Runtime.NODEJS_18_X,
      handler: 'index.handler',
      //   code: lambda.Code.fromAsset('lambda'),
      code: lambda.Code.fromAsset(path.join(__dirname, '..', 'lambda')),
      memorySize: props.memorySize || 128,
      environment: {
        AGENT_NAME: props.agentName,
      },
    });

    // Create the API Gateway
    this.api = new apigateway.RestApi(this, 'AIAgentAPI', {
      restApiName: `${props.agentName}-API`,
      description: `API for ${props.agentName} AI agent`,
    });

    // Create an API Gateway method
    const integration = new apigateway.LambdaIntegration(this.lambdaFunction);
    this.api.root.addMethod('POST', integration);

    // Grant the Lambda function permission to access other AWS services if needed
    this.lambdaFunction.addToRolePolicy(
      new iam.PolicyStatement({
        actions: ['comprehend:DetectSentiment', 'translate:TranslateText'],
        resources: ['*'],
      }),
    );
  }
}
