import numpy as np
import time
from collections import Counter
np.random.seed(12)
def rand_choice_center(a, size, center):
    # DONT USE THIS (too slow)
    choices = np.random.normal(center, a/6, size=size).astype(np.uint8) % a
    while np.unique(choices).shape != size:
        choices = np.random.normal(center, a/6, size=size).astype(np.uint8) % a
    return choices

#def rand_choice_center_fast(a, size, center):
#    def sub_func():
#        double_choices = np.random.normal(center, a/6, size=(2*size,)).astype(np.uint8) % a
#        used = set()
#        actual_choices = np.empty(size)
#        current = 0
#        for c in double_choices:
#            if current != size:
#                if c not in used:
#                    used.add(c)
#                    actual_choices[current] = c
#                    current += 1
#            else:
#                break
#        return actual_choices, current
#    choices, actual_size =  sub_func()
#    while actual_size != size:
#        choices, actual_size =  sub_func()
#    return choices

def rand_choice_center_fast(a, size, center):
    return np.random.choice(a, size=size, replace=False)

def truncated_normal_perms(center, inpts, inpt_size):
    return np.clip(np.random.normal(0.52-0.05*mod_dist(center, inpts, inpt_size)/float(inpt_size), 1e-2), 0.3, 0.7)

def rand_choice_center_bias(a, size, center):
    # DONT USE THIS (gives biased results [there is replacement])
    choices = np.random.normal(center, a/6, size=size).astype(np.uint8) % a
    return choices

def mod_dist(a, b, c):
    diffs = abs(a-b)
    return np.where(diffs < c//2, diffs, c - diffs)


def _binary_insert(l, lo, hi, val, old_mid):
    mid = (lo+hi)//2
    if mid == old_mid:
        if val < l[lo]:
            return mid-1
        elif val > l[hi]:
            return mid+1
        else:
            return mid
#    print("lo", l[lo], "hi", l[hi], "val", val, "mid", l[mid])
    if val <= l[mid]:
#       print("first path")
        return _binary_insert(l, lo, mid, val, mid)
    else:
#      print("second path")
        return _binary_insert(l, mid, hi, val, mid)

def binary_insert(l , val, key=None):
    if key is not None:
        l_actual = list(map(key, l))
        try:
            val = key(val)
        except Exception:
            pass
        return _binary_insert(l_actual, 0, len(l)-1, val, -1) + 1
    return _binary_insert(l, 0, len(l)-1, val, -1) + 1

def binary_find(l, val, key=None):
    # use this one if you want to delete from the sorted array
    res = binary_insert(l, val, key=key)
    try:
        if res == 1 and key(val) <= key(l[0]):     # this is the only difference between binary insert and binary find
            return 0
    except Exception:
        if res == 1 and val <= key(l[0]):
            return 0
    return res

def modular_radius(vals, mod, key=None):
    #sorted_vals = sorted(vals)
    #sorted_vals.append(sorted_vals[0])
    if key is not None:
        vals_actual = list(map(key, vals))
        vals_actual.append(key(vals[0]))
    else:
        vals_actual = vals
        vals_actual.append(vals[0])
    #print(vals_actual)
    lowest = mod
    for x,y in zip(vals_actual, vals_actual[1:]):
    #   print(x,y, "=>", mod - (y-x)%mod)
        lowest = min(lowest, mod - (y-x)%mod)
    return lowest

def simple_recptive_size(vals, col, mod, key=None):    # depreceated since it gives values that are too large which leads to issues
    if key is not None:
        vals_actual = np.array(list(map(key, vals)))
    else:
        vals_actual = np.array(vals)
    return np.square(mod_dist(vals_actual, col, mod)).sum()


def main():
    np.set_printoptions(precision=3)
    #starter = [5, 123, -23, 4, 0, 4,2, 13, 5, 2, 4, 123,5,3,3,3,3,523,43,212, 12, 13, 13, 13, 14, 15, 16]
    #starter.sort()
    #print(starter)
    #result = binary_insert(starter, 5)
    #starter.insert(result, 5)
    #result = binary_insert(starter, 27)
    #starter.insert(result, 27)
    #result = binary_insert(starter, -500)
    #starter.insert(result, -500)
    #result = binary_insert(starter, 5000)
    #starter.insert(result, 5000)
    #result = binary_insert(starter, 50)
    #starter.insert(result, 50)
    #print(starter)
    N = 50000


    #print(mod_dist(1,2,50), '1,2')
    #print(mod_dist(24,27,50), '24,27')
    #print(mod_dist(25,26,50), '25,26')
    #print(mod_dist(24,25,50), '24,25')
    #print(mod_dist(4,29,50), '4,29')
    #print(mod_dist(1,10,50), '0,10')
    #print(mod_dist(0,50,50), '0,50')
    #print(mod_dist(0,49,50), '0,49')
    #print(mod_dist(10,1,50), '10,1')
    #print(mod_dist(50,0,50), '50,0')
    #print(mod_dist(49,0,50), '49,0')
    #quit()
    #start = time.time()
    #for _ in range(N):
    #    rand_choice_center(50, (15,), 12)
    #print((time.time() - start))

    #start = time.time()
    #for _ in range(N):
    #    rand_choice_center_bias(50, (15,), 12)
    #t1 = ((time.time() - start))

    #start = time.time()
    #for _ in range(N):
    #    rand_choice_center_fast(50, 15, 12)
    #t2 = ((time.time() - start))
    #print(t1)
    #print(t2)
    #print(t2/t1)
    total_conn = 0
    total_discon = 0
    distr = Counter()
    total_distr = Counter()
    for _ in range(N):
        res = rand_choice_center_fast(50, 15, 0)
        perms = truncated_normal_perms(0, res, 50)
        amounts = np.where(perms > 0.5, 0, 1).sum()

        for count, perm in zip(res, perms):
            if perm > 0.5:
                distr[int(count)] += 1
            total_distr[int(count)] += 1

        total_discon += amounts
        total_conn += (15 - amounts)
    res = rand_choice_center_fast(50, 15, 0)
    perms = truncated_normal_perms(0, res, 50)
    print(res)
    print(mod_dist(0, res, 50))
    print(perms)
    print(np.where(perms > 0.5, 0, 1).sum())
    print(total_conn)
    print(total_discon)
    print(distr, ">0.5 coutns")
    print(total_distr, "potential synapse coutns")

if __name__ == "__main__":
    main()
