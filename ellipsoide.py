class Ellipsoide:
    
    def __init__(self, nom, a, b):
        self.nom = nom
        self.a = a
        self.b = b
        self.f = (a-b)/a
        self.e = ((a**2 - b**2)/a**2)**(1/2)