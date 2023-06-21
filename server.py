import mesa
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule, TextElement, BarChartModule
from mesa.visualization.ModularVisualization import CHART_JS_FILE, VisualizationElement


from cooperator import Cooperator
from defector import Defector

from PGG_model import PublicGoodGame


# add average money spent of punishment
# add average money lost due to being punished


def render(self, model):
    current_values = []
    data_collector = getattr(model, self.data_collector_name)

    for s in self.series:
        name = s["Label"]
        try:
            val = data_collector.model_vars[name][-1]  # Latest value
        except (IndexError, KeyError):
            val = 0
        current_values.append(val)

    return current_values


def agents_portrayal(agent):
    if type(agent) is Cooperator:
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "green",
            "r": 0.5,
        }
    if type(agent) is Defector:
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 0,
            "Color": "red",
            "r": 0.5,
        }

    return portrayal


model_params = {
    "height": 10,
    "width": 10,
    "num_cooperators": mesa.visualization.Slider("Number of Cooperators", 20, 0, 100, 5),
    "defector_ratio": mesa.visualization.Slider("Ratio", 0.5, 0.1, 1.0, 0.05),
    "altruistic_punishment_freq": mesa.visualization.Slider("Frequency of Punishment", 4, 0, 300, 1),
}

grid = mesa.visualization.CanvasGrid(agents_portrayal, 10, 10, 500, 500)
agent_count_graphs = BarChartModule(
    [
        {"Label": "Cooperator Count", "Color": "Green"},
        {"Label": "Defector Count", "Color": "Red"},
     ],
    data_collector_name='datacollector',
)

agent_wealth_graphs = BarChartModule(
    [
        {"Label": "Cooperator Average Wealth", "Color": "Green"},
        {"Label": "Defector Average Wealth", "Color": "Red"},
        {"Label": "Population Average Wealth", "Color": "Blue"},

     ],
    data_collector_name='datacollector',
)
agent_moral_worth_graphs = BarChartModule(
    [
        {"Label": "Cooperator Average Moral Worth:", "Color": "Green"},
        {"Label": "Defector Average Moral Worth:", "Color": "Red"},
        {"Label": "Population Average Moral Worth", "Color": "Blue"},

     ],
    data_collector_name='datacollector',
)

#Punishment graph

punishment_graphs = BarChartModule(
    [
        {"Label": "Altruistic Punishment", "Color": "Purple"},
        {"Label": "Antisocial Punishment", "Color": "Red"},
     ],
    data_collector_name='datacollector',
)


# server
server = mesa.visualization.ModularServer(PublicGoodGame,
                                          [grid, agent_count_graphs, agent_wealth_graphs,
                                           agent_moral_worth_graphs, punishment_graphs],
                                          "PublicGoodGame",
                                          model_params,
                                          )


