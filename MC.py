# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

#import re
import numpy as np
try:
    import gpstime as gps
except ImportError:
    print("WARNING : gpstime non installé")

#import math
#import matplotlib.pyplot as plt
#import skimage
import parse_pos

#Création des matrices
def matrice_B(list_pos):
    mat_basline=np.zeros((len(list_base)+24,1))
    j=0
    for i in range (len(list_base)):
        mat_basline[i]=list_base[i].X-list_base[i].X_o
        mat_basline[i+1]=list_base[i].Y-list_base[i].Y_o
        mat_basline[i+2]=list_base[i].Z-list_base[i].Z_o
        if list_base[i].parent:
            mat_basline[-24+j]=list_base[i].X_o
            j+=1
            mat_basline[-24+j]=list_base[i].Y_o
            j+=1
            mat_basline[-24+j]=list_base[i].Z_o
            j+=1
    return mat_basline

def matrice_A(list_pos,cheminement):
    mat= np.identity(len(list_pos)+24)
    j=0
    for i in range(list_pos):
        if list_pos[i].parent:
            mat[i,-24+j]=-1
            j+=1
            mat[i+1,-24+j]=-1
            j+=1
            mat[i+2,-24+j]=-1
            j+=1
        else:
            mat[i,i-3]=-1
            mat[i+1,i-2]=-1
            mat[i+2,i-1]=-1
    return mat

def matrice_cov(list_base):
    mat=np.zeros((len(list_base+24),len(list_base+24)))
    for i in range(list_base):
        mat[i,i]=list_base[i].sdx**2
        mat[i+1,i+1]=list_base[i].sdy**2
        mat[i+2,i+2]=list_base[i].sdz**2
        mat[i,i+1]=list_base[i].sdxy**2
        mat[i+1,i]=list_base[i].sdxy**2
        if list_base[i].sdxy <0:
            mat[i,i+1]= -list_base[i].sdxy**2
            mat[i+1,i]= -list_base[i].sdxy**2
        mat[i+1,i+2]=list_base[i].sdyz**2
        mat[i+2,i+1]=list_base[i].sdyz**2
        if list_base[i].sdyz <0:
            mat[i+1,i+2]= -list_base[i].sdyz**2
            mat[i+2,i+1]= -list_base[i].sdyz**2
        mat[i,i+2]=list_base[i].sdzx**2
        mat[i+2,i]=list_base[i].sdzx**2
        if list_base[i].sdzx <0:
            mat[i,i+2]= -list_base[i].sdzx**2
            mat[i+2,i]= -list_base[i].sdzx**2
    for j in range(0,24):
        mat[-24+j,-24+j]=0.01**2
    return mat
            
        
        
            