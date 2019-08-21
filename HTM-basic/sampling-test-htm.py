import numpy as np
import sys

q = 90
p = 256
w = 16
theta = 10
N = int(sys.argv[1])
runs = int(sys.argv[2])
total = 0
#avg_valid = 0

syns = np.random.choice(p//2, size=q, replace=False)+1
valids = syns
for _ in range(runs):
    inpts = np.random.choice(p, size=w, replace=False)+1
#    perms = np.round(np.random.uniform(0,1, size=(N,q)))
#    valids = np.multiply(perms, syns)
#    sum_valids = perms.sum()
    overlaps = 1 if len(np.intersect1d(valids,inpts)) >= theta else 0
    total += overlaps
#    avg_valid += sum_valids
print(float(total) / (N*runs))
#print(float(avg_valid) / (N*runs*q))
