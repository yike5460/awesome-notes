import torch
import triton
import triton.language as tl
import numpy as np
import pycuda.driver as cuda

# 1. Traditional PyTorch Implementation
def pytorch_matmul(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    return torch.matmul(a, b)

# 2. Basic CUDA Implementation (using cuBLAS through pycuda)
import pycuda.autoinit
import pycuda.gpuarray as gpuarray
from pycuda.compiler import SourceModule

cuda_kernel = """
__global__ void matmul_kernel(float* a, float* b, float* c, int M, int N, int K) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;
    
    if (row < M && col < N) {
        float sum = 0.0f;
        for (int k = 0; k < K; ++k) {
            sum += a[row * K + k] * b[k * N + col];
        }
        c[row * N + col] = sum;
    }
}
"""

# 3. Triton Implementation (detailed breakdown)
@triton.jit
# The @triton.jit decorator is used to compile this function for GPU execution
# It tells Triton to convert this Python function into optimized GPU code
# This allows us to write GPU kernels using Python syntax, which Triton then optimizes
def matmul_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    BLOCK_SIZE_M: tl.constexpr, 
    BLOCK_SIZE_N: tl.constexpr, 
    BLOCK_SIZE_K: tl.constexpr,
    stride_am, stride_ak,
    stride_bk, stride_bn,
    stride_cm, stride_cn
):
    # 3.1 Get program ID and compute block indices
    pid = tl.program_id(0)  # This is like CUDA's blockIdx
    num_pid_m = tl.cdiv(M, BLOCK_SIZE_M)  # Ceiling division
    num_pid_n = tl.cdiv(N, BLOCK_SIZE_N)
    pid_m = pid // num_pid_n
    pid_n = pid % num_pid_n

    # 3.2 Compute offsets for A and B matrices
    offs_am = pid_m * BLOCK_SIZE_M + tl.arange(0, BLOCK_SIZE_M)
    offs_bn = pid_n * BLOCK_SIZE_N + tl.arange(0, BLOCK_SIZE_N)
    offs_k = tl.arange(0, BLOCK_SIZE_K)
    
    # 3.3 Calculate memory pointers with strides
    # - Triton automatically optimizes memory access patterns
    # - Handles coalesced memory access for better performance
    # - Manages shared memory automatically
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)
    b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn)

    # 3.4 Initialize accumulator
    accumulator = tl.zeros((BLOCK_SIZE_M, BLOCK_SIZE_N), dtype=tl.float32)

    # 3.5 Main computation loop
    for k in range(0, tl.cdiv(K, BLOCK_SIZE_K)):
        # 3.5.1 Load matrix blocks
        a = tl.load(a_ptrs)
        b = tl.load(b_ptrs)
        # 3.5.2 Perform matrix multiplication using built-in dot product
        # - Optimized implementations of common operations
        # - Automatically uses tensor cores when available
        # - Fused operations for better performance
        accumulator += tl.dot(a, b)
        # 3.5.3 Move pointers to next block
        a_ptrs += BLOCK_SIZE_K * stride_ak
        b_ptrs += BLOCK_SIZE_K * stride_bk

    # 3.6 Write results back to memory
    c_ptrs = c_ptr + (offs_am[:, None] * stride_cm + offs_bn[None, :] * stride_cn)
    c_mask = (offs_am[:, None] < M) & (offs_bn[None, :] < N)
    tl.store(c_ptrs, accumulator, mask=c_mask)

