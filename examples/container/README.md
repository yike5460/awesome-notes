# Overall Architecture

## Why Karpenter instead of orginal Kubernetes Autoscaler?

1. Flexibility and fine-grained control: 
- Karpenter's NodePools allow specifying a wide variety of constraints like instance types, sizes, architectures, capacity types (Spot, On-Demand). This enables fine-grained control over resource utilization.
- NodePools can set taints, labels, annotations, and customize Kubelet arguments, providing more configuration options than node groups.
- A single NodePool can handle provisioning nodes for diverse pod requirements, reducing the need to manage many specific node groups.

2. Cost optimization:
- Karpenter can select the optimal instance type that closely matches pod resource requests, minimizing overprovisioning and reducing costs compared to node groups that use fixed instance types.
- NodePools allow mixing purchase options like On-Demand and Spot instances, enabling cost savings through Spot usage.
- Karpenter's consolidation feature can terminate underutilized nodes to optimize costs, which is not natively supported by node groups.

3. Speed and efficiency:
- By managing instances directly instead of relying on Auto Scaling groups, Karpenter can provision nodes much faster than Cluster Autoscaler. 
- Karpenter avoids potential race conditions between pod scheduling and node provisioning that can occur with Cluster Autoscaler.

4. Interruption handling:
- Karpenter offers native interruption handling for Spot instances without needing additional components like Node Termination Handler.

5. Provisioner consolidation:
- Karpenter's NodePool replaces the previous Provisioner, Machine, and AWSNodeTemplate resources, streamlining the APIs around the single concept of a node.

## Install [eksdemo](https://github.com/awslabs/eksdemo?tab=readme-ov-file#install-manually) for prototype

And knowing the the differences between eksdemo and eksctl is also important since we will use them interchangeably but for different purposes.
**Purpose:**
- eksctl is a CLI tool for creating and managing Amazon EKS clusters, it helps you easily create EKS clusters with options to customize the configuration.
- eksdemo is an easy button for learning, testing and demoing Amazon EKS. It is designed to quickly get you up and running with EKS for learning and experimentation purposes.
**Use cases:**
- eksctl is used for creating production-ready EKS clusters and managing them over time. It provides extensive configuration options suitable for real-world deployments.
- eksdemo is meant for iterative testing, learning EKS concepts, and giving demos. It prioritizes simplicity and getting a cluster running quickly over production-readiness.
**Approach:**
- eksctl uses a declarative Infrastructure as Code (IaC) approach built on tools like CloudFormation, Terraform or CDK. You define the desired cluster state and eksctl provisions it. 
- eksdemo takes an imperative approach with a kubectl-like CLI that installs apps and dependencies with simple commands. It is designed for fast iteration rather than defining declarative configuration.
**Scope:**
- eksctl allows detailed configuration of the EKS cluster, nodegroups, and add-ons through CLI flags and configuration file. It supports advanced customization and is a general purpose tool for EKS cluster management, from creation to deletion with full lifecycle support.
- eksdemo comes with a predefined application catalog that can be installed with single commands. It focuses on ease-of-use over deep customization and has a narrower scope focused on learning, testing and demoing EKS features and add-ons without full EKS management capabilities.
