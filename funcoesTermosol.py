# -*- coding: utf-8 -*-
"""
A funcao 'plota' produz um gráfico da estrutura definida pela matriz de nos N 
e pela incidencia Inc.

Sugestao de uso:

from funcoesTermosol import plota
plota(N,Inc)
-------------------------------------------------------------------------------
A funcao 'importa' retorna o numero de nos [nn], a matriz dos nos [N], o numero
de membros [nm], a matriz de incidencia [Inc], o numero de cargas [nc], o vetor
carregamento [F], o numero de restricoes [nr] e o vetor de restricoes [R] 
contidos no arquivo de entrada.

Sugestao de uso:
    
from funcoesTermosol import importa
[nn,N,nm,Inc,nc,F,nr,R] = importa('entrada.xlsx')
-------------------------------------------------------------------------------
A funcao 'geraSaida' cria um arquivo nome.txt contendo as reacoes de apoio Ft, 
deslocamentos Ut, deformacoes Epsi, forcas Fi e tensoes Ti internas. 
As entradas devem ser vetores coluna.

Sugestao de uso:
    
from funcoesTermosol import geraSaida
geraSaida(nome,Ft,Ut,Epsi,Fi,Ti)
-------------------------------------------------------------------------------

"""
from Domain import Node, Element, Solver
from math import *
import numpy as np

def plota(N,Inc,filename):
    # Numero de membros
    nm = len(Inc[:,0])
    
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    fig = plt.figure()
    # Passa por todos os membros
    for i in range(nm):
        
        # encontra no inicial [n1] e final [n2] 
        n1 = int(Inc[i,0])
        n2 = int(Inc[i,1])        

        plt.plot([N[0,n1-1],N[0,n2-1]],[N[1,n1-1],N[1,n2-1]],color='r',linewidth=3)


    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.grid(True)
    plt.axis('equal')
    plt.savefig(filename + '.eps', format='eps')
    plt.show()

def read_file(path):
    
    import xlrd
    
    arquivo = xlrd.open_workbook(path)
    
    ################################################## Ler os nos
    nos = arquivo.sheet_by_name('Nos')
    
    # Numero de nos
    nn = int(nos.cell(1,3).value)
                 
    # Matriz dos nós
    N = np.zeros((2,nn))
    
    for c in range(nn):
        N[0,c] = nos.cell(c+1,0).value
        N[1,c] = nos.cell(c+1,1).value
    
    ################################################## Ler a incidencia
    incid = arquivo.sheet_by_name('Incidencia')
    
    # Numero de membros
    nm = int(incid.cell(1,5).value)
                 
    # Matriz de incidencia
    Inc = np.zeros((nm,4))
    
    for c in range(nm):
        Inc[c,0] = int(incid.cell(c+1,0).value)
        Inc[c,1] = int(incid.cell(c+1,1).value)
        Inc[c,2] = incid.cell(c+1,2).value
        Inc[c,3] = incid.cell(c+1,3).value
    
    ################################################## Ler as cargas
    carg = arquivo.sheet_by_name('Carregamento')
    
    # Numero de cargas
    nc = int(carg.cell(1,4).value)
                 
    # Vetor carregamento
    F = np.zeros((nn*2,1))
    
    for c in range(nc):
        no = carg.cell(c+1,0).value
        xouy = carg.cell(c+1,1).value
        GDL = int(no*2-(2-xouy)) 
        F[GDL-1,0] = carg.cell(c+1,2).value
         
    ################################################## Ler restricoes
    restr = arquivo.sheet_by_name('Restricao')
    
    # Numero de restricoes
    nr = int(restr.cell(1,3).value)
                 
    # Vetor com os graus de liberdade restritos
    R = np.zeros((nr,1))
    
    for c in range(nr):
        no = restr.cell(c+1,0).value
        xouy = restr.cell(c+1,1).value
        GDL = no*2-(2-xouy) 
        R[c,0] = GDL-1


    return nn,N,nm,Inc,nc,F,nr,R

