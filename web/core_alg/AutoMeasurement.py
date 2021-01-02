# python libraries
from django.http import JsonResponse
import json
import logging
import numpy as np
import os
import open3d as o3d
from pathlib import Path
import pywavefront


# self defined functions
from core_alg.base import Bone
from core_alg.scan import image_process
from core_alg.utilities import logging_utils
from core_alg.utilities import dict_result_to_csv

# global variables
# logging file info
_out_root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
_root_dir = _out_root_dir.parent
# user log directory
_user_logs_file = os.path.join(
    _out_root_dir, 'out', 'core_alg', 'logs', 'logs.txt')


class AutoMeasurement(object):
    def __init__(self):
        self.bone_type = None
        # switch for structure sensor or iphone10
        self.structure_sensor = True
        # user log directory
        self._user_logs_file = os.path.join(
            _out_root_dir, 'out', 'core_alg', 'logs', 'logs.txt')
        logging_utils.init_logger(_user_logs_file)

    def load_file(self):
        obj_dir = os.path.join(_root_dir, 'web', 'cache', 'cache.obj')
        logging.info('Loading model from {0}'.format(obj_dir))
        scan_obj = pywavefront.Wavefront(
            obj_dir, strict=True, encoding="iso-8859-1", parse=True)

        # Scale unit length to 1 mm(coordinate 1000x)
        vertices = np.asarray(scan_obj.vertices) * 1000

        if not self.structure_sensor:
            # iphone_ten image has color info on "v" line
            vertices = vertices[:, :3]

        scan_pcd = o3d.geometry.PointCloud()
        scan_pcd.points = o3d.utility.Vector3dVector(vertices)

        # if show_figure:
        #     o3d.visualization.draw_geometries([scan_pcd], mesh_show_wireframe=True)
        return scan_pcd

    def process(self, scan_pcd):
        # 1. Init Bone
        bone = None
        if self.bone_type == Bone.Type.FEMUR:
            bone = Bone.Femur()
        elif self.bone_type == Bone.Type.HUMERUS:
            bone = Bone.Humerus()
        elif self.bone_type == Bone.Type.RADIUS:
            bone = Bone.Radius()
        elif self.bone_type == Bone.Type.TIBIA:
            bone = Bone.Tibia()

        # 2. 3D model pre-processing
        alpha_shape = image_process.preprocess_bone(
            scan_pcd, self.bone_type, show_figure=False)
        bone.set_alpha_shape(alpha_shape)

        # 3 Measurements
        bone.measure(show_figure=False)
        results = bone.get_measurement_results()
        logging.info(results)
        bone.reset_alpha_shape()
        return bone

    def compute(self, request):
        # get bone type from request
        bone_type = request.POST.get('bone_type', 'Femur')

        if bone_type == "Femur":
            self.bone_type = Bone.Type.FEMUR
        elif bone_type == "Humerus":
            self.bone_type = Bone.Type.HUMERUS
        elif bone_type == "Tibia":
            self.bone_type = Bone.Type.TIBIA
        else:
            self.bone_type = Bone.Type.RADIUS

        # take measurement
        scan_pcd = self.load_file()
        bone = self.process(scan_pcd)
        measurement_result = bone.get_measurement_results()

        csv_result = dict_result_to_csv.dict_result_to_csv(measurement_result, bone_type)
        return csv_result
