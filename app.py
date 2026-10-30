from flask import Flask, render_template
import requests
from datetime import datetime

app = Flask(__name__)

ESPN_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

@app.route('/')
def index():
    try:
        response = requests.get(ESPN_URL)
        data = response.json()
        games = []

        for event in data.get('events', []):
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            # Sort competitors: home usually last in list, but let's check homeAway
            home_team = next((c for c in competitors if c['homeAway'] == 'home'), competitors[0])
            away_team = next((c for c in competitors if c['homeAway'] == 'away'), competitors[1])

            status = event['status']['type']['state'] # pre, in, post
            status_detail = event['status']['type']['shortDetail']
            
            game_info = {
                'home_team': home_team['team']['displayName'],
                'away_team': away_team['team']['displayName'],
                'home_score': int(home_team.get('score', 0)),
                'away_score': int(away_team.get('score', 0)),
                'status': status_detail,
                'is_active': status == 'in',
                'is_completed': status == 'post',
                'hide_score': False,
                'winner': None
            }

            # Logic to hide scores
            if status in ['in', 'post']:
                diff = abs(game_info['home_score'] - game_info['away_score'])
                if diff < 4:
                    game_info['hide_score'] = True
                    # Generate YouTube search URL
                    query = f"{game_info['away_team']} vs {game_info['home_team']} nba game"
                    # Simple URL encoding by replacing spaces with +
                    encoded_query = query.replace(' ', '+')
                    game_info['youtube_url'] = f"https://www.youtube.com/results?search_query={encoded_query}"

            if status == 'post' and not game_info['hide_score']:
                if game_info['home_score'] > game_info['away_score']:
                    game_info['winner'] = 'home'
                elif game_info['away_score'] > game_info['home_score']:
                    game_info['winner'] = 'away'

            games.append(game_info)

        return render_template('index.html', games=games)
    except Exception as e:
        return f"Error fetching scores: {e}"

if __name__ == '__main__':
    app.run(debug=True, port=5001)
