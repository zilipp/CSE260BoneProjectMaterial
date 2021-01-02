# python libraries
import logging
import numpy
from matplotlib import pyplot
import matplotlib.pyplot as plt

# self defined functions
from core_alg.base import Bone
from core_alg.utilities import distance_util
from core_alg.utilities import bone_region_util

# parameter to tune error
hml_coeff = 0.996
heb_coeff = 0.994
hhd_coeff = 0.965


def get_hml(alpha_shape, show_figure, left_bone_points_ordered, right_bone_points_ordered):
    (min_x, _min_y, max_x, _max_y) = alpha_shape.exterior.bounds
    hml = max_x - min_x

    if show_figure:
        # most left point, 1st POIs
        p_left = []
        for i in range(len(left_bone_points_ordered)):
            if left_bone_points_ordered[i][0] == min_x:
                p_left = left_bone_points_ordered[i]
                break

        # most right point, 2nd POIs
        p_right = []
        right_most_idx = 0
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

    hml /= hml_coeff
    return hml


def get_heb(left_bone, show_figure, left_bone_points_ordered, alpha_shape):
    (_left_bone_min_x, left_bone_min_y, _left_bone_max_x,
     left_bone_max_y) = left_bone.exterior.bounds
    heb = left_bone_max_y - left_bone_min_y

    if show_figure:
        # top point, 1st POIs
        p_top = []
        for i in range(len(left_bone_points_ordered)):
            if left_bone_points_ordered[i][1] == left_bone_max_y:
                p_top = left_bone_points_ordered[i]
                break

        # bottom point, 1st POIs
        p_bottom = []
        for i in range(len(left_bone_points_ordered)):
            if left_bone_points_ordered[i][1] == left_bone_min_y:
                p_bottom = left_bone_points_ordered[i]
                break

        fig, ax = plt.subplots()
        x, y = alpha_shape.exterior.xy
        ax.plot(x, y)
        ax.plot(p_top[0], p_top[1], 'r+')
        ax.plot(p_bottom[0], p_bottom[1], 'r+')
        ax.set_aspect('equal')
        plt.show()

    heb /= heb_coeff
    return heb


def get_hhd(bone_right_region, right_region_points_ordered, show_figure, alpha_shape):
    (x_min, y_min, x_max, y_max) = bone_right_region.exterior.bounds

    convex_hull = list()
    for x, y in bone_right_region.convex_hull.exterior.coords:
        convex_hull.append([x, y])

    left_most_idx = [i for i, x_y in enumerate(convex_hull) if x_y[0] == x_min]
    if left_most_idx[1] - left_most_idx[0] == 1:
        convex_hull = convex_hull[left_most_idx[1]
            :] + convex_hull[:left_most_idx[0] + 1]

    up_most_idx = [i for i, x_y in enumerate(convex_hull) if x_y[1] == y_max]
    right_most_idx = [i for i, x_y in enumerate(
        convex_hull) if x_y[0] == x_max]
    bottom_most_idx = [i for i, x_y in enumerate(
        convex_hull) if x_y[1] == y_min]

    # Find point a and point b to get the upper point c
    y_delta_max = 0
    upper_point_a_idx = 0
    for i in range(up_most_idx[0], right_most_idx[0]):
        y_delta = convex_hull[i][1] - convex_hull[i+1][1]
        if y_delta > y_delta_max:
            y_delta_max = y_delta
            upper_point_a_idx = i
    point_a = convex_hull[upper_point_a_idx]
    point_b = convex_hull[upper_point_a_idx+1]

    point_a_idx = [i for i, x_y in enumerate(
        right_region_points_ordered) if x_y[0] == point_a[0]]
    point_b_idx = [i for i, x_y in enumerate(
        right_region_points_ordered) if x_y[0] == point_b[0]]

    max_dist = 0
    point_c_idx = 0

    num_of_points_between_a_b = point_b_idx[0] - point_a_idx[0]
    if num_of_points_between_a_b >= 3:
        for i in range(point_a_idx[0], point_b_idx[0] - 2):
            dist = 0
            for j in range(0, 3):
                dist = dist + distance_util.distance_point_to_line(
                    point_a, point_b, right_region_points_ordered[i+j])
            if dist > max_dist:
                max_dist = dist
                point_c_idx = i + 1

    point_c = right_region_points_ordered[point_c_idx]

    # Find bottom point d
    x_delta_max = 0
    point_d_idx = 0
    for i in range(bottom_most_idx[0], len(convex_hull)):
        x_delta = convex_hull[i-1][0] - convex_hull[i][0]
        if x_delta > x_delta_max:
            x_delta_max = x_delta
            point_d_idx = i-1
    point_d = convex_hull[point_d_idx]

    if show_figure:
        fig, ax = plt.subplots()

        data = numpy.asarray(right_region_points_ordered)
        x = data[:, 0].tolist()
        y = data[:, 1].tolist()
        ax.scatter(x, y, marker='o')

        data = numpy.asarray(convex_hull)
        x = data[:, 0].tolist()
        y = data[:, 1].tolist()
        ax.scatter(x, y, marker='*', facecolor='g')

        data = numpy.asarray([point_a, point_b])
        x = data[:, 0].tolist()
        y = data[:, 1].tolist()
        ax.scatter(x, y, marker='+', facecolor='orange')

        data = numpy.asarray([point_c, point_d])
        x = data[:, 0].tolist()
        y = data[:, 1].tolist()
        ax.scatter(x, y, marker='+', facecolor='r')

        ax.set_aspect('equal')
        plt.show()

    if show_figure:
        fig, ax = plt.subplots()
        x, y = alpha_shape.exterior.xy
        ax.plot(x, y)
        ax.plot(point_c[0], point_c[1], 'r+')
        ax.plot(point_d[0], point_d[1], 'r+')
        ax.set_aspect('equal')
        plt.show()

    hhd = distance_util.distance_point_to_point(point_c, point_d)
    hhd /= hhd_coeff
    return hhd


def get_measurement(humerus, show_figure):
    logging.info('Start measuring humerus...')

    left_region, left_region_points_ordered = bone_region_util.get_left_region(humerus.alpha_shape)
    right_region, right_region_points_ordered = bone_region_util.get_right_region(
        humerus.alpha_shape)

    humerus.hml = get_hml(humerus.alpha_shape, show_figure, left_region_points_ordered, right_region_points_ordered)
    humerus.heb = get_heb(left_region, show_figure, left_region_points_ordered, humerus.alpha_shape)
    humerus.hhd = get_hhd(
        right_region, right_region_points_ordered, show_figure, humerus.alpha_shape)
