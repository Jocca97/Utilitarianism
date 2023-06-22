import mesa
import numpy as np

from numpy import random

from cooperator import Cooperator
from defector import Defector

# Punishment
cost_punish_agent = 1
agent_punishment = 3


class PublicGoodGame(mesa.Model):
    def __init__(self, num_cooperators, defector_ratio, altruistic_punishment_freq, width=10,
                 height=10):
        super().__init__(num_cooperators, defector_ratio, altruistic_punishment_freq, width,
                         height)
        self.num_cooperators = num_cooperators
        self.num_defectors = round(self.num_cooperators * defector_ratio)
        self.defector_ratio = defector_ratio
        self.common_pool = 0
        self.multiplier = 1.6
        self.investment = 0
        self.schedule = mesa.time.RandomActivation(self)
        self.altruistic_punishment_freq = altruistic_punishment_freq
        self.transform = self.transform_agent()
        self.payoff = self.calculate_payoff()
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.datacollector = mesa.DataCollector(
            model_reporters={"Cooperator Count": count_agent_cooperator,
                             "Defector Count": count_agent_defector,
                             "Cooperator Average Wealth": cooperator_average_wealth,
                             "Defector Average Wealth": defector_average_wealth,
                             "Population Average Wealth": population_average_wealth,
                             "Cooperator Average Moral Worth:": cooperator_average_moral_worth,
                             "Defector Average Moral Worth:": defector_average_moral_worth,
                             "Population Average Moral Worth": population_average_moral_worth,
                             "Altruistic Punishment": altruistic_punishment_frequency,
                             "Antisocial Punishment": antisocial_punishment_frequency,
                             "AP Money Spent": money_spent_altruistic_punishment,
                             "AP Money Lost": money_lost_altruistic_punishment,
                             "ASP Money Spent": money_spent_antisocial_punishment,
                             "ASP Money Lost": money_lost_antisocial_punishment,
                             "Common Pool Wealth": common_pool_wealth,
                             },
        )

        # Create agents
        for i in range(int(num_cooperators)):
            # Create Cooperator
            moral_worth_initial_values = np.random.normal(5, 3.5, num_cooperators)
            a = Cooperator(self.next_id(), self)
            a.moral_worth = moral_worth_initial_values[i]

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
            self.schedule.add(a)
            self.datacollector.collect(self)

        # Create Defector
        for i in range(int(self.num_defectors)):
            moral_worth_initial_values = np.random.normal(5, 3.5, self.num_defectors)
            b = Defector(self.next_id(), self)
            b.moral_worth = moral_worth_initial_values[i]

            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(b, (x, y))
            self.schedule.add(b)
            self.datacollector.collect(self)

    def set_investment(self, investment):
        """

        This method calculates the investment amount of each agent belonging to the
        Cooperator and Defector classes and sums it all up.

        """
        cooperator_investment = 0
        defector_investment = 0
        # Calculate investment for each Cooperator instance
        for agent in self.schedule.agents:
            if isinstance(agent, Cooperator):
                cooperator_investment += agent.calculate_invest()

        # Calculate investment for each Defector instance
        for agent in self.schedule.agents:
            if isinstance(agent, Defector):
                defector_investment += agent.calculate_invest()

        investment += cooperator_investment + defector_investment
        self.investment += investment
        self.common_pool += investment

    def calculate_payoff(self):
        """

        This method calculates the payoff of each agent

        """
        print(self.investment)
        print(self.common_pool)
        self.payoff = (self.investment * self.multiplier) / (self.num_cooperators + self.num_defectors)

        return self.payoff

    # def common_pool_wealth(self):
    #     self.common_pool += self.calculate_payoff()

    def agent_transform(self):
        """

        A method that mutates agents according to their investment behaviors

        """
        for agent in self.schedule.agents:
            if isinstance(agent, Defector) and agent.calculate_invest() > 2:
                wealth = agent.wealth
                id = agent.unique_id
                new_agent = Cooperator(id, self, wealth)
                # Add the new agent to grid and remove old one
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                self.grid.place_agent(new_agent, (x, y))
                self.schedule.add(new_agent)
            elif isinstance(agent, Cooperator) and agent.calculate_invest() == 2:
                wealth = agent.wealth
                id = agent.unique_id
                new_agent = Defector(id, self, wealth)
                # Add the new agent to grid and remove old one
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                self.grid.remove_agent(agent)
                self.schedule.remove(agent)
                self.grid.place_agent(new_agent, (x, y))
                self.schedule.add(new_agent)

    def altruistic_punishment(self):
        for agent in self.schedule.agents:
            if isinstance(agent, Cooperator) or isinstance(agent, Defector):
                cellmates = self.grid.get_cell_list_contents([agent.pos])
                if len(cellmates) > 1:
                    other = self.random.choice(cellmates)
                    if agent.calculate_contribution_amount() > other.calculate_contribution_amount():
                        agent.wealth -= cost_punish_agent
                        other.wealth -= agent_punishment
                else:
                    pass

    def altruistic_punishment_frequency(self):
        altruistic_punishment_freq = 0
        for _ in self.schedule.agents:
            if self.altruistic_punishment():
                altruistic_punishment_freq += 1

        return altruistic_punishment_freq

    def antisocial_punishment(self):
        if self.altruistic_punishment_frequency() == self.altruistic_punishment_freq:
            for agent in self.schedule.agents:
                if isinstance(agent, Cooperator) or isinstance(agent, Defector):
                    cellmates = self.grid.get_cell_list_contents([agent.pos])
                    if len(cellmates) > 1:
                        other = self.random.choice(cellmates)
                        if agent.calculate_contribution_amount() < other.calculate_contribution_amount():
                            agent.wealth -= cost_punish_agent
                            other.wealth -= agent_punishment
                    else:
                        pass

    def step(self):
        self.schedule.step()
        self.agent_transform()
        self.set_investment(self.investment)
        self.calculate_payoff()
        self.altruistic_punishment()
        self.antisocial_punishment()
        self.datacollector.collect(self)


