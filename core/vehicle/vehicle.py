import uuid
import numpy as np


# create Vehicle class for simulation
class Vehicle:
    def __init__(self, config={}):
        # set default config
        self.set_default_config()

        # update config
        self.update_config(config)

    def set_default_config(self):
        self.id = uuid.uuid4()

        # minimal safe distance
        self.s0 = 4

        # reaction time
        self.T = 1.5

        self.length = 4
        self.v_max = 16
        self._v_max = 16

        self.a_max = 1.5
        self.b_max = 10

        self.path = []
        self.current_road_index = 0

        self.x = 0
        self.v = 0
        self.a = 0
        self.stopped = False

        self.sqrt_ab = 2 * np.sqrt(self.a_max * self.b_max)

    # update config with new  values
    def update_config(self, config):
        for key, value in config.items():
            setattr(self, key, value)

    # use IDM model to update speed, position and acceleration
    def update_position(self, lead, dt):
        # Update position and velocity
        if self.v +self.a * dt < 0:
            self.x -= 0.5*self.v**2 / self.a
            self.v = 0
        else:
            self.v += self.a * dt
            self.x += self.v * dt + self.a*dt**2 / 2

        # Update acceleration
        alpha = 0
        if lead:
            delta_x = lead.x - self.x - lead.length
            delta_v = self.v - lead.v

            alpha = (self.s0 + max(0, self.T * self.v + delta_v * self.v / self.sqrt_ab)) / delta_x

        self.a = self.a_max * (1 - (self.v / self.v_max) ** 4 - alpha ** 2)

        if self.stopped:
            self.a = -self.b_max*self.v/self.v_max

    def stop(self):
        self.stopped = True

    def unstop(self):
        self.stopped = False

    def slow(self, v):
        self.v_max = v

    def unslow(self):
        self.v_max = self._v_max









