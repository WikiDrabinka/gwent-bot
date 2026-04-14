from game.board import Board, Card
import numpy as np

class Agent():

    def __init__(self, deck: list[Card]):

        hand = list(np.random.choice(deck, size = 5, replace = False))
        used_deck = deck.copy()
        
        for card in hand:
            used_deck.remove(card)

        self.player = Board.Player(used_deck, hand)
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

                    actions.append((card, {"revived_card": revived_card}))
            
            else:

                actions.append((card, None))

        actions.append((self.pass_card, None))

        return actions

    def select_action(self, observation):
        return max(self.get_actions(), key=lambda x: x[0].points)

    def update(self, action, observation):
        pass

class GameHandler():

    def __init__(self, agents: list[Agent]):

        self.agents = agents
        self.board = Board([agent.player for agent in agents])

    def step(self):
        
        for agent in self.agents:

            next_action, kwargs = agent.select_action(self.board)

            if kwargs:

                self.board.play_card(agent.player, next_action, **kwargs)

            else:
                
                self.board.play_card(agent.player, next_action)

            agent.update((next_action, kwargs), self.board)


    

