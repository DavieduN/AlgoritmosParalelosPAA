from random import randint
from typing import List

sizes = [16, 32, 64, 128, 256]
test_set_size = 10
max_b = 50738
max_v = 50135

def rand_mat(n: int) -> List[List[int]]:
    ans = [[randint(-max_v, max_v) for _ in range(n)] for _ in range(n)]
    return ans

if __name__ == "__main__":
    index = 0
    for n in sizes:
        for _ in range(test_set_size):
            b = randint(2, max_b)
            print(f"test {index}: {n} {b}")
            mat = rand_mat(n)
            index += 1
            with open(f"tests/{index}.txt", "w") as f:
                f.write(f"{n} {b}\n")
                for line in mat:
                    f.write(" ".join([str(x) for x in line])+"\n")
            
            print(f"created")

