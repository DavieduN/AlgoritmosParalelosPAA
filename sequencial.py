from time import perf_counter
from typing import List
from copy import deepcopy

from shared import *

def mat_mul(a: List[List[int]], b: List[List[int]]) -> List[List]:
    n = len(a)
    c = [[0]*n for _ in range(n)]
    for i in range(n): 
        for j in range(n):
            for k in range(n):
                c[i][j] += a[i][k] * b[k][j]
            c[i][j] %= mod
    return c

def mat_exp(a: List[List], b: int):
    ans = mat_identity(len(a))
    base = deepcopy(a)
    while b:
        if b & 1:
            ans = mat_mul(ans, base)
        base = mat_mul(base, base)
        b //= 2
    return ans

if __name__ == "__main__":
    durations = []
    for i in range(testcases):
        n, b, mat = read_input(i)
        print(f"Test {i+1:02d} | N={n} B={b} |", end=" ")
        
        start_time = perf_counter()
        ans = mat_exp(mat, b)
        end_time = perf_counter()
        
        duration = end_time - start_time
        durations.append(duration)
        
        print(f"{duration:.4f}s")

    write_output("sequencial", durations)
    print(f"--- END ---")
