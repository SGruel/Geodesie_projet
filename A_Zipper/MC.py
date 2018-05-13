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
    """
    Créé la matrice contenant les lignes de bases.
    :param list_pos: liste d'objet Station venant de parse_pos
    :return: Matrice d'observation en colonne avec les lignes de base dans l'ordre suivi des coordonnées des stations du RGP
    """
    mat_basline = np.zeros((len(list_pos) * 3 + 12, 1))
    j = 0
    k = 0
    for i in range(len(list_pos)):
        #ajout des lignes de bases par groupes de trois X,Y,Z
        mat_basline[k] = float(list_pos[i].X) - float(list_pos[i].X_o)
        mat_basline[k + 1] = float(list_pos[i].Y) - float(list_pos[i].Y_o)
        mat_basline[k + 2] = float(list_pos[i].Z) - float(list_pos[i].Z_o)
        k += 3
        if list_pos[i].parent and j < 12:
            #ajout en fin de matrice des coordonnées du RGP
            mat_basline[-12 + j] = float(list_pos[i].X_o)
            j += 1
            mat_basline[-12 + j] = float(list_pos[i].Y_o)
            j += 1
            mat_basline[-12 + j] = float(list_pos[i].Z_o)
            j += 1
    return mat_basline


def matrice_A(list_pos):
    """
    Créé la matrice des paramètres du problème AX+V =B  les premières lignes correspondent au calculs des lignes de bases,
    les 12 dernières lignes sont un bloc Identité correspondant au stations du RGP.
    :param list_pos: listes des postions dans l'ordre du cheminement
    :return: matrice A
    """
    mat = np.zeros((len(list_pos) * 3 + 12, 18 * 3))
    # stations du RGP
    for i in range(-12, 0):
        mat[i, i] = 1

    #Calcul des lignes de bases
    for i in range(-12, 0):
        mat[i, i] = 1
    for i in range(3):
        mat[i, i] = 1
        mat[i + 3, i] = 1
        mat[i + 24, i + 18] = 1
        mat[i + 27, i + 18] = 1
        mat[i + 30, i + 21] = 1
        mat[i + 33, i + 21] = 1
        mat[i + 54, i + 39] = 1
        mat[i + 57, i + 39] = 1
        mat[i, -12 + i] = -1
        mat[i + 3, -12 + 3 + i] = -1
        mat[i + 24, -12 + 6 + i] = -1
        mat[i + 27, i - 12 + 9] = -1
        mat[i + 30, i - 12] = -1
        mat[i + 33, i - 12 + 3] = -1
        mat[i + 54, i - 12 + 6] = -1
        mat[i + 57, i - 12 + 9] = -1
    for i in range(18):
        mat[i + 6, i + 3] = 1
        mat[i + 6, i] = -1
        mat[i + 36, i + 24] = 1
        mat[i + 36, i + 21] = -1

    return mat


def matrice_cov(list_pos):
    """
    Calcule la matrice variance-covariance du problème. Il s'agit d'une matrice diagonale par bloc de trois sous la forme:
    (varX covXY covX)
    (covXY VarY covYZ)
    (covXZ covYZ varZ)  dans le cas d'une ligne de base
    (1cm² 0   0 )
    ( 0  1cm² 0 )
    ( 0   0  1cm²) dans le cas d'un station du RGP

    :param list_pos:
    :return:
    """
    mat = np.zeros((len(list_pos) * 3 + 12, len(list_pos) * 3 + 12))
    k = 0
    for i in range(len(list_pos)):
        mat[k, k] = float(list_pos[i].sdx) ** 2
        mat[k + 1, k + 1] = float(list_pos[i].sdy) ** 2
        mat[k + 2, k + 2] = float(list_pos[i].sdz) ** 2
        mat[k, k + 1] = float(list_pos[i].sdxy) ** 2
        mat[k + 1, k] = float(list_pos[i].sdxy) ** 2
        if float(list_pos[i].sdxy) < 0:
            mat[k, k + 1] = -float(list_pos[i].sdxy) ** 2
            mat[k + 1, k] = -float(list_pos[i].sdxy) ** 2
        mat[k + 1, k + 2] = float(list_pos[i].sdyz) ** 2
        mat[k + 2, k + 1] = float(list_pos[i].sdyz) ** 2
        if float(list_pos[i].sdyz) < 0:
            mat[k + 1, k + 2] = -float(list_pos[i].sdyz) ** 2
            mat[k + 2, k + 1] = -float(list_pos[i].sdyz) ** 2
        mat[k, k + 2] = float(list_pos[i].sdzx) ** 2
        mat[k + 2, k] = float(list_pos[i].sdzx) ** 2
        if float(list_pos[i].sdzx) < 0:
            mat[k, k + 2] = -float(list_pos[i].sdzx) ** 2
            mat[k + 2, k] = -float(list_pos[i].sdzx) ** 2
        k += 3
    for j in range(0, 12):
        mat[-12 + j, -12 + j] = 0.01 ** 2
    return mat


def xchap(A, mat_cov, B):
    """
    Résoud les moindres carrés à partir des matrices calculées précédement  on a Xchap = (AtPA)^-1 * AtPB
    :param A:
    :param mat_cov:
    :param B:
    :return:
    """
    P = np.linalg.inv(mat_cov)
    N = np.dot(np.transpose(A), np.dot(P, A))
    K = np.dot(np.transpose(A), np.dot(P, B))
    Ninv = np.linalg.inv(N)
    return np.dot(Ninv, K)


def Vnorm(A, mat_cov, B):
    """
    Calcul les résidus normalisés des moindres carrés et renvoie un affichage graphique permettant de vérifier si ceux ci suivent la loi du X²
    :param A:
    :param mat_cov:
    :param B:
    :return:
    """
    Xchap = xchap(A, mat_cov, B)
    V = np.dot(A, Xchap) - B
    P = np.linalg.inv(mat_cov)
    N = np.dot(np.transpose(A), np.dot(P, A))
    Ninv = np.linalg.inv(N)
    sigma2 = np.dot(np.transpose(V), np.dot(P, V)) / (
        len(B) - len(A[0]))
    Vnorm = np.zeros((V.shape[0], V.shape[1]))
    for i in range(len(V)):
        Vnorm[i] = V[i] / (np.sqrt((sigma2)) * np.sqrt(mat_cov[i,i] - np.dot(A, np.dot(Ninv, np.transpose(A)))[i][i]))
    plt.figure(0)
    plt.hist(Vnorm)
    plt.savefig("residus.png")
    plt.close()


def MC(list_pos):
    """
    Fonction formalisant le calcul des moindres carrés et leur vérification
    :param list_pos:
    :return:
    """
    A = matrice_A(list_pos)
    B = matrice_B(list_pos)
    mat = matrice_cov(list_pos)
    Vnorm(A, mat, B)
    return (xchap(A, mat, B))