# Example usage with performance comparison
def benchmark_comparison():
    print("Starting benchmark comparison...")

    # Define block sizes
    BLOCK_SIZE_M = 32
    BLOCK_SIZE_N = 32
    BLOCK_SIZE_K = 32

    # Setup test matrices
    M, N, K = 4096, 4096, 4096
    print(f"Matrix dimensions: M={M}, N={N}, K={K}")

    a = torch.randn(M, K, device='cuda')
    b = torch.randn(K, N, device='cuda')
    print("Test matrices generated on CUDA device")

    # PyTorch timing
    print("\nRunning PyTorch implementation...")
    torch.cuda.synchronize()
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    start.record()
    c_pytorch = torch.matmul(a, b)
    end.record()
    torch.cuda.synchronize()
    pytorch_time = start.elapsed_time(end)
    print(f"PyTorch implementation time: {pytorch_time:.4f} ms")

    # Basic CUDA implementation timing
    print("\nRunning basic CUDA implementation...")
    mod = SourceModule(cuda_kernel)
    matmul_cuda = mod.get_function("matmul_kernel")

    a_gpu = cuda.mem_alloc(a.numel() * 4)
    b_gpu = cuda.mem_alloc(b.numel() * 4)
    c_gpu = cuda.mem_alloc(M * N * 4)

    cuda.memcpy_htod(a_gpu, a.cpu().numpy())
    cuda.memcpy_htod(b_gpu, b.cpu().numpy())

    block = (32, 32, 1)
    grid = ((N + block[0] - 1) // block[0], (M + block[1] - 1) // block[1])

    start_cuda = cuda.Event()
    end_cuda = cuda.Event()
    start_cuda.record()

    matmul_cuda(a_gpu, b_gpu, c_gpu, np.int32(M), np.int32(N), np.int32(K),
                block=block, grid=grid)

    end_cuda.record()
    end_cuda.synchronize()
    cuda_time = start_cuda.time_till(end_cuda)
    print(f"Basic CUDA implementation time: {cuda_time:.4f} ms")

    c_cuda = np.empty((M, N), dtype=np.float32)
    cuda.memcpy_dtoh(c_cuda, c_gpu)
    c_cuda = torch.from_numpy(c_cuda).cuda()

    # Triton timing
    print("\nRunning Triton implementation...")
    start.record()
    grid = (triton.cdiv(M, BLOCK_SIZE_M) * triton.cdiv(N, BLOCK_SIZE_N),)
    print(f"Triton grid size: {grid}")
    c_triton = torch.empty_like(c_pytorch)
    matmul_kernel[grid](
        a_ptr=a, b_ptr=b, c_ptr=c_triton,
        M=M, N=N, K=K,
        BLOCK_SIZE_M=BLOCK_SIZE_M, BLOCK_SIZE_N=BLOCK_SIZE_N, BLOCK_SIZE_K=BLOCK_SIZE_K,
        stride_am=K, stride_ak=1,
        stride_bk=N, stride_bn=1,
        stride_cm=N, stride_cn=1
    )
    end.record()
    torch.cuda.synchronize()
    triton_time = start.elapsed_time(end)
    print(f"Triton implementation time: {triton_time:.4f} ms")

    # Verify results
    print("\nVerifying results...")
    try:
        torch.testing.assert_close(c_pytorch, c_triton, rtol=1e-1, atol=1e-1)
        print("Triton results match PyTorch within tolerance")
    except AssertionError as e:
        print("Triton results do not match PyTorch within tolerance")
        print(e)
        
        # Additional debug information for Triton
        abs_diff = torch.abs(c_pytorch - c_triton)
        max_diff = torch.max(abs_diff)
        max_diff_index = torch.argmax(abs_diff)
        print(f"Maximum absolute difference (Triton): {max_diff.item()}")
        print(f"Location of maximum difference (Triton): {max_diff_index.item()}")
        print(f"PyTorch value at max diff: {c_pytorch.flatten()[max_diff_index.item()]}")
        print(f"Triton value at max diff: {c_triton.flatten()[max_diff_index.item()]}")

    try:
        torch.testing.assert_close(c_pytorch, c_cuda, rtol=1e-1, atol=1e-1)
        print("CUDA results match PyTorch within tolerance")
    except AssertionError as e:
        print("CUDA results do not match PyTorch within tolerance")
        print(e)
        
        # Additional debug information for CUDA
        abs_diff = torch.abs(c_pytorch - c_cuda)
        max_diff = torch.max(abs_diff)
        max_diff_index = torch.argmax(abs_diff)
        print(f"Maximum absolute difference (CUDA): {max_diff.item()}")
        print(f"Location of maximum difference (CUDA): {max_diff_index.item()}")
        print(f"PyTorch value at max diff: {c_pytorch.flatten()[max_diff_index.item()]}")
        print(f"CUDA value at max diff: {c_cuda.flatten()[max_diff_index.item()]}")

    # Performance comparison
    print("\nPerformance Comparison:")
    print(f"PyTorch time: {pytorch_time:.4f} ms")
    print(f"Basic CUDA time: {cuda_time:.4f} ms")
    print(f"Triton time: {triton_time:.4f} ms")
    print(f"CUDA speedup over PyTorch: {pytorch_time / cuda_time:.2f}x")
    print(f"Triton speedup over PyTorch: {pytorch_time / triton_time:.2f}x")
    print(f"Triton speedup over CUDA: {cuda_time / triton_time:.2f}x")

    print("\nBenchmark comparison completed.")

# Add this line at the end of the file to run the benchmark when the script is executed
if __name__ == "__main__":
    '''
    Starting benchmark comparison...
    Matrix dimensions: M=4096, N=4096, K=4096
    Test matrices generated on CUDA device

    Running PyTorch implementation...
    PyTorch implementation time: 25.6604 ms

    Running basic CUDA implementation...
    Basic CUDA implementation time: 75.8191 ms

    Running Triton implementation...
    Triton grid size: (16384,)
    Triton implementation time: 560.5170 ms

    Verifying results...
    Triton results match PyTorch within tolerance
    CUDA results match PyTorch within tolerance

    Performance Comparison:
    PyTorch time: 25.6604 ms
    Basic CUDA time: 75.8191 ms
    Triton time: 560.5170 ms
    CUDA speedup over PyTorch: 0.34x
    Triton speedup over PyTorch: 0.05x
    Triton speedup over CUDA: 0.14x

    Benchmark comparison completed.
    '''
    benchmark_comparison()
