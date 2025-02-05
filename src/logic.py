from util.read import *
from collections import defaultdict
from typing import Dict, Optional, DefaultDict
from typing import List, Dict, Any

def calculate_total_transfers_cost(user_id):
    total_transfers_cost = 0
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tính tổng event_transfers_cost
    for event in user_events:
        event_transfers_cost = event.get('event_transfers_cost', 0)
        total_transfers_cost += event_transfers_cost
    return total_transfers_cost

def calculate_total_points(user_id):
    total_points = 0
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tính tổng điểm
    for event in user_events:
        points = event.get('points', 0)
        event_transfers = event.get('event_transfers', 0)
        event_transfers_cost = event.get('event_transfers_cost', 0)
        # Tính tổng điểm từ các thông tin quan trọng
        total_points += points - event_transfers_cost
    return total_points

def calculate_home_away_points(user_id):
    home_points = 0
    away_points = 0
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tính điểm lượt đi và lượt về
    for event in user_events:
        event_number = event.get('event', 0)
        points = event.get('points', 0)
        event_transfers_cost = event.get('event_transfers_cost', 0)
        # Tính điểm lượt đi và lượt về
        if 1 <= event_number <= 19:
            home_points += points - event_transfers_cost
        elif 20 <= event_number <= 38:
            away_points += points - event_transfers_cost
    return home_points, away_points

def find_events_with_transfers_cost(user_id):
    event_note = ""
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tìm các sự kiện có event_transfers_cost > 0
    for event in user_events:
        event_number = event.get('event', 0)
        event_transfers_cost = event.get('event_transfers_cost', 0)
        # Ghi chú các sự kiện có event_transfers_cost > 0
        if event_transfers_cost > 0:
            if event_note:
                event_note += f",{event_number}"
            else:
                event_note = f"{event_number}"
    return event_note

def get_chip_event(user_chips, chip_name):
    if chip_name.lower() != 'wildcard':
        for chip in user_chips:
            if chip['name'].lower() == chip_name.lower():
                return chip.get('event', '')
    else:
        event_note=""
        for chip in user_chips:
            if chip['name'].lower() == chip_name.lower():
                event_number=chip.get('event', '0')
                event_note +=f"{event_number} "
        return event_note
    return ''

def last_value_bank(user_id):
    max_event = 0
    last_value = 0.0
    last_bank = 0.0
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tìm sự kiện có số lớn nhất
    for event in user_events:
        event_number = event.get('event', 0)
        value = event.get('value', 0)
        bank = event.get('bank', 0)
        if event_number > max_event:
            max_event = event_number
            last_value = value
            last_bank = bank
    return last_value/10.0, last_bank/10.0

def get_web_name_by_element_id(element_id, file_path='data/player_info.json'):
    try:
        with open(file_path, 'r') as file:
            player_info_dict = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

    return player_info_dict.get(str(element_id))

def get_web_name_by_element_id_v1(element_id, file_path='data/player_full_info.json'):
    try:
        with open(file_path, 'r') as file:
            player_info_dict = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

    # Retrieve the player's web_name
    player_info = player_info_dict.get(str(element_id))
    if player_info:
        return player_info
    return None

def get_web_name_by_element_id_v2(element_id, file_path='data/player_full_info.json'):
    try:
        with open(file_path, 'r') as file:
            player_info_dict = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

    # Retrieve the player's web_name
    player_info = player_info_dict.get(str(element_id))
    if player_info:
        return player_info.get("web_name")
    return None

def get_captain_and_vice_captain(manager_id,event):
    file_path= f'data/{manager_id}_{event}.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None, None

    picks = data.get('picks', [])

    captain_id = None
    vice_captain_id = None

    for pick in picks:
        if pick.get('is_captain'):
            captain_id = pick.get('element')
        elif pick.get('is_vice_captain'):
            vice_captain_id = pick.get('element')

    return captain_id, vice_captain_id

