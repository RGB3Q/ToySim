
# coding: utf-8

from collections import deque
import logging
class Lane:
    def __init__(self, lane_index: int, lane_id: str, speed_limit: int, lane_width, lane_length):
        self.lane_index = lane_index
        self.lane_id = lane_id
        self.speed_limit = speed_limit
        self.lane_width = lane_width
        self.lane_length = lane_length

        self.vehicles = []

        self.index = None

        # self.allow_veh_type = None

    def create_vehicle_chain(self):
        for i in range(len(self.vehicles) - 2):
            self.vehicles[i].follow = self.vehicles[i + 1]
            self.vehicles[i + 1].lead = self.vehicles[i]
        return self.vehicles

    def add_vehicle(self, vehicle):
        if len(self.vehicles) > 0:
            vehicle.lead = self.vehicles[-1]
            self.vehicles[-1].follow = vehicle
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        self.vehicles.remove(vehicle)

        if vehicle.lead:
            vehicle.lead.follow = vehicle.follow
        if vehicle.follow:
            vehicle.follow.lead = vehicle.lead

        # 清除当前车辆与前后车辆的关联
        vehicle.lead = None
        vehicle.follow = None
        logging.info("REMOVE VEH: %s, AT LANE: %s, POS: %s" % (vehicle.id, self.lane_id, vehicle.x))
        logging.info("LANE VEH AFTER REMOVE: %s" % vehicle in self.vehicles)







