import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from chessdotcom import get_player_stats, get_player_games_by_month
import berserk
import os

username = os.environ.get('chessname')
apitoken = os.environ.get('lichess_api_token')


stats = get_player_stats(username).json


categories = ['chess_blitz', 'chess_rapid', 'chess_bullet', 'chess_daily']
print('Current')
for category in categories:
    print(category[6:] + ": " + str(stats[category]['last']['rating']))
    
print('\nBest')
for category in categories:
    print(category[6:] + ": " + str(stats[category]['best']['rating']))
    
print('\nPuzzle Rush')
print('Best: ' + str(stats['puzzle_rush']['best']['score']))
try:
	print('Today: ' + str(stats['puzzle_rush']['daily']['score']))
except:
	print("Tdoay: No attempt today.")