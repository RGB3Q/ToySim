from abc import ABC
from collections import deque
from scipy.interpolate import interp1d
from src.geometry.segment import Segment


class Connector(Segment, ABC):
    def __init__(self, id: str, points, from_segment: str, to_segment: str, connect_info: [list]):
        super().__init__(id, points, num_lanes=1, create_lanes=False)
        self.points = points
        self.from_segment = from_segment
        self.to_segment = to_segment

        self.id = from_segment+"_"+to_segment

        # 连接. eg. [[0,0],[1,1],[2,2]]表示连接上下游对应的三条直行车道
        # 连接. eg. [[0,0],[0,1]]可以用于表示车道在该连接处的拓展情况（一车道变两车道）
        self.connect_info = connect_info
        # 构建一个多级字典，用于存储连接信息  eg. {"0":{"0":[],"1":[],"2":[]}}
        self.connections = {}
        self.create_connections()

        self.is_available = True
        self.vehicles = []

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











