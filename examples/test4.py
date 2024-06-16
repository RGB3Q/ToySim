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
sim.create_segment('0', ((lane_space*1.5, length+intersection_size/2), (lane_space*1.5, intersection_size/2)), 3)
sim.create_segment('1', ((length+intersection_size/2, -lane_space*1.5), (intersection_size/2, -lane_space*1.5)), 3)
sim.create_segment('2', ((-lane_space*1.5, -length-intersection_size/2), (-lane_space*1.5, -intersection_size/2)), 3)
sim.create_segment('3', ((-length-intersection_size/2, lane_space*1.5), (-intersection_size/2, lane_space*1.5)), 3)

# Intersection out
sim.create_segment('4', ((-lane_space*1.5, intersection_size/2), (-lane_space*1.5, length+intersection_size/2)), 3)
sim.create_segment('5', ((intersection_size/2, lane_space*1.5), (length+intersection_size/2, lane_space*1.5)), 3)
sim.create_segment('6', ((lane_space*1.5, -intersection_size/2), (lane_space*1.5, -length-intersection_size/2)), 3)
sim.create_segment('7', ((-intersection_size/2, -lane_space*1.5), (-length-intersection_size/2, -lane_space*1.5)), 3)

# Straight
sim.create_segment('8', ((lane_space*1.5, intersection_size/2), (lane_space*1.5, -intersection_size/2)), 3)
sim.create_segment('9', ((intersection_size/2, -lane_space*1.5), (-intersection_size/2, -lane_space*1.5)), 3)
sim.create_segment('10', ((-lane_space/2, -intersection_size/2), (-lane_space/2, intersection_size/2)), 3)
sim.create_segment('11', ((-intersection_size/2, lane_space/2), (intersection_size/2, lane_space/2)), 3)

# Right turn
sim.create_quadratic_bezier_curve('12', ((lane_space*1.5, intersection_size/2), (lane_space*1.5, lane_space*1.5), (intersection_size/2, lane_space*1.5)), 3)
sim.create_quadratic_bezier_curve('13', ((intersection_size/2, -lane_space*1.5), (lane_space*1.5, -lane_space*1.5), (lane_space*1.5, -intersection_size/2)), 3)
sim.create_quadratic_bezier_curve('14', ((-lane_space*1.5, -intersection_size/2), (-lane_space*1.5, -lane_space*1.5), (-intersection_size/2, -lane_space*1.5)), 3)
sim.create_quadratic_bezier_curve('15', ((-intersection_size/2, lane_space*1.5), (-lane_space*1.5, lane_space*1.5), (-lane_space*1.5, intersection_size/2)), 3)

# Left turn
sim.create_quadratic_bezier_curve('16', ((lane_space*1.5, intersection_size/2), (lane_space*1.5, -lane_space*1.5), (-intersection_size/2, -lane_space*1.5)), 3)
sim.create_quadratic_bezier_curve('17', ((intersection_size/2, -lane_space*1.5), (-lane_space*1.5, -lane_space*1.5), (-lane_space*1.5, intersection_size/2)), 3)
sim.create_quadratic_bezier_curve('18', ((-lane_space*1.5, -intersection_size/2), (-lane_space*1.5, lane_space*1.5), (intersection_size/2, lane_space*1.5)), 3)
sim.create_quadratic_bezier_curve('19', ((-intersection_size/2, lane_space*1.5), (lane_space*1.5, lane_space*1.5), (lane_space*1.5, -intersection_size/2)), 3)

vg = VehicleGenerator({
    'vehicles':[
        (1, {'path': ['0', '8', '6'], 'v': 12}),
        (1, {'path': ['0', '12', '5'], 'v': 12})
        ]
    })

sim.add_vehicle_generator(vg)

sg = TrafficSignal('1', [[sim.segments['0'], sim.segments['2']], [sim.segments['1'], sim.segments['3']]])
sim.add_signal(sg)


win = Visualizer(sim)
win.run()
win.show()
