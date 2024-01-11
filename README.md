# fantasy

Replace the league_id of the fantasy group in the fpl.py file,

Use the API from https://fantasy.premierleague.com/api/ to retrieve team IDs of entries within the league. Aggregate and fetch information such as points for each gameweek, transfer points, bank, and used chips.
Generate HTML-formatted tables and display them on port 19999.

```
pip3 install requests flask
python3 fpl.py
```
