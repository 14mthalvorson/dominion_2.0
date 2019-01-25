import random


class Game:
    def __init__(self, player_names):
        self.player_list = []
        self.init_player_list(player_names)
        self.init_supply()

    def init_player_list(self, player_names):
        self.player_list += [Player(name) for name in player_names]
        self.shuffle_players()

    def shuffle_players(self):
        random.shuffle(self.player_list)

    def init_supply(self):
        pass

    def __str__(self):
        string = "\n"
        for player in self.player_list:
            string += "%s:\t Deck Size: %d\n" % (player.name, len(player.player_deck.draw_list) + len(player.player_deck.discard_list) + len(player.player_deck.hand_list))
        return string + "\n"

    def take_next_player_turn(self):
        # Take player at index 0, executes turn, returns to end of list
        pass


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
        self.discard_list.append(card);

    def reshuffle(self):
        self.draw_list += self.discard_list
        self.discard_list = []
        random.shuffle(self.draw_list)

    def redraw(self):
        # Throw error if cards already in hand_list when attempting to redraw
        if len(self.hand_list) > 0:
            raise Exception('in PlayerDeck: trying to redraw but cards already in hand')
        else:
            for i in range(5):
                # Check if cards are available to be drawn
                if len(self.draw_list) > 0:
                    self.hand_list.append(self.draw_list.pop(0))
                else:
                    self.reshuffle()
                    self.hand_list.append(self.draw_list.pop(0))