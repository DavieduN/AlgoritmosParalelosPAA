from typing import List
from copy import deepcopy
import csv

test_folder = "tests"
output_folder = "output"
testcases = 50
mod = 1000696969

def mat_identity(n: int) -> List[List[int]]:
    ans = [[0]*n for _ in range(n)]
    for i in range(n):
        ans[i][i] = 1
    return ans


def read_input(n: int):
    with open(f"{test_folder}/{n+1}.txt", 'r') as f:
        tokens = f.read().split()
    iterator = iter(tokens)
    n = int(next(iterator))
    b = int(next(iterator))
    mat = []
    for _ in range(n):
        line = []
        for _ in range(n):
            line.append(int(next(iterator)))
        mat.append(line)
        
    return n, b, mat

def write_output(filename: str, durations: List[int]):
    with open(f"{output_folder}/{filename}.csv", "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["duration"])
        for duration in durations:
            writer.writerow([duration])
