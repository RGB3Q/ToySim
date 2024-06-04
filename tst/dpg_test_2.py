import dearpygui.dearpygui as dpg
import math

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

with dpg.window(label="tutorial", width=550, height=550):

    with dpg.drawlist(width=500, height=500):

        with dpg.draw_node(tag="root node"):
            dpg.draw_circle([0, 0], 150, color=[0, 255, 0])                      # inner planet orbit
            dpg.draw_circle([0, 0], 200, color=[0, 255, 255])                    # outer planet orbit
            dpg.draw_circle([0, 0], 15, color=[255, 255, 0], fill=[255, 255, 0]) # sun

            with dpg.draw_node(tag="planet node 1"):
                dpg.draw_circle([0, 0], 10, color=[0, 255, 0], fill=[0, 255, 0]) # inner planet
                dpg.draw_circle([0, 0], 25, color=[255, 0, 255])                 # moon orbit path

                with dpg.draw_node(tag="planet 1, moon node"):
                    dpg.draw_circle([0, 0], 5, color=[255, 0, 255], fill=[255, 0, 255]) # moon

            with dpg.draw_node(tag="planet node 2"):
                dpg.draw_circle([0, 0], 10, color=[0, 255, 255], fill=[0, 255, 255]) # outer planet
                dpg.draw_circle([0, 0], 25, color=[255, 0, 255])                     # moon 1 orbit path
                dpg.draw_circle([0, 0], 45, color=[255, 255, 255])                   # moon 2 orbit path

                with dpg.draw_node(tag="planet 2, moon 1 node"):
                    dpg.draw_circle([0, 0], 5, color=[255, 0, 255], fill=[255, 0, 255]) # moon 1

                with dpg.draw_node(tag="planet 2, moon 2 node"):
                    dpg.draw_circle([0, 0], 5, color=[255, 255, 255], fill=[255, 255, 255]) # moon 2

planet1_distance = 150
planet1_angle = 45.0
planet1_moondistance = 25
planet1_moonangle = 45

planet2_distance = 200
planet2_angle = 0.0
planet2_moon1distance = 25
planet2_moon1angle = 45
planet2_moon2distance = 45
planet2_moon2angle = 120

dpg.apply_transform("root node", dpg.create_translation_matrix([250, 250]))
dpg.apply_transform("planet node 1", dpg.create_rotation_matrix(math.pi*planet1_angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet1_distance, 0]))
# dpg.apply_transform("planet 1, moon node", dpg.create_rotation_matrix(math.pi*planet1_moonangle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet1_moondistance, 0]))
# dpg.apply_transform("planet node 2", dpg.create_rotation_matrix(math.pi*planet2_angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_distance, 0]))
# dpg.apply_transform("planet 2, moon 1 node", dpg.create_rotation_matrix(math.pi*planet2_moon1distance/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_moon1distance, 0]))
# dpg.apply_transform("planet 2, moon 2 node", dpg.create_rotation_matrix(math.pi*planet2_moon2angle/180.0 , [0, 0, -1])*dpg.create_translation_matrix([planet2_moon2distance, 0]))

dpg.show_viewport()
while dpg.is_dearpygui_running():
    dpg.render_dearpygui_frame()

dpg.destroy_context()