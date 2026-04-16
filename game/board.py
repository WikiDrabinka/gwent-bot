import numpy as np

class Card():

    def __init__(self, **properties):

        self.id = properties.get("id")
        self.name = properties.get("name")
        self.points = properties.get("points", 0)
        self.modified_points = self.points
        self.rows = properties.get("rows", [-1])
        self.powers = properties.get("powers", [])

    def __repr__(self):

        return f"Card '{self.name}'"
    
    def __eq__(self, other):

        return self.name == other.name and self.points == other.points and set(self.rows) == set(other.rows) and set(self.powers) == set(other.powers)
    
    def __hash__(self):
        
        return hash((self.name, self.points, tuple(sorted(self.rows)), tuple(sorted(self.powers))))

class Board():

    class Player():

        def __init__(self, deck: list[Card], hand: list[Card] = [], played: dict[int, list[Card]] = None, cemetary: list[Card] = []):

            self.hand = hand
            self.deck = deck
            if played:
                self.played = played
            else: 
                self.played = {i: [] for i in range(3)}
            self.cemetary = cemetary
            self.passed = False

        def draw_card(self):
            
            if len(self.deck) == 0:
                return
            
            new_card = np.random.choice(self.deck)

            self.deck.remove(new_card)
            self.hand.append(new_card)

        def shuffle_deck(self):

            deck = self.deck + self.hand + self.cemetary + [card for row in self.played.values() for card in row]
            self.played = {i: [] for i in range(3)}
            self.cemetary = []
            self.passed = False
            self.hand = list(np.random.choice(deck, size = 10, replace = False))
            used_deck = deck.copy()
            
            for card in self.hand:
                used_deck.remove(card)

            self.deck = used_deck

        def get_score(self):

            score = 0

            for row in self.played:

                score += sum([card.modified_points for card in self.played[row]])

            return score

    def __init__(self, players: list[Player]):

        self.players = players
        self.weather = []
    
    def remove_card(self, card: Card, dead: bool = True):

        for player in self.players:
            
            for row in card.rows:

                if card in player.played[row]:
                    player.played[row].remove(card)
                    card.modified_points = card.points

                    if dead:
                        player.cemetary.append(card)


    def modify_cards(self, rows: list[int], function):
        
        for player in self.players:

            for row in rows:

                for card in player.played[row]:

                    card.modified_points = function(card, row = player.played[row])

    def play_card(self, player: Player, card: Card, **kwargs):

        row = kwargs.get("row", None)

        if card.name == "pass":
        
            player.passed = True
            return

        player.hand.remove(card)

        def apply_bonuses(card, **kwargs):

            morale = 0

            bonded = 0

            horn = 0

            for other_card in kwargs.get("row", []):

                if card.id == other_card.id:

                    continue

                if "tight bond" in card.powers and other_card.name.split(":")[0] == card.name.split(":")[0]:

                    bonded += 1

                if "morale boost" in other_card.powers:

                    morale += 1

                if "horn" in other_card.powers:

                    horn = 1
            
            return (card.modified_points * (bonded + 1) + morale) * (horn + 1)
        
        def apply_weather(card, **kwargs):

            return 1 if "hero" not in card.powers and card.points != 0 else card.points
        
        def reset_points(card, **kwargs):

            return card.points
            

        if "weather" in card.powers:

            self.weather.append(card)

            self.modify_cards(card.rows, apply_weather)

        elif "clear" in card.powers:

            self.weather.clear()
        
        elif "scorch" in card.powers:

            rows = list(range(3)) if -1 in card.rows else card.rows

            card_candidates = [candidate for player in self.players for row in rows for candidate in player.played[row] if "hero" not in candidate.powers]

            if len(card_candidates) > 0:

                max_points = max([card.modified_points for card in card_candidates])
                max_cards = [card for card in card_candidates if card.modified_points == max_points]

                for removed_card in max_cards:
                    self.remove_card(removed_card)
                        
        else:

            if row is None:

                row = card.rows[0]

            if "spy" in card.powers:

                self.players[self.players.index(player) - 1].played[row].append(card)
                player.draw_card()

            else:

                if "muster" in card.powers:

                    new_cards_hand = [new_card for new_card in player.hand if new_card.name.split(":")[0] == card.name.split(":")[0]]
                    new_cards_deck = [new_card for new_card in player.deck if new_card.name.split(":")[0] == card.name.split(":")[0]]

                    for new_card in new_cards_hand:

                        player.played[new_card.rows[0]].append(new_card)
                        player.hand.remove(new_card)

                    for new_card in new_cards_deck:

                        player.played[new_card.rows[0]].append(new_card)
                        player.deck.remove(new_card) 

                if "medic" in card.powers:

                    revived_card = kwargs.get("revived_card", None)
                    player.played[revived_card.rows[0]].append(revived_card)
                    player.cemetary.remove(revived_card)

                if "decoy" in card.powers:

                    replaced_card = kwargs.get("replaced_card", None)

                    if replaced_card:
                        player.hand.append(replaced_card)
                        self.remove_card(replaced_card, False)
                
                player.played[row].append(card)

        blocked_rows = set([row for weather_card in self.weather for row in weather_card.rows])
        if -1 in card.rows:
            self.modify_cards(list(range(3)), reset_points)
            self.modify_cards(list(blocked_rows), apply_weather)
            self.modify_cards(list(range(3)), apply_bonuses)    
        else:
            self.modify_cards(card.rows, reset_points)
            self.modify_cards(list(blocked_rows), apply_weather)
            self.modify_cards(card.rows, apply_bonuses)      