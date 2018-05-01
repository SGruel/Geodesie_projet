import proj
import ellipsoide
import Cone_CC
import numpy as np
import matplotlib.pyplot as plt

filename_gps = 'test_coo'

ellip_WGS84 = ellipsoide.Ellipsoide('WGS84', 6378137.0, 6356752.314)
# memes X0 et Y0 que le Lambert Zone... à modifier
# coo min de la boite englobante des points ?
X0 = 0
Y0 = 0

class Point():
    def __init__(self, nom, lat, lon, el):
        self.nom = nom
        self.lat = float(lat)
        self.lon = float(lon)
        self.el = float(el)


class Projection():
    def __init__(self, nom, phi0, phi1, phi2, X0, Y0, ellipsoide):
        self.nom = nom
        self.phi0 = float(phi0)
        self.phi1 = float(phi1)
        self.phi2 = float(phi2)
        self.X0 = X0
        self.Y0 = Y0
        self.ellipsoide = ellipsoide
        self.n = self.n()
        self.C = self.C()

    def n(self):
        phi1_rad = deg_to_rad(self.phi1)
        phi2_rad = deg_to_rad(self.phi2)
        return (np.log((self.N(phi2_rad) * np.cos(phi2_rad))/(self.N(phi1_rad) * np.cos(phi1_rad)))) / (self.lat_iso(phi1_rad) - self.lat_iso(phi2_rad))

    def C(self):
        phi1_rad = deg_to_rad(self.phi1)
        phi2_rad = deg_to_rad(self.phi2)
        return ((self.N(phi1_rad) * np.cos(phi1_rad)) / self.n) * np.exp(self.n * self.lat_iso(phi1_rad))

    def L(self, phi):
        return self.lat_iso(phi)

    def lat_iso(self, phi):
        phi_rad = deg_to_rad(phi)
        bloc1 = np.log(np.tan((np.pi / 4) + (phi_rad / 2)))
        bloc2 = (self.ellipsoide.e / 2) * np.log((1 + self.ellipsoide.e * np.sin(phi_rad)) / (1 - self.ellipsoide.e * np.sin(phi_rad)))
        return bloc1 - bloc2

    def N(self, phi):
        return self.ellipsoide.a / self.w(phi)

    def w(self, phi):
        return (1 - (self.ellipsoide.e ** 2) * np.sin(phi) ** 2) ** 0.5

    def trace(self, lst_points):
        print('Projection :', self.nom)

        x_proj = []
        y_proj = []

        for p in lst_points:
            x_proj.append(self.X0 + self.C * np.sin(self.n * p.lon))
            y_proj.append(self.Y0 + self.C * np.cos(self.n * self.lat_iso(p.lat)))


        plt.plot(x_proj, y_proj, 'r+')
        plt.axis('equal')
        plt.show()


def lecture(filename):
    points = []
    with open(filename, 'r') as f:
        lines = f.readlines()
        for li in lines:
            l = li.split(',')
            points.append(Point(l[0], l[1], l[2], l[3][:-1]))  # modifier selon format

    return points

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

def choix_proj_cc(lst_points):
    lat_min, lat_max = min_max(lst_points)
    min_modlin = 9999999999
    sol_cc = 0

    lst_proj_CC = []

    phi0 = lat_min
    while (phi0 < lat_max):
        d = 0.1
        while (d < (lat_max - lat_min) / 2):
            print(phi0, phi0 - d, phi0 + d)
            nom = 'CC_' + str(phi0) + '_' + str(phi0 - d) + '_' + str(phi0 + d)
            cc = Cone_CC.Cone_CC(nom, 0, phi0, phi0 - d, phi0 + d, X0, Y0, ellip_WGS84)
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

def deg_to_rad(ang):
    return ang * np.pi / 180

def rad_to_deg(ang):
    return ang * 180 / np.pi

def mu(phi, phi1, phi2, phi0,ellipsoide):
    return (n(phi1, phi2,ellipsoide) * C(phi1, phi2,ellipsoide) * np.exp(-n(phi1, phi2,ellipsoide) * L(phi))) \
           / (N(phi,ellipsoide) * np.cos(phi))

def lamb93_mod_lin(proj, lst_points):
    print('- LAMBERT 93 -')
    #    print('n = ', n(deg_to_rad(phi1), deg_to_rad(phi2)))
    #    print('C = ', C(deg_to_rad(phi1), deg_to_rad(phi2)))
    #    print('module linéaire de 49° : ', mu(deg_to_rad(49), phi1_rad, phi2_rad, phi0_rad))

    phi0_rad = deg_to_rad(proj.phi0)
    phi1_rad = deg_to_rad(proj.phi1)
    phi2_rad = deg_to_rad(proj.phi2)
    ellipsoide = proj.ellipsoide

    list_val_rad = []
    i = deg_to_rad(proj.phi1)
    while i < deg_to_rad(proj.phi2):
        list_val_rad.append(i)
        i += deg_to_rad(0.1)

    List_mu = []
    List_x = []
    for phi in list_val_rad:
        List_mu.append(mu(phi, phi1_rad, phi2_rad, phi0_rad, ellipsoide))
        List_x.append(rad_to_deg(phi))

    plt.plot(List_x, List_mu)

def con_conf_mod_lin():
    print('- CONIQUES CONFORMES 9 ZONES -')

    liste_NZ = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    for nz in liste_NZ:
        phi0_deg = 41 + nz
        phi0_rad = deg_to_rad(phi0_deg)
        phi1_deg = phi0_deg - 0.75
        phi1_rad = deg_to_rad(phi1_deg)
        phi2_deg = phi0_deg + 0.75
        phi2_rad = deg_to_rad(phi2_deg)
        #        lambda0_deg = 3
        #        lambda0_rad = deg_to_rad(lambda0_deg)
        #        YO = nz * 1000000+200000
        #        X0 = 1700000
        #    print(mu(phi0_rad, phi1_rad, phi2_rad, phi0_rad))

        list_val_rad = []
        i = deg_to_rad(phi0_deg - 1)
        while i < deg_to_rad(phi0_deg + 1):
            list_val_rad.append(i)
            i += deg_to_rad(0.1)
        List_mu = []
        List_x = []
        for phi in list_val_rad:
            List_mu.append(mu(phi, phi1_rad, phi2_rad, phi0_rad))
            List_x.append(rad_to_deg(phi))
        plt.plot(List_x, List_mu)


if __name__ == '__main__':
    points = lecture(filename_gps)
    pr = choix_proj_cc(points)
    proj = Projection(pr.nom, pr.phi0, pr.phi1, pr.phi2, X0, Y0, ellip_WGS84)
    proj.trace(points)

