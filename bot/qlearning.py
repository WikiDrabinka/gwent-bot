from bot.agent import Agent
from game.board import Board, Card
import numpy as np

class QLearningAgent(Agent):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.q_values = {}
        self.state = None
        self.action = None
        self.learning_rate = kwargs.get("learning_rate", 0.1)
        self.gamma = kwargs.get("gamma", 0.95)
        self.epsilon = kwargs.get("epsilon", 0.1)

    def get_state(self, observation: Board) -> tuple[int, int]:

        state = []

        for card in set(self.deck):
            for row in range(0,2):
                if card in self.player.played[row]:
                    state.append("0")
                else:
                    state.append("1")
                if card in self.player.hand:
                    state.append("0")
                else:
                    state.append("1")

        if sum([self.player.get_score() - player.get_score() for player in observation.players]) > 0:
            state.append("1")
        else:
            state.append("0")

        return "".join(state)
    

    def select_action(self, observation: Board) -> tuple[Card, dict]:

        actions = self.get_actions()
        state = self.get_state(observation)
        actions_hashable = []

        for action in actions:

            action_hashable = (action[0], tuple(sorted(action[1].values()))) if action[1] else action
            actions_hashable.append(action_hashable)

        q_values = [(i, self.q_values.get(state, {}).get(action, 0)) for i, action in enumerate(actions_hashable)]

        if self.epsilon < np.random.random():

            return actions[max(q_values, key=lambda x: x[1])[0]]
        
        else:

            return actions[np.random.randint(len(actions))]
        
    def update(self, action, observation: Board):
        
        s = self.state
        action_hashable = (action[0], tuple(sorted(action[1].values()))) if action[1] else action
        a = action_hashable
        next_s = self.get_state(observation)

        current_score = sum([self.player.get_score() - player.get_score() for player in observation.players])

        r = self.player.won - self.player.lost + (current_score > 0)*0.5

        self.action = a
        if s not in self.q_values:
            self.q_values[s] = {a : 0}
        if a not in self.q_values[s]:
            self.q_values[s][a] = 0

        self.q_values[s][a] += self.learning_rate * (r + self.gamma * max(self.q_values.get(next_s, {a: 0}).values()) - self.q_values[s][a])

        self.epsilon = self.epsilon * 0.9

        self.state = next_s





