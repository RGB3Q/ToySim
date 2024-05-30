from dearpygui.dearpygui import *

def clear_window(sender, app_data):
    delete_item(main_window, children_only=True)

with window() as main_window:
    add_text("This is the main window!")

with window():
    add_button("Clear Main Window", callback=clear_window)

setup_dearpygui()
show_viewport()
start_dearpygui()