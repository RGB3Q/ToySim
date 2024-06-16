from abc import ABC

from scipy.interpolate import interp1d
from src.geometry.segment import Segment


class Connector:
    def __init__(self, id: str, points, from_segment: str, to_segment: str, connect_info: [list], ):
        self.id = id
        self.points = points
        self.from_segment = from_segment
        self.to_segment = to_segment

        # 连接. eg. [[0,0],[1,1],[2,2]]表示连接上下游对应的三条直行车道
        # 连接. eg. [[0,0],[0,1]]可以用于表示车道在该连接处的拓展情况（一车道变两车道）
        self.connect_info = connect_info
        # 构建一个多级字典，用于存储连接信息  eg. {"0":{"0":[],"1":[],"2":[]}}
        self.connections = {}
        self.create_connections()

        self.is_available = True

    def create_connections(self):
        """
        create connections between upstream and downstream
        :return:
        """
        for info in self.connect_info:
            connection_id = info[0]
            if not connection_id in self.connections:
                self.connections[connection_id] = {}
            for i in range(len(info)):
                segment_id = info[i]
                if not segment_id in self.connections[connection_id]:
                    self.connections[connection_id][segment_id] = []
                self.connections[connection_id][segment_id].append(self)
            if not connection_id in self.connections:
                self.connections[connection_id] =




