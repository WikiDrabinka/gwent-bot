import random

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

        def __init__(self, deck: list[Card], hand: list[Card], played: dict[int, list[Card]] = None, cemetary: list[Card] = []):

            self.hand = hand
            self.deck = deck
            if played:
                self.played = played
            else: 
                self.played = {i: [] for i in range(3)}
            self.cemetary = cemetary

        def draw_card(self):
            
            if len(self.deck) == 0:
                return
            
            new_card = random.choice(self.deck)

            self.deck.remove(new_card)
            self.hand.append(new_card)

    def __init__(self, players: list[Player]):

        self.players = players
        self.weather = []
        self.turn = 0

    def get_score(self, player_id: int):

        score = 0
        player = self.players[player_id]

        for row in player.played:

            score += sum([card.modified_points for card in player.played[row]])

        return score
    
    def remove_card(self, card: Card, dead: bool = True):

        for player in self.players:
            
            for row in card.rows:

                player.played[row].remove(card)
                card.modified_points = card.points

                if dead:
                    player.cemetary.append(card)


    def modify_cards(self, rows, function):
        
        for player in self.players:

            for row in rows:

                for card in player.played[row]:

                    card.modified_points = function(card, row = player.played[row])

    def play_card(self, card: Card, row = None, **kwargs):

        player = self.players[self.turn]

        player.hand.remove(card)

        def apply_bonuses(card, **kwargs):

            morale = 0

            bonded = 0

            horn = 0

            for other_card in kwargs.get("row", []):

                if card == other_card:

                    continue

                if "tight bond" in card.powers and other_card.name == card.name:

                    bonded += 1

                if "morale boost" in other_card.powers:

                    morale += 1

                if "horn" in other_card.powers:

                    horn = 1
            
            return (card.modified_points * (bonded + 1) + morale) * (horn + 1)
        
        def apply_weather(card, **kwargs):

            return 1 if "hero" not in card.powers and card.points != 0 else card.points
            

        if "weather" in card.powers:

            self.weather.append(card)

            self.modify_cards(card.rows, apply_weather)
        
        elif "scorch" in card.powers:

            card_candidates = [candidate for player in self.players for row in range(3) for candidate in player.played[row] if "hero" not in candidate.powers]

            max_points = max([card.modified_points for card in card_candidates])
            max_cards = [card for card in card_candidates if card.modified_points == max_points]

            for removed_card in max_cards:
                self.remove_card(removed_card)
                        
        else:

            if not row:

                row = card.rows[0]

            if "spy" in card.powers:

                self.players[self.turn - 1].played[row].append(card)
                player.draw_card()

            else:

                if "muster" in card.powers:

                    new_cards_hand = [new_card for new_card in player.hand if new_card.name == card.name]
                    new_cards_deck = [new_card for new_card in player.deck if new_card.name == card.name]

                    for new_card in new_cards_hand:

                        player.played[new_card.rows[0]].append(new_card)
                        player.hand.remove(new_card)

                    for new_card in new_cards_deck:

                        player.played[new_card.rows[0]].append(new_card)
                        player.deck.remove(new_card) 

                if "medic" in card.powers:

                    revived_card = player.cemetary[kwargs.get("index", 0)] 
                    player.played[revived_card.rows[0]].append(revived_card)
                    player.cemetary.remove(revived_card)

                if "decoy" in card.powers:

                    replaced_card = kwargs.get("replaced_card", None)

                    if replaced_card:
                        player.hand.append(replaced_card)
                        self.remove_card(replaced_card, False)
                
                player.played[row].append(card)

        blocked_rows = set([row for weather_card in self.weather for row in weather_card.rows])
        self.modify_cards(card.rows, lambda card, row: card.points)
        self.modify_cards(list(blocked_rows), apply_weather)
        self.modify_cards(card.rows, apply_bonuses)
 

        self.turn = (self.turn + 1) % len(self.players)        