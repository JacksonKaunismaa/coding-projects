import numpy as np
import string
# Let's make an HTM that can learn alphabetical order ie. input size is in [0,25] corresponding to elements, with constant size gaps
ALPHA_SIZE = 26
LETTERS = string.ascii_lowercase
num_to_alpha = {i: LETTERS[i] for i in range(ALPHA_SIZE)}

def rand_letter():
    return np.random.randint(0,26,1)[0]

def get_gap_data(gap_size, amount):
    first_letters = np.random.randint(0, ALPHA_SIZE//2, size=(amount,))
    full_seq = [np.array(list(range(fl,ALPHA_SIZE,gap_size))) for fl in first_letters]
    #rand_seq = []
    #for fs in full_seq:
    #    fs[np.random.randint(2,len(fs)-2)] = rand_letter()
    #    rand_seq.append(fs)
    #return rand_seq
    return full_seq

def num_to_let(seqs):
    if type(seqs) == list:
        map_func = lambda seq: ''.join(list(map(lambda x: num_to_alpha[x], seq)))
        return list(map(map_func, seqs))
    return ''.join(list(map(lambda x: num_to_alpha[x], seq)))

test = get_gap_data(3,5)
print(rand_letter())
print(test)
print(num_to_let(test))

