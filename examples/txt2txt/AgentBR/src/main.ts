import { App, Stack, StackProps } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3Assets from 'aws-cdk-lib/aws-s3-assets';

export class AgentStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    // Create IAM role for the Agent
    const agentRole = new iam.Role(this, 'AgentRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com')
    });

    // Grant the Agent role permissions to invoke bedrock model
    agentRole.addToPolicy(
      new iam.PolicyStatement({
        effect: iam.Effect.ALLOW,
        actions: ['bedrock:InvokeModel'],
        // concatenate the region and model
        resources: ["arn:" + this.partition + ":bedrock:" + this.region + "::foundation-model/anthropic.*"],
      })
    )

    // Create S3 bucket for storing the OpenAPI schema file
    const schemaBucket = new s3.Bucket(this, 'SchemaBucket', {
      bucketName: 'agent-demo',
    });

    // Upload the OpenAPI schema file to the S3 bucket
    const schemaAsset = new s3Assets.Asset(this, 'SchemaAsset', {
      path: './schema/openapi.yaml',
    });

    const cfnAgent = new bedrock.CfnAgent(this, 'MyCfnAgent', {
      agentName: 'AgentDemo',
    
      // the properties below are optional
      actionGroups: [{
        actionGroupName: 'actionGroupAPISchema',
    
        // the properties below are optional
        actionGroupExecutor: {
          lambda: 'lambda',
        },
        actionGroupState: 'actionGroupState',
        apiSchema: {
          payload: 'payload',
          s3: {
            s3BucketName: 's3BucketName',
            s3ObjectKey: 's3ObjectKey',
          },
        },
        description: 'description',
        parentActionGroupSignature: 'parentActionGroupSignature',
        skipResourceInUseCheckOnDelete: false,
      }],
      agentResourceRoleArn: 'agentRole',
      autoPrepare: false,
      customerEncryptionKeyArn: 'customerEncryptionKeyArn',
      description: 'description',
      foundationModel: "arn:" + this.partition + ":bedrock:" + this.region + "::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
      idleSessionTtlInSeconds: 600,
      instruction: 'You are an office assistant in an insurance agency. You are friendly and polite. You help with managing insurance claims and coordinating pending paperwork.',
      // knowledgeBases: [{
      //   description: 'description',
      //   knowledgeBaseId: 'knowledgeBaseId',
    
      //   // the properties below are optional
      //   knowledgeBaseState: 'knowledgeBaseState',
      // }],
      // promptOverrideConfiguration: {
      //   promptConfigurations: [{
      //     basePromptTemplate: 'basePromptTemplate',
      //     inferenceConfiguration: {
      //       maximumLength: 123,
      //       stopSequences: ['stopSequences'],
      //       temperature: 123,
      //       topK: 123,
      //       topP: 123,
      //     },
      //     parserMode: 'parserMode',
      //     promptCreationMode: 'promptCreationMode',
      //     promptState: 'promptState',
      //     promptType: 'promptType',
      //   }],
    
      //   // the properties below are optional
      //   overrideLambda: 'overrideLambda',
      // },
      // skipResourceInUseCheckOnDelete: false,
      // tags: {
      //   tagsKey: 'tags',
      // },
      // testAliasTags: {
      //   testAliasTagsKey: 'testAliasTags',
      // },
    });

  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

new AgentStack(app, 'Agent-dev', { env: devEnv });
// new MyStack(app, 'Agent-prod', { env: prodEnv });

app.synth();