def calculate_all_bonus_points(file_path: str) -> Dict[int, Dict[str, Any]]:
    """
    Calculate bonus points for all fixtures and group players by fixture ID.
    Add a "running" status to indicate if the fixture has started.

    Args:
        file_path (str): Path to the JSON file containing player data.

    Returns:
        Dict[int, Dict[str, Any]]: A dictionary mapping fixture IDs to bonus points and running status.
    """
    try:
        # Load the JSON file
        with open(file_path, "r") as file:
            data = json.load(file)

        # Prepare a dictionary to store bonus points and running status grouped by fixture_id
        fixture_bonus_data = defaultdict(lambda: {"running": False, "bonus_points": {}})

        # Collect all unique fixture IDs
        fixture_ids = {explain["fixture"] for player in data["elements"] for explain in player["explain"]}

        # Process each fixture
        for fixture_id in fixture_ids:
            # Extract players participating in this fixture
            players = [
                {
                    "id": player["id"],
                    "bps": player["stats"]["bps"]
                }
                for player in data["elements"]
                if any(explain["fixture"] == fixture_id for explain in player["explain"])
            ]

            # Check if all BPS are zero
            if all(player["bps"] == 0 for player in players):
                # Set running status to False and assign 0 points to all players
                fixture_bonus_data[fixture_id]["running"] = False
                #print(f"{fixture_id} not started")
                for player in players:
                    fixture_bonus_data[fixture_id]["bonus_points"][player["id"]] = 0
            else:
                # Set running status to True
                fixture_bonus_data[fixture_id]["running"] = True
                #print(f"{fixture_id} Started")
                # Sort players by BPS in descending order
                players = sorted(players, key=lambda x: x["bps"], reverse=True)

                # Calculate bonus points based on the rules
                n = len(players)
                i = 0
                rank_bonus_points = {0: 3, 1: 2, 2: 1}  # Points for first, second, and third places

                while i < n:
                    # Get the players with the same BPS
                    tie_group = [players[i]]
                    while i + 1 < n and players[i + 1]["bps"] == players[i]["bps"]:
                        tie_group.append(players[i + 1])
                        i += 1

                    # Assign bonus points based on the tie rules
                    current_rank = len(fixture_bonus_data[fixture_id]["bonus_points"])
                    if current_rank <= 2:  # Only first, second, and third ranks get points
                        for player in tie_group:
                            fixture_bonus_data[fixture_id]["bonus_points"][player["id"]] = rank_bonus_points.get(current_rank, 0)
                    i += 1

        return fixture_bonus_data

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

def get_expected_bonus_points(file_path: str) -> DefaultDict[int, DefaultDict[int, int]]:
    """
    Calculate and store expected bonus points for all players grouped by fixture IDs.

    Args:
        file_path (str): Path to the JSON file containing player data.

    Returns:
        DefaultDict[int, DefaultDict[int, int]]: A nested dictionary where
            - The first key is the fixture ID.
            - The second key is the player ID.
            - The value is the expected bonus points for the player.
            Default value is 0 if a player or fixture doesn't exist.
    """
    try:
        # Calculate expected bonus points
        raw_bonus_data = calculate_all_bonus_points(file_path)

        # Convert to a defaultdict structure for easy access
        expected_bonus_points = defaultdict(lambda: defaultdict(int))

        for fixture_id, player_bonus in raw_bonus_data.items():
            for player_id, bonus in player_bonus.items():
                expected_bonus_points[fixture_id][player_id] = bonus

        return expected_bonus_points

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading or parsing the file: {e}")
        return defaultdict(lambda: defaultdict(int))
    

