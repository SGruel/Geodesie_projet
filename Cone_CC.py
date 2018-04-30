import numpy as np

class Cone_CC:
    def __init__(self, nom, lambda0, phi0, phi1, phi2, X0, Y0, ellipsoide):
        self.nom = nom
        self.lambda0 = lambda0*np.pi/180
        self.phi0 = phi0*np.pi/180
        self.phi1 = phi1*np.pi/180
        self.phi2 = phi2*np.pi/180
        self.X0 = X0
        self.Y0 = Y0
        self.ellipsoide = ellipsoide
        
        self.n = np.log((1 - ellipsoide.e**2*np.sin(self.phi1)**2)**(1/2)*np.cos(self.phi2)/(1-ellipsoide.e**2*np.sin(self.phi2)**2)**(1/2)/np.cos(self.phi1)) / (self.L_CC(self.phi1) - self.L_CC(self.phi2))
        self.C = ellipsoide.a*np.cos(self.phi1)/(1 - ellipsoide.e**2*np.sin(self.phi1)**2)**(1/2)/self.n*np.exp(self.n * self.L_CC(self.phi1))
        
        
    def L_CC(self, phi):
        e = self.ellipsoide.e
        return np.log((1 + np.sin(phi))/(1 - np.sin(phi)))/2 - e/2*np.log((1 + e*np.sin(phi))/(1 - e*np.sin(phi)))
        
    def L_iso_inverse(self, L):
        phi0 = 2*np.arctan(np.exp(L)) - np.pi/2
        ecart = 1;
        while(ecart>0.0000000001):
            phi1 = 2*np.arctan(((1 + self.ellipsoide.e*np.sin(phi0))/(1 - self.ellipsoide.e*np.sin(phi0)))**(self.ellipsoide.e/2)*np.exp(L)) - np.pi/2
            ecart = np.abs(phi1 - phi0)
            phi0 = phi1
        
        return phi0
        
    def proj_to_CC(self, lambd, phi):
        R = self.C*np.exp(-self.n*self.L_CC(phi))
        X = self.X0 + R*np.sin(self.n*(lambd - self.lambda0))
        Y = self.Y0 + self.C*np.exp(-self.n*self.L_CC(self.phi0)) - R*np.cos(self.n*(lambd - self.lambda0))
        return np.array(X, Y)
        
    def CC_to_geog(self, X, Y):
        Ys = self.Y0 + self.C*np.exp(-self.n*self.L_CC(self.phi0))
        R = ((X - self.X0)**2 + (Y - Ys)**2)**(1/2)
        lambd = self.lambda0 + np.arctan((X - self.X0)/(Ys - Y))/self.n
        L = -np.log(R/np.abs(self.C))/self.n
        phi = self.L_iso_inverse(L)
        
        return np.array(lambd, phi)
        
    def module_lineaire(self, phi):
        r = self.ellipsoide.a/(1 - self.ellipsoide.e**2*np.sin(phi)**2)**(1/2)*np.cos(phi)
        m = self.n*self.C*np.exp(-self.n*self.L_CC(phi))/r
        
        return (m - 1)*10**5

    def __str__(self):
        return str(self.nom)+'\n'+str(self.phi0*180/np.pi)+' '+str(self.phi1*180/np.pi)+' '+str(self.phi2*180/np.pi)+'\n'+str(self.X0)+', '+str(self.Y0)+'\n'