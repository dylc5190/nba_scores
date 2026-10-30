#!/usr/bin/python3
import requests
import sys

def fetch_and_print_scores():
    ESPN_URL = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
    
    try:
        response = requests.get(ESPN_URL)
        response.raise_for_status()
        data = response.json()
        
        print(f"NBA Scores - {data.get('day', {}).get('date', 'Unknown Date')}")
        print("-" * 40)

        events = data.get('events', [])
        if not events:
            print("No games found for today.")
            return

        for event in events:
            competition = event['competitions'][0]
            competitors = competition['competitors']
            
            home_team = next((c for c in competitors if c['homeAway'] == 'home'), competitors[0])
            away_team = next((c for c in competitors if c['homeAway'] == 'away'), competitors[1])

            home_name = home_team['team']['displayName']
            away_name = away_team['team']['displayName']
            
            # Helper to safely get score as int
            def get_score(comp):
                try:
                    return int(comp.get('score', 0))
                except (ValueError, TypeError):
                    return 0

            home_score = get_score(home_team)
            away_score = get_score(away_team)
            
            status_detail = event['status']['type']['shortDetail']
            state = event['status']['type']['state'] # pre, in, post
            
            hide_score = False
            if state in ['in', 'post']:
                diff = abs(home_score - away_score)
                if diff < 4:
                    hide_score = True
            
            # Format output
            print(f"{away_name} vs {home_name}")
            print(f"Status: {status_detail}")
            
            if hide_score:
                print("Result: [HIDDEN - CLOSE GAME]")
            else:
                print(f"Score: {away_score} - {home_score}")
            
            print("-" * 40)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching scores: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)

if __name__ == "__main__":
    fetch_and_print_scores()