# Agent Count

def count_agent_cooperator(model):
    num_cooperator = sum(1 for agent in model.schedule.agents if isinstance(agent, Cooperator))

    return num_cooperator


def count_agent_defector(model):
    num_defector = sum(1 for agent in model.schedule.agents if isinstance(agent, Defector))

    return num_defector


# Wealth

def cooperator_average_wealth(model):
    cooperator_wealth_report = [agent.wealth for agent in model.schedule.agents if isinstance(agent, Cooperator)]
    if len(cooperator_wealth_report) > 0:
        cooperator_avg_wealth = sum(cooperator_wealth_report) / len(cooperator_wealth_report)
    else:
        cooperator_avg_wealth = 0  # Set a default value when there are no cooperators in the model

    return cooperator_avg_wealth


def defector_average_wealth(model):
    defector_wealth_report = [agent.wealth for agent in model.schedule.agents if isinstance(agent, Defector)]
    if len(defector_wealth_report) > 0:
        defector_avg_wealth = sum(defector_wealth_report) / len(defector_wealth_report)
    else:
        defector_avg_wealth = 0

    return defector_avg_wealth


def population_average_wealth(model):
    cooperator_avg_wealth = cooperator_average_wealth(model)
    defector_avg_wealth = defector_average_wealth(model)
    pop_avg_wealth = (cooperator_avg_wealth + defector_avg_wealth) / 2

    return pop_avg_wealth


# Moral Worth

def cooperator_average_moral_worth(model):
    cooperator_moral_worth_report = [agent.moral_worth for agent in model.schedule.agents if
                                     isinstance(agent, Cooperator)]
    if len(cooperator_moral_worth_report) > 0:
        cooperator_avg_moral_worth = sum(cooperator_moral_worth_report) / len(cooperator_moral_worth_report)
    else:
        cooperator_avg_moral_worth = 0

    return cooperator_avg_moral_worth


def defector_average_moral_worth(model):
    defector_moral_worth_report = [agent.moral_worth for agent in model.schedule.agents if
                                   isinstance(agent, Defector)]
    if len(defector_moral_worth_report) > 0:
        defector_avg_moral_worth = sum(defector_moral_worth_report) / len(defector_moral_worth_report)
    else:
        defector_avg_moral_worth = 0

    return defector_avg_moral_worth


def population_average_moral_worth(model):
    cooperator_avg_moral_worth = cooperator_average_moral_worth(model)
    defector_avg_moral_worth = defector_average_moral_worth(model)
    pop_avg_moral_worth = (cooperator_avg_moral_worth + defector_avg_moral_worth) / 2

    return pop_avg_moral_worth


# Money spent and lost within each punishment type

def money_spent_altruistic_punishment(model):
    money_spent = 0
    for _ in model.schedule.agents:
        if model.altruistic_punishment():
            money_spent += cost_punish_agent

    return money_spent


def money_lost_altruistic_punishment(model):
    money_lost = 0
    for _ in model.schedule.agents:
        if model.altruistic_punishment():
            money_lost += agent_punishment

    return money_lost


def money_spent_antisocial_punishment(model):
    money_spent = 0
    for _ in model.schedule.agents:
        if model.antisocial_punishment():
            money_spent += cost_punish_agent

    return money_spent


def money_lost_antisocial_punishment(model):
    money_lost = 0
    for _ in model.schedule.agents:
        if model.antisocial_punishment():
            money_lost += agent_punishment

    return money_lost


# Frequency of each punishment type

def altruistic_punishment_frequency(model):
    altruistic_frequency = 0
    for agent in model.schedule.agents:
        if isinstance(agent, Cooperator) or isinstance(agent, Defector):
            if model.altruistic_punishment():
                altruistic_frequency += 1

    return altruistic_frequency


def antisocial_punishment_frequency(model):
    antisocial_frequency = 0
    for agent in model.schedule.agents:
        if isinstance(agent, Cooperator) or isinstance(agent, Defector):
            if model.antisocial_punishment():
                antisocial_frequency += 1

    return antisocial_frequency


# Common Pool

def common_pool_wealth(model):
    cp_wealth = model.common_pool

    return cp_wealth
