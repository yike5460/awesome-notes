## Key insights and steps to build a [depot](https://news.ycombinator.com/item?id=39930908) alike service that allows users to customize their GitHub workflow runners using AWS:

### Key Components

1. Launching dedicated EC2 instances for each GitHub Actions job
2. Registering the EC2 instance as a self-hosted runner in the user's GitHub organization 
3. Executing the GitHub Actions job on the EC2 instance
4. Terminating the EC2 instance when the job completes
5. Integrating with a distributed cache for faster job execution
6. Providing a seamless user experience to configure runners from their GitHub workflow YAML

### Implementation Steps

1. Set up an AWS account and create an IAM user with programmatic access to EC2, S3, and other required services.

2. Create a service that listens for GitHub Actions job requests via a webhook. This can be built using a web framework like Express.js in TypeScript.

3. When a job request is received, launch a new EC2 instance using the AWS SDK. Use an AMI that has the required dependencies pre-installed (Docker, Node.js, etc).

4. Register the EC2 instance as a GitHub self-hosted runner using the GitHub Actions API. This involves:
   - Generating a registration token for the repo/org
   - Installing the runner application on the EC2 instance 
   - Configuring the runner with the registration token

5. Execute the GitHub Actions job on the EC2 instance by running the runner application. Stream the job logs back to the GitHub Actions API.

6. Monitor the job status. When it completes, terminate the EC2 instance using the AWS SDK.

7. Integrate a distributed cache (like Redis) to store job artifacts, packages, etc. This will speed up subsequent job runs.

8. Provide a simple YAML configuration for users to specify the EC2 instance type, cache settings, etc directly in their GitHub workflow file:

```yaml
jobs:
  test:
    runs-on: depot
    with:
      ec2-instance-type: c5.xlarge  
      cache-enabled: true
```

9. Add support for GitHub OIDC integration, so temporary AWS credentials can be issued to each job, rather than using static IAM user keys.

Here's a simplified code snippet to launch an EC2 instance using the AWS SDK in TypeScript:

```typescript
import { EC2Client, RunInstancesCommand } from "@aws-sdk/client-ec2";

const ec2Client = new EC2Client({ region: "us-east-1" });

const runInstancesCommand = new RunInstancesCommand({
  ImageId: "ami-1a2b3c4d",
  InstanceType: "t2.micro",
  MinCount: 1,
  MaxCount: 1,
  TagSpecifications: [
    {
      ResourceType: "instance",
      Tags: [ { Key: "Purpose", Value: "github-actions-runner" } ]
    }
  ]
});

const response = await ec2Client.send(runInstancesCommand);
console.log(response.Instances[0].InstanceId);
```

## Consideration to use docker for optimized resource management 

### Architecture Overview

- Use Kubernetes to orchestrate the lifecycle of the runner containers
- Leverage the actions-runner-controller (ARC) project to manage the runners
- Configure ARC to automatically scale the number of runners based on job demand
- Use spot instances for the Kubernetes worker nodes to reduce costs
- Implement a caching solution to speed up job execution and reduce billable minutes

### Detailed Steps

1. Set up a Kubernetes cluster using a managed service like Amazon EKS or a self-managed cluster on EC2 spot instances to reduce costs compared to on-demand instances.

2. Install cert-manager on the cluster to manage TLS certificates for ARC.

3. Install actions-runner-controller (ARC) on the cluster using Helm. This will manage the lifecycle of the runner pods.

4. Configure ARC to use the new "RunnerSets" CRD which enables autoscaling of runners based on job demand. Specify min/max replicas and scale-down delays.

5. Create a container image for the runner that includes any required dependencies like Docker, Java, etc. Use multi-stage builds to minimize image size.

6. Configure the runner image to disable automatic updates to have control over when new versions are deployed.

7. Deploy the runner image to a container registry like Amazon ECR that the cluster has access to pull from.

8. Create a "RunnerDeployment" manifest to instruct ARC to provision runner pods using the custom container image

9. Set up a cache server like Redis in the cluster to persist the runner's package and build caches across pods. Configure this in the runner deployment.

10. Configure your GitHub Actions workflows to use the self-hosted runners by specifying the labels defined on the runner deployment.

11. Set up monitoring and alerts on key metrics like job queue time, runner utilization, and cache hit rates to help guide scaling decisions.

12. Implement a system to clean up orphaned runners that are no longer needed by ARC due to scale-in events to avoid hitting registration limits.

By leveraging Kubernetes and the actions-runner-controller, you can achieve a scalable and cost-effective solution for hosting GitHub runners compared to statically provisioned EC2 instances. The ability to automatically scale the runners and use spot instances for the worker nodes provides flexibility in resource management and helps optimize costs.

Persisting the runner's cache across pods speeds up job execution by avoiding the need to re-download packages and re-build artifacts on each run. This further reduces billable Actions minutes.