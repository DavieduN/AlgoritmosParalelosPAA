from mpi4py import MPI
from time import perf_counter
from typing import List, Optional
from copy import deepcopy
from shared import *

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def local_mat_mul(a: List[List[int]], b: List[List[int]]) -> List[List[int]]:
    n = len(b)
    rows = len(a)
    partial_c = [[0] * n for _ in range(rows)]
    
    for i in range(rows):
        for j in range(n):
            for k in range(n):
                partial_c[i][j] += a[i][k] * b[k][j]
            partial_c[i][j] %= mod
    return partial_c

def distributed_matmul(a: Optional[List[List[int]]], b: Optional[List[List[int]]]) -> Optional[List[List[int]]]:
    # cut into chunks
    chunks_a = None
    if rank == 0 and a is not None:
        n = len(a)
        chunks_a = []
        chunk_size = n // size
        remainder = n % size
        start = 0
        for i in range(size):
            end = start + chunk_size + (1 if i < remainder else 0)
            chunks_a.append(a[start:end])
            start = end

    # send chunk_A and B
    chunk_a = comm.scatter(chunks_a, root=0)
    b_local = comm.bcast(b if rank == 0 else None, root=0)

    # calculate
    local_ans = local_mat_mul(chunk_a, b_local)

    # gather answer
    list_of_chunks = comm.gather(local_ans, root=0)
    ans = None
    if rank == 0:
        ans = []
        for chunk in list_of_chunks:
            ans.extend(chunk)
    
    return ans

def mat_exp_mpi(a: Optional[List[List[int]]], b: int) -> Optional[List[List[int]]]:
    ans = None
    base = None
    if rank == 0 and a is not None:
        n = len(a)
        ans = mat_identity(n)
        base = deepcopy(a)

    while b:
        if b & 1:
            ans = distributed_matmul(ans, base)
        base = distributed_matmul(base, base)
        b //= 2
        
    return ans

if __name__ == "__main__":
    if rank == 0:
        durations = []
        print(f"--- {size} Processes ---")

    for i in range(testcases):
        n, b_val, mat = None, None, None
        
        if rank == 0:
            n, b_val, mat = read_input(i)
            print(f"Teste {i+1:02d} | N={n} B={b_val} |", end=" ")

        n = comm.bcast(n, root=0)  
        b_val = comm.bcast(b_val, root=0)
        
        comm.Barrier()
        start = perf_counter()
        ans = mat_exp_mpi(mat, b_val)
        comm.Barrier()
        end = perf_counter()

        if rank == 0:
            duration = end - start
            durations.append(duration)
            print(f"{duration:.4f}s")

    if rank == 0:
        write_output("distribuido", durations)
        print("--- FIM ---")