import dearpygui.dearpygui as dpg
import os

# Get the absolute path to the image
image_path = os.path.join(os.path.dirname(__file__), "logo_1.png")
icon_path = os.path.join(os.path.dirname(__file__), "logo_icon256.ico")


class Visualizer:
    def __init__(self, simulation):
        self.simulation = simulation
        self.is_running = False

        self.zoom = 5
        self.offset = (0, 0)

        # simulation speed
        self.speed = 1

        self.setup()
        self.create_windows()

        self.setup_themes()

    def setup(self):
        dpg.create_context()

        dpg.create_viewport(title='Toy SIM', width=1200, height=800, decorated=True, clear_color=(33, 33, 33))
        # Set the small and large icons (replace with your actual icon file paths)
        dpg.set_viewport_small_icon(icon_path)

        dpg.setup_dearpygui()
        width, height, channels, data = dpg.load_image(image_path)
        with dpg.texture_registry():
            self.logo = dpg.add_static_texture(width, height, data, tag="logo_compressed")



    def create_tab(self):
        self.tab = dpg.generate_uuid()
        with dpg.tab(label="Kramers-Kronig", tag=self.tab):
            with dpg.child_window(border=False):
                with dpg.group(horizontal=True):
                    self.create_windows(label = 'tst')

    def create_windows(self):
        # create main window to display simulation
        dpg.add_window(tag='viz_port',
                       label="Simulation",
                       width=900,
                       height=600,
                       no_close=True,
                       pos=(250, 0),
                       no_background=True,
                       no_collapse=False)

        dpg.add_draw_node(tag="OverlayCanvas", parent="viz_port")
        dpg.add_draw_node(tag="Canvas", parent="viz_port")

        with dpg.window(tag="SimControl", label="sim_control", no_close=True, no_collapse=True, width=240, no_resize=True, no_move=True):

            with dpg.group(horizontal=True):
                dpg.add_button(label="Run", tag="RunStopButton", callback=self.toggle, width=60)
                dpg.add_button(label="Step", tag="StepButton", callback=self.simulation.update, width=60)
        # with dpg.window(tag="logo", label="logo", width=300, height=300, no_resize=False, no_move=False, no_title_bar=False, no_background=True):
        #     dpg.add_image(self.logo)

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
        # Remove old drawings
        dpg.delete_item("OverlayCanvas", children_only=True)
        dpg.delete_item("Canvas", children_only=True)

        self.draw_segments()
        self.draw_vehicles()

        # Apply transformations
        self.apply_transformation()

        if self.is_running:
            self.simulation.run(self.speed)

    def draw_segments(self):
        for _, segment in self.simulation.segments.items():
            segment_width = segment.num_lanes * segment.lane_width
            dpg.draw_polyline(segment.points,
                              color=(180, 180, 220),
                              thickness=segment_width * self.zoom,
                              parent="Canvas",
                              )
            dpg.draw_arrow(segment.points[-1], segment.points[-2], thickness=0, size=1, color=(0, 0, 0, 50), parent="Canvas")

    def draw_vehicles(self):
        for _, segment in self.simulation.segments.items():
            for vehicle_id in segment.vehicles:
                vehicle = self.simulation.vehicles[vehicle_id]
                progress = vehicle.x / segment.length

                position = segment.get_point(progress)
                heading = segment.get_heading(progress)

                node = dpg.add_draw_node(parent="Canvas")
                dpg.draw_line(
                    (0, 0),
                    (vehicle.length, 0),
                    thickness=1.76 * self.zoom,
                    color=(0, 0, 200),
                    parent=node
                )

                translate = dpg.create_translation_matrix(position)
                rotate = dpg.create_rotation_matrix(heading, [0, 0, 1])
                dpg.apply_transform(node, translate * rotate)

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

    @property
    def canvas_width(self):
        return dpg.get_item_width("viz_port")

    @property
    def canvas_height(self):
        return dpg.get_item_height("viz_port")


if __name__ == "__main__":
    viz = Visualizer()
    viz.setup()
    viz.show()
