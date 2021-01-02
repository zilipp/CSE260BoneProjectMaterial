# python libraries
import logging
import os
import open3d as o3d
import pywavefront
import numpy as np
from pathlib import Path

# self defined functions
from core_alg.base import Bone
from core_alg.scan import image_process
from core_alg.utilities import logging_utils
from core_alg.utilities import csv_out_utils
from core_alg.utilities import results_anlysis

# global variables
# logging file info
_out_root_dir = Path(os.path.dirname(os.path.abspath(__file__)))
_root_dir = _out_root_dir.parent
# user log directory
_user_logs_file = os.path.join(
    _out_root_dir, 'out', 'core_alg', 'logs', 'logs.txt')
_user_result_dir = os.path.join(_out_root_dir, 'out', 'core_alg', 'results')
# process more files
multi_files = False
index_default = 0
# switch for figure
show_figure = True
bone_type = Bone.Type.RADIUS
# switch for structure sensor or iphone10
structure_sensor = True


def load_file(index=index_default):
    bone_type_str = bone_type.name.lower()
    if structure_sensor:
        device = 'structure_sensor'
    else:
        device = 'iphone_ten'
    obj_dir = os.path.join(_root_dir, 'data', device, 'scan', bone_type_str,
                           '{}_{}.obj'.format(bone_type_str, str(index)))

    logging.info('Loading {0} dataset from {1}'.format(bone_type_str, obj_dir))
    scan_obj = pywavefront.Wavefront(
        obj_dir, strict=True, encoding="iso-8859-1", parse=True)

    # Scale unit length to 1 mm(coordinate 1000x)
    vertices = np.asarray(scan_obj.vertices) * 1000

    if not structure_sensor:
        # iphone_ten image has color info on "v" line
        vertices = vertices[:, :3]

    scan_pcd = o3d.geometry.PointCloud()
    scan_pcd.points = o3d.utility.Vector3dVector(vertices)

    if show_figure:
        o3d.visualization.draw_geometries([scan_pcd], mesh_show_wireframe=True)
    return scan_pcd


def process(scan_pcd):
    # 1. Init Bone
    bone = None
    if bone_type == Bone.Type.FEMUR:
        bone = Bone.Femur()
    elif bone_type == Bone.Type.HUMERUS:
        bone = Bone.Humerus()
    elif bone_type == Bone.Type.RADIUS:
        bone = Bone.Radius()
    elif bone_type == Bone.Type.TIBIA:
        bone = Bone.Tibia()

    # 2. 3D model pre-processing
    alpha_shape = image_process.preprocess_bone(
        scan_pcd, bone_type, show_figure)
    bone.set_alpha_shape(alpha_shape)

    # 3 Measurements
    bone.measure(show_figure)
    results = bone.get_measurement_results()
    logging.info(results)
    bone.reset_alpha_shape()

    return bone


if __name__ == "__main__":
    logging_utils.init_logger(_user_logs_file)

    bones = list()
    if multi_files:
        for i in range(9):
            # 1. Load file
            scan_pcd = load_file(i)
            bones.append(process(scan_pcd))
    else:
        scan_pcd = load_file()
        bones.append(process(scan_pcd))

    logging.info("writing results to csv file in output folder...")
    filename = csv_out_utils.csv_out(bones, bone_type, _user_result_dir)

    if multi_files:
        logging.info("analysing the results for multi-bones, last four rows are: "
                     "abs_avg_res, abs_std_res, scale_avg_res, scale_std_res")
        results_anlysis.analysis_csv(filename, bone_type)
