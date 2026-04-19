from game.board import Board, Card
import numpy as np

class Agent():

    def __init__(self, deck: list[Card], name = "Default Agent"):

        self.name = name

        self.deck = deck
        self.player = Board.Player(deck)
        self.player.shuffle_deck()
        self.pass_card = Card(name = "pass")

    def get_actions(self) -> list[tuple[Card, dict]]:

        actions = []

        for card in self.player.hand:

            if "decoy" in card.powers:
                
                for row in self.player.played.values():

                    for removed_card in row:

                        actions.append((card, {"removed_card": removed_card}))

            elif "medic" in card.powers:

                for revived_card in self.player.cemetary:

                    if -1 not in revived_card.rows:

                        actions.append((card, {"revived_card": revived_card}))

            elif "horn" in card.powers:

                for row in range(3):

                    actions.append((card, {"row": row}))
            
            else:

                actions.append((card, None))

        actions.append((self.pass_card, None))

        return actions

    def select_action(self, observation: Board) -> tuple[Card, dict]:

        # if np.random.random() < 0.5:
        #     return self.get_actions()[-1]

        return max(self.get_actions(), key=lambda x: x[0].points)

    def update(self, action, observation: Board):
        pass

class GameHandler():

    def __init__(self, agents: list[Agent]):

        self.agents = agents
        self.board = Board([agent.player for agent in agents])
        self.finished = [False] * len(agents)

    def step(self):
        
        for idx, agent in enumerate(self.agents):

            next_action, kwargs = agent.select_action(self.board)

            if kwargs:

                # print(f"[{agent.name}] played {next_action.name} for row {kwargs.get("row", next_action.rows[0])}")

                self.board.play_card(agent.player, next_action, **kwargs)

            else:

                # print(f"[{agent.name}] played {next_action.name} for row {next_action.rows[0]}")
                
                self.board.play_card(agent.player, next_action)

            agent.update((next_action, kwargs), self.board)
            print(f"{agent.name} score: {agent.player.get_score()}")

            if next_action.name == "pass":

                self.finished[idx] = True

    def game(self):

        for agent in self.agents:

            agent.player.shuffle_deck()

        while all([agent.player.lost < 2 for agent in self.agents]):

            self.finished = [False] * len(self.agents)

            for agent in self.agents:

                agent.player.clear_played()

            self.board.clear_weather()

            while not all(self.finished):

                self.step()

            scores = [agent.player.get_score() for agent in self.agents]
            max_score = max(scores)

            if scores.count(max_score) > 1:

                for agent in self.agents:

                    agent.player.lost += 1
            
            else:

                for agent in self.agents:

                    if agent.player.get_score() == max_score:

                        agent.player.won += 1
                    
                    else:

                        agent.player.lost += 1