# python libraries
import logging
import numpy as np
import open3d as o3d
from sklearn.decomposition import PCA
import alphashape
from shapely import affinity
from shapely.geometry import Polygon
from matplotlib import pyplot as plt
import random

# self defined functions
from core_alg.base import Bone
from core_alg.utilities import distance_util
from core_alg.utilities import visualization_util

# random.seed(1)

# params for remove background
distance_threshold_femur = 3
distance_threshold_radius = 3
distance_threshold_tibia = 2
ransac_n = 3
num_iterations = 10000

nb_neighbors_femur = 20
nb_neighbors_radius = 20
nb_neighbors_humerus = 20

std_ratio_femur = 0.5
std_ratio_radius = 2
std_ratio_humerus = 2

# params for alpha-shape
alpha_radius = 0.05
alpha_femur = 0.4


def scale_image(scan_obj):
    # Scale unit length from 1m to 1mm (coordinate 1000x)
    points_center = scan_obj.get_center()
    scan_obj.scale(1000.0, points_center)
    return scan_obj


def mesh_to_points_cloud(scan_obj):
    number_of_points = np.asarray(scan_obj.vertices).shape[0]
    scan_obj.compute_vertex_normals()
    scan_pcd1 = scan_obj.sample_points_uniformly(number_of_points*2)

    # todo: check for randomness
    scan_pcd2 = scan_obj.sample_points_uniformly(number_of_points*2)

    return scan_pcd1


def remove_background(scan_pcd, bone_type, show_figure):
    # find plane using RANSAC: plane function: ax + by + cz + d = 0
    # todo: check for randomness
    plane_model, inliers = None, None
    if bone_type == Bone.Type.RADIUS:
        plane_model, inliers = scan_pcd.segment_plane(distance_threshold=distance_threshold_radius,
                                                      ransac_n=ransac_n,
                                                      num_iterations=num_iterations)
    elif bone_type == Bone.Type.TIBIA:
        plane_model, inliers = scan_pcd.segment_plane(distance_threshold=distance_threshold_tibia,
                                                      ransac_n=ransac_n,
                                                      num_iterations=num_iterations)
    else:
        plane_model, inliers = scan_pcd.segment_plane(distance_threshold=distance_threshold_femur,
                                                      ransac_n=ransac_n,
                                                      num_iterations=num_iterations)

    plane = plane_model
    # print(f"Plane equation: {plane[0]:.5f}x + {plane[1]:.5f}y + {plane[2]:.5f}z + {plane[3]:.5f} = 0")

    # floor
    inlier_cloud = scan_pcd.select_by_index(inliers)
    inlier_cloud.paint_uniform_color([1.0, 0, 0])

    # bone
    bone_cloud = scan_pcd.select_by_index(inliers, invert=True)
    # show image without background
    if show_figure:
        o3d.visualization.draw_geometries([bone_cloud], mesh_show_wireframe=True)
    return bone_cloud, plane


def remove_noise_points(bone_cloud, bone_type, show_figure):
    cl, ind = None, None
    if bone_type == Bone.Type.HUMERUS:
        cl, ind = bone_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors_humerus,
                                                        std_ratio=std_ratio_humerus)
    elif bone_type == Bone.Type.RADIUS:
        cl, ind = bone_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors_radius,
                                                        std_ratio=std_ratio_radius)
    else:
        cl, ind = bone_cloud.remove_statistical_outlier(nb_neighbors=nb_neighbors_femur,
                                                        std_ratio=std_ratio_femur)

    # display outliers
    if show_figure:
        visualization_util.display_inlier_outlier(bone_cloud, ind)

    bone_cloud = bone_cloud.select_by_index(ind)
    return bone_cloud


def project_points_to_plane(bone_cloud, plane, show_figure):
    # project 3D points to the ground plane
    # return points on the ground plane
    # https://math.stackexchange.com/questions/100761/how-do-i-find-the-projection-of-a-point-onto-a-plane
    bone_points = np.array(bone_cloud.points)
    projected_bone_points = []
    for i in range(bone_points.shape[0]):
        point = bone_points[i]
        projected_bone_points.append(
            distance_util.point_to_plane(point, plane))

    bone_points = np.array(projected_bone_points)

    bone_pcd = o3d.geometry.PointCloud()
    bone_pcd.points = o3d.utility.Vector3dVector(bone_points)

    if show_figure:
        o3d.visualization.draw_geometries(
            [bone_pcd, visualization_util.get_visualization_axis()])
    return bone_pcd


def change_axis_with_PCA(bone_pcd, show_figure):
    # move the center to original point
    bone_points = np.asarray(bone_pcd.points)
    bone_points = bone_points - bone_points.mean(axis=0, keepdims=True)
    # print('bone_points move to original point: ', bone_points)

    pca = PCA(n_components=3)
    pca.fit(bone_points)
    # print('pca.components_: ', pca.components_)

    # use right-hand rule to prevent flipping
    x_ = pca.components_[0]
    y_ = pca.components_[1]
    z_ = np.cross(x_, y_)
    tran_matrix = np.array([x_, y_, z_])
    # print('tran_matrix: ', tran_matrix)

    bone_after_pca = np.dot(tran_matrix, bone_points.T).T
    # print('bone_after_pca: ', bone_after_pca)

    final_pcd = o3d.geometry.PointCloud()
    final_pcd.points = o3d.utility.Vector3dVector(bone_after_pca)

    if show_figure:
        o3d.visualization.draw_geometries(
            [final_pcd, visualization_util.get_visualization_axis()])

    return final_pcd


