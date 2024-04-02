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
