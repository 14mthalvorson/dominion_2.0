import random


class Simulator:
    def __init__(self, player_names, default_supply_size=30):
        self.buy_matrix = None
        self.player_names = player_names
        self.total_games = 0
        self.default_supply_size = default_supply_size

    def run_n_games(self, n):
        for i in range(n):
            g1 = Game(self.player_names, self.buy_matrix, default_supply_size=self.default_supply_size)
            g1.run()
            self.total_games += 1

            g1.winner.buy_matrix.normalize_matrix()

            if n % 21 == 0:
                g1.winner.buy_matrix.normalize_with_avg()

            self.buy_matrix = g1.winner.buy_matrix

    def __str__(self):
        string = ""
        string += "Games: %d   " % self.total_games
        string += "Supply size: %d\n" % self.default_supply_size
        return string


class Game:
    def __init__(self, player_names, buy_matrix=None, default_supply_size=30):
        self.player_list = None
        self.first_player = None
        self.current_player = None
        self.winner = None
        self.buy_matrix = buy_matrix
        self.round = -1
        self.list_of_card_names = None
        self.default_supply_size = default_supply_size

        self.init_player_list(player_names)
        self.init_supply()
        self.init_player_matrices()

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
        self.player_list = [Player(name) for name in player_names]
        self.shuffle_players()
        self.first_player = self.player_list[0]

    def shuffle_players(self):
        random.shuffle(self.player_list)

    def init_supply(self):
        self.supply = {
            'copper': self.default_supply_size,
            'silver': self.default_supply_size,
            'gold': self.default_supply_size,
            'estate': self.default_supply_size,
            'duchy': self.default_supply_size,
            'province': self.default_supply_size
        }

    def init_player_matrices(self):
        self.list_of_card_names = list(self.supply.keys())
        # list_of_card_names.sort()

        # Player buy matrix
        for player in self.player_list:
            if self.buy_matrix is None: # First game
                player.init_player_matrix(self.list_of_card_names)
            else: # Not the first game
                player.copy_player_matrix(self.list_of_card_names, self.buy_matrix)

    def buy_card(self, treasure_total):
        valid_buys = list(self.supply.keys())

        # Remove cards with 0 in the supply
        valid_buys = [card_name for card_name in valid_buys if self.supply.get(card_name, -1) > 0]

        # Remove cards that are too expensive
        valid_buys = [card_name for card_name in valid_buys if treasure_total >= self.card_stats.get(card_name, -1)[1]]

        if len(valid_buys) > 0:
            # Random selection
            #selected_card_name = random.choice(valid_buys)

            valid_buys_sum_probs = 0
            for card_name in valid_buys:
                valid_buys_sum_probs += self.current_player.buy_matrix.matrix[self.round][self.list_of_card_names.index(card_name)]

            valid_buys_normalized_probs = []
            for card_name in valid_buys:
                valid_buys_normalized_probs.append(self.current_player.buy_matrix.matrix[self.round][self.list_of_card_names.index(card_name)] / valid_buys_sum_probs)

            selected_card_name = None
            prob_total = 0
            for i in range(len(valid_buys)):
                random_num = random.random()
                if random_num < valid_buys_normalized_probs[i] / (1 - prob_total):
                    selected_card_name = valid_buys[i]
                else:
                    prob_total += valid_buys_normalized_probs[i]


            type = self.card_stats[selected_card_name][0]
            cost = self.card_stats[selected_card_name][1]
            treasure = self.card_stats[selected_card_name][2]
            victory = self.card_stats[selected_card_name][3]

            self.supply[selected_card_name] -= 1
            self.current_player.player_deck.add_card(Card(selected_card_name, type, cost, treasure_value=treasure, victory_points=victory))

            # Update player buy matrix
            self.current_player.buy_matrix.update_prob(self.round, selected_card_name)
        else:
            return

    def take_next_player_turn(self):
        # Take player at index 0, executes turn, returns to end of list
        self.current_player = self.player_list.pop(0)

        # Update round when at first_player's turn
        if self.current_player == self.first_player:
            self.round = min(self.round + 1, 25)

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
                self.determine_winner()
                #print("Winner: %s" % self.winner.name)
                break

    def run(self):
        while not self.is_game_over():
            self.take_next_player_turn()

        self.determine_winner()
        #print("Winner: %s" % self.winner.name)

    def is_game_over(self):
        if list(self.supply.values()).count(0) >= 3:
            return True
        elif self.supply.get('province', -1) == 0:
            return True
        else:
            return False

    def determine_winner(self):
        max_victory_points = 0
        for player in self.player_list:
            if player.player_deck.count_victory_points() > max_victory_points:
                self.winner = player
                max_victory_points = player.player_deck.count_victory_points()

    def __str__(self):
        string = "\n"
        string += "Supply:  "
        for card_name in list(self.supply.keys()):
            string += "%s: %d   " % (card_name, self.supply[card_name])
        string += "\n"
        for player in self.player_list:
            string += "%s:\t Deck Size: %d\n" % (player.name, len(player.player_deck.draw_list) + len(player.player_deck.discard_list) + len(player.player_deck.hand_list))
        return string + "\n"


class Player:
    def __init__(self, name):
        self.name = name
        self.player_deck = PlayerDeck()
        self.buy_matrix = None

    def init_player_matrix(self, list_of_card_names):
        self.buy_matrix = ProbabilityMatrix(list_of_card_names)

    def copy_player_matrix(self, list_of_card_names, other_matrix):
        self.buy_matrix = ProbabilityMatrix(list_of_card_names)

        for round_index in range(len(self.buy_matrix.matrix)):
            for card_index in range(len(self.buy_matrix.matrix[round_index])):
                self.buy_matrix.matrix[round_index][card_index] = other_matrix.matrix[round_index][card_index]

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

class ProbabilityMatrix:
    def __init__(self, list_of_card_names, max_rounds=26):
        self.max_rounds = max_rounds
        self.list_of_card_names = list_of_card_names
        self.matrix = [[1.0 for i in range(len(list_of_card_names))] for j in range(max_rounds)]
        self.normalize_matrix()

    def update_prob(self, round, card_name):
        alpha = 0.01
        index = self.list_of_card_names.index(card_name)

        # Update probability function
        self.matrix[round][index] += 0.01
        #self.matrix[round][index] += alpha * (1 - self.matrix[round][index])

    def normalize_matrix(self):
        for round in range(len(self.matrix)):
            prob_total = sum(self.matrix[round])
            self.matrix[round] = [x / prob_total for x in self.matrix[round]]

    def normalize_with_avg(self):
        for round in range(len(self.matrix)):
            self.matrix[round] = [x + 0.1 for x in self.matrix[round]]
        self.normalize_matrix()

    def __str__(self):
        string = ""
        for card_name in self.list_of_card_names:
            string += " %.4s  \t" % card_name
        string += "\n"
        for round_probs in self.matrix:
            for prob in round_probs:
                string += "%.1f \t " % (prob * 100)
            string += "\n"
        return string

