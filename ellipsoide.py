import numpy as np

class Ellipsoide:
    
    def __init__(self, nom, a, b):
        self.nom = nom
        self.a = a
        self.b = b
        self.f = (a-b)/a
        self.e = np.sqrt((a**2 - b**2)/a**2)