from abc import ABC
from collections import deque

import numpy as np
from scipy.interpolate import interp1d
from src.geometry.segment import Segment


def generate_bezier_path(points, CURVE_RESOLUTION=15):
    start, control, end = points
    t = np.linspace(0, 1, CURVE_RESOLUTION)
    one_minus_t = 1 - t
    t_one_minus_t = t * one_minus_t

    x = t ** 2 * end[0] + 2 * t_one_minus_t * control[0] + one_minus_t ** 2 * start[0]
    y = t ** 2 * end[1] + 2 * t_one_minus_t * control[1] + one_minus_t ** 2 * start[1]

    path = np.column_stack((x, y))
    return path.tolist()


class Connector(Segment, ABC):
    def __init__(self, id: str, points, from_segment: str, to_segment: str, connect_info: [list], generative_bezier_curve=False):
        super().__init__(id, points, num_lanes=1, create_lanes=False)
        self.points = points

        self.from_segment = from_segment
        self.to_segment = to_segment

        self.id = from_segment + "_" + to_segment

        # 连接. eg. [[0,0],[1,1],[2,2]]表示连接上下游对应的三条直行车道
        # 连接. eg. [[0,0],[0,1]]可以用于表示车道在该连接处的拓展情况（一车道变两车道）
        self.connect_info = connect_info
        self.num_lanes = len(connect_info)
        # 构建一个多级字典，用于存储连接信息  eg. {"0":{"0":[],"1":[],"2":[]}}
        self.connections = {}
        self.create_connections()

        self.is_available = True
        self.vehicles = []
        # 获取最内侧（左侧）的连接线编号
        self.innermost_connection_id = min(self.connect_info, key=lambda x: x[0])[0]

        self.generative_bezier_curve = generative_bezier_curve
        if self.generative_bezier_curve:
            self.start = points[0]
            self.control = points[1]
            self.end = points[2]
            self.points = generate_bezier_path(self.points)
            super().__init__(id, self.points, num_lanes=self.num_lanes, create_lanes=False)

    def create_connections(self):
        """
        create connections between upstream and downstream segments
        :return:
        """
        for info in self.connect_info:
            connection_id = str(info[0])
            if not connection_id in self.connections:
                self.connections[connection_id] = {str(info[1]): deque()}
            else:
                self.connections[connection_id].update({str(info[1]): deque()})

    def add_vehicle(self, veh, from_lane, to_lane):
        target_connection = self.connections[from_lane][to_lane]
        target_connection.append(veh)
        if len(target_connection) > 1:
            veh.lead = target_connection[-2]
            target_connection[-2].follow = veh
        self.vehicles.append(veh)

    def remove_vehicle(self, veh, from_lane, to_lane):
        target_connection = self.connections[from_lane][to_lane]
        target_connection.remove(veh)
        if veh.lead:
            print('Error: vehicle is not at the front of the connection queue')
            veh.lead.follow = veh.follow
        if veh.follow:
            veh.follow.lead = None
        # 清除当前车辆与前后车辆的关联
        veh.lead = None
        veh.follow = None
        self.vehicles.remove(veh)

    def get_closest_lane(self, lane_id: int):
        """
        get the closest lane to the given lane_id
        :param lane_id: 车辆在进入连接处时所在的lane_id
        :return: 离当前lane_id最近的连接器from lane_id
        """
        if str(lane_id) in self.connections.keys():
            return str(lane_id)
        else:  # get number which is closest to lane_id
            min_gap: int = 100
            closest_lane_id = None
            for candidate_lane_id in self.connections.keys():
                gap = abs(int(candidate_lane_id) - lane_id)
                if gap < min_gap:
                    min_gap = gap
                    closest_lane_id = candidate_lane_id
            return closest_lane_id

    def compute_x(self, t):
        return t ** 2 * self.end[0] + 2 * t * (1 - t) * self.control[0] + (1 - t) ** 2 * self.start[0]

    def compute_y(self, t):
        return t ** 2 * self.end[1] + 2 * t * (1 - t) * self.control[1] + (1 - t) ** 2 * self.start[1]

    def compute_dx(self, t):
        return 2 * t * (self.end[0] - 2 * self.control[0] + self.start[0]) + 2 * (self.control[0] - self.start[0])

    def compute_dy(self, t):
        return 2 * t * (self.end[1] - 2 * self.control[1] + self.start[1]) + 2 * (self.control[1] - self.start[1])
