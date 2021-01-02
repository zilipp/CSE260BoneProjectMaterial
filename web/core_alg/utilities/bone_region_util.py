# python libraries
from shapely.geometry import Polygon


def get_left_region(alpha_shape):
    (minx, miny, maxx, maxy) = alpha_shape.exterior.bounds
    # todo: coefficient
    left_box = Polygon([(minx, miny), (minx, maxy), (minx / 1.5, maxy), (minx / 1.5, miny)])
    left_region = alpha_shape.intersection(left_box)

    left_region_line = left_region.exterior
    left_region_points = []
    for x, y in left_region_line.coords:
        left_region_points.append([x, y])
    # the first and last element are the same point in Polygon object, remove last element
    left_region_points = left_region_points[:-1]

    max_diff_y = 0
    a_idx = 0
    for i in range(len(left_region_points) - 1):
        diff_cur = abs(left_region_points[i][1] - left_region_points[i + 1][1])
        if diff_cur > max_diff_y:
            max_diff_y = diff_cur
            a_idx = i

    diff_last = abs(left_region_points[len(left_region_points) - 1][1] - left_region_points[0][1])
    if diff_last > max_diff_y:
        max_diff_y = diff_last
        a_idx = len(left_region_points) - 1

    # a(-, +), b(-, -)
    # start with point_b(right-lower point)
    left_region_points_ordered = left_region_points[a_idx + 1:] + left_region_points[:a_idx + 1]

    return left_region, left_region_points_ordered


def get_right_region(alpha_shape):
    (minx, miny, maxx, maxy) = alpha_shape.exterior.bounds
    # todo: coefficient
    right_box = Polygon([(maxx / 1.5, miny), (maxx / 1.5, maxy), (maxx, maxy), (maxx, miny)])
    right_region = alpha_shape.intersection(right_box)

    right_region_line = right_region.exterior
    right_region_points = []
    for x, y in right_region_line.coords:
        right_region_points.append([x, y])
    # the first and last element are the same point in Polygon object, remove last element
    right_region_points = right_region_points[:-1]

    max_diff_y = 0
    a_idx = 0
    for i in range(len(right_region_points) - 1):
        diff_cur = abs(right_region_points[i][1] - right_region_points[i + 1][1])
        if diff_cur > max_diff_y:
            max_diff_y = diff_cur
            a_idx = i

    diff_last = abs(right_region_points[len(right_region_points) - 1][1] - right_region_points[0][1])
    if diff_last > max_diff_y:
        a_idx = len(right_region_points) - 1

    # a(+, -), b(+, +)
    # start with point_b(left-upper point)
    right_region_points_ordered = right_region_points[a_idx + 1:] + right_region_points[:a_idx + 1]
    return right_region, right_region_points_ordered


def get_center_region(alpha_shape):
    (minx, miny, maxx, maxy) = alpha_shape.exterior.bounds
    # todo: coefficient
    center_box = Polygon([(minx / 4, miny), (minx / 4, maxy), (maxx / 4, maxy), (maxx / 4, miny)])
    center_bone = alpha_shape.intersection(center_box)

    center_bone_line = center_bone.exterior
    center_bone_points = []
    for x, y in center_bone_line.coords:
        center_bone_points.append([x, y])
    center_bone_points = center_bone_points[:-1]

    return center_bone, center_bone_points
