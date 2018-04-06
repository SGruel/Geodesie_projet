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
def matriceB(list_pos):
    mat_basline=np.zeros((len(list_base)+24,1))
    j=0
    for i in range (len(list_base)):
        mat_basline[i]=list_base[i].X-list_base[i].X_o
        mat_basline[i+1]=list_base[i].Y-list_base[i].Y_o
        mat_basline[i+2]=list_base[i].Z-list_base[i].Z_o
        if list_base[i].parent:
            mat_baslin[-24+j]=list_base[i].X_o
            j+=1
            mat_baslin[-24+j]=list_base[i].Y_o
            j+=1
            mat_baslin[-24+j]=list_base[i].Z_o
            j+=1

def matrice_A(list_pos):
    