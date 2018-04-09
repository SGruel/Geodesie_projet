# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

# import re
import numpy as np

try:
    import gpstime as gps
except ImportError:
    print("WARNING : gpstime non installé")
import matplotlib.pyplot as plt

# import math
# import matplotlib.pyplot as plt
# import skimage
import parse_pos


# Création des matrices
def matrice_B(list_pos):
    mat_basline = np.zeros((len(list_pos) + 24, 1))
    j = 0
    for i in range(len(list_pos)):
        mat_basline[i] = list_pos[i].X - list_pos[i].X_o
        mat_basline[i + 1] = list_pos[i].Y - list_pos[i].Y_o
        mat_basline[i + 2] = list_pos[i].Z - list_pos[i].Z_o
        if list_pos[i].parent:
            mat_basline[-24 + j] = list_pos[i].X_o
            j += 1
            mat_basline[-24 + j] = list_pos[i].Y_o
            j += 1
            mat_basline[-24 + j] = list_pos[i].Z_o
            j += 1
    return mat_basline


def matrice_A(list_pos, cheminement):
    mat = np.identity(len(list_pos) + 24)
    j = 0
    for i in range(list_pos):
        if list_pos[i].parent:
            mat[i, -24 + j] = -1
            j += 1
            mat[i + 1, -24 + j] = -1
            j += 1
            mat[i + 2, -24 + j] = -1
            j += 1
        else:
            mat[i, i - 3] = -1
            mat[i + 1, i - 2] = -1
            mat[i + 2, i - 1] = -1
    return mat


def matrice_cov(list_pos):
    mat = np.zeros((len(list_pos + 24), len(list_pos + 24)))
    for i in range(list_pos):
        mat[i, i] = list_pos[i].sdx ** 2
        mat[i + 1, i + 1] = list_pos[i].sdy ** 2
        mat[i + 2, i + 2] = list_pos[i].sdz ** 2
        mat[i, i + 1] = list_pos[i].sdxy ** 2
        mat[i + 1, i] = list_pos[i].sdxy ** 2
        if list_pos[i].sdxy < 0:
            mat[i, i + 1] = -list_pos[i].sdxy ** 2
            mat[i + 1, i] = -list_pos[i].sdxy ** 2
        mat[i + 1, i + 2] = list_pos[i].sdyz ** 2
        mat[i + 2, i + 1] = list_pos[i].sdyz ** 2
        if list_pos[i].sdyz < 0:
            mat[i + 1, i + 2] = -list_pos[i].sdyz ** 2
            mat[i + 2, i + 1] = -list_pos[i].sdyz ** 2
        mat[i, i + 2] = list_pos[i].sdzx ** 2
        mat[i + 2, i] = list_pos[i].sdzx ** 2
        if list_pos[i].sdzx < 0:
            mat[i, i + 2] = -list_pos[i].sdzx ** 2
            mat[i + 2, i] = -list_pos[i].sdzx ** 2
    for j in range(0, 24):
        mat[-24 + j, -24 + j] = 0.01 ** 2
    return mat


def xchap(A, mat_cov, B):
    P = np.linalg.inv(mat_cov)
    N = np.dot(np.transpose(A), np.dot(P, A))
    K = np.dot(np.transpose(A), np.dot(P, B))
    Ninv = np.linalg.inv(N)
    return np.dot(Ninv, K)


def Vnorm(A, mat_cov, B):
    Xchap = xchap(A, mat_cov, B)
    V = np.dot(A, Xchap) - B
    P = np.linalg.inv(mat_cov)
    Vnorm = np.zeros((V.shape[0], V.shape[1]))
    N = np.dot(np.transpose(A), np.dot(P, A))
    Ninv = np.linalg.inv(N)
    sigma = sigma2 = np.dot(np.transpose(V), np.dot(P, V)) / (
        len(B) - len(A[1]))
    Vnorm = np.zeros((V.shape[0], V.shape[1]))
    for i in range(len(V)):
        Vnorm[i] = V[i] / np.sqrt(sigma2 * (1 / P[i][i] - np.dot(A[i], np.dot(Ninv, A[i].reshape((len(A[i]), 1))))))


    plt.figure(0)
    plt.hist(Vnorm,"o")
    plt.savefig("residus.jpg")
    plt.close()


    