import ellipsoide
import Cone_CC
import pyproj
import numpy as np

"""
1) lecture des points GPS 
2) détermination de la proj minimisant l'altération linéaire
    déterminer: la latitude moyenne
                les latitudes min et max 

3) affichage sur une carte avec la projection correspondante

"""

filename_gps = 'resultat.csv'

ellip_WGS84 = ellipsoide.Ellipsoide('WGS84', 6378137.0, 6356752.314)
# memes X0 et Y0 que le Lambert Zone... à modifier
# coo min de la boite englobante des points ?
X0 = 600000
Y0 = 200000

class Point():
    def __init__(self, nom, lat, lon, el):
        self.nom = nom
        self.lat = float(lat)
        self.lon = float(lon)
        self.el = float(el)


def lecture(filename):
    points = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for li in lines:
            l = li.split(';')

            lon,lat,alt = coo_ECEF_to_LLA(float(l[1]), float(l[2]), float(l[3][:-1]))

            points.append(Point(l[0], lon, lat, alt)) #modifier selon format

    return points

def coo_ECEF_to_LLA(X, Y, Z):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, alt = pyproj.transform(ecef, lla, X, Y, Z, radians=True)
    return lon*180/np.pi, lat*180/np.pi, alt

def min_max(points):
    min = points[0].lat
    max = points[0].lat

    for p in points:
        if p.lat < min:
            min = p.lat
        else:
            if p.lat > max:
                max = p.lat

    return (min, max)

def projection(lst_points)

def choix_proj_cc(lst_points):
    lat_min, lat_max = min_max(lst_points)
    min_modlin = 9999999999
    sol_cc = 0

    lst_proj_CC = []

    phi0 = lat_min
    while (phi0 < lat_max):
        d = 0.1
        while(d < (lat_max-lat_min)/2):
            print(phi0, phi0-d, phi0+d)
            nom = 'CC_'+str(phi0)+'_'+str(phi0-d)+'_'+str(phi0+d)
            cc = Cone_CC.Cone_CC(nom, 0, phi0, phi0-d, phi0+d, X0, Y0, ellip_WGS84)
            lst_proj_CC.append(cc)
            sum_modlin = 0
            for p in lst_points:
                sum_modlin += cc.module_lineaire(p.lat)
            print(sum_modlin)

            if sum_modlin < min_modlin:
                min_modlin = sum_modlin
                sol_cc = cc
            d += 0.5
        phi0 += 0.5

    print('module lineaire', min_modlin)
    print(sol_cc)
    return sol_cc

if __name__ == '__main__':
    points = lecture(filename_gps)
    choix_proj_cc(points)