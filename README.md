# ToySim: Micro Traffic Simulation using IDM & MOBILE Model

ToySim is a microscopic traffic simulation project that utilizes the Intelligent Driver Model (IDM) and MOBILE lane change model to simulate traffic flow. This project is designed to provide a detailed and interactive simulation of traffic scenarios, including vehicle generation, traffic signal control, and visualization.

![dbp9x-ys0p9](https://github.com/user-attachments/assets/4bb1125a-5cd3-4b05-9530-4d997c98e659)


## Features

- **Vehicle Simulation**: Simulate vehicle movements based on the IDM model.
- **Traffic Signal Control**: Manage traffic signals to control the flow of vehicles.
- **Interactive Visualization**: Visualize the simulation in real-time.
- **Flexible Configuration**: Easily configure vehicle generation and traffic scenarios.

## Getting Started

To get started with ToySim, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/RGB3Q/ToySim.git
   cd ToySim
   ```

2. **Install Dependencies**:
   We use Python 3 and several scientific libraries. Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

   This will install the following packages with their respective versions:
   - dearpygui (approximately version 1.8.0)
   - numpy (approximately version 1.24.2)
   - scipy (approximately version 1.13.0)
   - colorlog (approximately version 6.8.2)

3. **Run the Simulation**:
   Execute the main script to start the simulation:
   ```bash
   python test5.py
   ```
   
## Features

- **Vehicle Simulation**: Simulate vehicle movements based on the IDM model.
- **Traffic Signal Control**: Manage traffic signals to control the flow of vehicles.
- **Interactive Visualization**: Visualize the simulation in real-time.
- **Flexible Configuration**: Easily configure vehicle generation and traffic scenarios.

## Core Components

- **Simulator**: Manages the overall simulation logic.
- **Vehicles**: Represents vehicles with dynamic properties and behaviors.
- **Connectors**: Handles connections between road segments, including curve calculations.
- **Traffic Signals**: Simulates traffic lights to control vehicle flow.

## Visualization

ToySim includes a basic visualization module that allows you to see the simulation in action. This can be further extended or integrated with more advanced visualization tools.

## Contributing

Contributions to ToySim are welcome! Please submit a pull request or open an issue to suggest improvements or report bugs.

## License

ToySim is released under the [MIT License](LICENSE). Feel free to use, modify, and distribute this project for any purpose.
```

