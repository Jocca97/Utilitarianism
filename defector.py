import mesa
import random
from numpy import random

# Parameters
# Payoffs
fixed_loss = 2



class Defector(mesa.Agent):
    def __init__(self, unique_id, model, wealth=20):
        super().__init__(unique_id, model)
        self.public_good_game = model

        # Assign to self object
        self.wealth = wealth
        self.moral_worth = 0
        self.probability_contributing = self.calculate_probability_contributing()
        self.contribution_amount = self.calculate_contribution_amount()
        self.invest = self.calculate_invest()

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def calculate_probability_contributing(self):
        """

        A function that defines the probability of contribution according to the agent's moral worth

        """
        if 0 <= self.moral_worth <= 4:
            self.probability_contributing = 0.1
        elif 5 <= self.moral_worth <= 10:
            self.probability_contributing = 0.2
        elif 11 <= self.moral_worth <= 20:
            self.probability_contributing = 0.3
        else:
            self.probability_contributing = 0

        return self.probability_contributing

    def calculate_contribution_amount(self):
        """

        A function that defines the probability of the amount of a contribution according to the agent's moral wort

        """
        self.contribution_amount = 0
        if 0 <= self.moral_worth <= 4:
            self.contribution_amount = self.wealth * 0.2 + fixed_loss
        elif 5 <= self.moral_worth <= 10:
            self.contribution_amount = self.wealth * 0.3 + fixed_loss
        elif 11 <= self.moral_worth <= 20:
            self.contribution_amount = self.wealth * 0.5 + fixed_loss
        else:
            self.contribution_amount = self.wealth * 0.1 + fixed_loss

        return self.contribution_amount

    def calculate_invest(self):
        """

        A function that defines the investment behaviors of defector

        """
        if self.calculate_probability_contributing() >= random.random():
            invest = self.calculate_contribution_amount()
        else:
            invest = fixed_loss

        return invest

    def moral_worth_assignment(self):  # Change
        """

        This function is supposed to give moral worth to defectors
        according to their contribution behaviors

        """
        if 1 <= self.calculate_invest() <= 5:
            self.moral_worth += 1
        elif 6 <= self.calculate_invest() <= 10:
            self.moral_worth += 2
        elif self.calculate_invest() >= 11:
            self.moral_worth += 3
        else:
            self.moral_worth -= 1

        return self.moral_worth

    # def altruistic_punishment(self):
    #     cellmates = self.model.grid.get_cell_list_contents([self.pos])
    #     if len(cellmates) > 1:
    #         other = self.random.choice(cellmates)
    #         if self.calculate_contribution_amount() > other.calculate_contribution_amount():
    #             self.wealth -= cost_punish_agent
    #             other.wealth -= agent_punishment
    #
    # def antisocial_punishment(self):
    #     cellmates = self.model.grid.get_cell_list_contents([self.pos])
    #     if len(cellmates) > 1:
    #         other = self.random.choice(cellmates)
    #         if self.calculate_contribution_amount() < other.calculate_contribution_amount():
    #             self.wealth -= cost_punish_agent
    #             other.wealth -= agent_punishment

    def step(self):
        self.move()
        if self.wealth > 0:
            self.calculate_probability_contributing()
            self.calculate_contribution_amount()
            self.calculate_invest()
            self.moral_worth_assignment()
            # self.public_good_game.altruistic_punishment()
            # self.public_good_game.antisocial_punishment_initiator()
            # self.altruistic_punishment()
            # self.antisocial_punishment()
        else:
            pass