def process_user_picks(live_user_picks: List[Dict[str, Any]],active_chip) -> Dict[str, Any]:
    """
    Process 15 players to select the final 11 based on rules and calculate total points.

    Args:
        live_user_picks (List[Dict[str, Any]]): List of 15 player details.

    Returns:
        Dict[str, Any]: Processed data containing the final 11 players, substitutions, total points, and change log.
    """
    # Separate starters and substitutes
    starters = [player for player in live_user_picks if player["multiplier"] > 0]
    substitutes = [player for player in live_user_picks if player["multiplier"] == 0 ]
    bb = 0

    # Ensure exactly 11 players in starters
    if len(starters) >=15 and active_chip != "manager":
        for player in starters:
            bb += player["point"] * player["multiplier"]
        return {
            "final_11": 'BBOOST',
            "substitutions": "BBOOST",
            "total_points": bb,
            "change_log": "BBOOST",
            "bonus_log": "BBOOST",
            "live_bps_log": "BBOOST"
        }
        #raise ValueError("Initial starters must be exactly 11 players.")

    # Formation requirements
    required_formation = {
        "1": 1,  # GK
        "2": 3,  # DEF
        "3": 2,  # MID
        "4": 1,  # FWD
        "5": 0,  # MANAGER
    }
    max_formation = {   
        "1": 1,  # GK
        "2": 5,  # DEF
        "3": 5,  # MID
        "4": 3,  # FWD
        "5": 1,  # MANAGER
    }

    # Current formation count
    formation = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    for player in starters:
        formation[str(player["element_type"])] += 1

    # Ensure formation meets minimum requirements
    for key, min_count in required_formation.items():
        if formation[key] < min_count:
            raise ValueError(f"Formation error: Not enough players in position {key}.")

    # Handle captain and vice-captain logic
    total_points = 0
    captain = next((p for p in starters if p["is_captain"]), None)
    vice_captain = next((p for p in starters if p["is_vice_captain"]), None)

    if captain and captain["minutes"] == 0 and captain["running"]:
        # Apply vice-captain points if captain does not play
        if vice_captain:
            vice_captain_points = ( vice_captain["point"] - vice_captain['bonus'] + vice_captain['expected_bonus'] )* ( captain["multiplier"] - 1)
            total_points += vice_captain_points
    elif captain:
        # Apply captain points if they play
        captain_points = ( captain["point"] - captain['bonus'] + captain['expected_bonus'] ) * captain["multiplier"]
        total_points += captain_points

    # Apply points for other starters
    for player in starters:
        if not player["is_captain"]:
            total_points += ( player["point"] - player['bonus'] + player['expected_bonus']  ) * player["multiplier"]


    # Log of substitutions and changes
    change_log = []
    bonus_log = []
    live_bps_log = []

    # Identify players to replace
    to_replace = [player for player in starters if player["minutes"] == 0 and player["running"] and player["element_type"] != 5]

    # Substitute players if needed
    for sub in to_replace:
        # Remove the player from starters
        starters.remove(sub)
        formation[str(sub["element_type"])] -= 1

        # Find a suitable substitute that satisfies min/max formation requirements
        substitute_found = False
        for sub_player in substitutes:
            if (sub_player["minutes"] == 0):
                continue
            potential_formation = formation.copy()
            potential_formation[str(sub_player["element_type"])] += 1

            # Check if adding this substitute satisfies formation constraints
            valid_formation = all(
                required_formation[key] <= potential_formation[key] <= max_formation[key]
                for key in required_formation
            )

            if valid_formation:
                # Add substitute and update formation
                #sub_player["multiplier"] = sub["multiplier"]  # Use multiplier of the replaced player
                formation[str(sub_player["element_type"])] += 1
                substitutes.remove(sub_player)
                total_points = total_points + sub_player["point"] - sub_player['bonus'] + sub_player['expected_bonus'] 

                # Log the substitution
                change_log.append(
                    f"{sub['web_name']} <== {sub_player['web_name']}"
                )
                substitute_found = True
                break

        # If no substitute is found, log an error
        if not substitute_found:
            starters.append(sub)
            formation[str(sub["element_type"])] += 1            
            change_log.append(
                f"{sub['web_name']} (NotSub)"
            )
    # Apply points for other starters
    for p in live_user_picks:
        if  p["bonus"] > 0:
            bonus_log.append(
                f"{p['web_name']}: {p['bonus']}"
            )
        if  p["expected_bonus"] > 0 and p["expected_bonus"] != p["bonus"]:
            live_bps_log.append(
                f"{p['web_name']}: {p['expected_bonus']}"
            )

    # Ensure final formation still meets minimum requirements
    for key, min_count in required_formation.items():
        if formation[key] < min_count:
            raise ValueError(f"Formation error after substitution: Not enough players in position {key}.")
    return {
        "final_11": starters,
        "substitutions": to_replace,
        "total_points": total_points,
        "change_log": "<br>".join(change_log),
        "bonus_log": "<br>".join(bonus_log),
        "live_bps_log": "<br>".join(live_bps_log)
    }
