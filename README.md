
# Robot Swarm Model

## Try it Live
Access the live simulation at: https://replit.com/@YOUR_USERNAME/simulations

## Installation
```bash
git clone <your-repository-url>
pip install -r requirements.txt
```

## Running the Model
```bash
python main.py
```
The simulation will be available at `http://YOUR_REPLIT_URL`

## Overview
A Mesa-based robot swarm simulation modeling autonomous robots that complete tasks while managing battery levels.

## Key Features
- **Dynamic Task Allocation**: Robots autonomously find and complete tasks across a 20x20 grid
- **Battery Management**: Robots monitor energy levels (100% max) and seek charging when below 20%
- **Autonomous Navigation**: Smart pathfinding to efficiently reach tasks
- **Real-time Visualization**:
  - Blue circles: Idle robots
  - Red circles: Robots with active tasks
  - Yellow circles: Charging robots
  - Battery level displayed on each robot

## Performance Metrics
- Task Completion Counter
- Swarm Efficiency Tracking
- Average Battery Level Monitor
- Step Counter for Movement Analysis

## Technical Details
- Grid Size: 20x20
- Default Configuration:
  - 10 robots
  - 15 initial tasks
  - Tasks regenerate with 10% probability per step
- Visualization Port: 8989

## Behavior Patterns
The simulation demonstrates emergent swarm behavior as robots coordinate task completion while managing their energy levels. This creates a dynamic balance between task efficiency and resource management.
