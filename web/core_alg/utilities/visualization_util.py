import open3d as o3d


# utils for visualization
def get_visualization_axis():
    # add axis on image
    aix_points = [[0, 0, 0],
                  [0, 0, 100],
                  [400, 0, 0],
                  [0, 100, 0],
                  [-400, 0, 0]]
    aix_lines = [[0, 1],  # z-axis
                 [0, 2],  # x-axis
                 [0, 3]]  # y-axis

    # z: magenta, y: black, x: black
    colors = [[1, 0, 1], [0, 0, 0], [0, 0, 0]]
    aix_line_set = o3d.geometry.LineSet(points=o3d.utility.Vector3dVector(aix_points),
                                        lines=o3d.utility.Vector2iVector(aix_lines))
    aix_line_set.colors = o3d.utility.Vector3dVector(colors)
    return aix_line_set


def display_inlier_outlier(cloud, ind):
    # Showing outliers (red) and inliers (gray)
    inlier_cloud = cloud.select_by_index(ind)
    outlier_cloud = cloud.select_by_index(ind, invert=True)

    outlier_cloud.paint_uniform_color([1, 0, 0])
    inlier_cloud.paint_uniform_color([0.8, 0.8, 0.8])
    o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])
