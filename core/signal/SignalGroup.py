class TrafficSignal:
    def __init__(self, signal_id, segments_group, config=None):
        # Initialize segments   eg. [ [road1, road2], [road3, road4] ]
        self.signal_id = signal_id
        if config is None:
            config = {}
        self.segments_group = segments_group
        # Set default configuration
        self.set_default_config()
        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        self.cycle = [(False, True), (True, False)]
        self.slow_distance = 40
        self.slow_factor = 10
        self.stop_distance = 15
        self.phase_num = len(self.cycle)
        self.slow_speed = 10

        self.current_cycle_index = 0
        self.last_t = 0

    def init_properties(self):
        for i in range(len(self.segments_group)):
            for segment in self.segments_group[i]:
                # here we bind the signal and corresponding signal group index to the target segment
                segment.set_traffic_signal(signal=self, group=i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]

    def update(self, sim):
        # Goes through all cycles every cycle_length and repeats
        cycle_length = 30
        k = (sim.t // cycle_length) % self.phase_num
        self.current_cycle_index = int(k)

