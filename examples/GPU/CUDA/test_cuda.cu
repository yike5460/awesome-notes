#include <iostream>
#include <cuda_runtime.h>

__global__ void hello_cuda() {
    printf("Hello, CUDA!\n");
}

int main() {
    hello_cuda<<<1, 1>>>();
    cudaDeviceSynchronize();
    return 0;
}
