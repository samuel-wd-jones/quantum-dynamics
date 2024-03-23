# Imports
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import multiprocessing as mp
import os
import secrets
import pickle


# Variables
LOCAL_DIR = "/".join(__file__.split("/")[:-1])
THREADS = int([ts := os.cpu_count(), 1][int(ts is None)] / 2)
mpl.rcParams["mathtext.fontset"] = "cm"
mpl.rcParams["font.family"] = "serif"

# Functions
def atomic_qubits_evolution(rf, dr, ld, n=50000, ts=None, qs=None, threads=THREADS):
    rg = np.random.default_rng(secrets.randbits(128))
    ts = [ts, np.linspace(0, np.pi * 20 / rf, 10000)][ts is None]
    qs = [qs, (gq := np.outer((np.arange(2) == 0), np.ones(n)))][qs is None]
    n = np.shape(qs)[1]
    if threads > 1:
        return aqe_handler(rf, dr, ld, n, ts, qs, threads)
    h1 = -(1j / 2) * np.array(((ld, rf), (rf, -1j*dr-ld)))
    aq = [(np.average(qs, axis=1), np.average(np.abs(qs) ** 2, axis=1))]
    for t0, t1 in zip(ts[:-1], ts[1:]):
        dt = t1 - t0
        gr = np.matmul(h1, qs)
        qs = qs + gr * dt
        qs = qs / np.sqrt(np.sum(np.abs(qs) ** 2, axis=0))
        dm = np.abs(qs[1]) ** 2 * dr * dt > rg.random(n)
        qs = qs * (1 - dm) + gq * dm
        aq.append((np.average(qs, axis=1), np.average(np.abs(qs) ** 2, axis=1)))
    aq = np.array(aq)
    return aq[:,0,:].T, np.abs(aq[:,1,:]).T, ts, qs


def aqe_handler(rf, dr, ld, n, ts, qs, threads):
    threads = [threads, 1][int(n <= threads)]
    ks = np.linspace(0, n, threads + 1, dtype=np.int_)
    qc = [qs[:,int(ks[i]):int(ks[i + 1])] for i in range(threads)]
    with mp.Pool(threads) as pool:
        qs = pool.starmap(atomic_qubits_evolution, [[rf, dr, ld, None, ts, q, 1] for q in qc])
    return (np.average([q[0] for q in qs], axis=0, weights=np.diff(ks)), 
            np.average([q[1] for q in qs], axis=0, weights=np.diff(ks)), 
            ts, 
            np.hstack([q[3] for q in qs]))