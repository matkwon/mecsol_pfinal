class Node:

    def __init__(self, n, x, y):
        self.n = n
        self.x = x
        self.y = y
        self.gdl = [n*2 - 1, n*2]
    
    def set_u(self, u):
        self.u = u
    
    def set_v(self, v):
        self.v = v