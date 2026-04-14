class Card():

    def __init__(self, **properties):

        self.name = properties.get("name")
        self.points = properties.get("points", 0)
        self.modified_points = self.points
        self.rows = properties.get("rows", [-1])
        self.powers = properties.get("powers", [])

    def __repr__(self):

        return f"Card '{self.name}'\nPoints: {self.points}, Powers: {self.powers}, Rows: {self.rows}"

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

        score = 0
        player = self.players[player_id]

        for row in player.played:

            score += sum([card.modified_points for card in player.played[row]])

        return score
    
    def remove_card(self, card: Card):

        for player in self.players:
            
            for row in card.rows:

                player.played[row].remove(card)

    def modify_cards(self, rows, function):
        
        for player in self.players:

            for row in rows:

                for card in player.played[row]:

                    card.modified_points = function(card, row = player.played[row])


    def play_card(self, card: Card, row = None):

        player = self.players[self.turn]

        player.deck.remove(card)

        def apply_bonuses(card, **kwargs):

            morale = 0

            bonded = 0

            for other_card in kwargs.get("row", []):

                if card == other_card:

                    continue

                if "tight bond" in card.powers and other_card.name == card.name:

                    bonded += 1

                if "morale boost" in other_card.powers:

                    morale += 1
            
            return card.modified_points * (bonded + 1) + morale  
            

        if "weather" in card.powers:

            self.weather.append(card)

            self.modify_cards(card.rows, lambda x, row: 1)
                        
        else:

            if not row:

                row = card.rows[0]

            player.played[row].append(card)

            if "tight bond" in card.powers or "morale boost" in card.powers:

                self.modify_cards(card.rows, lambda card, row: card.points)

                blocked_rows = set([row for weather_card in self.weather for row in weather_card.rows])

                self.modify_cards(list(blocked_rows), lambda x, row: 1)

        self.modify_cards(card.rows, apply_bonuses)
 

        self.turn = (self.turn + 1) % len(self.players)
        


        


    