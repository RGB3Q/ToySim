import dearpygui.dearpygui as dpg


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

    def setup(self):
        dpg.create_context()
        dpg.create_viewport(title='IDM SIM', width=1200, height=800)
        dpg.setup_dearpygui()

    def create_windows(self):
        # create mainwindow to display simulation
        dpg.add_window(tag='viz_port',
                       label="Simulation",
                       width=600,
                       height=600)

        dpg.add_draw_node(tag="OverlayCanvas", parent="viz_port")
        dpg.add_draw_node(tag="Canvas", parent="viz_port")

        with dpg.window(tag="SimControl",
                        label="sim_control"):
            with dpg.collapsing_header(label="Simulation Control", default_open=True):

                with dpg.group(horizontal=True):
                    dpg.add_button(label="Run", tag="RunStopButton", callback=self.toggle)
                    dpg.add_button(label="Step", tag="StepButton", callback=self.simulation.update)
                    # dpg.add_button(label="Reset", tag="Reset")

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.run()

    def run(self):
        self.is_running = True
        dpg.set_item_label("RunStopButton", "Stop")

    def stop(self):
        self.is_running = False
        dpg.set_item_label("RunStopButton", "Run")

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
        for segment in self.simulation.segments:
            dpg.draw_polyline(segment.points,
                              color=(180, 180, 220),
                              thickness=3.5*self.zoom,
                              parent="Canvas",
                              )
            # dpg.draw_arrow(segment.points[-1], segment.points[-2], thickness=0, size=2, color=(0, 0, 0, 50), parent="Canvas")

    def draw_vehicles(self):
        for segment in self.simulation.segments:
            for vehicle_id in segment.vehicles:
                vehicle = self.simulation.vehicles[vehicle_id]
                progress = vehicle.x / segment.length

                position = segment.get_point(progress)
                heading = segment.get_heading(progress)

                node = dpg.add_draw_node(parent="Canvas")
                dpg.draw_line(
                    (0, 0),
                    (vehicle.length, 0),
                    thickness=1.76*self.zoom,
                    color=(0, 0, 200),
                    parent=node
                )

                translate = dpg.create_translation_matrix(position)
                rotate = dpg.create_rotation_matrix(heading, [0, 0, 1])
                dpg.apply_transform(node, translate*rotate)

    def apply_transformation(self):
        screen_center = dpg.create_translation_matrix([self.canvas_width/2, self.canvas_height/2, -0.01])
        translate = dpg.create_translation_matrix(self.offset)
        scale = dpg.create_scale_matrix([self.zoom, self.zoom])
        dpg.apply_transform("Canvas", screen_center*scale*translate)

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