
# coding: utf-8


class Lane:
    def __init__(self, lane_id: str, speed_limit: int, lane_width, lane_length):
        self.lane_id = lane_id
        self.speed_limit = speed_limit
        self.lane_width = lane_width
        self.lane_length = lane_length

        self.vehicles = []

        # self.allow_veh_type = None

    def create_vehicle_chain(self):
        for i in range(len(self.vehicles) - 2):
            self.vehicles[i].follow = self.vehicles[i + 1]
            self.vehicles[i + 1].lead = self.vehicles[i]
        return self.vehicles

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        if len(self.vehicles) > 1:
            vehicle.lead = self.vehicles[-2]
            self.vehicles[-2].follow = vehicle

    def remove_vehicle(self, vehicle):
        self.vehicles.remove(vehicle)
        vehicle.lead.follow = vehicle.follow
        vehicle.follow.lead = vehicle.lead






