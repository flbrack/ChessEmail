# Import libraries
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from chessdotcom import get_player_stats, get_player_games_by_month
import berserk
import os

# Retrieve envrionment variables of my lcihess API token and my username
username = os.environ.get('chessname')
apitoken = os.environ.get('lichess_api_token')

# Get datetime for lastweek
lastweek = datetime.now()  - timedelta(days=7)
year, month = lastweek.year, lastweek.month

# Get my chess.com personal stats
stats = get_player_stats(username).json

categories = ['chess_bullet', 'chess_blitz', 'chess_rapid', 'chess_daily']
print('Chess.com Current Rankings')
for category in categories:
    print(category[6:] + ": " + str(stats[category]['last']['rating']))
"""    
print('\nBest')
for category in categories:
    print(category[6:] + ": " + str(stats[category]['best']['rating']))
"""    
print('\nPuzzle Rush')
print('Best: ' + str(stats['puzzle_rush']['best']['score']))

# Set up lichess API session
session = berserk.TokenSession(apitoken)
client = berserk.Client(session=session)

# Get my lichess personal stats
profile = client.account.get()
categories2 = ['bullet', 'blitz', 'rapid']
print("\nLichess Current Rankings")
for category in categories2:
    print(category + ": " + str(profile['perfs'][category]['rating']))

# Get my chess.com games from the last week
chesscom_games = get_player_games_by_month('flbrack', year, month).json['games']

if lastweek.month != datetime.now().month:
    chesscom_games += get_player_games_by_month('flbrack', year, month+1).json['games']
# Logic to take care of if last week covered two different months
for game in chesscom_games[:]:
    if datetime.fromtimestamp(game['end_time']) < lastweek:
        chesscom_games.remove(game)

# List of strings used to represent different types of draws in the chess.com API
chesscomDrawTypes = ['agreed', 'stalemate', 'repition', 'insufficient', '50move', 'timevsinsufficient', 'abandoned']

# Count wins, draws and losses from last week on chess.com
chesscom_wins, chesscom_draws, chesscom_losses = 0, 0, 0
for game in chesscom_games:
    if game['white']['username'] == 'flbrack':
        result = game['white']['result']
    else:
        result = game['black']['result']
    if result == 'win':
        chesscom_wins += 1
    elif result in chesscomDrawTypes:
        chesscom_draws += 1
    else:
        chesscom_losses += 1

# Put the datetime into required format for lichess API
starttime = int(datetime.timestamp(lastweek)*1000)
endtime = int(datetime.timestamp(datetime.now())*1000)

# Retrieve lichess games from past week
lichess_games = list(client.games.export_by_player(username='flbrack',since=starttime, until=endtime, max=500))

# Count wins, draws and losses from last week on lichess
lichess_wins, lichess_draws = 0, 0
for game in lichess_games:
    try:
        if game['players']['white']['user']['name'] == 'flbrack' and game['winner'] == 'white':
            lichess_wins+=1
        elif game['players']['black']['user']['name'] == 'flbrack' and game['winner'] == 'black':
            lichess_wins+=1
        if game['winner'] == 'draw':
            lichess_draws+=1
    except:
        lichess_draws+=1
lichess_losses = len(lichess_games) - lichess_wins - lichess_draws


total_games = len(lichess_games) + len(chesscom_games)
total_wins = lichess_wins + chesscom_wins
total_losses = lichess_losses + chesscom_losses
total_draws = lichess_draws + chesscom_draws

sizes = [total_wins, total_draws, total_losses]
labels = ['wins', 'draws', 'losses']

print("\nLast Week")
for i in range(3):
    print(f"{labels[i]}: {sizes[i]}")    

plt.pie(sizes, labels = labels, startangle = 270, autopct='%1.1f%%')
plt.title(f"Total Games: {total_games}")
plt.show()









