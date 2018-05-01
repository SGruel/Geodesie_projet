import ellipsoide
import Cone_CC
import pyproj
import numpy as np
import matplotlib.pyplot as plt

"""
1) lecture des points GPS 
2) determination de la proj minimisant l'alteration lineaire
    determiner: la latitude moyenne
                les latitudes min et max 

3) affichage sur une carte avec la projection correspondante

"""

filename_gps = 'resultats.csv'

ellip_WGS84 = ellipsoide.Ellipsoide('WGS84', 6378137.0, 6356752.314)
# memes X0 et Y0 que le Lambert Zone... a modifier
# coo min de la boite englobante des points ?
X0 = 0
Y0 = 0

class Point():
    def __init__(self, nom, lon, lat, el):
        self.nom = nom
        self.lat = float(lat)
        self.lon = float(lon)
        self.el = float(el)

    def __str__(self):
        return self.nom+' '+str(self.lat)+' '+str(self.lon)+' '+str(self.el)

    def save(self, filename):
        with open(filename, 'a') as f:
            f.write(self.nom+';'+str(self.lon)+';'+str(self.lat)+';'+str(self.el)+'\n')

def lecture(filename):
    points = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for li in lines:
            l = li.split(';')

            lon,lat,alt = coo_ECEF_to_LLA(float(l[1]), float(l[2]), float(l[3][:-1]))

            points.append(Point(l[0], lon, lat, alt)) #modifier selon format
            points[-1].save('coo_lat_lon.csv')

    return points

def coo_ECEF_to_LLA(X, Y, Z):
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, alt = pyproj.transform(ecef, lla, X, Y, Z, radians=True)
    return lon, lat, alt

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

def projection(lst_points, proj):
    """
    cette fonction dessinera la carte des points dans la projection adaptee
    :param lst_points: liste des points
    :param proj: projection conique conforme
    :return:
    """
    pass

def deg_to_rad(deg):
    return deg * np.pi / 180.0

def rad_to_deg(rad):
    return rad * 180.0 / np.pi

def choix_proj_cc(lst_points):
    lat_min, lat_max = min_max(lst_points)
    min_modlin = 9999999999
    sol_cc = 0

    lst_proj_CC = []

    phi0 = lat_min
    while (phi0 < lat_max):
        d = deg_to_rad(0.01)
        while(d < (lat_max-lat_min)/2):
            nom = 'CC_'+str(phi0)+'_'+str(phi0-d)+'_'+str(phi0+d)
            phi0_rad = phi0
            cc = Cone_CC.Cone_CC(nom, 0, phi0_rad, phi0_rad-d, phi0_rad+d, X0, Y0, ellip_WGS84)
            lst_proj_CC.append(cc)
            sum_modlin = 0
            for p in lst_points:
                phi_rad = p.lat
                sum_modlin += cc.module_lineaire(phi_rad)**2

            if sum_modlin < min_modlin:
                min_modlin = sum_modlin
                sol_cc = cc
            d += deg_to_rad(0.01)
        phi0 += deg_to_rad(0.05)
    return sol_cc

def projeter(cc, lambd, phi):
    return cc.proj_to_CC(lambd, phi)


if __name__ == '__main__':
    points = lecture(filename_gps)
    pr = choix_proj_cc(points)
    print('Paramètres de la projection conique conforme minimisant le module linéaire:\n','Phi0:',rad_to_deg(pr.phi0),'\n','Phi1:',rad_to_deg(pr.phi1),'\n','Phi2:',\
          rad_to_deg(pr.phi2),'\n','X0 :',pr.X0,'Y0 :',pr.Y0,'\n', "ellipsoide de référence WGS 84")

    points_proj = []
    for p in points:
        points_proj.append(projeter(pr, p.lon, p.lat))

    x_cc=[]
    y_cc=[]

    for p in points_proj:
        x_cc.append(p[0])
        y_cc.append(p[1])

    plt.plot(x_cc, y_cc, 'b+')
    plt.axis('equal')
    plt.title('Points GPS représentés dans la projection conique conforme optimale')
    plt.show()

