#!/opt/anaconda3/bin/python3

# Import libraries
import matplotlib.pyplot as plt
from datetime import timedelta, datetime
from chessdotcom import get_player_stats, get_player_games_by_month
import berserk
import os
import io
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid


USERNAME = os.getenv('CHESSNAME')
APITOKEN = os.getenv('APITOKEN')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASS = os.getenv('EMAIL_PASS')


# Get datetime for lastweek
lastweek = datetime.now()  - timedelta(days=7)
year, month = lastweek.year, lastweek.month

# Get my chess.com personal stats
stats = get_player_stats(USERNAME).json

categories = ['chess_bullet', 'chess_blitz', 'chess_rapid', 'chess_daily']
chessdotcom_rankingstring = ""
for category in categories:
    chessdotcom_rankingstring += category[6:] + ": " + str(stats[category]['last']['rating']) + "<br>"
chessdotcom_rankingstring += 'puzzle rush: ' + str(stats['puzzle_rush']['best']['score']) + "<br>"

# Set up lichess API session
session = berserk.TokenSession(APITOKEN)
client = berserk.Client(session=session)

# Get my lichess personal stats
profile = client.account.get()
categories2 = ['bullet', 'blitz', 'rapid']

lichess_rankingstring = ""
for category in categories2:
    lichess_rankingstring += category + ": " + str(profile['perfs'][category]['rating']) + "<br>"

# Get my chess.com games from the last week
chesscom_games = get_player_games_by_month(USERNAME, year, month).json['games']

if lastweek.month != datetime.now().month:
    chesscom_games += get_player_games_by_month(USERNAME, year, month+1).json['games']
# Logic to take care of if last week covered two different months
for game in chesscom_games[:]:
    if datetime.fromtimestamp(game['end_time']) < lastweek:
        chesscom_games.remove(game)

# List of strings used to represent different types of draws in the chess.com API
chesscomDrawTypes = ['agreed', 'stalemate', 'repetition', 'insufficient', '50move', 'timevsinsufficient', 'abandoned']

# Count wins, draws and losses from last week on chess.com
chesscom_wins, chesscom_draws, chesscom_losses = 0, 0, 0
for game in chesscom_games:
    if game['white']['username'] == USERNAME:
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
lichess_games = list(client.games.export_by_player(username=USERNAME,since=starttime, until=endtime, max=500))

# Count wins, draws and losses from last week on lichess
lichess_wins, lichess_draws = 0, 0
for game in lichess_games:
    try:
        if game['players']['white']['user']['name'] == USERNAME and game['winner'] == 'white':
            lichess_wins+=1
        elif game['players']['black']['user']['name'] == USERNAME and game['winner'] == 'black':
            lichess_wins+=1
        if game['winner'] == 'draw':
            lichess_draws+=1
    except Exception:
        lichess_draws+=1
lichess_losses = len(lichess_games) - lichess_wins - lichess_draws

# Summarise stats
total_games = len(lichess_games) + len(chesscom_games)
total_wins = lichess_wins + chesscom_wins
total_losses = lichess_losses + chesscom_losses
total_draws = lichess_draws + chesscom_draws

# Create pie chart
sizes = [total_wins, total_draws, total_losses]
labels = ['wins', 'draws', 'losses']

plt.pie(sizes, labels = labels, startangle = 270, autopct='%1.1f%%')
plt.title(f"Total Games: {total_games}")

# Save figure to memory
buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)

# Compose html message
msg = EmailMessage()
msg['Subject'] = 'Your Weekly Chess Update'
msg['From'] = EMAIL_ADDRESS
msg['To'] = EMAIL_ADDRESS

msg.set_content('HTML is not working for your email client')

piechart_cid = make_msgid()
msg.add_alternative(f"""\
<!DOCTYPEhtml>
<html>
    <body> 
        <h1>Your Chess Stats From Last Week</h1>
        
        <h3>Games Played</h3>
        <p>
            Total Games Played: {total_games}
            <br>
            Lichess Games Played: {len(lichess_games)}
            <br>
            Chess dot com Games Played: {len(chesscom_games)}
        </p>
        <h3>Wins, Losses and Draws</h3>
        <p>
            Wins: {total_wins}, Percentage: {100*total_wins/total_games:.2f}%
            <br>
            Losses: {total_losses}, Percentage: {100*total_losses/total_games:.2f}%
            <br>
            Draws: {total_draws}, Percentage: {100*total_draws/total_games:.2f}%
        </p>
        <h3>Rankings</h3>
        <h4>Chess dot com Rankings</h4>
        <p>
            {chessdotcom_rankingstring}
        </p>
        <h4>Lichess Rankings</h4>
        <p>
            {lichess_rankingstring}
        </p>

        <img src="cid:{piechart_cid[1:-1]}" width=200 height=200 />
    </body>
</html>
""", subtype='html')

msg.get_payload()[1].add_related(buf.read(), 'image', 'png', cid=piechart_cid)

# Send the email
with smtplib.SMTP('smtp.office365.com', 587) as smtp:
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(EMAIL_ADDRESS, EMAIL_PASS)
        smtp.send_message(msg)
    except Exception:
        print("Error: Failed to send email.")