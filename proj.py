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


ellip_WGS84 = ellipsoide.Ellipsoide('WGS84', 6378137.0, 6356752.314)
# memes X0 et Y0 que le Lambert Zone... a modifier
# coo min de la boite englobante des points ?
X0 = 0
Y0 = 0

class Point():
    """
    Classe Point
    """
    def __init__(self, nom, lon, lat, el):
        """

        :param nom: str
        :param lon: float
        :param lat: float
        :param el: float
        """
        self.nom = nom
        self.lat = float(lat)
        self.lon = float(lon)
        self.el = float(el)

    def __str__(self):
        return self.nom+' '+str(self.lat)+' '+str(self.lon)+' '+str(self.el)

    def save(self, filename):
        """
        Ajoute le point au fichier 'filename' en suivant les specifications du csv
        :param filename: str
        :return: None
        """
        with open(filename, 'a') as f:
            f.write(self.nom+';'+str(self.lon)+';'+str(self.lat)+';'+str(self.el)+'\n')

def lecture(filename):
    """
    Lecture d'un fichier csv,
    Passage de coordonnées XYZ en lon, lat, alt
    :param filename: str
    :return: liste d'objets Points
    """
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
    """
    Conversion de coordonnees XYZ (ECEF) en LLA
    :param X: float
    :param Y: float
    :param Z: float
    :return: float,float,float
    """
    ecef = pyproj.Proj(proj='geocent', ellps='WGS84', datum='WGS84')
    lla = pyproj.Proj(proj='latlong', ellps='WGS84', datum='WGS84')
    lon, lat, alt = pyproj.transform(ecef, lla, X, Y, Z, radians=True)
    return lon, lat, alt

def min_max(points):
    """
    renvoie les latitudes extremes d'une liste de points
    :param points: liste d'objets Points
    :return:
    """
    min = points[0].lat
    max = points[0].lat

    for p in points:
        if p.lat < min:
            min = p.lat
        else:
            if p.lat > max:
                max = p.lat

    return (min, max)

def deg_to_rad(deg):
    """
    Conversion de degres en radians
    :param deg: float
    :return:
    """
    return deg * np.pi / 180.0

def rad_to_deg(rad):
    """
    Conversion de radians en degres
    :param rad: float
    :return:
    """
    return rad * 180.0 / np.pi

def choix_proj_cc(lst_points):
    """
    Choix d'une projection conique conforme secante adaptee
    a un ensemble de points
    :param lst_points: liste d'objets Points
    :return:
    """
    lat_min, lat_max = min_max(lst_points)
    min_altlin_moy = 99999999999999999
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
            sum_altlin = 0
            for p in lst_points:
                phi_rad = p.lat
                sum_altlin += np.abs(cc.alteration_lineaire(phi_rad))
            moy_altlin = sum_altlin/len(lst_points)

            if moy_altlin < min_altlin_moy:
                min_altlin_moy = moy_altlin
                sol_cc = cc
            d += deg_to_rad(0.005)
        phi0 += deg_to_rad(0.005)
    print('altération linéaire :', min_altlin_moy, 'mm/km')
    return sol_cc


def affiche(lst_points, cc):
    """
    affiche la carte 
    :param lst_points: liste d'objets Point
    :param cc: projection conique conforme
    :return:
    """
    points_proj = []
    for p in lst_points:
        points_proj.append(cc.proj_to_CC(p.lon, p.lat))

    x_cc = []
    y_cc = []

    for p in points_proj:
        x_cc.append(p[0])
        y_cc.append(p[1])

    plt.plot(x_cc, y_cc, 'b+')
    plt.axis('equal')
    plt.title('Points GPS représentés dans la projection conique conforme optimale')
    plt.show()


if __name__ == '__main__':
    points = lecture("resultats.csv")
    pr = choix_proj_cc(points)

    print('Paramètres de la projection conique conforme minimisant le module linéaire:\n', 'Phi0 =', \
          rad_to_deg(pr.phi0), '\n', 'Phi1 =', rad_to_deg(pr.phi1), '\n', 'Phi2 =', rad_to_deg(pr.phi2), \
          '\n', 'X0 :', pr.X0, 'Y0 :', pr.Y0, '\n', "ellipsoide de référence WGS 84")

    affiche(points, pr)

