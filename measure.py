import csv
import numpy as np

if __name__ == "__main__":
    with open("res.csv", "r") as f:
        res = csv.reader(f)
        improvement = []
        is_before = True
        for line in res:
            if line[0] == "benchmark":
                continue
            if is_before:
                before = int(line[2])
                is_before = False
            else:
                after = int(line[2])
                improvement.append((before - after) / before)
                is_before = True
            print(line)
    print(improvement)
    print(np.mean(improvement))
            