def three_d_to_two_d(bone_pcd):
    three_d_points = np.asarray(bone_pcd.points)
    two_d_points = []
    for i in range(three_d_points.shape[0]):
        point = three_d_points[i]
        x = point[0]
        y = point[1]
        two_d_points.append([x, y])

    res = np.array(two_d_points)
    return res


def get_alpha_shape(points, bone_type, show_figure):
    # todo: a-value
    alpha_shape = None
    if bone_type == Bone.Type.RADIUS:
        alpha_shape = alphashape.alphashape(points, alpha_radius)
    else:
        alpha_shape = alphashape.alphashape(points, alpha_femur)

    if alpha_shape.geom_type == 'MultiPolygon':
        areas = [i.area for i in alpha_shape]
        # Get the area of the largest part
        max_area = areas.index(max(areas))
        # Return the index of the largest area
        alpha_shape = alpha_shape[max_area]

    if show_figure:
        alpha_shape_pts = alpha_shape.exterior.coords.xy
        fig, ax = plt.subplots()
        ax.scatter(points[:, 0], points[:, 1], color='blue')
        ax.scatter(alpha_shape_pts[0], alpha_shape_pts[1], color='red')
        # ax.add_patch(PolygonPatch(alpha_shape, fill=False, color='green'))
        ax.set_aspect('equal')
        plt.show()

    (min_x, min_y, max_x, max_y) = alpha_shape.exterior.bounds
    x_length = max_x - min_x
    y_length = max_y - min_y

    if bone_type == Bone.Type.TIBIA or bone_type == Bone.Type.RADIUS:
        # radius and tibia: need bigger part on the left
        left_box = Polygon([(min_x, min_y), (min_x, max_y), (min_x +
                                                             x_length / 8, max_y), (min_x + x_length / 10, min_y)])
        left_bone = alpha_shape.intersection(left_box)
        right_box = Polygon([(max_x - x_length / 8, min_y), (max_x -
                                                             x_length / 8, max_y), (max_x, max_y), (max_x, min_y)])
        right_bone = alpha_shape.intersection(right_box)
        if left_bone.area < right_bone.area:
            alpha_shape = affinity.scale(
                alpha_shape, xfact=-1, yfact=1, origin=(0, 0))

    elif bone_type == Bone.Type.FEMUR or bone_type == Bone.Type.HUMERUS:
        # both femur and humerus need put head to right-lower corner
        # femur and humerus: head on the left or right
        left_box = Polygon(
            [(min_x, min_y), (min_x, max_y), (min_x + x_length / 10, max_y), (min_x + x_length / 10, min_y)])
        left_bone = alpha_shape.intersection(left_box)
        right_box = Polygon(
            [(max_x - x_length / 10, min_y), (max_x - x_length / 10, max_y), (max_x, max_y), (max_x, min_y)])
        right_bone = alpha_shape.intersection(right_box)
        if left_bone.area < right_bone.area:
            alpha_shape = affinity.scale(
                alpha_shape, xfact=-1, yfact=1, origin=(0, 0))

        # head on the upper or lower part
        center_box = Polygon([(min_x + x_length * 0.4, min_y), (min_x + x_length * 0.4, max_y),
                              (max_x + x_length * 0.6, max_y), (max_x + x_length * 0.6, min_y)])
        center_bone = alpha_shape.intersection(center_box)
        if (max_y - center_bone.centroid.y) > y_length / 2:
            alpha_shape = affinity.scale(
                alpha_shape, xfact=1, yfact=-1, origin=(0, 0))

    if show_figure:
        fig, ax = plt.subplots()
        x, y = alpha_shape.exterior.xy
        ax.plot(x, y)
        ax.set_aspect('equal')
        plt.show()
    return alpha_shape


def preprocess_bone(scan_pcd, bone_type, show_figure):
    logging.info('Pre-processing {}'.format(bone_type.name.lower()))

    # 1. Scale unit length to 1 mm(coordinate 1000x)
    # scan_pcd = scale_image(scan_pcd)

    # 2. Change mesh to point cloud
    # scan_pcd = mesh_to_points_cloud(scan_pcd)

    # 3. Remove background
    bone_cloud, plane = remove_background(scan_pcd, bone_type, show_figure)

    # 4. Remove noise points
    bone_cloud = remove_noise_points(bone_cloud, bone_type, show_figure)

    # 5. Project points to plane
    bone_pcd = project_points_to_plane(bone_cloud, plane, show_figure)

    # 6. PCA: find longest axis
    bone_pcd = change_axis_with_PCA(bone_pcd, show_figure)

    # 7. 3d points to 2D points:
    bone_points = three_d_to_two_d(bone_pcd)

    # 8. Get alpha shape
    alpha_shape = get_alpha_shape(bone_points, bone_type, show_figure)
    return alpha_shape
