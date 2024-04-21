## Prerequisites
- You have access to the Amazon Management Console or you installed and configured the AWS CLI. Refer to Installing or updating to the latest version of the AWS CLI and Configuring the AWS CLI in the AWS CLI documentation.
- You installed the eksctl CLI if you prefer it as your client application. The CLI is available from https://eksctl.io/introduction/#installation.
- You have the AMI value from https://cloud-images.ubuntu.com/aws-eks/.
- You have the EC2 instance type to use for your nodes.

## Step 1: Create an Amazon EKS cluster
First [Retrieving Amazon EKS optimized Amazon Linux AMI IDs](https://docs.aws.amazon.com/eks/latest/userguide/retrieve-ami-id.html) (Optonal)
```
${AMI_ID}=aws ssm get-parameter --name /aws/service/eks/optimized-ami/1.29/amazon-linux-2-gpu/recommended/image_id --region <region> --query "Parameter.Value" --output text
```
Then create the cluster with explicit options
```
eksctl create cluster --name <cluster-name> --region <region> --version 1.29 --node-type <node-type> --nodes <number-of-nodes> --nodes-min <min-nodes> --nodes-max <max-nodes> --node-ami ${AMI_ID}
```

e.g. 
aws ssm get-parameter --name /aws/service/eks/optimized-ami/1.29/amazon-linux-2-gpu/recommended/image_id --region us-west-2 --query "Parameter.Value" --output text
eksctl create cluster --name demo --region us-west-2 --version 1.29 --node-type g4dn.2xlarge --nodes 2 --nodes-min 1 --nodes-max 3 --node-ami ami-0c4e110a8b27bba88

eksctl create cluster --name demo --region ap-northeast-1 --version 1.29 --node-type g4dn.2xlarge --nodes 2 --nodes-min 1 --nodes-max 3