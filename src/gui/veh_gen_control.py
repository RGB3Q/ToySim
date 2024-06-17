import dearpygui.dearpygui as dpg
from src.vehicle.vehicle_generator import VehicleGenerator


class VehicleGeneratorControl:
    def __init__(self, vehicle_generator):
        self.b_max = None
        self.v_max = None
        self.s_safe = None
        self.a_max = None
        self.vehicle_length = None
        self.vehicle_generator = vehicle_generator
        self.create_veh_generator_control_windows()

    def create_veh_generator_control_windows(self):
        # ... your existing code ...

        # Create Vehicle Behaviour window
        with dpg.window(tag="VehicleBehaviour", label="Vehicle Behaviour", no_close=True, no_collapse=True, width=250,
                        height=250, no_resize=True, no_move=True, no_scrollbar=True, pos=(0, 340)):

            # Vehicle parameters
            self.vehicle_length = dpg.add_input_float(tag="VehicleLength", label="Length", default_value=5.0,
                                                      callback=self.set_vehicle_length)
            self.a_max = dpg.add_input_float(tag="AMax", label="a_max", default_value=2.0,
                                             callback=self.set_a_max)
            self.s_safe = dpg.add_input_float(tag="SSafe", label="Safety Distance", default_value=10.0,
                                              callback=self.set_s_safe)
            self.v_max = dpg.add_input_float(tag="VMax", label="v_max", default_value=30.0,
                                             callback=self.set_v_max)
            self.b_max = dpg.add_input_float(tag="BMax", label="b_max", default_value=5.0,
                                             callback=self.set_b_max)

    def set_vehicle_length(self, sender, app_data):
        for gen in self.vehicle_generator:
            gen.length = app_data
            gen.init_properties()  # Recalculate properties after updating length

    def set_a_max(self, sender, app_data):
        for gen in self.vehicle_generator:
            gen.a_max = app_data
            gen.init_properties()  # Recalculate properties after updating a_max

    def set_s_safe(self, sender, app_data):
        for gen in self.vehicle_generator:
            gen.s_safe = app_data
            gen.init_properties()  # Recalculate properties after updating s_safe

    def set_v_max(self, sender, app_data):
        for gen in self.vehicle_generator:
            gen.v_max = app_data
            gen.init_properties()  # Recalculate properties after updating v_max

    def set_b_max(self, sender, app_data):
        for gen in self.vehicle_generator:
            gen.b_max = app_data
            gen.init_properties()  # Recalculate properties after updating b_max

