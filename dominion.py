import random


class Game:
    def __init__(self, player_names):
        self.player_list = []
        self.init_player_list(player_names)
        self.init_supply()
        self.current_player = None

        # Card Stats Format:
        #   'name': ['type', cost, treasure_value, victory_points]
        self.card_stats = {
            'copper':  ['treasure', 0, 1, 0],
            'silver':  ['treasure', 3, 2, 0],
            'gold':    ['treasure', 6, 3, 0],
            'estate':   ['victory', 2, 0, 1],
            'duchy':    ['victory', 5, 0, 3],
            'province': ['victory', 8, 0, 6]
        }

    def init_player_list(self, player_names):
        self.player_list += [Player(name) for name in player_names]
        self.shuffle_players()

    def shuffle_players(self):
        random.shuffle(self.player_list)

    def init_supply(self):
        self.supply = {
            'copper': 30,
            'silver': 30,
            'gold': 30,
            'estate': 30,
            'duchy': 30,
            'province': 30
        }

    def __str__(self):
        string = "\n"
        string += "Supply:  "
        for card_name in list(self.supply.keys()):
            string += "%s: %d   " % (card_name, self.supply[card_name])
        string += "\n"
        for player in self.player_list:
            string += "%s:\t Deck Size: %d\n" % (player.name, len(player.player_deck.draw_list) + len(player.player_deck.discard_list) + len(player.player_deck.hand_list))
        return string + "\n"

    def take_next_player_turn(self):
        # Take player at index 0, executes turn, returns to end of list
        self.current_player = self.player_list.pop(0)

        # Buy phase
        treasure_total = 0
        for card in self.current_player.player_deck.hand_list:
            treasure_total += card.treasure_value

        # Purchase card
        self.buy_card(treasure_total)

        self.current_player.player_deck.redraw()
        self.player_list.append(self.current_player)
        self.current_player = None

    def take_n_turns(self, n):
        for i in range(n):
            self.take_next_player_turn()

            # Check if game is over
            if self.is_game_over():
                print("Winner: %s" % self.determine_winner().name)
                break

    def buy_card(self, treasure_total):
        valid_buys = list(self.supply.keys())

        # Remove cards with 0 in the supply
        valid_buys = [card_name for card_name in valid_buys if self.supply.get(card_name, -1) > 0]

        # Remove cards that are too expensive
        valid_buys = [card_name for card_name in valid_buys if treasure_total >= self.card_stats.get(card_name, -1)[1]]

        if len(valid_buys) > 0:
            selected_card_name = random.choice(valid_buys)
            type = self.card_stats[selected_card_name][0]
            cost = self.card_stats[selected_card_name][1]
            treasure = self.card_stats[selected_card_name][2]
            victory = self.card_stats[selected_card_name][3]

            self.supply[selected_card_name] -= 1
            self.current_player.player_deck.add_card(Card(selected_card_name, type, cost, treasure_value=treasure, victory_points=victory))
        else:
            return

    def is_game_over(self):
        if list(self.supply.values()).count(0) >= 3:
            return True
        elif self.supply.get('province', -1) == 0:
            return True
        else:
            return False

    def determine_winner(self):
        winner = None
        max_victory_points = 0
        for player in self.player_list:
            if player.player_deck.count_victory_points() > max_victory_points:
                winner = player
                max_victory_points = player.player_deck.count_victory_points()
        return winner


class Player:
    def __init__(self, name):
        self.name = name
        self.player_deck = PlayerDeck()

    def __str__(self):
        string = "%s" % (self.name)
        string += "\n\tHand:    "
        for card in self.player_deck.hand_list:
            string += "%s  " % (card.name)
        string += "\n\tDraw:    "
        for card in self.player_deck.draw_list:
            string += "%s  " % (card.name)
        string += "\n\tDiscard: "
        for card in self.player_deck.discard_list:
            string += "%s  " % (card.name)
        return string


class Card:
    def __init__(self, name, type, cost, treasure_value=0, victory_points=0):
        self.name = name
        self.type = type
        self.cost = cost
        self.treasure_value = treasure_value
        self.victory_points = victory_points


class PlayerDeck:
    def __init__(self):
        self.draw_list = []
        self.hand_list = []
        self.discard_list = []
        self.init_card_list()

    def init_card_list(self):
        # 7 coppers, 3 estates per hand
        self.draw_list += [Card('copper', 'treasure', 0, treasure_value=1) for i in range(7)]
        self.draw_list += [Card('estate', 'victory', 2, victory_points=1) for i in range(3)]
        self.reshuffle()
        self.redraw()

    def add_card(self, card):
        self.discard_list.append(card)

    def reshuffle(self):
        self.draw_list += self.discard_list
        self.discard_list = []
        random.shuffle(self.draw_list)

    def redraw(self):
        # Empty hand
        while len(self.hand_list) > 0:
            self.discard_list.append(self.hand_list.pop(0))
        # Refill hand
        for i in range(5):
            # Check if cards are available to be drawn
            if len(self.draw_list) > 0:
                self.hand_list.append(self.draw_list.pop(0))
            else:
                self.reshuffle()
                self.hand_list.append(self.draw_list.pop(0))

    def count_victory_points(self):
        victory_points = 0
        for card in self.draw_list + self.hand_list + self.discard_list:
            victory_points += card.victory_points
        return victory_points