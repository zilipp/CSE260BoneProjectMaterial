from enum import Enum

from core_alg.scan import measure_radius, measure_tibia, measure_humerus, measure_femur


class Type(Enum):
    FEMUR = 1
    HUMERUS = 2
    RADIUS = 3
    TIBIA = 4


class BaseBone:

    def __init__(self, alpha_shape=None):
        self.alpha_shape = alpha_shape

    def set_alpha_shape(self, alpha_shape):
        self.alpha_shape = alpha_shape

    def reset_alpha_shape(self):
        self.alpha_shape = None


class Femur(BaseBone):

    def __init__(self, alpha_shape=None):
        super().__init__(alpha_shape)
        self.feb = None
        self.fbml = None
        self.fhd = None
        self.fml = None
        self.fmld = None

    def get_measurement_results(self):
        measurements = {
            'feb': self.feb,
            'fbml': self.fbml,
            'fhd': self.fhd,
            'fml': self.fml,
            'fmld': self.fmld
        }
        return measurements

    def measure(self, show_figure=False):
        measure_femur.get_measurement(self, show_figure)


class Humerus(BaseBone):

    def __init__(self, alpha_shape=None):
        super().__init__(alpha_shape)
        self.heb = None
        self.hhd = None
        self.hml = None

    def get_measurement_results(self):
        measurements = {
            'heb': self.heb,
            'hhd': self.hhd,
            'hml': self.hml
        }
        return measurements

    def measure(self, show_figure=False):
        measure_humerus.get_measurement(self, show_figure)


class Radius(BaseBone):

    def __init__(self, alpha_shape=None):
        super().__init__(alpha_shape)
        self.rml = None
        self.rmld = None

    def get_measurement_results(self):
        measurements = {
            'rml': self.rml,
            'rmld': self.rmld
        }
        return measurements

    def measure(self, show_figure=False):
        measure_radius.get_measurement(self, show_figure)


class Tibia(BaseBone):

    def __init__(self, alpha_shape=None):
        super().__init__(alpha_shape)
        self.tml = None
        self.tpb = None

    def get_measurement_results(self):
        measurements = {
            'tml': self.tml,
            'tpb': self.tpb
        }
        return measurements

    def measure(self, show_figure=False):
        measure_tibia.get_measurement(self, show_figure)
