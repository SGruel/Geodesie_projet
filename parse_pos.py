# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

import numpy as np
import os
import pyproj
"""
Etapes : 
    1) recuperer le cheminement et le stocker dans un 
        dictionnaire: {(origine : destination)}

    2) lire tous les fichiers .pos
        stocker dans un dico la correspondance nom de fichier:position dans la matrice
        stocker dans un objet X,Y,Z, sdx, sdy, sdz, sdxy, sdyz, sdzx
        
    3) créer la matrice correspondante
        
"""

class Pos():
    """
    objet Pos construit a partir d'un fichier .pos
    """
    def __init__(self, filename):
        self.name = filename[:-4]
        data = self.parse()
        #XYZ de la ref pos
        self.X_o = data[0]
        self.Y_o = data[1]
        self.Z_o = data[2]
        #XYZ du point courant
        self.X = data[3]
        self.Y = data[4]
        self.Z = data[5]
        #ecarts types fournis dans le .pos
        self.sdx = data[6]
        self.sdy = data[7]
        self.sdz = data[8]
        self.sdxy = data[9]
        self.sdyz = data[10]
        self.sdzx = data[11]
        #coord. WGS84
        self.lat, self.lon, self.alt = self.coo_ECEF_to_LLA()
        #booleen indiquant si le point a un parent du RGP
        self.parent = self.compute_parent()
        
        
    def coo_ECEF_to_LLA(self):
        ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
        lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
        lon, lat, alt = pyproj.transform(ecef, lla, self.X, self.Y, self.Z, radians=True)
        return lon*180/np.pi, lat*180/np.pi, alt
        
        
    def add_to_file(self, filename):
        with open(filename, 'a') as f:
            f.write(str(self.name)+';'+str(self.lat)+';'+str(self.lon)+';'+str(self.alt)+'\n')
    
    
    def parse(self):
        """
        parsing du .pos pour completer les champs de l'objet Pos
        """
        data = []
        with open(str(self.name)+'.pos', 'r') as f:
            lines = f.readlines()
        
        for l in lines:
            if "% ref pos" in l:
                for j in range(5):
                    l = l.replace('  ',' ')
                l = l.split('\n')
                l = l[0].split(' ')
                data.append(l[4])
                data.append(l[5])
                data.append(l[6])
        l = lines[-1]
        for j in range(5):
            l = l.replace('  ',' ')
        l = l.split('\n')
        l = l[0].split(' ')
        data.append(l[2])
        data.append(l[3])
        data.append(l[4])
        data.append(l[7])
        data.append(l[8])
        data.append(l[9])
        data.append(l[10])
        data.append(l[11])
        data.append(l[12])
        return data
        
    def compute_parent(self):
        """
        determine si le point a un parent membre du RGP
        renvoie un booleen
        True = a un parent du RGP
        False = non
        """
        if '_' in self.name:
            return True
        else:
            return False
    
    def __str__(self):
        ch = self.name+' :\n  XYZ :\t'+str(self.X)+' '+str(self.Y)+' '+str(self.Z)+'\n  sd:\t'+str(self.sdx)+' '+str(self.sdy)+' '+str(self.sdz)+' '+str(self.sdxy)+' '+str(self.sdyz)+' '+str(self.sdzx)+'\n  ref :\t'+str(self.X_o)+' '+str(self.Y_o)+' '+str(self.Z_o)+'\n  WGS84 :\t'+str(self.lat)+' '+str(self.lon)+' '+str(self.alt)+'\n'
        return ch

def parse_chem(filename):
    """
    parsing du fichier txt decrivant le cheminement
    renvoie la liste des noms de fichiers ordonnee
    """    
    lst_ordre = []

    chem_d = np.genfromtxt(filename)
    print(chem_d)
    for i in range(len(chem_d)):
        for j in range(len(chem_d[i])):
            if(int(chem_d[i][0]) != int(chem_d[i][j])):
                lst_ordre.append('sxj'+str(int(chem_d[i][j]))+'0'+str(int(chem_d[i][0]))+'z')
                
    print(lst_ordre)
    return lst_ordre
    
if __name__ == "__main__":

    lst_pos_f = [] #liste des fichiers .pos
    lst_Pos = [] #liste d'objets Pos
    lst_pos_ord = [] #liste des fichiers .oos ordonnee

    
    #Recuperation des fichiers .pos et du fichier txt de cheminement
    for element in os.listdir():
        if element.endswith('.pos'):
            lst_pos_f.append(element)
        if element.endswith('.txt'):
            cheminement = element
    print(cheminement)
    #parsing du fichier de cheminement
    lst_o = parse_chem(cheminement)

    for e in lst_o:
        for f in lst_pos_f:
            if e in f:
                lst_pos_ord.append(f)
    
    for p in lst_pos_ord:
        pos = Pos(p)
        lst_Pos.append(pos)
        
    for p in lst_Pos:
        p.add_to_file('coo_r.csv')
        print(p)