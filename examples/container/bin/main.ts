import { App, Stack, StackProps } from 'aws-cdk-lib';
import { EksClusterStack } from '../lib/eks-cluster';
import { Construct } from 'constructs';
// import nested stacks

export class MyStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps = {}) {
    super(scope, id, props);

    const cluster = new EksClusterStack(this, 'EksClusterStack', {
      clusterName: 'host-llm',
    });
  }
}

// for development, use account/region from cdk cli
const devEnv = {
  account: process.env.CDK_DEFAULT_ACCOUNT,
  region: process.env.CDK_DEFAULT_REGION,
};

const app = new App();

new MyStack(app, 'host-llm-dev', { env: devEnv });
// new MyStack(app, 'host-llm-prod', { env: prodEnv });

app.synth();