from core.vehicle.vehicle_generator import VehicleGenerator
from core.geometry.quadratic_curve import QuadraticCurve
from core.geometry.cubic_curve import CubicCurve
from core.geometry.segment import Segment
from core.vehicle.vehicle import Vehicle
from core.signal.SignalGroup import TrafficSignal


class Simulation:

    def __init__(self):
        self.segments = []
        self.vehicles = {}
        self.vehicle_generator = []

        self.t = 0.0
        self.frame_count = 0
        self.dt = 1/60
        self.traffic_signals = {}

    def add_signal(self, signal):
        self.traffic_signals[signal.signal_id] = signal

    def add_vehicle(self, veh):
        self.vehicles[veh.id] = veh
        if len(veh.path) > 0:
            self.segments[veh.path[0]].add_vehicle(veh)

    def add_segment(self, seg):
        self.segments.append(seg)

    def add_vehicle_generator(self, gen):
        self.vehicle_generator.append(gen)

    def create_vehicle(self, **kwargs):
        veh = Vehicle(kwargs)
        self.add_vehicle(veh)

    def create_segment(self, *args):
        seg = Segment(args)
        self.add_segment(seg)

    def create_quadratic_bezier_curve(self, start, control, end):
        cur = QuadraticCurve(start, control, end)
        self.add_segment(cur)

    def create_cubic_bezier_curve(self, start, control_1, control_2, end):
        cur = CubicCurve(start, control_1, control_2, end)
        self.add_segment(cur)

    def create_vehicle_generator(self, **kwargs):
        gen = VehicleGenerator(kwargs)
        self.add_vehicle_generator(gen)

    def run(self, steps):
        for _ in range(steps):
            self.update()

    def update(self):
        # Update vehicles
        for segment in self.segments:
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
                    if self.vehicles[head_veh_id].x >= segment.length - segment.traffic_signal.stop_distance and \
                            self.vehicles[head_veh_id].x <= segment.length - segment.traffic_signal.stop_distance / 2:
                        # Stop vehicles in the stop zone
                        self.vehicles[head_veh_id].stop()
                self.vehicles[head_veh_id].update_position(None, self.dt)

            for i in range(1, len(segment.vehicles)):
                self.vehicles[segment.vehicles[i]].update_position(self.vehicles[segment.vehicles[i-1]], self.dt)

        # Check roads for out of bounds vehicle
        for segment in self.segments:
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
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.segments[next_road_index].vehicles.append(vehicle_id)
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











