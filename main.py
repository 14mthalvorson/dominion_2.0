from dominion import *

s1 = Simulator(['AAA', 'BBB', 'CCC', 'DDD'])

s1.run_n_games(10)

print(s1.buy_matrix)

