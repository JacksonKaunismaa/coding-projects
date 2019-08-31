import numpy as np
import sys

q = 180   # => 1 - (((16 choose i) * (240 choose (90-i)) sum from i=0 to 9)/(256 choose 90))
p = 256
w = 16
theta = 10
runs = int(sys.argv[1])
total = 0
#avg_valid = 0
syns = np.random.choice(p, size=q//2, replace=False)+1
valids = syns
#perms = np.round(np.random.uniform(0,1, size=q))
#valids = np.multiply(perms, syns)
for _ in range(runs):
    inpts = np.random.choice(p, size=w, replace=False)+1
#    sum_valids = perms.sum()
    overlaps = 1 if len(np.intersect1d(valids,inpts)) >= theta else 0
    total += overlaps
#    avg_valid += sum_valids
print(float(total) / (runs))
#print(float(avg_valid) / (N*runs*q))
