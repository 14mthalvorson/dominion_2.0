from dominion import *

s1 = Simulator(['AAA', 'BBB', 'CCC', 'DDD'], default_supply_size=30)

s1.run_n_games(500)
print(s1.buy_matrix)

s1.run_n_games(1000)
print(s1.buy_matrix)

s1.run_n_games(2000)
print(s1.buy_matrix)

s1.run_n_games(5000)
print(s1.buy_matrix)

print(s1)
