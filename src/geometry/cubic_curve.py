from src.geometry.segment import Segment

CURVE_RESOLUTION = 50


class CubicCurve(Segment):
    def __init__(self, id: str, points, num_lanes):
        # Store characteristic points
        self.id = id
        self.start = points[0]
        self.control_1 = points[1]
        self.control_2 = points[2]
        self.end = points[3]

        # Generate path
        path = []
        for i in range(CURVE_RESOLUTION):
            t = i/CURVE_RESOLUTION
            x = t**3*self.end[0] + 3*t**2*(1-t)*self.control_2[0] + 3*(1-t)**2*t*self.control_1[0] + (1-t)**3*self.start[0]
            y = t**3*self.end[1] + 3*t**2*(1-t)*self.control_2[1] + 3*(1-t)**2*t*self.control_1[1] + (1-t)**3*self.start[1]
            path.append((x, y))

        super().__init__(id, path, num_lanes)
        # Arc-length parametrization
        normalized_path = self.find_normalized_path(CURVE_RESOLUTION)
        super().__init__(id, normalized_path, num_lanes)

    def compute_x(self, t):
        return t**3*self.end[0] + 3*t**2*(1-t)*self.control_2[0] + 3*(1-t)**2*t*self.control_1[0] + (1-t)**3*self.start[0]

    def compute_y(self, t):
        return t**3*self.end[1] + 3*t**2*(1-t)*self.control_2[1] + 3*(1-t)**2*t*self.control_1[1] + (1-t)**3*self.start[1]

    def compute_dx(self, t):
        return 3*t**2*(self.end[0]-3*self.control_2[0]+3*self.control_1[0]-self.start[0]) + 6*t*(self.control_2[0]-2*self.control_1[0]+self.start[0]) + 3*(self.control_1[0]-self.start[0])

    def compute_dy(self, t):
        return 3*t**2*(self.end[1]-3*self.control_2[1]+3*self.control_1[1]-self.start[1]) + 6*t*(self.control_2[1]-2*self.control_1[1]+self.start[1]) + 3*(self.control_1[1]-self.start[1])
