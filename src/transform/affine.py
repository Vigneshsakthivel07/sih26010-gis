import numpy as np


def calculate_affine_transform(source_points, target_points):
    """
    Calculate affine transformation parameters.

    source_points:
        Historical FMB coordinates

    target_points:
        Modern projected coordinates
    """

    A = []
    B = []

    for (x, y), (X, Y) in zip(source_points, target_points):

        A.append([x, y, 1, 0, 0, 0])
        A.append([0, 0, 0, x, y, 1])

        B.append(X)
        B.append(Y)

    A = np.array(A)
    B = np.array(B)

    params, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

    return params


def transform_point(point, params):

    x, y = point

    a, b, c, d, e, f = params

    X = a * x + b * y + c
    Y = d * x + e * y + f

    return X, Y
