import time

import dearpygui.dearpygui as dpg
import os
import math
from src.gui.segment_highlighter import SegmentHighlighter
import numpy as np
from src.gui.veh_gen_control import VehicleGeneratorControl

# Get the absolute path to the image
image_path = os.path.join(os.path.dirname(__file__), "logo_1.png")
icon_path = os.path.join(os.path.dirname(__file__), "logo_icon256.ico")


def offset_position(position, heading, lane_width, offset_multiplier):
    """
    结合当前所在车道偏移车辆的位置,默认向右偏移为正
    :param position: 原始位置，一个包含x和y坐标的元组 (x, y)
    :param heading: 车辆前进方向，以弧度为单位
    :param lane_width: 车道宽度，用于偏移的固定量
    :param offset_multiplier: 偏移的倍数，正数为向右偏移，负数为向左偏移
    :return: 偏移后的新位置 (x, y)
    """
    dx = -lane_width * math.sin(heading)
    dy = lane_width * math.cos(heading)
    # 应用偏移
    new_x = position[0] + offset_multiplier * dx
    new_y = position[1] + offset_multiplier * dy
    return new_x, new_y


class Visualizer:
    def __init__(self, simulation):
        print("Initializing Visualizer...")
        self.simulation = simulation
        self.is_running = False
        self.is_dragging = False

        self.zoom = 5
        self.offset = (0, 0)

        # simulation speed
        self.speed = 1
        self.delay = 0
        self.zoom_speed = 1

        self.setup()
        self.create_windows()
        self.create_veh_gen_control_window()
        self.create_handlers()
        self.setup_themes()

        self.show_speed = True
        self.show_acceleration = True
        self.show_id = True

        self.show_status_color = False

        # 实例化SegmentHighlighter
        # self.initialize_highlighter()

    def setup(self):
        dpg.create_context()

        dpg.create_viewport(title='Toy SIM', width=1200, height=800, decorated=True, clear_color=(33, 33, 33))
        # Set the small and large icons (replace with your actual icon file paths)
        dpg.set_viewport_small_icon(icon_path)

        dpg.setup_dearpygui()
        width, height, channels, data = dpg.load_image(image_path)
        with dpg.texture_registry():
            self.logo = dpg.add_static_texture(width, height, data, tag="logo_compressed")

    def create_veh_gen_control_window(self):
        veh_gen_control_window = VehicleGeneratorControl(self.simulation.vehicle_generator)

    def create_windows(self):
        # create main window to display simulation
        dpg.add_window(tag='viz_port',
                       label="Simulation",
                       width=900,
                       height=800,
                       no_close=True,
                       pos=(250, 0),
                       no_background=True,
                       no_collapse=True,
                       no_title_bar=True,
                       no_move=True)

        dpg.add_draw_node(tag="OverlayCanvas", parent="viz_port")
        dpg.add_draw_node(tag="Canvas", parent="viz_port")

        with dpg.window(tag="SimControl", label="SimControl", no_close=True, no_collapse=True, width=250, height=190,
                        no_resize=True, no_move=True, no_scrollbar=True, ):

            with dpg.group(horizontal=True):
                dpg.add_button(label="Run", tag="RunStopButton", callback=self.toggle, width=60)
                dpg.add_button(label="Step", tag="StepButton", callback=self.simulation.update_with_lane, width=60)

            dpg.add_slider_int(tag="SpeedUp", label=">> Speed Up", width=150, min_value=1, max_value=100,
                               default_value=1,
                               callback=self.set_speed)
            dpg.add_slider_int(tag="Delay", label=">> Delay", width=150, min_value=10, max_value=200,
                               default_value=0,
                               callback=self.delay)

            with dpg.table(header_row=False):
                dpg.add_table_column()
                dpg.add_table_column()

                with dpg.table_row():
                    dpg.add_text("Status:")
                    dpg.add_text("_", tag="StatusText")

                with dpg.table_row():
                    dpg.add_text("Time:")
                    dpg.add_text("_s", tag="TimeStatus")

                with dpg.table_row():
                    dpg.add_text("Frame:")
                    dpg.add_text("_", tag="FrameStatus")
        # with dpg.window(tag="logo", label="logo", width=300, height=300, no_resize=False, no_move=False, no_title_bar=False, no_background=True):
        #     dpg.add_image(self.logo)
        if not hasattr(self, 'show_speed'):
            self.show_speed = True
        if not hasattr(self, 'show_acceleration'):
            self.show_acceleration = True
        if not hasattr(self, 'show_id'):
            self.show_id = True
        if not hasattr(self, 'show_status_color'):
            self.show_status_color = False
        with dpg.window(label="Vehicle Info", pos=[0, 190], width=250, height=130, no_close=True, no_collapse=True,
                        no_resize=True, no_move=True):
            dpg.add_checkbox(label="Show Speed", default_value=self.show_speed,
                             callback=lambda sender, app_data: setattr(self, 'show_speed', app_data))
            dpg.add_checkbox(label="Show Acceleration", default_value=self.show_acceleration,
                             callback=lambda sender, app_data: setattr(self, 'show_acceleration', app_data))
            dpg.add_checkbox(label="Show ID", default_value=self.show_id,
                             callback=lambda sender, app_data: setattr(self, 'show_id', app_data))
            dpg.add_checkbox(label="Show status", default_value=self.show_status_color,
                             callback=lambda sender, app_data: setattr(self, 'show_status_color', app_data))

    def create_handlers(self):
        with dpg.handler_registry():
            dpg.add_mouse_down_handler(callback=self.mouse_down)
            dpg.add_mouse_drag_handler(callback=self.mouse_drag)
            dpg.add_mouse_release_handler(callback=self.mouse_release)
            dpg.add_mouse_wheel_handler(callback=self.mouse_wheel)

    def update_panels(self):
        # Update status text
        if self.is_running:
            dpg.set_value("StatusText", "Running")
            dpg.configure_item("StatusText", color=(0, 255, 0))
        else:
            dpg.set_value("StatusText", "Stopped")
            dpg.configure_item("StatusText", color=(255, 0, 0))

        # Update time and frame text
        dpg.set_value("TimeStatus", f"{self.simulation.t:.2f}s")
        dpg.set_value("FrameStatus", self.simulation.frame_count)

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.run()

    def run(self):
        self.is_running = True
        dpg.set_item_label("RunStopButton", "Stop")
        dpg.bind_item_theme("RunStopButton", "StopButtonTheme")

    def stop(self):
        self.is_running = False
        dpg.set_item_label("RunStopButton", "Run")
        dpg.bind_item_theme("RunStopButton", "RunButtonTheme")

    def show(self):
        dpg.show_viewport()
        while dpg.is_dearpygui_running():
            self.render_loop()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()

    def render_loop(self):
        # print('updating frame: ', self.simulation.frame_count)
        self.update_inertial_zoom()
        # Remove old drawings
        dpg.delete_item("OverlayCanvas", children_only=True)
        dpg.delete_item("Canvas", children_only=True)

        self.draw_segments()
        self.draw_connectors()
        # print('drawing vehicles at segment')
        self.draw_vehicles()
        # print('drawing vehicles at connections')
        self.draw_vehicle_at_connections()

        self.draw_tl()
        self.draw_grid(10)
        self.draw_grid(50)

        # Apply transformations
        self.apply_transformation()

        # Update panels
        self.update_panels()

        if self.is_running:
            self.simulation.run(self.speed, self.delay)

    def draw_connectors(self):
        for _, connector in self.simulation.connectors.items():
            connector_width = len(connector.connections) * connector.lane_width
            dpg.draw_polyline(connector.points,
                              color=(180, 180, 220, 10),
                              thickness=connector_width * self.zoom,
                              parent="Canvas")
            dpg.draw_polyline(connector.points,
                              color=(180, 180, 220, 10),
                              thickness=0.5 * self.zoom,
                              parent="Canvas")

    def draw_segments(self):
        for _, segment in self.simulation.segments.items():
            segment_width = segment.num_lanes * segment.lane_width
            dpg.draw_polyline(segment.points,
                              color=(180, 180, 220, 10),
                              thickness=segment_width * self.zoom,
                              parent="Canvas",
                              )
            # Calculate the unit normal vector of the segment
            # Assuming points are given in order and we use the first two to calculate direction
            delta = np.array(segment.points[1]) - np.array(segment.points[0])
            normal_vector = np.array([-delta[1], delta[0]])  # Rotate by 90 degrees counter-clockwise
            unit_normal_vector = normal_vector / np.linalg.norm(normal_vector)

            # Calculate the lane lines
            half_segment_width = segment_width / 2
            lane_width = segment.lane_width * self.zoom
            num_lanes = segment.num_lanes
            lane_offset = np.linspace(-half_segment_width, half_segment_width, num=num_lanes + 1)

            for offset in lane_offset:
                lane_points = []
                for p in segment.points:
                    # Offset each point along the unit normal vector
                    adjusted_point = np.array(p) + offset * unit_normal_vector
                    lane_points.append(tuple(adjusted_point))

                # Draw the lane line
                dpg.draw_polyline(lane_points,
                                  color=(102, 102, 102),  # White color for lane lines
                                  thickness=0.1 * self.zoom,
                                  parent="Canvas",
                                  )
            # dpg.draw_arrow(segment.points[-1], segment.points[-2], thickness=0, size=1, color=(0, 0, 0, 50), parent="Canvas")

    def draw_vehicles(self):
        for _, segment in self.simulation.segments.items():
            for lane in segment.lanes:
                for vehicle in lane.vehicles:
                    progress = vehicle.x / segment.length
                    if progress > 1:
                        progress = 1

                    position = segment.get_point(progress)

                    offset_num = ((vehicle.at_lane + 1) * 2 - 1 - segment.num_lanes) / 2
                    heading = segment.get_heading(progress)
                    position_at_lane = offset_position(position, heading, segment.lane_width, offset_num)

                    node = dpg.add_draw_node(parent="Canvas")
                    if not self.show_status_color:
                        dpg.draw_line(
                            (0, 0),
                            (vehicle.length, 0),
                            thickness=1.76 * self.zoom,
                            color=(0, 0, 200, 127),
                            parent=node,
                        )
                    elif self.show_status_color:
                        if vehicle.stopped:
                            dpg.draw_line(
                                (0, 0),
                                (vehicle.length, 0),
                                thickness=1.76 * self.zoom,
                                color=(255, 0, 0),
                                parent=node
                            )
                        elif vehicle.slowing_down:
                            dpg.draw_line(
                                (0, 0),
                                (vehicle.length, 0),
                                thickness=1.76 * self.zoom,
                                color=(0, 255, 0),
                                parent=node
                            )
                            # print('slowing down color change: %s' % vehicle.id)
                        else:
                            dpg.draw_line(
                                (0, 0),
                                (vehicle.length, 0),
                                thickness=1.76 * self.zoom,
                                color=(0, 0, 200),
                                parent=node
                            )

                    translate = dpg.create_translation_matrix(position_at_lane)
                    rotate = dpg.create_rotation_matrix(heading, [0, 0, 1])
                    dpg.apply_transform(node, translate * rotate)

                    # Draw speed text
                    # Calculate text position relative to the vehicle's tail
                    text_position = (
                        position_at_lane[0] + vehicle.length * math.cos(heading),
                        position_at_lane[1] + vehicle.length * math.sin(heading)
                    )
                    # Optionally offset the text vertically so it doesn't overlap with the vehicle
                    text_position = (text_position[0], text_position[1] + 2)

                    self.activate_vehicle_info(lane, text_position, vehicle)

    def activate_vehicle_info(self, lane, text_position, vehicle):
        # 绘制速度、加速度和ID的
        if self.show_speed:
            # 绘制速度
            dpg.draw_text(
                pos=text_position,
                text=f"V:{vehicle.v:.2f}",
                size=2 * self.zoom,
                color=(255, 255, 255),
                parent="Canvas"
            )
            new_pos = (text_position[0] + 7, text_position[1])
            dpg.draw_text(pos=new_pos, text=f"at:{str(lane.lane_id) + ' ' + str(vehicle.x)}",
                          size=2 * self.zoom, color=(255, 255, 255), parent="Canvas")
        if self.show_acceleration:
            # 计算并绘制加速度
            acceleration_position = (text_position[0], text_position[1] + 2)
            dpg.draw_text(
                pos=acceleration_position,
                text=f"A:{vehicle.a:.2f}",
                size=2 * self.zoom,
                color=(255, 255, 255),
                parent="Canvas"
            )
        if self.show_id:
            # 计算并绘制ID
            id_position = (text_position[0], text_position[1] + 4)
            dpg.draw_text(
                pos=id_position,
                text=f"ID:{vehicle.id}",
                size=2 * self.zoom,
                color=(255, 255, 255),
                parent="Canvas"
            )

    def draw_vehicle_at_connections(self):
        for connector in self.simulation.connectors.values():
            if not connector.vehicles:
                continue
            for vehicle in connector.vehicles:
                progress = vehicle.x / connector.length
                if progress > 1:
                    progress = 1

                # print('getting position: ', vehicle.id)
                position = connector.get_point(progress)

                offset_num = ((vehicle.at_lane + 1) * 2 - 1 - connector.num_lanes) / 2
                # print('getting heading: ', vehicle.id)
                heading = connector.get_heading(progress)

                position_at_lane = offset_position(position, heading, connector.lane_width, offset_num)

                node1 = dpg.add_draw_node(parent="Canvas")

                translate = dpg.create_translation_matrix(position_at_lane)
                rotate = dpg.create_rotation_matrix(heading, [0, 0, 1])
                dpg.apply_transform(node1, translate * rotate)

                dpg.draw_line(
                    (0, 0),
                    (vehicle.length, 0),
                    thickness=1.76 * self.zoom,
                    color=(0, 0, 200, 127),
                    parent=node1,
                )

                # self.activate_vehicle_info(lane, text_position, vehicle)

    def draw_tl(self):
        """
        绘制交通灯
        """
        for _, segment in self.simulation.segments.items():
            segment_width = segment.num_lanes * segment.lane_width
            if segment.has_traffic_signal:
                # Get the last two points of the segment.
                last_point = segment.points[-1]
                second_last_point = segment.points[-2]

                # Calculate the direction vector of the segment.
                direction_vector = [
                    last_point[0] - second_last_point[0],
                    last_point[1] - second_last_point[1]
                ]

                # Calculate the perpendicular vector to the direction vector.
                perpendicular_vector = [
                    -direction_vector[1],  # Rotate by 90 degrees counterclockwise
                    direction_vector[0]
                ]

                # Normalize the perpendicular vector.
                length = math.sqrt(perpendicular_vector[0] ** 2 + perpendicular_vector[1] ** 2)
                unit_perpendicular_vector = [
                    perpendicular_vector[0] / length,
                    perpendicular_vector[1] / length
                ]
                # Calculate the start and end points of the traffic light line.
                traffic_light_start = [
                    last_point[0] + unit_perpendicular_vector[0] * segment_width / 2,
                    last_point[1] + unit_perpendicular_vector[1] * segment_width / 2
                ]
                traffic_light_end = [
                    last_point[0] - unit_perpendicular_vector[0] * segment_width / 2,
                    last_point[1] - unit_perpendicular_vector[1] * segment_width / 2
                ]

                with dpg.draw_node(parent="Canvas"):
                    if segment.traffic_signal_state:  # 为绿灯
                        dpg.draw_line(p1=traffic_light_start, p2=traffic_light_end, color=(0, 255, 0),
                                      thickness=0.5 * self.zoom)

                    else:  # 为红灯
                        dpg.draw_line(p1=traffic_light_start, p2=traffic_light_end, color=(255, 0, 0),
                                      thickness=0.5 * self.zoom)

    def apply_transformation(self):
        screen_center = dpg.create_translation_matrix([self.canvas_width / 2, self.canvas_height / 2, -0.01])
        translate = dpg.create_translation_matrix(self.offset)
        scale = dpg.create_scale_matrix([self.zoom, self.zoom])
        dpg.apply_transform("Canvas", screen_center * scale * translate)

    def close_logo(self):
        dpg.delete_item("logo")

    def setup_themes(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
                # dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, (8, 6), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (90, 90, 95))
                dpg.add_theme_color(dpg.mvThemeCol_Header, (0, 91, 140))
            with dpg.theme_component(dpg.mvInputInt):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (90, 90, 95), category=dpg.mvThemeCat_Core)
            #     dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.bind_theme(global_theme)

        # dpg.show_style_editor()

        with dpg.theme(tag="RunButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (5, 150, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (12, 207, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (2, 120, 10))

        with dpg.theme(tag="StopButtonTheme"):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (150, 5, 18))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (207, 12, 23))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (120, 2, 10))

        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font("../fonts/pingfang.otf", 16)
            dpg.bind_font(default_font)

    @property
    def canvas_width(self):
        return dpg.get_item_width("viz_port")

    @property
    def canvas_height(self):
        return dpg.get_item_height("viz_port")

    def mouse_down(self):
        if not self.is_dragging:
            if dpg.is_item_hovered("viz_port"):
                self.is_dragging = True
                self.old_offset = self.offset

    def mouse_drag(self, sender, app_data):
        if self.is_dragging:
            self.offset = (
                self.old_offset[0] + app_data[1] / self.zoom,
                self.old_offset[1] + app_data[2] / self.zoom
            )

    def mouse_release(self):
        self.is_dragging = False

    def mouse_wheel(self, sender, app_data):
        if dpg.is_item_hovered("viz_port"):
            self.zoom_speed = 1 + 0.01 * app_data

    def update_inertial_zoom(self, clip=0.005):
        if self.zoom_speed != 1:
            self.zoom *= self.zoom_speed
            self.zoom_speed = 1 + (self.zoom_speed - 1) / 1.05
        if abs(self.zoom_speed - 1) < clip:
            self.zoom_speed = 1

    def set_speed(self):
        self.speed = dpg.get_value("SpeedUp")

    def slow_down(self):
        delay = dpg.get_value("Delay")
        self.delay = int(delay)

    def draw_grid(self, unit=10, opacity=10):
        color = (255, 255, 255, opacity)
        x_start, y_start = self.to_world(0, 0)
        x_end, y_end = self.to_world(self.canvas_width, self.canvas_height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit) + 1
        m_y = int(y_end / unit) + 1

        for i in range(n_x, m_x):
            dpg.draw_line(
                self.to_screen(unit * i, y_start - 10 / self.zoom),
                self.to_screen(unit * i, y_end + 10 / self.zoom),
                thickness=1,
                color=color,
                parent="OverlayCanvas"
            )

        for i in range(n_y, m_y):
            dpg.draw_line(
                self.to_screen(x_start - 10 / self.zoom, unit * i),
                self.to_screen(x_end + 10 / self.zoom, unit * i),
                thickness=1,
                color=color,
                parent="OverlayCanvas"
            )

    def to_screen(self, x, y):
        return (
            self.canvas_width / 2 + (x + self.offset[0]) * self.zoom,
            self.canvas_height / 2 + (y + self.offset[1]) * self.zoom
        )

    def to_world(self, x, y):
        return (
            (x - self.canvas_width / 2) / self.zoom - self.offset[0],
            (y - self.canvas_height / 2) / self.zoom - self.offset[1]
        )
    # def initialize_highlighter(self):
    #     # Assuming 'canvas_tag' is the ID of your canvas element
    #     self.highlighter = SegmentHighlighter(self.simulation, self.zoom)
    #     self.highlighter.attach_canvas_callback("Canvas")  # Replace "Canvas" with the actual tag of your canvas


if __name__ == "__main__":
    viz = Visualizer()
    viz.setup()
    viz.show()
