from dominion import *

g1 = Game(['AAA', 'BBB', 'CCC', 'DDD'])

for player in g1.player_list:
    print(player)
print(g1)

g1.take_n_turns(120)

for player in g1.player_list:
    print(player)
print(g1)