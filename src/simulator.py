import time

from src.vehicle.vehicle_generator import VehicleGenerator
from src.geometry.quadratic_curve import QuadraticCurve
from src.geometry.cubic_curve import CubicCurve
from src.geometry.segment import Segment
from src.geometry.connectors import Connector
from src.vehicle.vehicle import Vehicle
from src.signal.SignalGroup import TrafficSignal
import random
import logging
import colorlog

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
# 将颜色输出格式添加到控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(color_formatter)
logger = logging.getLogger()
for handler in logger.handlers:
    logger.removeHandler(handler)
    # 将控制台日志处理器添加到logger对象
    logger.addHandler(console_handler)

class Simulation:

    def __init__(self):
        self.segments = {}
        self.connectors = {}
        self.vehicles = {}
        self.vehicle_generator = []

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1 / 60
        self.traffic_signals = {}

        # self.lanes = {}

    def add_signal(self, signal):
        self.traffic_signals[signal.signal_id] = signal

    def add_vehicle(self, veh):
        self.vehicles[veh.id] = veh
        if len(veh.path) > 0:
            # 从lanes列表中随机选取一个对象
            obj_lane = random.choice(self.segments[veh.path[0]].lanes)
            obj_lane.add_vehicle(veh)
            veh.at_lane = obj_lane.lane_index
            # log the add veh time and veh id
            logging.info("T: %s, ADD VEH: %s, AT LANE: %s" % (self.t, veh.id, obj_lane.lane_id))

    def add_segment(self, seg):
        self.segments.update({seg.id: seg})

    def add_connector(self, connector: Connector):
        self.connectors.update({connector.id: connector})

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, *args):
        seg = Segment(*args)
        self.add_segment(seg)

    def create_connector(self, *args, generative_bezier_curve=False):
        if not generative_bezier_curve:
            connector = Connector(*args)
        else:
            connector = Connector(*args, generative_bezier_curve=True)
        self.add_connector(connector)

    def create_quadratic_bezier_curve(self, id, points, lanes):
        cur = QuadraticCurve(id, points, lanes)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, id, points, lanes):
        cur = CubicCurve(id, points, lanes)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)

    def run(self, steps, delay: int):
        """
        Run the simulation for a given number of steps
        :param steps:
        :param delay: ms
        :return:
        """
        for _ in range(steps):
            self.update_with_lane(delay)

    # update_without_lane未加入换道逻辑，已弃用
    def update_without_lane(self):
        # Update vehicles
        for segment in self.segments.values():
            if len(segment.vehicles) != 0:
                head_veh_id = segment.vehicles[0]
                # segment.update()
                if segment.traffic_signal_state:
                    # If traffic signal is green or doesn't exist
                    # Then let vehicles pass
                    self.vehicles[head_veh_id].unstop()
                    for vehicle_id in segment.vehicles:
                        self.vehicles[vehicle_id].unslow()
                else:
                    # If traffic signal is red
                    if self.vehicles[head_veh_id].x >= segment.length - segment.traffic_signal.slow_distance:
                        # Slow vehicles in slowing zone
                        self.vehicles[head_veh_id].slow(segment.traffic_signal.slow_speed)
                    if segment.length - segment.traffic_signal.stop_distance <= \
                            self.vehicles[head_veh_id].x <= segment.length - segment.traffic_signal.stop_distance / 2:
                        # if self.vehicles[head_veh_id].x >= segment.length - segment.traffic_signal.stop_distance and \
                        #         self.vehicles[head_veh_id].x <= segment.length - segment.traffic_signal.stop_distance / 2:
                        # Stop vehicles in the stop zone
                        self.vehicles[head_veh_id].stop()
                self.vehicles[head_veh_id].IDM(None, self.dt)

            for i in range(1, len(segment.vehicles)):
                self.vehicles[segment.vehicles[i]].IDM(self.vehicles[segment.vehicles[i - 1]], self.dt)

        # Check roads for out of bounds vehicle
        for segment in self.segments.values():
            # If road has no vehicles, continue
            if len(segment.vehicles) == 0:
                continue
            # If not
            vehicle_id = segment.vehicles[0]
            vehicle = self.vehicles[vehicle_id]
            # If first vehicle is out of road bounds
            if vehicle.x >= segment.length:
                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Add it to the next road
                    next_road_id = vehicle.path[vehicle.current_road_index]
                    self.segments[next_road_id].vehicles.append(vehicle_id)
                # Reset vehicle properties
                vehicle.x = 0
                # In all cases, remove it from its road
                segment.vehicles.popleft()

        # Update traffic lights
        for sigal_id, signal in self.traffic_signals.items():
            signal.update(self)

        # Update vehicle generators
        for gen in self.vehicle_generator:
            gen.update(self)
        # Increment time
        self.t += self.dt
        self.frame_count += 1

    def update_with_lane(self, delay: int):
        # Update vehicles
        for segment in self.segments.values():
            for lane_index, lane in enumerate(segment.lanes):
                adjacent_lanes = [
                    lane,
                    segment.lanes[lane_index - 1] if lane_index > 0 else None,
                    segment.lanes[lane_index + 1] if lane_index + 1 < len(segment.lanes) else None
                ]

                # update vehicles on each lane
                if len(lane.vehicles) != 0:
                    head_veh: Vehicle = lane.vehicles[0]
                    # segment.update()
                    if segment.traffic_signal_state:
                        # If TRUE: traffic signal is green or doesn't exist, Then let vehicles pass
                        head_veh.unstop()
                        head_veh.unslow()
                    else:
                        # If traffic signal is red
                        if head_veh.x >= segment.length - segment.traffic_signal.slow_distance:
                            # Slow vehicles in slowing zone
                            if not head_veh.slowing_down:
                                head_veh.slow(segment.traffic_signal.slow_speed)
                            # print("slowing down: %s  %.2f" % (head_veh.id, head_veh.x), head_veh.slowing_down)
                        if segment.length - segment.traffic_signal.stop_distance <= \
                                head_veh.x <= segment.length - segment.traffic_signal.stop_distance / 2:
                            if not head_veh.stopped:
                                head_veh.stop()
                    # 注意：slow() 和 stop() 用于改变车辆的状态标记，IDM函数会根据状态标记记性对应的加速度计算
                    head_veh.present_a = head_veh.IDM(None, self.dt)  # 计算假使保持在当前车道上的加速度
                    if not head_veh.x > segment.length - segment.ban_lane_change_distance:
                        head_veh.a = head_veh.evaluate_and_perform_lane_change(adjacent_lanes)
                        head_veh.update_position_and_velocity()
                    else:
                        head_veh.a = head_veh.present_a
                        head_veh.update_position_and_velocity()

                # update vehicles using IDM and MOBIL
                if len(lane.vehicles) > 1:
                    for veh in lane.vehicles[1:]:
                        veh.present_a = veh.IDM(veh.lead, self.dt)
                        if not veh.x > segment.length - segment.ban_lane_change_distance:
                            veh.a = veh.evaluate_and_perform_lane_change(adjacent_lanes)
                            veh.update_position_and_velocity()
                        else:
                            veh.a = veh.present_a
                            veh.update_position_and_velocity()

            # Check segment for out of bounds vehicle, perform segment->connector transfer
            for lane in segment.lanes:
                # If seg has no vehicles, continue
                if len(lane.vehicles) == 0:
                    continue
                # If not
                vehicle = lane.vehicles[0]
                # If first vehicle is out of road bounds
                if vehicle.x >= lane.lane_length:
                    # If vehicle has a next road
                    if vehicle.current_road_index + 1 < len(vehicle.path):
                        # Update current road to next road
                        # vehicle.current_road_index += 1
                        # Add it to the next road
                        # next_road_id = vehicle.path[vehicle.current_road_index]
                        next_connector_index = vehicle.path[vehicle.current_road_index] + "_" + \
                                               vehicle.path[vehicle.current_road_index + 1]
                        next_connector: Connector = self.connectors[next_connector_index]
                        if next_connector.is_available:
                            from_lane = next_connector.get_closest_lane(vehicle.at_lane)
                            to_lane_candidates = next_connector.connections[from_lane]
                            # 选取连接器链接的下游路段lane
                            vehicle.to_lane = random.choice(list(to_lane_candidates.keys()))
                            # obj_connect = to_lane_candidates[vehicle.to_lane]
                            lane.remove_vehicle(vehicle)
                            next_connector.add_vehicle(vehicle, from_lane, vehicle.to_lane)
                            # 更新vehicle在连接器上的相对位置，便于绘制
                            vehicle.at_lane = int(from_lane) - next_connector.innermost_connection_id
                            vehicle.x = 0

                        # self.segments[next_road_id].lanes[vehicle.at_lane].add_vehicle(vehicle)
                        # remove it from its road
                        # lane.vehicles.remove(vehicle)
                        # lane.remove_vehicle(vehicle)
                        # Reset vehicle properties
                        # vehicle.x = 0
                    else:
                        # lane.vehicles.remove(vehicle)
                        lane.remove_vehicle(vehicle)

        for connector in self.connectors.values():
            for from_lane, to_lane_dic in connector.connections.items():
                for to_lane, d_que in to_lane_dic.items():
                    if len(d_que) == 0:
                        continue
                    # Check connectors for out of bounds vehicle, perform connector->segment transfer
                    head_veh = d_que[0]
                    head_veh.a = head_veh.IDM(None, self.dt)
                    head_veh.update_position_and_velocity()
                    if len(d_que) > 1:
                        i = 0
                        for veh in d_que:
                            if i == 0:
                                i += 1
                                continue
                            veh.a = veh.IDM(veh.lead, self.dt)
                            veh.update_position_and_velocity()

                    if head_veh.x > connector.length:
                        connector.remove_vehicle(head_veh, from_lane, to_lane)
                        self.segments[connector.to_segment].lanes[int(to_lane)].add_vehicle(head_veh)
                        head_veh.x = 0
                        head_veh.current_road_index += 1

        # Update traffic lights
        for signal_id, signal in self.traffic_signals.items():
            signal.update(self)

        # Update vehicle generators
        for gen in self.vehicle_generator:
            gen.update(self)
        # Increment time
        self.t += self.dt
        self.frame_count += 1
        # time.sleep(delay/100)
