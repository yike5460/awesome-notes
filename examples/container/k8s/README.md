# GPU feature (Time Slicing) with Kubernetes

## Create AWS EKS cluster
```
eksctl create cluster -f eks-gpu-cluster.yaml 
```

## Enable time slicing
```
cat << EOF > /tmp/dp-example-config.yaml
version: v1
flags:
  migStrategy: "none"
  failOnInitError: true
  nvidiaDriverRoot: "/"
  plugin:
    passDeviceSpecs: false
    deviceListStrategy: "envvar"
    deviceIDStrategy: "uuid"
  gfd:
    oneshot: false
    noTimestamp: false
    outputFile: /etc/kubernetes/node-feature-discovery/features.d/gfd
    sleepInterval: 60s
sharing:
  timeSlicing:
    resources:
    - name: nvidia.com/gpu
      replicas: 10
EOF
```

## Check the node feature discovery
The device plugin advertises 4*10 GPUs as allocatable
```
kubectl describe nodes
...
Capacity:
  cpu:                32
  ephemeral-storage:  83873772Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             251509044Ki
  nvidia.com/gpu:     40
  pods:               234
Allocatable:
  cpu:                31850m
  ephemeral-storage:  76224326324
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             248509748Ki
  nvidia.com/gpu:     40
  pods:               234
```

## Create the DCGM ProfTester pods and check the GPU utilization

```
cat << EOF | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester-1
spec:
  restartPolicy: "Never"
  containers:
  - name: dcgmproftester11
    image: nvcr.io/nvidia/cloud-native/dcgm:3.3.0-1-ubuntu22.04
    command: ["/usr/bin/dcgmproftester12"]
    args: ["--no-dcgm-validation", "-t 1004", "-d 30"]  
    resources:
      limits:
         nvidia.com/gpu: 1    
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]  

---

apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester-2
spec:
  restartPolicy: "Never"
  containers:
  - name: dcgmproftester11
    image: nvcr.io/nvidia/cloud-native/dcgm:3.3.0-1-ubuntu22.04
    command: ["/usr/bin/dcgmproftester12"]
    args: ["--no-dcgm-validation", "-t 1004", "-d 30"]  
    resources:
      limits:
         nvidia.com/gpu: 1    
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]

---

apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester-3
spec:
  restartPolicy: "Never"
  containers:
  - name: dcgmproftester11
    image: nvcr.io/nvidia/cloud-native/dcgm:3.3.0-1-ubuntu22.04
    command: ["/usr/bin/dcgmproftester12"]
    args: ["--no-dcgm-validation", "-t 1004", "-d 30"]  
    resources:
      limits:
         nvidia.com/gpu: 1    
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]

---

apiVersion: v1
kind: Pod
metadata:
  name: dcgmproftester-4
spec:
  restartPolicy: "Never"
  containers:
  - name: dcgmproftester11
    image: nvcr.io/nvidia/cloud-native/dcgm:3.3.0-1-ubuntu22.04
    command: ["/usr/bin/dcgmproftester12"]
    args: ["--no-dcgm-validation", "-t 1004", "-d 30"]  
    resources:
      limits:
         nvidia.com/gpu: 1    
    securityContext:
      capabilities:
        add: ["SYS_ADMIN"]

EOF
```

```
watch -n 1 kubelet get pods -n default
watch -n 1 nvida-smi
```

# Install Karpenter into existing EKS cluster
```
export KARPENTER_NAMESPACE="kube-system"
export KARPENTER_VERSION="0.36.1"
export K8S_VERSION="1.29"
export CLUSTER_NAME="demo"

helm registry logout public.ecr.aws
helm upgrade --install karpenter oci://public.ecr.aws/karpenter/karpenter --version "${KARPENTER_VERSION}" --namespace "${KARPENTER_NAMESPACE}" --create-namespace \
  --set "settings.clusterName=${CLUSTER_NAME}" \
  --set "settings.interruptionQueue=${CLUSTER_NAME}" \
  --set controller.resources.requests.cpu=1 \
  --set controller.resources.requests.memory=1Gi \
  --set controller.resources.limits.cpu=1 \
  --set controller.resources.limits.memory=1Gi \
  --wait

check if karpenter is successfully installed in helm
helm list -n kube-system
```