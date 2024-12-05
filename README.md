# fantasy for test

Replace the league_id of the fantasy group in the main.py file,

Use the API from https://fantasy.premierleague.com/api/ to retrieve team IDs of entries within the league. Aggregate and fetch information such as points for each gameweek, transfer points, bank, and used chips.
Generate HTML-formatted tables and display them on port 19999.

```
pip3 install requests flask
python3 main.py
```

**Sample:**

http://fantasy.io.vn/


# DATA JSON
## data/league.json
    Stores all football managers in your league.
## data/player_info.json
    Stores all football player information.
## data/events_<GW>.json
    Stores all events for the specified Gameweek (GW).
## data/<userid>.json
    Stores the scores of a user from GW 1 to the current Gameweek.
## data/<userid>_<GW>.json
    Stores all football players selected by the user for the specified Gameweek.
## data/html_<GW>.json
    Caches all HTML tables for your league for the specified Gameweek.

# Update
    job auto update json data file and update HTML



