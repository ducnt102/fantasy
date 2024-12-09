import json
from typing import List, Dict, Any

# Hàm để lấy dữ liệu từ tệp JSON về chip của người dùng
def get_user_chips(user_id):
    with open(f"data/{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'chips' in user_data:
        return user_data['chips']
    return []

def get_active_chip(user_id, event):
    file_name = f"data/{user_id}_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
    if 'active_chip' in data:
        chip = data['active_chip']
        return chip
    else:
        print(f"Yêu cầu get chip không thành công cho {user_id} event {event}")
        return None

def get_live_player_stats(event, user_picks):
    file_name = f"data/events_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
        # Khởi tạo biến để lưu tổng số goals_scored và assists
    if data:
        total_goals_scored = 0
        total_assists = 0
        live_user_points = 0
        # Duyệt qua từng lựa chọn của người chơi
        for user_pick in user_picks['picks']:
            element_id = user_pick['element']
            multiplier = user_pick['multiplier']
            # Kiểm tra điều kiện multiplier !=0
            if multiplier == 1 or multiplier == 2 or multiplier == 3:
                # Tìm thông tin về cầu thủ trong response của API
                for player_info in data['elements']:
                    if player_info['id'] == element_id:
                        # Cộng dồn goals_scored và assists
                        total_goals_scored += player_info['stats']['goals_scored']
                        total_assists += player_info['stats']['assists']
                        live_user_points += player_info['stats']['total_points'] * int(multiplier)
                        break
        # Trả về tổng số goals_scored và assists
        return total_goals_scored, total_assists, live_user_points
    else:
        print(f"Yêu cầu không thành công cho event {event}")
        return None

def get_pick_live_players_v2(
    event: int, 
    user_picks: Dict[str, Any], 
    all_bonus_points: Dict[int, Dict[int, float]], 
    player_info_path: str = "data/player_full_info.json"
) -> List[Dict[str, Any]]:
    """
    Retrieve detailed information about 15 players in user picks.

    Args:
        event (int): The event ID.
        user_picks (dict): User's picks containing player IDs and multipliers.
        all_bonus_points (dict): A dictionary containing expected bonus points.
        player_info_path (str): Path to the player information JSON file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing player details.
    """
    file_name = f"data/events_{str(event)}.json"
    try:
        # Load event data
        with open(file_name, "r") as event_file:
            event_data = json.load(event_file)

        # Load player info data
        with open(player_info_path, "r") as player_file:
            player_info_dict = json.load(player_file)

        players_info = []

        # Process each pick
        for user_pick in user_picks['picks']:
            element_id = user_pick['element']
            multiplier = user_pick['multiplier']
            is_captain = user_pick['is_captain']
            is_vice_captain = user_pick['is_vice_captain']
            position = user_pick['position']

            # Default values if the player data is not found
            player_details = {
                "ID": element_id,
                "web_name": player_info_dict.get(str(element_id), {}).get("web_name", "Unknown"),
                "point": 0,
                "bonus": 0,
                "expected_bonus": 0,
                "element_type": player_info_dict.get(str(element_id), {}).get("element_type", "Unknown"),
                "minutes": 0,
                "multiplier": multiplier,
                "is_captain": is_captain,
                "is_vice_captain": is_vice_captain,
                "running": False,
                "position": position,
                "fixture": 0
            }

            # Find the player in the event data
            for player in event_data.get('elements', []):
                if player['id'] == element_id:
                    player_details["point"] = player['stats']['total_points']
                    player_details["bonus"] = player['stats']['bonus']
                    player_details["minutes"] = player['stats']['minutes']
                    try:
                        # Safely access the explain array
                        explain_data = player.get('explain', [])
                        if explain_data:
                            # Extract the first fixture ID (if multiple, select the first occurrence)
                            player_details["fixture"] = explain_data[0].get('fixture', '0')
                        else:
                            player_details["fixture"] = '0'
                            player_details["minutes"] = 0
                            player_details["running"] = True
                            player_details["expected_bonus"] = 0
                            break
                    except Exception as e:
                        print(f"Error extracting fixture for player {element_id}: {e}")
                        player_details["fixture"] = '0'
                    try:
                        #chi co 3 player co bonus
                        player_details["expected_bonus"] = all_bonus_points[player_details["fixture"]]["bonus_points"][element_id]
                    except Exception as e:
                        player_details["expected_bonus"] = 0
                    player_details["running"] = all_bonus_points[player_details["fixture"]]["running"]
                    break
            players_info.append(player_details)

        return players_info

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []


def get_user_picks(user_id, event):
    with open(f"data/{user_id}_{event}.json", "r") as file:
        data = json.load(file)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if data:
        # Lấy dữ liệu JSON từ phản hồi
        #data = response.json()
        return data
    else:
        print(f"Yêu cầu không thành công cho user_id {user_id}, event {event}")
        return None

def get_user_events(user_id):
    with open(f"data/{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'current' in user_data:
        return user_data['current']
    return []

def get_live_element_id(event, element_id):
    file_name = f"data/events_{str(event)}.json"
    total_point = 0
    with open(file_name, "r") as file:
        data = json.load(file)        
    if data:
        for player_info in data['elements']:
                    if player_info['id'] == element_id:
                        # Cộng dồn goals_scored và assists
                        total_point = player_info['stats']['total_points']
                        break
        # Trả về tổng số goals_scored và assists
        return total_point
    else:
        print(f"Yêu cầu không thành công cho event {event}")
        return None
