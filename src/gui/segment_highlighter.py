import dearpygui.dearpygui as dpg
import numpy as np


class SegmentHighlighter:
    def __init__(self, simulation, zoom):
        self.simulation = simulation
        self.zoom = zoom
        self.canvas_tag = None

    # def attach_canvas_callback(self, canvas_tag):
    #     self.canvas_tag = canvas_tag
    #     # Create a handler for mouse events
    #     with dpg.handler_registry():
    #         dpg.add_mouse_click_handler(callback=self.handle_mouse_click)
    #
    #     # Bind the handler to the canvas
    #     dpg.bind_item_handler_registry(canvas_tag, dpg.last_item())

    def attach_canvas_callback(self, canvas_tag):
        self.canvas_tag = canvas_tag
        # Create a handler registry outside of the with statement
        handler_registry_tag = dpg.generate_uuid()
        # Add mouse click handler to the registry
        with dpg.handler_registry(tag=handler_registry_tag):
            dpg.add_mouse_click_handler(callback=self.handle_mouse_click)

        # Now bind the handler registry to the canvas
        dpg.bind_item_handler_registry(canvas_tag, handler_registry_tag)

    def handle_mouse_click(self, sender, app_data):
        if app_data[1] == 0:  # 检查是否是鼠标左键
            mouse_pos = dpg.get_mouse_pos()
            clicked_segment = self.find_clicked_segment(mouse_pos)
            if clicked_segment:
                self.highlight_segment(clicked_segment)
                self.display_segment_points(clicked_segment)

    def find_clicked_segment(self, mouse_pos):
        # 这里实现寻找被点击路段的逻辑
        for segment_id, segment in self.simulation.segments.items():
            if self.is_point_in_segment(mouse_pos, segment):
                return segment
        return None

    def is_point_in_segment(self, point, segment):
        # 简单的矩形检查
        x_min = min(segment.points[0][0], segment.points[1][0])
        x_max = max(segment.points[0][0], segment.points[1][0])
        y_min = min(segment.points[0][1], segment.points[1][1])
        y_max = max(segment.points[0][1], segment.points[1][1])
        return x_min <= point[0] <= x_max and y_min <= point[1] <= y_max

    def highlight_segment(self, segment):
        # 高亮显示路段
        segment_id = self.get_segment_draw_id(segment)  # 这个函数需要实现
        dpg.configure_item(segment_id, color=(255, 0, 0))
        dpg.configure_item(segment_id, thickness=segment_width * self.zoom * 2)

    def display_segment_points(self, segment):
        # 显示路段的points信息
        if dpg.does_item_exist("SegmentPointsInfo"):
            dpg.delete_item("SegmentPointsInfo")
        with dpg.window(label=f"Segment Points for Segment ID: {segment.id}", tag="SegmentPointsInfo"):
            for point in segment.points:
                dpg.add_text(f"Point: {point}", bullet=True)
        dpg.configure_item("SegmentPointsInfo", pos=dpg.get_mouse_pos())

    def get_segment_draw_id(self, segment):
        # 返回用于绘制路段的Dear ImGui元素的ID
        # 这个函数需要根据实际的绘图逻辑实现
        pass