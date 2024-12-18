
from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
import numpy as np

class RobotAgent(Agent):
    def __init__(self, unique_id, model, task_location=None):
        super().__init__(unique_id, model)
        self.task_location = task_location
        self.has_task = task_location is not None
        self.completed_tasks = 0
        self.battery = 100
        self.steps_taken = 0
        self.charging = False

    def move(self):
        if self.battery <= 20:  # Return to charging when battery is low
            self.charging = True
            self.has_task = False
            self.task_location = None
            return
            
        if self.charging:
            self.battery = min(100, self.battery + 10)
            if self.battery >= 90:
                self.charging = False
            return
            
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        available_steps = [pos for pos in possible_steps 
                         if not self.model.grid.get_cell_list_contents(pos)]
        if available_steps:
            new_position = self.random.choice(available_steps)
            self.model.grid.move_agent(self, new_position)
            self.battery -= 1
            self.steps_taken += 1

    def move_towards_task(self):
        if not self.task_location:
            return
        
        current_x, current_y = self.pos
        target_x, target_y = self.task_location
        
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        # Choose step that minimizes distance to target
        best_step = min(
            possible_steps,
            key=lambda p: ((p[0] - target_x) ** 2 + (p[1] - target_y) ** 2)
        )
        
        # Check if the best step is not occupied
        if not self.model.grid.get_cell_list_contents(best_step):
            self.model.grid.move_agent(self, best_step)

    def step(self):
        if self.has_task:
            if self.pos == self.task_location:
                self.completed_tasks += 1
                self.has_task = False
                self.task_location = None
            else:
                self.move_towards_task()
        else:
            # Try to find a new task
            available_tasks = self.model.get_available_tasks()
            if available_tasks:
                self.task_location = self.random.choice(available_tasks)
                self.has_task = True
            else:
                self.move()

class RobotSwarmModel(Model):
    def __init__(self, N, width, height, num_tasks):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.tasks = set()
        self.running = True

        # Create agents
        for i in range(self.num_agents):
            robot = RobotAgent(i, self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(robot, (x, y))
            self.schedule.add(robot)

        # Create tasks
        for _ in range(num_tasks):
            self.add_new_task()

        self.datacollector = DataCollector(
            model_reporters={
                "Completed_Tasks": lambda m: sum(a.completed_tasks for a in m.schedule.agents),
                "Efficiency": lambda m: sum(a.completed_tasks for a in m.schedule.agents) / 
                                     (sum(a.steps_taken for a in m.schedule.agents) + 1),
                "Average_Battery": lambda m: sum(a.battery for a in m.schedule.agents) / m.num_agents
            }
        )

    def add_new_task(self):
        if len(self.tasks) >= self.grid.width * self.grid.height:
            return
        
        while True:
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            if (x, y) not in self.tasks:
                self.tasks.add((x, y))
                break

    def get_available_tasks(self):
        return list(self.tasks)

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        
        # Add new tasks occasionally
        if self.random.random() < 0.1:  # 10% chance each step
            self.add_new_task()

def run_simulation():
    # Create and run the model
    model = RobotSwarmModel(N=10, width=20, height=20, num_tasks=15)
    for _ in range(100):
        model.step()
    
    # Get the data
    model_data = model.datacollector.get_model_vars_dataframe()
    print("Simulation completed!")
    print(f"Total tasks completed: {model_data['Completed_Tasks'].iloc[-1]}")

if __name__ == "__main__":
    from mesa.visualization.modules import CanvasGrid
    from mesa.visualization.ModularVisualization import ModularServer

    def agent_portrayal(agent):
        if isinstance(agent, RobotAgent):
            portrayal = {
                "Shape": "circle",
                "Filled": "true",
                "r": 0.5,
                "Layer": 0,
                "text": f"{agent.battery}%",
                "text_color": "white"
            }
            if agent.charging:
                portrayal["Color"] = "yellow"
            elif agent.has_task:
                portrayal["Color"] = "red"
            else:
                portrayal["Color"] = "blue"
            return portrayal
        return None

    def draw_task(agent):
        if agent is None:
            return
        portrayal = agent_portrayal(agent)
        return portrayal

    # Add task portrayal
    grid = CanvasGrid(draw_task, 20, 20, 500, 500)
    
    # Add charts
    from mesa.visualization.modules import ChartModule
    completed_tasks_chart = ChartModule([{"Label": "Completed_Tasks",
                                         "Color": "Black"}],
                                      data_collector_name='datacollector')
    
    efficiency_chart = ChartModule([{"Label": "Efficiency",
                                   "Color": "Red"}],
                                 data_collector_name='datacollector')

    server = ModularServer(RobotSwarmModel,
                          [grid, completed_tasks_chart, efficiency_chart],
                          "Robot Swarm Model",
                          {"N": 10, "width": 20, "height": 20, "num_tasks": 15})
    
    server.port = 8989  # Port for visualization
    server.launch(open_browser=False)
