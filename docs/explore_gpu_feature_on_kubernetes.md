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

eksctl create cluster --name demo --region us-west-2 --version 1.29 --node-type g4dn.2xlarge --nodes 2 --nodes-min 1 --nodes-max 3

## Step 2, Pre-flight checks

Check if current instance contain GPU
```
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.capacity.nvidia\.com/gpu}{"\n"}{end}'
```

Install & Check if Node Feature Discovery (NFD) is enabled
```
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-feature-discovery/v0.8.2/deployments/static/nfd.yaml

kubectl get pods -n node-feature-discovery -l app=nfd
NAME        READY   STATUS    RESTARTS   AGE
nfd-pj2vx   2/2     Running   0          52s
nfd-qr5df   2/2     Running   0          52s
```

Check if nvidia-docker2 is installed on your GPU nodes and Docker default runtime is set to nvidia
```
<!-- Get AWS EC2 instance id, the output was list of "aws:///us-west-2a/i-06584f1737e1933ef aws:///us-west-2b/i-0f9a9f4d543d45da9 ..." and filter to print out all the instance id -->
kubectl get nodes -o jsonpath='{.items[*].spec.providerID}' | grep -o 'i-[^ ]*' | xargs

<!-- Get instance name for following ssh access -->
aws ec2 describe-instances --instance-ids <instance-id> --region <aws-region-name> --query 'Reservations[*].Instances[*].[PublicIpAddress,KeyName]'

ssh -i <key.pem> ec2-user@<node-public-ip>
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

Install & Check if GPU Feature Discovery (GFD) is enabled
```
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/gpu-feature-discovery/v0.8.2/deployments/static/gpu-feature-discovery-daemonset.yaml
<!-- Get current nodes list -->
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}'
export NODE_NAME=<your-node-name>
curl https://raw.githubusercontent.com/NVIDIA/gpu-feature-discovery/v0.8.2/deployments/static/gpu-feature-discovery-job.yaml.template \
    | sed "s/NODE_NAME/${NODE_NAME}/" > gpu-feature-discovery-job.yaml
kubectl apply -f gpu-feature-discovery-job.yaml
```

Check if both NFD and GFD deployed and running
```
kubectl get nodes -o yaml | grep -A 1 -B 1 nvidia.com/gpu
```

