from time import perf_counter
from multiprocessing import Pool, cpu_count
from typing import List
from copy import deepcopy
from shared import *

def worker_task(rows_a: List[List[int]], b: List[List[int]], mod_val: int) -> List[List[int]]:
    n = len(b)
    partial = [[0]*n for _ in range(len(rows_a))]
    
    for i in range(len(rows_a)):
        for j in range(n):
            for k in range(n):
                partial[i][j] += rows_a[i][k] * b[k][j]
            partial[i][j] %= mod_val
        
    return partial

def mat_mul_parallel(a: List[List[int]], b: List[List[int]], pool: Pool) -> List[List[int]]:
    n = len(a)
    num_processes = pool._processes
    
    chunk_size = n // num_processes
    chunks_a = []
    
    for i in range(num_processes):
        start = i * chunk_size
        end = n if i == num_processes - 1 else (i + 1) * chunk_size
        chunks_a.append(a[start:end])
    
    tasks = [(chunk, b, mod) for chunk in chunks_a]
    results = pool.starmap(worker_task, tasks)

    c = []
    for partial_result in results:
        c.extend(partial_result)
        
    return c

def mat_exp(a: List[List[int]], b: int, pool: Pool) -> List[List[int]]:
    n = len(a)
    ans = mat_identity(n)
    base = deepcopy(a)
    
    while b:
        if b & 1:
            ans = mat_mul_parallel(ans, base, pool)
        base = mat_mul_parallel(base, base, pool)
        b //= 2
    return ans

if __name__ == "__main__":
    cores = int(input("How many cores will you use? "))
    print(f"--- {cores} Cores ---")

    durations = []
    with Pool(processes=cores) as pool:
        for i in range(testcases):
            n, b, mat = read_input(i)
            
            print(f"Teste {i+1:02d} | N={n} B={b} |", end=" ")
            
            start_time = perf_counter()
            ans = mat_exp(mat, b, pool)
            end_time = perf_counter()
            duration = end_time - start_time
            durations.append(duration)
            
            print(f"{duration:.4f}s")

    write_output(f"paralelo{cores}", durations)
    print(f"--- END ---")