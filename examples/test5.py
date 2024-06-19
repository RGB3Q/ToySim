from src import simulator as ts
from src.vehicle.vehicle_generator import VehicleGenerator
from src.gui.visualizer import Visualizer
from src.signal.SignalGroup import TrafficSignal

sim = ts.Simulation()

lane_space = 3
intersection_size = 36
length = 100

# SOUTH, EAST, NORTH, WEST

# Intersection in
# (1,6)(1,2) (6,-1)(1,-1) (-1,-6)(-1,-1) (-6,1)(-1,1)
sim.create_segment('0', ((lane_space * 1.5, length + intersection_size / 2), (lane_space * 1.5, intersection_size / 2)),
                   3)
sim.create_segment('1',
                   ((length + intersection_size / 2, -lane_space * 1.5), (intersection_size / 2, -lane_space * 1.5)), 3)
sim.create_segment('2',
                   ((-lane_space * 1.5, -length - intersection_size / 2), (-lane_space * 1.5, -intersection_size / 2)),
                   3)
sim.create_segment('3',
                   ((-length - intersection_size / 2, lane_space * 1.5), (-intersection_size / 2, lane_space * 1.5)), 3)

# Intersection out
sim.create_segment('4',
                   ((-lane_space * 1.5, intersection_size / 2), (-lane_space * 1.5, length + intersection_size / 2)), 3)
sim.create_segment('5', ((intersection_size / 2, lane_space * 1.5), (length + intersection_size / 2, lane_space * 1.5)),
                   3)
sim.create_segment('6',
                   ((lane_space * 1.5, -intersection_size / 2), (lane_space * 1.5, -length - intersection_size / 2)), 3)
sim.create_segment('7',
                   ((-intersection_size / 2, -lane_space * 1.5), (-length - intersection_size / 2, -lane_space * 1.5)),
                   3)

# Straight connection
sim.create_connector('0_6', ((lane_space * 1.5, intersection_size / 2), (lane_space * 1.5, -intersection_size / 2)),
                     '0', '6', [[0, 0], [1, 1], [2, 2]])
sim.create_connector('2_4', ((-lane_space * 1.5, -intersection_size / 2), (-lane_space * 1.5, intersection_size / 2)),
                     '2', '4', [[0, 0], [1, 1], [2, 2]])
sim.create_connector('3_5', ((-intersection_size / 2, lane_space * 1.5), (intersection_size / 2, lane_space * 1.5)),
                     '3', '5', [[0, 0], [1, 1], [2, 2]])
sim.create_connector('1_7', ((intersection_size / 2, -lane_space * 1.5), (-intersection_size / 2, -lane_space * 1.5)),
                     '1', '7', [[0, 0], [1, 1], [2, 2]])
# Right turn connection
sim.create_connector('0_5', ((lane_space * 2.5, intersection_size / 2), (lane_space * 2.5, lane_space * 2.5), (intersection_size / 2, lane_space * 2.5)),
                     '0', '5', [[2, 2]], generative_bezier_curve=True)
sim.create_connector('1_6', ((intersection_size / 2, -lane_space * 2.5), (lane_space * 2.5, -lane_space * 2.5), (lane_space * 2.5, -intersection_size / 2)),
                     '1', '6', [[2, 2]], generative_bezier_curve=True)
sim.create_connector('2_7', ((-lane_space * 2.5, -intersection_size / 2), (-lane_space * 2.5, -lane_space * 2.5), (-intersection_size / 2, -lane_space * 2.5)),
                     '2', '7', [[2, 2]], generative_bezier_curve=True)
sim.create_connector('3_4', ((-intersection_size / 2, lane_space * 2.5), (-lane_space * 2.5, lane_space * 2.5), (-lane_space * 2.5, intersection_size / 2)),
                     '3', '4', [[2, 2]], generative_bezier_curve=True)

# Left turn connection
sim.create_connector('0_7', ((lane_space * 0.5, intersection_size / 2), (lane_space * 0.5, -lane_space * 0.5), (-intersection_size / 2, -lane_space * 0.5)),
                     '0', '7', [[0, 0]], generative_bezier_curve=True)
sim.create_connector('1_4', ((intersection_size / 2, -lane_space * 0.5), (-lane_space * 0.5, -lane_space * 0.5), (-lane_space * 0.5, intersection_size / 2)),
                     '1', '4', [[0, 0]], generative_bezier_curve=True)
sim.create_connector('2_5', ((-lane_space * 0.5, -intersection_size / 2), (-lane_space * 0.5, lane_space * 0.5), (intersection_size / 2, lane_space * 0.5)),
                     '2', '5', [[0, 0]], generative_bezier_curve=True)
sim.create_connector('3_6', ((-intersection_size / 2, lane_space * 0.5), (lane_space * 0.5, lane_space * 0.5), (lane_space * 0.5, -intersection_size / 2)),
                     '3', '6', [[0, 0]], generative_bezier_curve=True)

vg = VehicleGenerator({
    'vehicles': [
        (1, {'path': ['0', '6'], 'v': 12}),
        (1, {'path': ['0', '5'], 'v': 20}),
        (1, {'path': ['0', '7'], 'v': 12}),
        (1, {'path': ['2', '4'], 'v': 12}),
        (1, {'path': ['2', '7'], 'v': 12}),
        (1, {'path': ['2', '5'], 'v': 12}),
    ]
})

sim.add_vehicle_generator(vg)

sg = TrafficSignal('1', [[sim.segments['0'], sim.segments['2']], [sim.segments['1'], sim.segments['3']]])
sim.add_signal(sg)

win = Visualizer(sim)
win.run()
win.show()
