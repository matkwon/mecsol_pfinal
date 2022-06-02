import numpy as np


def gauss_seidel(a,b):

    n = len(b)

    # initialize x
    x = np.zeros((n,1))

    # counter for number of iterations
    iterations = 0
    loop = True

    # perform Gauss-Seidel iterations until convergence
    while loop:
        for i in range(0,n):
            sum = 0
            for j in range(0,n):
                if j != i:
                    sum += a[i][j] * x[j]

            new_x = (b[i] - sum) / a[i][i]

            if new_x != 0:
                if abs((new_x - x[i]) / new_x) < 1e-10:
                    loop = False
                    break
                x[i] = new_x

        iterations += 1

    return x, iterations


def jacobi(a,b):

    n = len(b)

    # initialize x
    x = np.zeros((n, 1))

    # counter for number of iterations
    iterations = 0
    loop = True

    # perform Gauss-Seidel iterations until convergence
    while loop:
        prev_x = x.copy()
        for i in range(0,n):
            sum = 0
            for j in range(0,n):
                if j != i:
                    sum += a[i][j] * prev_x[j]

            new_x = (b[i] - sum) / a[i][i]

            if new_x != 0:
                if abs((new_x - x[i]) / new_x) < 1e-10:
                    loop = False
                    break
                x[i] = new_x

        iterations += 1

    return x, iterations