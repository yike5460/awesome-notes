#include <cuda_runtime.h>
#include <infiniband/verbs.h>
#include <nv_peer_mem.h>

size_t size = 1024 * 1024 * 1024; // 1GB
// Allocate GPU memory on each system
void* gpuPtr1, gpuPtr2;
cudaMalloc(&gpuPtr1, size); 
cudaMalloc(&gpuPtr2, size);

// Get GPU memory info 
CUdeviceptr gpuVirtAddr1 = (CUdeviceptr)gpuPtr1;
CUdeviceptr gpuVirtAddr2 = (CUdeviceptr)gpuPtr2;

// Pass to RDMA lib
size_t gpuBufferSize = size;
gpuDirectRdmaBuffer buf1(gpuVirtAddr1, gpuBufferSize); 
gpuDirectRdmaBuffer buf2(gpuVirtAddr2, gpuBufferSize);

// Pin GPU memory
buf1.pin();
buf2.pin();

// Get DMA addresses 
uint64_t* dmaAddrs1 = buf1.getDmaAddresses();
uint64_t* dmaAddrs2 = buf2.getDmaAddresses();

// Program RDMA transfer from GPU1 to GPU2
rdmaConnection.postWrite(dmaAddrs1, dmaAddrs2, gpuBufferSize);

// Initiate transfer
rdmaConnection.pollForCompletion();

// Unpin GPU memory  
buf1.unpin();
buf2.unpin();