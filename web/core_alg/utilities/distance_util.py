import open3d as o3d
import numpy as np
import math
import numpy.polynomial.polynomial as poly
import matplotlib.pyplot as plt


# functions for getting distances
def distance_point_to_line(p1, p2, p3):
    # point1 and point 2 formed a line, distance is point3 to that line
    p1 = np.asarray(p1)
    p2 = np.asarray(p2)
    p3 = np.asarray(p3)
    return np.abs(np.cross(p2 - p1, p3 - p1) / np.linalg.norm(p2 - p1))


def distance_2_point_to_point(p1, p2):
    # square of distance between point1 and point 2
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2


def distance_point_to_point(p1, p2):
    # distance between point1 and point 2
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# function for project point to plane
def point_to_plane(point, plane):
    # project point(xi, yi, zi) to plane[a, b, c, d]: ax + by + cz + d = 0
    # return new coordinates on the plane
    a = plane[0]
    b = plane[1]
    c = plane[2]
    d = plane[3]

    xi = point[0]
    yi = point[1]
    zi = point[2]

    t = (a * xi + b * yi + c * zi + d) / (a ** 2 + b ** 2 + c ** 2)
    x = xi - a * t
    y = yi - b * t
    z = zi - c * t

    res = [x, y, z]
    return res


# functions for fit line
def fit_line(points_array, show_figure):
    x = points_array[:, 0]
    y = points_array[:, 1]
    x_new = np.linspace(x[0], x[-1], num=len(x)*10)
    coefs = poly.polyfit(x, y, 2)

    y_draw = []
    for num in x_new:
        y_draw.append(coefs[2] * num*num + coefs[1] * num + coefs[0])

    if show_figure:
        plt.plot(x, y, label="line 1")
        plt.plot(x_new, y_draw, label="line 3")

        plt.legend()
        # plt.axes().set_aspect(1)
        plt.show()
    return coefs
