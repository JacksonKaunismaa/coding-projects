import numpy as np
import matplotlib.pyplot as plt
import glob

files = glob.glob("cout*")
COL = 1
def read(fname):
    with open(fname, "r") as f:
        data = f.readlines()
    numbers = [list(map(int, x.split("\t"))) for x in data]
    return np.array(numbers)[:,COL]

def proc(nums):
    avg = nums.mean()
    std = nums.std()
    low = nums.min()
    big = nums.max()
    return (avg, std, low, big)

if COL == 1:
    full_data = {int(n[4:]): proc(read(n)) for n in files}
    full_data = dict(sorted(full_data.items()))
    points = np.array([[x,y[0]] for x,y in full_data.items()])
    errors_std = np.array([y[1] for x,y in full_data.items()])
    errors_min_max = np.array([[y[2], y[3]] for x,y in full_data.items()])


    #plt.plot(points[:,0], points[:,1], 'go-', linewidth=2, markersize=5)
    plt.title("Snake length as a function of board size")
    upper, = plt.plot(points[:,0], errors_min_max[:,1], 'g-', linewidth=1, markersize=1)
    lower, = plt.plot(points[:,0], errors_min_max[:,0], 'r-', linewidth=1, markersize=1)
    average =   plt.errorbar(points[:,0], points[:,1], yerr=errors_std, fmt='bo-', linewidth=2, markersize=5, ecolor='k', capsize=5)
    optimal, = plt.plot(points[:,0], points[:,0]**2, 'c--')

    plt.xlabel("Board size")
    plt.ylabel("Snake length")
    plt.grid()
    plt.xticks(range(2, 26, 2))
    plt.legend((optimal, upper, average, lower), ("Best possible length", "Highest length attained", "Average length", "Lowest length attained"))
    plt.ylim(bottom=0, top=410)
    plt.xlim(left=1)
    plt.show()
else:
    full_data = {int(n[4:]): proc(read(n)) for n in files}
    full_data = dict(sorted(full_data.items()))
    points = np.array([[x,y[0]] for x,y in full_data.items()])
    errors_std = np.array([y[1] for x,y in full_data.items()])
    errors_min_max = np.array([[y[2], y[3]] for x,y in full_data.items()])


    #plt.plot(points[:,0], points[:,1], 'go-', linewidth=2, markersize=5)
    plt.title("Final score as a function of board size")
    upper, = plt.plot(points[:,0], errors_min_max[:,1], 'g-', linewidth=1, markersize=1)
    lower, = plt.plot(points[:,0], errors_min_max[:,0], 'r-', linewidth=1, markersize=1)
    average =   plt.errorbar(points[:,0], points[:,1], yerr=errors_std, fmt='bo-', linewidth=2, markersize=5, ecolor='k', capsize=5)

    plt.xlabel("Board size")
    plt.ylabel("Final score")
    plt.grid()
    plt.xticks(range(2, 26, 2))
    plt.legend((upper, average, lower), ("Highest score attained", "Average score", "Lowest score attained"))
    plt.xlim(left=1)
    plt.show()
