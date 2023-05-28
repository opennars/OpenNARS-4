import numpy as np
from ordered_set import OrderedSet

from pynars.Narsese import Term, Judgement, Task


def generate_dataset(seqs, n_train = 10000, n_test = 10000, seed = 137, exclude_sample = False, randoms = True, n_rand=4):
    np.random.seed(seed)
    samples = OrderedSet([chr(i) for i in range(65, 91)])
    if exclude_sample:
        samples_seqs = set()
        for seq in seqs:
            samples_seqs |= set(seq)
        samples -= samples_seqs

    def produce_sequence(seqs, n = 10000):
        sequence = []
        for _ in range(n):
            seq = seqs[(np.random.choice(len(seqs), 1))[0]]
            if randoms:
                seq = seq + list(np.random.choice(samples, n_rand))
            sequence.extend(seq)
        return sequence

    D_train = produce_sequence(seqs, n_train)
    D_test = produce_sequence(seqs, n_test)
    return D_train, D_test
