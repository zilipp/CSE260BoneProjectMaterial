# python libraries
import logging
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import matplotlib.patches as patches

from core_alg.base import Bone
from core_alg.utilities import bone_region_util

tml_coeff = 0.995
tpb_coeff = 0.985


def get_tml(alpha_shape, show_figure, left_bone_points_ordered, right_bone_points_ordered):
    (min_x, min_y, max_x, max_y) = alpha_shape.exterior.bounds
    x_length = max_x - min_x
    y_length = max_y - min_y

    # left-upper box
    left_upper_box = Polygon([(min_x, min_y + y_length * 0.75), (min_x, max_y), (min_x + x_length / 10, max_y), (min_x + x_length / 10, min_y + y_length * 0.75)])
    left_upper_bone = alpha_shape.intersection(left_upper_box)
    (min_x_left_upper, _, _, _) = left_upper_bone.exterior.bounds

    # left-lower box
    left_lower_box = Polygon([(min_x, min_y), (min_x, min_y + y_length * 0.25), (min_x + x_length / 10, min_y + y_length * 0.25),
                              (min_x + x_length / 10,  min_y)])
    left_lower_bone = alpha_shape.intersection(left_lower_box)
    (min_x_left_lower, _, _, _) = left_lower_bone.exterior.bounds

    poi_x = min(min_x_left_upper, min_x_left_lower)
    tml = max_x - poi_x

    if show_figure:
        # most left point, 1st POIs
        p_left = []
        for i in range(len(left_bone_points_ordered)):
            if left_bone_points_ordered[i][0] == poi_x:
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

        p_rec_left_bottom = [min_x - 20, min_y + y_length * 0.25]
        rect = patches.Rectangle((p_rec_left_bottom[0], p_rec_left_bottom[1]), 40, y_length * 0.5, linestyle='dashed',
                                 linewidth=0.5, edgecolor='b', facecolor='none')
        ax.add_patch(rect)
        ax.set_aspect('equal')
        plt.show()

    tml /= tml_coeff
    return tml


def get_tpb(alpha_shape, show_figure, left_bone, left_bone_points_ordered):
    (min_x, min_y, max_x, max_y) = alpha_shape.exterior.bounds
    tpb = max_y - min_y

    if show_figure:
        (left_bone_min_x, left_bone_min_y, left_bone_max_x,
         left_bone_max_y) = left_bone.exterior.bounds
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

    tpb /= tpb_coeff
    return tpb


def get_measurement(tibia, show_figure):
    logging.info('Start measuring tibia')
    left_region, left_region_points_ordered = bone_region_util.get_left_region(
        tibia.alpha_shape)
    _, right_region_points_ordered = bone_region_util.get_right_region(
        tibia.alpha_shape)
    tibia.tml = get_tml(tibia.alpha_shape, show_figure, left_region_points_ordered, right_region_points_ordered)
    tibia.tpb = get_tpb(tibia.alpha_shape, show_figure, left_region, left_region_points_ordered)
