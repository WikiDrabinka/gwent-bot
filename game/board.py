class Card():

    def __init__(self, **properties):

        self.name = properties.get("name")
        self.points = properties.get("points", 0)
        self.rows = properties.get("rows", [-1])
        self.powers = properties.get("powers", [])

class Board():

    class Player():

        def __init__(self, deck: list[Card]):

            self.deck = deck
            self.played = {i: [] for i in range(3)}

    def __init__(self, players):

        self.players = players

        self.weather = []

        self.turn = 0

    def get_score(self, player_id: int):

        blocked_rows = set([row for card in self.weather for row in card.rows])

        score = 0

        player = self.players[player_id]

        for row in player.played:

            if row in blocked_rows:

                score += len(player.played[row])

            else:

                score += sum([card.points for card in player.played])

        return score


    