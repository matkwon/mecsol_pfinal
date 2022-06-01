class Element:

    def __init__(self, n1, n2, E, A):
        self.n1 = n1
        self.n2 = n2
        self.E = E
        self.A = A
        self.l = ((n2.x - n1.x)**2 + (n2.y - n1.y)**2) ** (1/2)
        self.s = (n2.y - n1.y) / self.l
        self.c = (n2.x - n1.x) / self.l
    
    def Ke(self):
        matrix  =  [[self.c**2, self.c*self.s, -self.c**2, -self.c*self.s],
                    [self.c*self.s, self.s**2, -self.c*self.s, -self.s**2],
                    [-self.c**2, -self.c*self.s, self.c**2, self.c*self.s],
                    [-self.c*self.s, -self.s**2, self.c*self.s, self.s**2]]
        
        for l in range(4):
            for c in range(4):
                matrix[l][c] *= (self.E * self.A / self.l)

        return matrix
    
    def deform(self):
        return (- self.c*self.n1.u - self.s*self.n1.v + self.c*self.n2.u + self.s*self.n2.v) / self.l
    
    def tension(self):
        return self.deform(self) * self.E