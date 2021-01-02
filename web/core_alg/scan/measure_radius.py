# python libraries
import logging
import numpy as np
import math
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly

# self defined functions
from core_alg.base import Bone
from core_alg.utilities import distance_util
from core_alg.utilities import bone_region_util

# parameter to tune error
rml_coeff = 0.996
rmld_coeff = 1.035


def get_rml(alpha_shape, show_figure, left_bone_points_ordered, right_bone_points_ordered):
    (min_x, min_y, max_x, max_y) = alpha_shape.exterior.bounds
    rml = max_x - min_x
    if show_figure:
        # most left point, 1st POIs
        p_left = []
        for i in range(len(left_bone_points_ordered)):
            if left_bone_points_ordered[i][0] == min_x:
                p_left = left_bone_points_ordered[i]
                break

        # most right point, 2nd POIs
        p_right = []
        for i in range(len(right_bone_points_ordered)):
            if right_bone_points_ordered[i][0] == max_x:
                p_right = right_bone_points_ordered[i]
                break

        fig, ax = plt.subplots()
        x, y = alpha_shape.exterior.xy
        ax.plot(x, y)
        ax.plot(p_left[0], p_left[1], 'r+')
        ax.plot(p_right[0], p_right[1], 'r+')
        ax.set_aspect('equal')
        plt.show()

    rml /= rml_coeff
    return rml


def get_rmld(center_bone_points, show_figure, alpha_shape):
    center_bone_points = np.asarray(center_bone_points)
    center_bone_points_upper = np.asarray(
        [x for x in center_bone_points if x[1] >= 0])
    center_bone_points_upper = center_bone_points_upper[np.argsort(
        center_bone_points_upper[:, 0])]

    center_bone_points_lower = np.asarray(
        [x for x in center_bone_points if x[1] <= 0])
    center_bone_points_lower = center_bone_points_lower[np.argsort(
        center_bone_points_lower[:, 0])]

    # fit two lines
    top_line_p = distance_util.fit_line(center_bone_points_upper, show_figure)
    bottom_line_p = distance_util.fit_line(
        center_bone_points_lower, show_figure)

    if show_figure:
        x = np.linspace(-25, 25, num=100)
        a = top_line_p[2] * x * x + top_line_p[1] * x + top_line_p[0]
        b = bottom_line_p[2] * x * x + bottom_line_p[1] * x + bottom_line_p[0]
        plt.plot(x, a, 'r')  # plotting t, a separately
        plt.plot(x, b, 'r')  # plotting t, b separately

        plt.scatter(
            center_bone_points_upper[:, 0], center_bone_points_upper[:, 1])
        plt.scatter(
            center_bone_points_lower[:, 0], center_bone_points_lower[:, 1])

        plt.scatter(
            center_bone_points_upper[:, 0], center_bone_points_upper[:, 1], marker='+')
        plt.scatter(
            center_bone_points_lower[:, 0], center_bone_points_lower[:, 1],  marker='+')

        plt.plot([0], [0], '*')  # plotting t, c separately
        plt.show()

    if show_figure:
        fig, ax = plt.subplots()
        x, y = alpha_shape.exterior.xy
        ax.plot(x, y)
        x = np.linspace(-25, 25, num=100)
        a = top_line_p[2] * x * x + top_line_p[1] * x + top_line_p[0]
        b = bottom_line_p[2] * x * x + bottom_line_p[1] * x + bottom_line_p[0]
        ax.plot(x, a, 'r')  # plotting t, a separately
        ax.plot(x, b, 'r')  # plotting t, b separately
        ax.plot([0], [0], 'r*')  # plotting t, c separately
        ax.set_aspect('equal')
        plt.show()

    # vertical line
    rmld = poly.polyval(0, top_line_p) - poly.polyval(0, bottom_line_p)

    # min_line_segment_length = rmld ** 2
    # for i in np.arange(-30, 30, .05):
    #     if i == 0:
    #         continue
    #     x = i
    #     y = top_line_p[2] * x * x + top_line_p[1] * x + top_line_p[0]
    #     k = y / x
    #     [x_res1, x_res2] = np.roots([bottom_line_p[2], bottom_line_p[1] - k, bottom_line_p[0]])
    #
    #     y_res1 = k * x_res1
    #     dis_1 = x_res1 ** 2 + y_res1 ** 2
    #     y_res2 = k * x_res2
    #     dis_2 = x_res2 ** 2 + y_res2 ** 2
    #
    #     [x1, y1] = [x_res1, y_res1] if dis_1 < dis_2 else [x_res2, y_res2]
    #
    #     dis_cur = distance_util.distance_2_point_to_point([x, y], [x1, y1])
    #     min_line_segment_length = min(dis_cur, min_line_segment_length)
    #
    # rmld = math.sqrt(min_line_segment_length)
    rmld /= rmld_coeff
    return rmld


def get_measurement(radius, show_figure):
    logging.info('Start measuring radius...')

    _, left_region_points_ordered = bone_region_util.get_left_region(
        radius.alpha_shape)
    center_region, center_region_points = bone_region_util.get_center_region(
        radius.alpha_shape)
    _, right_region_points_ordered = bone_region_util.get_right_region(
        radius.alpha_shape)

    radius.rml = get_rml(radius.alpha_shape, show_figure, left_region_points_ordered, right_region_points_ordered)
    radius.rmld = get_rmld(center_region_points, show_figure, radius.alpha_shape)
