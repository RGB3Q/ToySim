from src import simulator as ts
from src.gui.visualizer import Visualizer

sim = ts.Simulation()

# Add road segments
sim.create_segment((-100, 3), (100, 2))
sim.create_segment((100, -3), (-100, -2))

# Add vehicle generator
sim.create_vehicle_generator(
    vehicle_rate=20,
    vehicles=[
        (10, {'path': [0], 'v': 16.6}),
        (1, {'path': [0], 'v': 16.6, 'l': 7}),

        (10, {'path': [1], 'v': 16.6}),
        (1, {'path': [1], 'v': 16.6, 'l': 7})
        ]
    )

# Show simulation visualization
win = Visualizer(sim)
win.show()
