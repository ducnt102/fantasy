## cache api to file
import requests
import json
from html.render import *
from src.logic import *

def get_league_name(league_id):
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    # Gửi yêu cầu GET đến API
    response = requests.get(url)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        data = response.json()
        # Kiểm tra xem dữ liệu có chứa thông tin standings không
        if 'league' in data:
            league_info = data['league']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'name' in league_info:
                name = league_info['name']
                return name
    else:
        print(f"Yêu cầu không thành công cho id {league_id}. Status code:", response.status_code)    
        return None

def generate_json_data_daily(league_id):
    save_all_players_to_file()
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    # Gửi yêu cầu GET đến API
    response = requests.get(url)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        data = response.json()
        with open("data/league_id.json", "w") as file:
            json.dump(data, file)
        # Kiểm tra xem dữ liệu có chứa thông tin standings không
        if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                if results:
                    for result in results:
                        user_id = result['entry']
                        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"
                        # Gửi yêu cầu GET đến API
                        response = requests.get(url)
                        # Kiểm tra xem yêu cầu có thành công không (status code 200)
                        if response.status_code == 200:
                          # Lấy dữ liệu JSON từ phản hồi
                          user_data = response.json()
                          # Lưu dữ liệu vào tệp JSON
                          with open(f"data/{user_id}.json", "w") as file:
                            json.dump(user_data, file)
                          user_events = get_user_events_x(user_id)
                          last_event = user_events[-1] if user_events else None
                          get_user_picks_file(user_id,last_event['event'])
                          get_events_file(last_event['event'])
                          print(f"Daily: Dữ liệu cho user_id {user_id},event {last_event['event']} đã được lưu vào file json")
                else:
                    print(f"Daily: Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)

def generate_json_data_hourly(league_id):
    #save_all_players_to_filed()
    current_event_id, finished_status = get_current_event()
    if finished_status == True:
        print(f"HOURLY ====> GW {current_event_id} is FINISHED!!!!!!!!!!!")
        return
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    # Gửi yêu cầu GET đến API
    response = requests.get(url)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        data = response.json()
        #with open("data/league_id.json", "w") as file:
        #    json.dump(data, file)
        # Kiểm tra xem dữ liệu có chứa thông tin standings không
        if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                if results:
                    for result in results:
                        user_id = result['entry']
                        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"
                        # Gửi yêu cầu GET đến API
                        response = requests.get(url)
                        # Kiểm tra xem yêu cầu có thành công không (status code 200)
                        if response.status_code == 200:
                          # Lấy dữ liệu JSON từ phản hồi
                          user_data = response.json()
                          # Lưu dữ liệu vào tệp JSON
                          with open(f"data/{user_id}.json", "w") as file:
                            json.dump(user_data, file)
                          user_events = get_user_events_x(user_id)
                          last_event = user_events[-1] if user_events else None
                        get_user_picks_file_live(user_id,last_event['event'])
                        get_events_file_live(last_event['event'])
                        print(f"GW {current_event_id} not finish, live update : Dữ liệu cho user_id {user_id}, event {last_event['event']} đã được lưu vào file json")
                else:
                    print(f"Hourly: Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)

def generate_json_data_live(league_id):
    # using to update <user_id>.json and <userid>_<current_event_id>.json to live
    current_event_id, finished_status = get_current_event()
    if finished_status == True:
        print(f"LIVE ====> GW {current_event_id} is FINISHED!!!!!!!!!!!")
        return
    get_events_file_live(current_event_id)
    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"
    # Gửi yêu cầu GET đến API
    response = requests.get(url)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        data = response.json()
        #with open("data/league_id.json", "w") as file:
        #    json.dump(data, file)
        # Kiểm tra xem dữ liệu có chứa thông tin standings không
        if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                if results:
                    for result in results:
                        user_id = result['entry']
                        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"
                        # Gửi yêu cầu GET đến API
                        response = requests.get(url)
                        # Kiểm tra xem yêu cầu có thành công không (status code 200)
                        if response.status_code == 200:
                          # Lấy dữ liệu JSON từ phản hồi
                          user_data = response.json()
                          # Lưu dữ liệu vào tệp JSON
                          with open(f"data/{user_id}.json", "w") as file:
                            json.dump(user_data, file)
                          #user_events = get_user_events_x(user_id) # not need , replace  current_event_id
                          #last_event = user_events[-1] if user_events else None
                          get_user_picks_file_live(user_id,current_event_id)
                          print(f"Event live: Dữ liệu cho user_id {user_id}, event {current_event_id} đã được lưu vào file json")
                else:
                    print(f"Event live: Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)

def get_user_events_x(user_id):
    user_events = []
    url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"
    # Gửi yêu cầu GET đến API
    response = requests.get(url)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        user_data = response.json()
        # Kiểm tra và lấy thông tin sự kiện của người dùng
        if 'current' in user_data:
            user_events = user_data['current']
    else:
        print(f"Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)
    return user_events

def get_events_file(gw_id):
    # get events_file old
    for event in range(1, int(gw_id)):
        file_name = f"data/events_{event}.json"
        url = f"https://fantasy.premierleague.com/api/event/{event}/live/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(file_name, "w") as file:
                json.dump(data, file)
        else:
            print(f"Yêu cầu không thành công cho event {event}. Status code:", response.status_code)
            return None

def get_events_file_live(event):
        file_name = f"data/events_{event}.json"
        url = f"https://fantasy.premierleague.com/api/event/{event}/live/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(file_name, "w") as file:
                json.dump(data, file)
        else:
            print(f"Yêu cầu không thành công cho event {event}. Status code:", response.status_code)
            return None

def get_user_picks_file(user_id, event):
    for gw_id in range(1, int(event)):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw_id}/picks/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(f"data/{user_id}_{gw_id}.json", "w") as file:
                json.dump(data, file)
        else:
            print(f"Yêu cầu không thành công cho user_id {user_id}, event {gw_id}. Status code:", response.status_code)

def get_user_picks_file_live(user_id, event):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{event}/picks/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(f"data/{user_id}_{event}.json", "w") as file:
                json.dump(data, file)
        else:
            print(f"Yêu cầu không thành công cho user_id {user_id}, event {event}. Status code:", response.status_code)

def save_all_players_to_file(file_path='data/player_info.json'):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        elements = data.get('elements', [])
        
        player_info_dict = {player.get('id'): player.get('web_name') for player in elements}

        with open(file_path, 'w') as file:
            json.dump(player_info_dict, file, indent=4)

        print(f"All player info saved successfully to {file_path}.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def get_current_event(api_url="https://fantasy.premierleague.com/api/bootstrap-static/"):
    """
    Fetch the current event ID and its 'finished' status from the FPL API.

    Args:
        api_url (str): The API endpoint to fetch data from.

    Returns:
        tuple: (current_event_id, finished_status) if found, otherwise None.
    """
    try:
        # Fetch data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for failed requests
        
        # Parse JSON
        data = response.json()
        events = data.get("events", [])
        
        # Find the current event
        for event in events:
            if event.get("is_current", False):
                return event["id"], event["finished"]
        
        # No current event found
        return None, None
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None

# Example usage
#current_event_id, finished_status = get_current_event()


def render_old_gw_to_file(league_id):
  try:
    print("RENDER ALL HTML FILE================================>")
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    current_event_id, finished_status = get_current_event()
    for gw_id in range(1, current_event_id+1):
        #print(f"RENDER ALL HTML FILE================================> {gw_id}")
        user_info = []
        if 'standings' in data:
            standings_info = data['standings']
            if 'results' in standings_info:
                results = standings_info['results']
                if results:
                    for result in results:
                        user_id = result['entry']
                        user_events = get_user_events_x(user_id)
                        event_selected = user_events[gw_id-1] if user_events else None
                        last_event = user_events[-1] if user_events else None
                        if event_selected:
                            player_name = result.get('player_name', '')
                            entry_name = result.get('entry_name', '')
                            total_points = calculate_total_points(user_id)
                            last_event_transfers_cost = event_selected.get('event_transfers_cost', 0)
                            last_event_points = event_selected.get('points', 0) - last_event_transfers_cost 
                            event_transfers = event_selected.get('event_transfers', 0)
                            # Sử dụng hàm get_user_picks để lấy thông tin về các lựa chọn
                            user_picks = get_user_picks(user_id, event_selected['event'])
                            captain, vice_captain = get_captain_and_vice_captain(user_id, event_selected['event'])
                            captain_name = get_web_name_by_element_id(captain)
                            captain_point = get_live_element_id(event_selected['event'],captain) 
                            vice_point = get_live_element_id(event_selected['event'],vice_captain)
                            vice_name = get_web_name_by_element_id(vice_captain)
                            active_chip= get_active_chip(user_id, last_event['event'])
                            active_chip= get_active_chip(user_id, event_selected['event'])
                            if user_picks:
                                # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                                total_goals_scored, total_assists, event_points  = get_live_player_stats(event_selected['event'], user_picks)
                                user_info.append({
                                    'user_id': user_id,
                                    'player_name': player_name,
                                    'entry_name': entry_name,
                                    'total_points': total_points,
                                    'last_event_points': last_event_points,
                                    'last_event_transfers_cost': last_event_transfers_cost,
                                    'user_picks': user_picks,
                                    'total_goals_scored': total_goals_scored,
                                    'total_assists': total_assists,
                                    'active_chip': active_chip,
                                    'event_transfers': event_transfers,
                                    'captain_name': captain_name,
                                    'vice_name': vice_name,
                                    'captain_point': captain_point                                
                                })
                    # Sắp xếp theo điểm của sự kiện cuối cùng từ cao đến thấp
                    #user_info.sort(key=lambda x: x['last_event_points'], reverse=True)
                    user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']), reverse=True)
                    output_file = 'data/' + 'gw_' + str(gw_id) + '.html'
                    with open(output_file, "w") as file:
                        file.write(render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event']))
        #return render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event'])
  except Exception as e:
    print(e)

def render_live_gw_to_file(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    current_event_id, finished_status = get_current_event()
    if finished_status == True:
        print(f"GW {gw_id} HAS FINISHED ===========================>")
        return
    gw_id = current_event_id + 1
    print(f"RENDER LIVE HTML FILE================================> {gw_id}")
    user_info = []
    if 'standings' in data:
        standings_info = data['standings']
        if 'results' in standings_info:
            results = standings_info['results']
            if results:
                for result in results:
                    user_id = result['entry']
                    user_events = get_user_events_x(user_id)
                    event_selected = user_events[gw_id-1] if user_events else None
                    last_event = user_events[-1] if user_events else None
                    if event_selected:
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        total_points = calculate_total_points(user_id)
                        last_event_transfers_cost = event_selected.get('event_transfers_cost', 0)
                        last_event_points = event_selected.get('points', 0) - last_event_transfers_cost 
                        event_transfers = event_selected.get('event_transfers', 0)
                        # Sử dụng hàm get_user_picks để lấy thông tin về các lựa chọn
                        user_picks = get_user_picks(user_id, event_selected['event'])
                        captain, vice_captain = get_captain_and_vice_captain(user_id, event_selected['event'])
                        captain_name = get_web_name_by_element_id(captain)
                        captain_point = get_live_element_id(event_selected['event'],captain) 
                        vice_point = get_live_element_id(event_selected['event'],vice_captain)
                        vice_name = get_web_name_by_element_id(vice_captain)
                        active_chip= get_active_chip(user_id, last_event['event'])
                        active_chip= get_active_chip(user_id, event_selected['event'])
                        if user_picks:
                            # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                            total_goals_scored, total_assists, event_points  = get_live_player_stats(event_selected['event'], user_picks)
                            user_info.append({
                                'user_id': user_id,
                                'player_name': player_name,
                                'entry_name': entry_name,
                                'total_points': total_points,
                                'last_event_points': last_event_points,
                                'last_event_transfers_cost': last_event_transfers_cost,
                                'user_picks': user_picks,
                                'total_goals_scored': total_goals_scored,
                                'total_assists': total_assists,
                                'active_chip': active_chip,
                                'event_transfers': event_transfers,
                                'captain_name': captain_name,
                                'vice_name': vice_name,
                                'captain_point': captain_point                                
                            })
                # Sắp xếp theo điểm của sự kiện cuối cùng từ cao đến thấp
                #user_info.sort(key=lambda x: x['last_event_points'], reverse=True)
                user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']), reverse=True)
                output_file = 'data/' + 'gw_' + str(gw_id) + '.html'
                with open(output_file, "w") as file:
                    file.write(render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event']))
    #return render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event'])
  except Exception as e:
    print(e)

