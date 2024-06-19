from scipy.spatial import distance
from scipy.interpolate import interp1d
from collections import deque
from numpy import arctan2, unwrap, linspace
from abc import ABC, abstractmethod
from math import sqrt
from scipy.integrate import quad
from src.signal.SignalGroup import TrafficSignal
from src.geometry.lanes import Lane


# define a class for a road segment for micro simulation
class Segment:
    def __init__(self, id: str, points, num_lanes, create_lanes=True):
        self.get_heading = None
        self.speed_limit = None
        self.lanes = []
        self.id = id

        self.points = points
        # Point
        self.get_point = interp1d(linspace(0, 1, len(self.points)), self.points, axis=0)

        self.vehicles = deque()
        self.length = self.get_length()

        self.set_heading_functions()

        self.has_traffic_signal = None
        self.traffic_signal_group = None
        self.traffic_signal = None

        # number of lanes
        self.num_lanes = num_lanes

        self.lane_width = 3

        self.ban_lane_change_distance = 18

        if create_lanes:
            self.create_lanes()

    def get_vehicles(self):
        return self.vehicles

    def set_heading_functions(self):
        # Heading
        headings = unwrap([arctan2(
            self.points[i + 1][1] - self.points[i][1],
            self.points[i + 1][0] - self.points[i][0]
        ) for i in range(len(self.points) - 1)])
        if len(headings) == 1:
            self.get_heading = lambda x: headings[0]
        else:
            self.get_heading = interp1d(linspace(0, 1, len(self.points) - 1), headings, axis=0)

    # methods to calculate length using geometry [(x1,y1),(x2,y2),...(xn,yn)]
    def get_length(self):
        length = 0
        for i in range(len(self.points)-1):
            length += distance.euclidean((self.points[i][0], self.points[i][1]),
                                         (self.points[i+1][0], self.points[i+1][1]))
        return length

    @abstractmethod
    def compute_x(self, t):
        pass

    @abstractmethod
    def compute_y(self, t):
        pass

    @abstractmethod
    def compute_dx(self, t):
        pass

    @abstractmethod
    def compute_dy(self, t):
        pass

    def abs_f(self, t):
        return sqrt(self.compute_dx(t) ** 2 + self.compute_dy(t) ** 2)

    def find_t(self, a, L, epsilon):
        """  Finds the t value such that the length of the curve from a to t is L.

        Parameters
        ----------
        a : float
            starting point of the integral
        L : float
            target length
        epsilon : float
            precision of the approximation
        """

        def f(t):
            integral_value, _ = quad(self.abs_f, a, t)
            return integral_value

        # if we cannot reach the target length, return 1
        if f(1) < L:
            return 1

        lower_bound = a
        upper_bound = 1
        mid_point = (lower_bound + upper_bound) / 2.0
        integ = f(mid_point)
        while abs(integ - L) > epsilon:
            if integ < L:
                lower_bound = mid_point
            else:
                upper_bound = mid_point
            mid_point = (lower_bound + upper_bound) / 2.0
            integ = f(mid_point)
        return mid_point

    def find_normalized_path(self, CURVE_RESOLUTION=15):
        normalized_path = [(self.compute_x(0), self.compute_y(0))]
        l = self.get_length()
        target_l = l / (CURVE_RESOLUTION - 1)
        epsilon = 0.01
        a = 0
        for i in range(CURVE_RESOLUTION - 1):
            t = self.find_t(a, target_l, epsilon)
            new_point = (self.compute_x(t), self.compute_y(t))
            normalized_path.append(new_point)
            if t == 1:
                break
            else:
                a = t
        return normalized_path

    def set_traffic_signal(self, signal, group):
        self.traffic_signal = signal
        self.traffic_signal_group = group
        self.has_traffic_signal = True

    def set_speed_limit(self, speed_limit):
        self.speed_limit = speed_limit

    @property
    def traffic_signal_state(self):
        if self.has_traffic_signal:
            i = self.traffic_signal_group
            return self.traffic_signal.current_cycle[i]
        return True

    def create_lanes(self):
        for i in range(self.num_lanes):
            lane_index = i
            lane_id = self.id + "_" + str(i)
            speed_limit = self.speed_limit
            lane_width = self.lane_width
            lane_length = self.length
            self.lanes.append(Lane(lane_index, lane_id, speed_limit, lane_width, lane_length))