def geraSaida(nome,Ft,Ut,Epsi,Fi,Ti):
    nome = nome + '.txt'
    f = open(nome, "w+")
    f.write('Reacoes de apoio [N]\n')
    f.write(str(Ft))
    f.write('\n\nDeslocamentos [m]\n')
    f.write(str(Ut))
    f.write('\n\nDeformacoes []\n')
    f.write(str(Epsi))
    f.write('\n\nForcas internas [N]\n')
    f.write(str(Fi))
    f.write('\n\nTensoes internas [Pa]\n')
    f.write(str(Ti))
    f.close()

def nodes(nn, N):
    # Vetor dos nós
    nodes = [None] * nn
    for c in range(nn):
        nodes[c] = Node.Node(c+1, N[0,c], N[1,c])
    return nodes

def elements(nm, Inc, nodes):
    # Vetor de elementos
    E = [None] * nm
    for c in range(nm):
        E[c] = Element.Element(nodes[int(Inc[c,0] - 1)], nodes[int(Inc[c,1] - 1)], Inc[c,2], Inc[c,3])
    return E

def Kglobal(nn, E):
    # Matriz de rigidez global
    Kg = np.zeros((nn*2, nn*2))
    for e in E:
        Ke = e.Ke()
        for l in range(4):
            if l <= 1:
                gdl1 = e.n1.gdl[l]
            else:
                gdl1 = e.n2.gdl[l-2]
            
            for c in range(4):
                if c <= 1:
                    gdl2 = e.n1.gdl[c]
                else:
                    gdl2 = e.n2.gdl[c-2]
                
                Kg[gdl1-1, gdl2-1] += Ke[l][c]
    return Kg

def displacements(nr, R, E, Kg, F):
    # Aplicando condições de contorno
    Kg_ = Kg
    for a in range(nr):
        r = int(R[nr - a - 1][0])
        nrows, ncols = Kg_.shape
        for l in range(nrows):
            if nrows - l - 1 == r:
                F = np.delete(F, r)
                Kg_ = np.delete(Kg_, r, 0)
                break
        for c in range(ncols):
            if ncols - c - 1 == r:
                Kg_ = np.delete(Kg_, r, 1)
                Kg_.reshape(nrows-1, ncols-1)
                break
    
    # u, it = Solver.jacobi(Kg_, F)
    u, it = Solver.gauss_seidel(Kg_, F)

    for a in range(nr):
        r = int(R[a][0])
        u = np.insert(u, r, 0, 0)

    for e in E:
        e.n1.set_u(u[(e.n1.n - 1)*2])
        e.n2.set_u(u[(e.n2.n - 1)*2])
        e.n1.set_v(u[(e.n1.n)*2 - 1])
        e.n2.set_v(u[(e.n2.n)*2 - 1])
    
    return u

def lean_reactions(nr, R, nn, u, Kg):
    lean_R = R
    for i in range(nr):
        a = int(R[i][0])
        for x in range(nn*2):
            lean_R[i] += u[x]*Kg[a][x]
    return lean_R

def deform(E):
    E_d = np.zeros((len(E),1))
    for i in range(len(E)):
        E_d[i] = E[i].deform()
    return E_d
    
def internal_f(E):
    E_if = np.zeros((len(E),1))
    for i in range(len(E)):
        E_if[i] = E[i].internal_f()
    return E_if
    
def tension(E):
    E_t = np.zeros((len(E),1))
    for i in range(len(E)):
        E_t[i] = E[i].tension()
    return E_t

def new_nodes(N, u):
    newN = N
    Nrows, Ncols = N.shape
    for c in range(Ncols):
        for r in range(Nrows):
            newN[r][c] += u[c*Nrows + r]
    return newN

def main():
    filename = "entrada"
    nn, N, nm, Inc, nc, F, nr, R = read_file(filename + ".xlsx")

    nos = nodes(nn, N)
    E = elements(nm, Inc, nos)
    Kg = Kglobal(nn, E)

    u = displacements(nr, R, E, Kg, F)
    Ft = lean_reactions(nr, R, nn, u, Kg)
    Epsi = deform(E)
    Fi = internal_f(E)
    Ti = tension(E)
    geraSaida(filename, Ft, u, Epsi, Fi, Ti)

    plota(N, Inc, "antes")
    plota(new_nodes(N, u), Inc, "depois")

main()