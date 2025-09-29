## cache api to file
import requests
import json
from html.render import *
from src.logic import *
import time
from datetime import datetime, timedelta, timezone
from datetime import datetime
from typing import List
import os, json
from typing import Dict, Any, List, Tuple


_SESSION = requests.Session()
_SESSION.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; FPLTools/1.0)",
    "Accept": "application/json",
})

BOOTSTRAP_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"

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
    print(f"DAILY JOB: ======================================================>")
    save_all_players_to_file()
    save_all_players_full_to_file()
    save_fixtures_to_file()
    save_bootstrap_to_file()    
    current_event_id, finished_status = get_current_event()
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
                          get_user_picks_file(user_id,current_event_id)
                    get_events_file(current_event_id)
    else:
        print(f"DAILY JOB: ======================================================> ERROR Status code:", response.status_code)
    render_home_to_file(league_id)
    render_away_to_file(league_id)
    render_total_to_file(league_id)
    render_old_gw_to_file(league_id)
    render_months_until_now(league_id)

def generate_json_data_hourly(league_id):
    print(f"HOURLY JOB: ======================================================>")    
    save_fixtures_to_file()
    save_bootstrap_to_file()
    current_event_id, finished_status = get_current_event()
    running = check_fixtures_match_running_v2(current_event_id,8,2)
    if running == False:
        print(f"HOURLY JOB ====> GW {current_event_id} running={running} ====> DO NOTHING !!!!!!!!!!!")
        return
    print(f"HOURLY JOB START ====> GW {current_event_id} ======================================================>")
    get_events_file_live(current_event_id)
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
                        get_user_picks_file_live(user_id,last_event['event'])
    else:
        print(f"HOURLY JOB: ======================================================> ERROR Status code:", response.status_code)
    render_live_gw_to_file_v2(league_id)
    render_live_gw_to_file(league_id)
    render_months_until_now(league_id)
    

def generate_json_data_live(league_id):
    # using to update events_<gw>.json to live
    current_event_id, finished_status = get_current_event()
    running = check_fixtures_match_running_v2(current_event_id,24,24)
    if running == False:
        print(f"LIVE JOB ====> GW {current_event_id} running={running} ====> DO NOTHING !!!!!!!!!!!")
        return
    print(f"LIVE JOB START ====> GW {current_event_id} ==========================================>")
    get_events_file_live(current_event_id)
    render_live_gw_to_file_v2(league_id)


def _event_placeholder(ev: int) -> dict:
    """Fake record đủ schema của /entry/{id}/history/ cho 1 event, mọi số liệu = 0/None."""
    return {
        "event": ev,
        "points": 0,
        "total_points": 0,
        "rank": 0,
        "rank_sort": 0,
        "overall_rank": 0,
        "percentile_rank": 0,
        "bank": 0,
        "value": 0,
        "event_transfers": 0,
        "event_transfers_cost": 0,
        "points_on_bench": 0,
    }


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
            print(f"EVENT FILES ==> event_{event}.json")
        else:
            print(f"ERROR API CALL /event/{event}/live/ Status code:", response.status_code)
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
            print(f"EVENT FILES ==> event_{event}.json")
        else:
            print(f"ERROR API CALL /event/{event}/live/ Status code:", response.status_code)
            return None

def _placeholder_picks(entry_id, gw_id):
    """
    Fake dữ liệu picks đầy đủ khi API trả 404 hoặc không có data.
    Tất cả giá trị = 0 hoặc None, nhưng đủ schema để renderer không lỗi.
    """
    return {
        "active_chip": None,
        "automatic_subs": [],
        "entry_history": {
            "event": gw_id,
            "points": 0,
            "total_points": 0,
            "rank": 0,
            "rank_sort": 0,
            "overall_rank": 0,
            "percentile_rank": 0,
            "bank": 0,
            "value": 0,
            "event_transfers": 0,
            "event_transfers_cost": 0,
            "points_on_bench": 0
        },
        "picks": []
    }

def get_user_picks_file(user_id, event):
    for gw_id in range(1, int(event)):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw_id}/picks/"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
            elif response.status_code == 404:
                # User chưa có dữ liệu ở GW này -> ghi placeholder
                data = _placeholder_picks(user_id, gw_id)
                print(f"[INFO] 404 for {user_id} GW{gw_id} -> write placeholder")
            else:
                print(f"[WARN] Picks {user_id} GW{gw_id} status={response.status_code} -> write placeholder")
                data = _placeholder_picks(user_id, gw_id)
        except Exception as e:
            print(f"[ERROR] Picks {user_id} GW{gw_id}: {e} -> write placeholder")
            data = _placeholder_picks(user_id, gw_id)

        with open(f"data/{user_id}_{gw_id}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)
        print(f"USER_PICKS FILES ==> {user_id}_{gw_id}.json")

def _get_user_picks_file(user_id, event):
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
            print(f"USER_PICKS FILES ==> {user_id}_{gw_id}.json")
        else:
            print(f"YERROR API CALL user_id /entry/{user_id}/event/{gw_id}/picks/. Status code:", response.status_code)

def get_user_picks_file_live(user_id, event):
    url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{event}/picks/"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 404:
            data = _placeholder_picks(user_id, event)
            print(f"[INFO] 404 LIVE for {user_id} GW{event} -> write placeholder")
        else:
            print(f"[WARN] LIVE Picks {user_id} GW{event} status={response.status_code} -> write placeholder")
            data = _placeholder_picks(user_id, event)
    except Exception as e:
        print(f"[ERROR] LIVE Picks {user_id} GW{event}: {e} -> write placeholder")
        data = _placeholder_picks(user_id, event)

    with open(f"data/{user_id}_{event}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)
    print(f"USER_PICKS FILES ==> {user_id}_{event}.json")
    
def _get_user_picks_file_live(user_id, event):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{event}/picks/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(f"data/{user_id}_{event}.json", "w") as file:
                json.dump(data, file)
            print(f"USER_PICKS FILES ==> {user_id}_{event}.json")
        else:
            print(f"YERROR API CALL user_id /entry/{user_id}/event/{event}/picks/. Status code:", response.status_code)

def save_all_players_full_to_file(file_path='data/player_full_info.json'):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    player_info = {}
    if response.status_code == 200:
        data = response.json()
        elements = data.get('elements', [])
        player_info_dict = {player.get('id'): player.get('web_name') for player in elements}
        for player in elements:
            player_info[player["id"]] = {
                "web_name": player["web_name"],
                "team": player["team"],
                "element_type": player["element_type"]
            }
    with open(file_path, "w") as file:
        json.dump(player_info, file, indent=4)
    print(f"Player info saved to {file_path}.")

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

def save_fixtures_to_file(file_path='data/fixtures.json'):
    url = 'https://fantasy.premierleague.com/api/fixtures/'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)

        print(f"All fixtures info saved successfully to {file_path}.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def save_bootstrap_to_file(api_url="https://fantasy.premierleague.com/api/bootstrap-static/",file_path='data/bootstrap-static.json'):
    try:
        # Fetch data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for failed requests
        if response.status_code == 200:
            data = response.json()
            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            print(f"All fixtures info saved successfully to {file_path}.")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None    

def get_current_event(file_path='data/bootstrap-static.json'):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)        # Fetch data from the API
        events = data.get("events", [])
        for event in events:
            if event.get("is_current", False):
                return event["id"], event["finished"]
        # No current event found
        return None, None
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None, None

def render_old_gw_to_file(league_id):
    try:
        with open("data/league_id.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        current_event_id, finished_status = get_current_event()

        for gw_id in range(1, current_event_id + 1):
            print(f"RENDER OLD HTML FILE ================================> data/gw_{gw_id}.html")
            user_info = []

            if 'standings' in data:
                standings_info = data['standings']
                if 'results' in standings_info:
                    results = standings_info['results']
                    if results:
                        for result in results:
                            user_id = result['entry']

                            # Lấy lịch sử user (API /entry/{user_id}/history/)
                            user_events = get_user_events_x(user_id) or []
                            # Dựng map theo event để tránh lệch khi thiếu GW đầu
                            events_by_event = {e.get('event'): e for e in user_events if isinstance(e, dict)}

                            # Chọn record của GW cần render; nếu thiếu → placeholder 0
                            event_selected = events_by_event.get(gw_id, _event_placeholder(gw_id))

                            # Xác định "last_event" thực sự có data (max event có trong map), fallback = gw_id
                            last_event_num = max(events_by_event.keys(), default=gw_id)
                            last_event = events_by_event.get(last_event_num, _event_placeholder(last_event_num))

                            print(f"RENDER {user_id} OLD HTML FILE ================================> ev{gw_id}/{event_selected.get('event')}")

                            player_name = result.get('player_name', '')
                            entry_name  = result.get('entry_name',  '')

                            # Tổng điểm toàn mùa theo logic sẵn có
                            total_points = calculate_total_points(user_id)

                            # Điểm sự kiện đã trừ hit
                            last_event_transfers_cost = event_selected.get('event_transfers_cost', 0) or 0
                            last_event_points_raw     = event_selected.get('points', 0) or 0
                            last_event_points         = last_event_points_raw - last_event_transfers_cost

                            event_transfers = event_selected.get('event_transfers', 0) or 0

                            # Lấy picks cho đúng event (có thể là placeholder nếu bạn đã vá 404 → ghi file đầy đủ)
                            user_picks = get_user_picks(user_id, event_selected['event'])

                            # Captain / vice + điểm live (các hàm này nên tự chống null/0)
                            captain, vice_captain = get_captain_and_vice_captain(user_id, event_selected['event'])
                            captain_name = get_web_name_by_element_id(captain) if captain else ""
                            vice_name    = get_web_name_by_element_id(vice_captain) if vice_captain else ""
                            captain_point = get_live_element_id(event_selected['event'], captain) if captain else 0
                            vice_point    = get_live_element_id(event_selected['event'], vice_captain) if vice_captain else 0

                            # Active chip theo đúng event đang render
                            active_chip = get_active_chip(user_id, event_selected['event'])

                            if user_picks is not None:
                                total_goals_scored, total_assists, event_points = get_live_player_stats(
                                    event_selected['event'], user_picks
                                )

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

                        # Giữ nguyên tiêu chí sort hiện tại
                        user_info.sort(
                            key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']),
                            reverse=True
                        )

                        output_file = f"data/gw_{gw_id}.html"
                        text_html = render_live_info(
                            user_info,
                            get_league_name(league_id),
                            event_selected['event'],
                            last_event['event']
                        )
                        with open(output_file, "w", encoding="utf-8") as f:
                            f.write(text_html)

    except Exception as e:
        print(e)


def render_live_gw_to_file(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    current_event_id, finished_status = get_current_event()
    gw_id = current_event_id
    print(f"RENDER OLD HTML FILE ================================> data/gw_{gw_id}.html")
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
                text_html = render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event'])
                with open(output_file, "w") as file:
                    file.write(text_html)
  except Exception as e:
    print(e)

def check_fixtures_match_running(gw_id):
    """
    Reads a JSON file and checks if any event satisfies the following conditions:
    - event == gw_id
    - finished == False
    - started == True

    Args:
    - gw_id (int): The Gameweek ID to check.

    Returns:
    - bool: True if conditions are met, False otherwise.
    """
    try:
        file_path = "data/fixtures.json"
        with open(file_path, "r") as file:
            data = json.load(file)  # Load JSON data

            for event in data:  # Iterate through the list of events
                if (
                    event.get("event") == gw_id and
                    event.get("finished") is False and
                    event.get("started") is True
                ):
                    return True  # Return True if all conditions are met

        return False  # Return False if no matching event is found

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading the file: {e}")
        return False
def check_fixtures_match_running_v2(gw_id,b,a):
    """
    Reads a JSON file and checks if any events have a kickoff time where the current time falls within:
    - kickoff_time - 1 hour to kickoff_time + 3 hours.

    Args:
    - gw_id (int): The Gameweek ID to check.

    Returns:
    - list: A list of kickoff times where the current time is within the specified range.
    """
    try:
        file_path = "data/fixtures.json"
        with open(file_path, "r") as file:
            data = json.load(file)  # Load JSON data

        current_time = datetime.now(timezone.utc)
        matching_kickoff_times = []

        for event in data:
            if event.get("event") == gw_id:  # Check the event ID matches the GW ID
                kickoff_time_str = event.get("kickoff_time")
                if kickoff_time_str:
                    kickoff_time = datetime.fromisoformat(kickoff_time_str.replace("Z", "+00:00"))
                    # Check if current_time is within the range
                    if ( kickoff_time >= current_time - timedelta(hours=b)) and (kickoff_time <= current_time + timedelta(hours=a)):
                        return True
        return False  # Return list of matching kickoff times

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error reading the file: {e}")
        return False
    
def render_away_to_file(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    user_info = []
    # Kiểm tra xem dữ liệu có chứa thông tin standings không
    if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                # Kiểm tra xem danh sách kết quả có rỗng không
                if results:
                    for result in results:
                        user_id = result['entry']
                        total_points = calculate_total_points(user_id)
                        home_points, away_points = calculate_home_away_points(user_id)
                        last_value, last_bank = last_value_bank(user_id)
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        event_note = find_events_with_transfers_cost(user_id)
                        total_transfers_cost = calculate_total_transfers_cost(user_id)
                        user_chips = get_user_chips(user_id)
                        wildcard_event = get_chip_event(user_chips, 'wildcard')
                        bboost_event = get_chip_event(user_chips, 'bboost')
                        cxc_event = get_chip_event(user_chips, '3xc')
                        freehit_event = get_chip_event(user_chips, 'freehit')
                        # Thêm thông tin người dùng vào danh sách
                        user_info.append({
                            'user_id': user_id,
                            'total_points': total_points,
                            'home_points': home_points,
                            'away_points': away_points,
                            'player_name': player_name,
                            'entry_name': entry_name,
                            'event_note': event_note,
                            'total_transfers_cost': total_transfers_cost,
                            'wildcard_event': wildcard_event,
                            'bboost_event': bboost_event,
                            'cxc_event': cxc_event,
                            'last_value': last_value,
                            'last_bank' : last_bank,
                            'freehit_event': freehit_event
                        })
                    # Sắp xếp theo tổng điểm từ cao đến thấp
                    user_info.sort(key=lambda x: x['away_points'], reverse=True)
                    output_file = 'data/away.html'
                    with open(output_file, "w") as file:
                        file.write(render_user_info(user_info,get_league_name(league_id)))
  except Exception as e:
    print(e)

def render_home_to_file(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    user_info = []
    # Kiểm tra xem dữ liệu có chứa thông tin standings không
    if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                # Kiểm tra xem danh sách kết quả có rỗng không
                if results:
                    for result in results:
                        user_id = result['entry']
                        total_points = calculate_total_points(user_id)
                        home_points, away_points = calculate_home_away_points(user_id)
                        last_value, last_bank = last_value_bank(user_id)
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        event_note = find_events_with_transfers_cost(user_id)
                        total_transfers_cost = calculate_total_transfers_cost(user_id)
                        user_chips = get_user_chips(user_id)
                        wildcard_event = get_chip_event(user_chips, 'wildcard')
                        bboost_event = get_chip_event(user_chips, 'bboost')
                        cxc_event = get_chip_event(user_chips, '3xc')
                        freehit_event = get_chip_event(user_chips, 'freehit')
                        # Thêm thông tin người dùng vào danh sách
                        user_info.append({
                            'user_id': user_id,
                            'total_points': total_points,
                            'home_points': home_points,
                            'away_points': away_points,
                            'player_name': player_name,
                            'entry_name': entry_name,
                            'event_note': event_note,
                            'total_transfers_cost': total_transfers_cost,
                            'wildcard_event': wildcard_event,
                            'bboost_event': bboost_event,
                            'cxc_event': cxc_event,
                            'last_value': last_value,
                            'last_bank' : last_bank,
                            'freehit_event': freehit_event
                        })
                    # Sắp xếp theo tổng điểm từ cao đến thấp
                    user_info.sort(key=lambda x: x['home_points'], reverse=True)
                    output_file = 'data/home.html'
                    with open(output_file, "w") as file:
                        file.write(render_user_info(user_info,get_league_name(league_id)))
  except Exception as e:
    print(e)

def render_total_to_file(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    user_info = []
    # Kiểm tra xem dữ liệu có chứa thông tin standings không
    if 'standings' in data:
            standings_info = data['standings']
            # Kiểm tra xem có kết quả (results) nào trong standings hay không
            if 'results' in standings_info:
                results = standings_info['results']
                # Kiểm tra xem danh sách kết quả có rỗng không
                if results:
                    for result in results:
                        user_id = result['entry']
                        total_points = calculate_total_points(user_id)
                        home_points, away_points = calculate_home_away_points(user_id)
                        last_value, last_bank = last_value_bank(user_id)
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        event_note = find_events_with_transfers_cost(user_id)
                        total_transfers_cost = calculate_total_transfers_cost(user_id)
                        user_chips = get_user_chips(user_id)
                        wildcard_event = get_chip_event(user_chips, 'wildcard')
                        bboost_event = get_chip_event(user_chips, 'bboost')
                        cxc_event = get_chip_event(user_chips, '3xc')
                        freehit_event = get_chip_event(user_chips, 'freehit')
                        # Thêm thông tin người dùng vào danh sách
                        user_info.append({
                            'user_id': user_id,
                            'total_points': total_points,
                            'home_points': home_points,
                            'away_points': away_points,
                            'player_name': player_name,
                            'entry_name': entry_name,
                            'event_note': event_note,
                            'total_transfers_cost': total_transfers_cost,
                            'wildcard_event': wildcard_event,
                            'bboost_event': bboost_event,
                            'cxc_event': cxc_event,
                            'last_value': last_value,
                            'last_bank' : last_bank,
                            'freehit_event': freehit_event
                        })
                    # Sắp xếp theo tổng điểm từ cao đến thấp
                    user_info.sort(key=lambda x: x['total_points'], reverse=True)
                    output_file = 'data/total.html'
                    with open(output_file, "w") as file:
                        file.write(render_user_info(user_info,get_league_name(league_id)))
  except Exception as e:
    print(e)

def _render_live_gw_to_file_v2(league_id):
  try:
    with open("data/league_id.json", "r") as file:
        data = json.load(file)
    current_event_id, finished_status = get_current_event()
    gw_id = current_event_id
    print(f"RENDER LIVE HTML FILE FOR GW {gw_id} ================================> data/live.html")
    user_info = []
    file_event="data/events_" + str(gw_id) + ".json" #data/events_15.json
    if 'standings' in data:
        standings_info = data['standings']
        if 'results' in standings_info:
            results = standings_info['results']
            if results:
                for result in results:
                    user_id = result['entry']
                    user_events = get_user_events(user_id)
                    # gw_id - 1 => start array start with index
                    event_selected = user_events[gw_id-1] if user_events else None
                    last_event = user_events[-1] if user_events else None
                    if event_selected:
                        
                        player_name = result.get('player_name', '')
                        print(f"AAAAAAAAAAAAA ============== {player_name}")
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
                        all_bonus_points = get_expected_bonus_points(file_event)
                        
                        if user_picks:
                            # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                            total_goals_scored, total_assists, event_points  = get_live_player_stats(event_selected['event'], user_picks)
                            print(f"AAAAAAAA")
                            try:
                                live_user_picks = get_pick_live_players_v2(gw_id, user_picks,all_bonus_points)
                                exp_user_picks = process_user_picks(live_user_picks,active_chip)
                            except Exception as e:
                                print(e)
                            print(f"live_user_picks {live_user_picks}")
                            print(f"{player_name} ====== {exp_user_picks}")
                            #break
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
                                'captain_point': captain_point,
                                'live_total_points': (int(exp_user_picks["total_points"])- last_event_transfers_cost),
                                'chang_log': exp_user_picks["change_log"],
                                'bonus_log': exp_user_picks["bonus_log"],
                                'live_bps_log': exp_user_picks["live_bps_log"],
                                'vice_point': vice_point,
                                'count_player': exp_user_picks["count_player"],
                                'remain_player': exp_user_picks["remain_player"]
                            })
                # Sắp xếp theo điểm của sự kiện cuối cùng từ cao đến thấp
                #user_info.sort(key=lambda x: x['last_event_points'], reverse=True)
                user_info.sort(key=lambda x: (x['live_total_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']), reverse=True)
                output_file = 'data/' + 'live.html'
                text_html = render_user_live_v2(user_info,get_league_name(league_id),gw_id,gw_id)
                with open(output_file, "w") as file:
                    file.write(text_html)
  except Exception as e:
    print(e)

def render_live_gw_to_file_v2(league_id):
    try:
        with open("data/league_id.json", "r", encoding="utf-8") as file:
            data = json.load(file)

        current_event_id, finished_status = get_current_event()
        gw_id = current_event_id
        print(f"RENDER LIVE HTML FILE FOR GW {gw_id} ================================> data/live.html")

        user_info = []
        file_event = f"data/events_{gw_id}.json"

        if 'standings' in data:
            standings_info = data['standings']
            if 'results' in standings_info:
                results = standings_info['results']
                if results:
                    for result in results:
                        user_id = result['entry']

                        # Lấy lịch sử theo event (không index theo vị trí)
                        user_events = get_user_events(user_id) or []
                        events_by_event = {e.get('event'): e for e in user_events if isinstance(e, dict)}

                        # Chọn event hiện tại; nếu thiếu → placeholder
                        event_selected = events_by_event.get(gw_id, _event_placeholder(gw_id))

                        # Xác định last_event thực sự có trong lịch sử; nếu trống → gw_id
                        last_event_num = max(events_by_event.keys(), default=gw_id)
                        last_event = events_by_event.get(last_event_num, _event_placeholder(last_event_num))

                        player_name = result.get('player_name', '')
                        entry_name  = result.get('entry_name',  '')
                        total_points = calculate_total_points(user_id)

                        last_event_transfers_cost = event_selected.get('event_transfers_cost', 0) or 0
                        last_event_points_raw     = event_selected.get('points', 0) or 0
                        last_event_points         = last_event_points_raw - last_event_transfers_cost
                        event_transfers           = event_selected.get('event_transfers', 0) or 0

                        # Picks của event đang hiển thị (có thể là placeholder rỗng nếu 404)
                        user_picks = get_user_picks(user_id, event_selected['event'])

                        # Captain/vice (các hàm này nên tự chịu null; ở đây vẫn guard)
                        captain, vice_captain = get_captain_and_vice_captain(user_id, event_selected['event'])
                        captain_name  = get_web_name_by_element_id(captain) if captain else ""
                        vice_name     = get_web_name_by_element_id(vice_captain) if vice_captain else ""
                        captain_point = get_live_element_id(event_selected['event'], captain) if captain else 0
                        vice_point    = get_live_element_id(event_selected['event'], vice_captain) if vice_captain else 0

                        # Active chip theo đúng event đang render (không dựa vào index)
                        active_chip = get_active_chip(user_id, event_selected['event'])

                        # Bonus kỳ vọng và live-points
                        try:
                            all_bonus_points = get_expected_bonus_points(file_event)
                        except Exception as e:
                            print(f"[WARN] get_expected_bonus_points({file_event}): {e}")
                            all_bonus_points = {}

                        # Mặc định nếu không có picks
                        live_total_points = last_event_points
                        change_log = []
                        bonus_log = []
                        live_bps_log = []

                        if user_picks:
                            # Tính thống kê goals/assists theo picks
                            total_goals_scored, total_assists, event_points = get_live_player_stats(
                                event_selected['event'], user_picks
                            )
                            try:
                                # Lấy danh sách cầu thủ live; hàm v2 đã được gia cố để bỏ pick không hợp lệ
                                live_user_picks = get_pick_live_players_v2(gw_id, user_picks, all_bonus_points)
                                exp_user_picks  = process_user_picks(live_user_picks, active_chip)
                                # Live total points (đã trừ hit)
                                live_total_points = int(exp_user_picks.get("total_points", 0)) - last_event_transfers_cost
                                change_log  = exp_user_picks.get("change_log", [])
                                bonus_log   = exp_user_picks.get("bonus_log", [])
                                live_bps_log = exp_user_picks.get("live_bps_log", [])
                            except Exception as e:
                                print(f"[WARN] live picks processing failed for {user_id}: {e}")
                                # fallback: giữ nguyên last_event_points và logs rỗng
                        else:
                            # Không có picks (user join muộn / placeholder) → goals/assists = 0
                            total_goals_scored, total_assists = 0, 0

                        user_info.append({
                            'user_id': user_id,
                            'player_name': player_name,
                            'entry_name': entry_name,
                            'total_points': total_points,
                            'last_event_points': last_event_points,
                            'last_event_transfers_cost': last_event_transfers_cost,
                            'user_picks': user_picks or {"picks": []},
                            'total_goals_scored': total_goals_scored,
                            'total_assists': total_assists,
                            'active_chip': active_chip,
                            'event_transfers': event_transfers,
                            'captain_name': captain_name,
                            'vice_name':  vice_name,
                            'captain_point': captain_point,
                            'live_total_points': live_total_points,
                            'chang_log': change_log,
                            'bonus_log': bonus_log,
                            'live_bps_log': live_bps_log,
                            'vice_point': vice_point,
                            'count_player': exp_user_picks["count_player"],
                            'remain_player': exp_user_picks["remain_player"]
                        })

                    # Sắp xếp live desc theo tiêu chí cũ
                    user_info.sort(
                        key=lambda x: (x['live_total_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']),
                        reverse=True
                    )

                    output_file = 'data/live.html'
                    text_html = render_user_live_v2(user_info, get_league_name(league_id), gw_id, gw_id)
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(text_html)

    except Exception as e:
        print(e)

def get_bootstrap_static(cache_path="data/bootstrap-static.json", max_age_hours=6):
    """Tải bootstrap-static và cache để giảm gọi API."""
    try:
        if os.path.exists(cache_path):
            age_hours = (time.time() - os.path.getmtime(cache_path)) / 3600
            if age_hours <= max_age_hours:
                return _load_json_safe(cache_path, {})
        r = _SESSION.get(BOOTSTRAP_URL, timeout=15)
        r.raise_for_status()
        data = r.json()
        _atomic_write(cache_path, data)
        return data
    except Exception as e:
        print(f"[WARN] get_bootstrap_static fallback cache: {e}")
        return _load_json_safe(cache_path, {})

def get_event_by_mon(mon: int) -> list[int]:
    """
    Trả về danh sách event IDs theo tháng (1..12) dựa trên events[].deadline_time (UTC).
    Ví dụ: mon=8 -> [1,2,3] (tuỳ mùa).
    """
    bs = get_bootstrap_static()
    events = bs.get("events", []) or []
    result = []
    for ev in events:
        # deadline_time dạng "YYYY-MM-DDTHH:MM:SSZ"
        dt_str = ev.get("deadline_time")
        ev_id = ev.get("id")
        if not dt_str or not ev_id:
            continue
        try:
            # parse ISO với Z (UTC)
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).astimezone(timezone.utc)
            if dt.month == int(mon):
                result.append(int(ev_id))
        except Exception:
            continue
    return sorted(result)

def _load_json_safe(path, default=None):
    if default is None: default = {}
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"[WARN] Cannot read {path}: {e}")
    return default

def _sum_points_for_events(user_history: Dict[str, Any], event_ids: set[int]) -> tuple[int, int, int]:
    """
    Cộng điểm theo các event trong user_history (data/<user_id>.json) cho tập event_ids.
    Trả về:
      - total_net_points:   tổng (points - event_transfers_cost)
      - total_transfers:    tổng event_transfers
      - total_hits:         tổng event_transfers_cost
    """
    total_net_points = 0
    total_transfers = 0
    total_hits = 0

    current = user_history.get("current", []) or []
    for rec in current:
        try:
            ev = int(rec.get("event", -1))
            if ev in event_ids:
                pts   = int(rec.get("points", 0) or 0)
                hits  = int(rec.get("event_transfers_cost", 0) or 0)
                trans = int(rec.get("event_transfers", 0) or 0)

                total_net_points += (pts - hits)
                total_transfers  += trans
                total_hits       += hits
        except Exception:
            continue

    return total_net_points, total_transfers, total_hits

def _compute_month_points(mon: int, league_id: int) -> List[Dict[str, Any]]:
    """
    Đọc data/league_id.json để lấy danh sách user trong league,
    sau đó đọc data/<user_id>.json và cộng điểm theo các event thuộc tháng mon.

    Trả về mỗi user:
      {
        "user_id": ...,
        "player_name": ...,
        "entry_name": ...,
        "month_points": <điểm ròng (points - hits)>,
        "month_transfers": <tổng event_transfers>,
        "month_hits": <tổng event_transfers_cost>
      }
    """
    month_events = set(get_event_by_mon(int(mon)))
    if not month_events:
        print(f"[INFO] No events mapped for month {mon}")

    league_path = "data/league_id.json"
    league_data = _load_json_safe(league_path, {})
    results: List[Dict[str, Any]] = []

    standings = (league_data.get("standings") or {}).get("results") or []
    for row in standings:
        user_id = row.get("entry")
        player_name = row.get("player_name", "")
        entry_name  = row.get("entry_name", "")
        if not user_id:
            continue

        user_hist = _load_json_safe(f"data/{user_id}.json", {"current": []})
        month_points_net, month_transfers, month_hits = _sum_points_for_events(user_hist, month_events)

        results.append({
            "user_id": user_id,
            "player_name": player_name,
            "entry_name": entry_name,
            "month_points": month_points_net,   # đã trừ hits
            "month_transfers": month_transfers, # chỉ số phụ 1
            "month_hits": month_hits            # chỉ số phụ 2
        })

    # Sort: điểm ròng desc, rồi transfers asc, rồi hits asc
    results.sort(
        key=lambda x: (int(x.get("month_points", 0)),
                       -int(x.get("month_transfers", 0)) * -1,  # giữ thứ tự rõ ràng
                       -int(x.get("month_hits", 0)) * -1),
        reverse=True
    )
    # Lưu ý: biểu thức trên tương đương sort theo
    # (month_points desc, month_transfers asc, month_hits asc).
    # Có thể viết gọn hơn như dưới, nhưng cần hai bước hoặc sort tuple phức tạp.
    # Để tránh nhầm, ta có thể làm như sau (dễ đọc):
    results.sort(
        key=lambda x: (
            -int(x.get("month_points", 0)),          # điểm ròng cao hơn trước
             int(x.get("month_transfers", 0)),       # transfers ít hơn trước
             int(x.get("month_hits", 0))             # hits ít hơn trước
        )
    )

    return results

def compute_month_points(mon: int, league_id: int) -> List[Dict[str, Any]]:
    """
    Tính điểm tháng cho tất cả user trong league, kèm chỉ số phụ của vòng cuối tháng
    để dùng làm tie-breaker.
    """
    month_events = sorted(get_event_by_mon(int(mon)))
    last_gw = month_events[-1] if month_events else None

    league_path = "data/league_id.json"
    league_data = _load_json_safe(league_path, {})
    standings = (league_data.get("standings") or {}).get("results") or []

    results: List[Dict[str, Any]] = []

    for row in standings:
        user_id = row.get("entry")
        player_name = row.get("player_name", "")
        entry_name  = row.get("entry_name", "")
        if not user_id:
            continue

        # Tổng điểm tháng (ròng), tổng transfers, tổng hits
        user_hist = _load_json_safe(f"data/{user_id}.json", {"current": []})
        month_points_net, month_transfers, month_hits = _sum_points_for_events(user_hist, set(month_events))

        # --- Tie-break từ vòng cuối tháng ---
        last_event_points = 0
        last_event_goals  = 0
        last_event_assists = 0
        last_event_transfers = 0

        if last_gw is not None:
            # Lấy record event cuối của tháng trong data/<user_id>.json
            for rec in (user_hist.get("current") or []):
                if int(rec.get("event", -1)) == int(last_gw):
                    pts  = int(rec.get("points", 0) or 0)
                    hits = int(rec.get("event_transfers_cost", 0) or 0)
                    last_event_points     = pts - hits
                    last_event_transfers  = int(rec.get("event_transfers", 0) or 0)
                    break

            # Tính G/A theo picks * multiplier trong GW cuối (đọc events_<gw>.json)
            picks = _load_json_safe(f"data/{user_id}_{last_gw}.json", {})
            events_live = _load_json_safe(f"data/events_{last_gw}.json", {"elements": []})
            elements_by_id = {e.get("id"): e for e in (events_live.get("elements") or []) if isinstance(e, dict)}

            for p in (picks.get("picks") or []):
                try:
                    el  = int(p.get("element"))
                    mul = int(p.get("multiplier", 0) or 0)
                    if mul not in (1, 2, 3):
                        continue
                    stats = (elements_by_id.get(el) or {}).get("stats", {}) or {}
                    last_event_goals   += int(stats.get("goals_scored", 0) or 0) * mul
                    last_event_assists += int(stats.get("assists", 0) or 0) * mul
                except Exception:
                    continue

        results.append({
            "user_id": user_id,
            "player_name": player_name,
            "entry_name": entry_name,

            # Điểm tháng và tổng meta
            "month_points": month_points_net,
            "month_transfers": month_transfers,
            "month_hits": month_hits,

            # Chỉ số phụ cho tie-break vòng cuối tháng
            "last_event_id": last_gw,
            "last_event_points": last_event_points,
            "last_event_goals": last_event_goals,
            "last_event_assists": last_event_assists,
            "last_event_transfers": last_event_transfers,
        })

    # Không sort ở đây; sort ở render để có thể thay đổi tiêu chí hiển thị linh hoạt
    return results


def get_months_to_render(now: datetime | None = None, season_start_month: int = 8) -> List[int]:
    """
    Trả về danh sách các tháng cần render kể từ đầu mùa (mặc định tháng 8)
    đến THÁNG HIỆN TẠI, có xử lý qua năm (8..12,1..current).
    Ví dụ:
      - now.month = 8  -> [8]
      - now.month = 12 -> [8,9,10,11,12]
      - now.month = 3  -> [8,9,10,11,12,1,2,3]
    """
    if now is None:
        now = datetime.now()
    cur = now.month
    if cur >= season_start_month:
        return list(range(season_start_month, cur + 1))
    # wrap sang năm sau
    return list(range(season_start_month, 13)) + list(range(1, cur + 1))


def render_current_month(league_id: int, now: datetime | None = None) -> str:
    """
    Render đúng THÁNG HIỆN TẠI ra data/month_<mon>.html
    """
    if now is None:
        now = datetime.now()
    mon = now.month
    return render_month_points_to_file(mon=mon, league_id=league_id)


def render_months_until_now(league_id: int, now: datetime | None = None, season_start_month: int = 8) -> list[str]:
    """
    Render TẤT CẢ các tháng từ tháng 8 (mặc định) đến THÁNG HIỆN TẠI.
    Trả về list đường dẫn file đã tạo.
    """
    if now is None:
        now = datetime.now()
    months = get_months_to_render(now=now, season_start_month=season_start_month)
    outputs = []
    for mon in months:
        out = render_month_points_to_file(mon=mon, league_id=league_id)
        outputs.append(out)
    return outputs

def _render_month_points_to_file(mon: int, league_id: int, out_dir: str = "data") -> str:
    """
    Render bảng xếp hạng theo tháng ra HTML: data/month_<mon>.html
    - Giao diện theo format đã yêu cầu (banner, màu nền các hàng, chữ trắng).
    - Có thanh điều hướng các tháng (8 -> tháng hiện tại), bôi đậm tháng đang xem.
    - Bảng hiển thị: #, User ID, Player, Team, Điểm tháng (điểm ròng),
      kèm 2 chỉ số phụ: Transfers (tổng event_transfers) và Hits (tổng event_transfers_cost).
    """
    # Lấy dữ liệu
    rows = compute_month_points(mon, league_id)  # yêu cầu: month_points, month_transfers, month_hits
    try:
        rows = sorted(
            rows,
            key=lambda r: (-int(r.get("month_points", 0)),
                           int(r.get("month_transfers", 0)),
                           int(r.get("month_hits", 0)))
        )
    except Exception:
        pass

    league_name = get_league_name(league_id) if "get_league_name" in globals() else f"League {league_id}"
    events_list = get_event_by_mon(int(mon))
    events_str = ", ".join(str(e) for e in events_list) if events_list else "—"

    # Tính dải tháng theo mùa (8 -> tháng hiện tại, có wrap qua năm)
    now = datetime.now()
    cur_mon = now.month
    if cur_mon >= 8:
        months = list(range(8, cur_mon + 1))
    else:
        months = list(range(8, 13)) + list(range(1, cur_mon + 1))

    # ---- HTML theo format yêu cầu ----
    html = []
    html.append("<html><head>")
    html.append("<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'/>")
    html.append("<style>")
    html.append("body {")
    html.append("    margin: 0;")
    html.append("    padding: 0;")
    html.append("    font-family: Arial, sans-serif;")
    html.append("    background-image: url('https://www.ncfsc.co.uk/wp-content/uploads/2023/05/FPL_Banner.png');")
    html.append("    background-size: 20% auto;")
    html.append("    background-repeat: no-repeat;")
    html.append("    background-position: left top;")
    html.append("}")
    html.append("#header {")
    html.append("    background-color: transparent;")
    html.append("    text-align: center;")
    html.append("    padding: 20px;")
    html.append("    color: #4CAF50;")
    html.append("}")
    html.append("#nav { margin: 6px 0 0; }")
    html.append("#nav a { color: #4CAF50; text-decoration: none; margin: 0 6px; }")
    html.append("#nav a.active { font-weight: bold; text-decoration: underline; }")
    html.append("#table-container {")
    html.append("    background-color: transparent;")
    html.append("    padding: 20px;")
    html.append("    overflow-x: auto;")
    html.append("}")
    html.append("table {")
    html.append("    border-collapse: collapse;")
    html.append("    width: 100%;")
    html.append("    margin: 0 auto;")
    html.append("}")
    html.append("th, td {")
    html.append("    border: 1px solid white;")
    html.append("    padding: 10px;")
    html.append("    text-align: center;")
    html.append("    color: white;")
    html.append("}")
    html.append("th {")
    html.append("    font-weight: bold;")
    html.append("}")
    html.append("tr.row-0 td { background-color: #13174B; }")
    html.append("tr.row-1 td { background-color: #4CAF50; }")
    html.append("tr.row-2 td { background-color: #ED4D5E; }")
    html.append("th.highlight { background-color: #ED4D5E; }")
    html.append("</style>")
    html.append("</head><body>")

    # Header
    html.append("<div id='header'>")
    html.append(f"<h1>{league_name} — Tháng {int(mon)}</h1>")
    html.append(f"<div>Gameweeks: <b>{events_str}</b></div>")

    # Điều hướng theo THÁNG
    html.append("<div id='nav'>")
    # nếu bạn phục vụ file tĩnh, có thể đổi href thành f'/month_{m}.html'
    for m in months:
        cls = "active" if m == int(mon) else ""
        html.append(f"<a class='{cls}' href='/month?mon={m}'>Tháng {m}</a>")
    html += "<a href='/' style='color:#4CAF50; text-decoration;'>Total </a>"
    html += "<a href='/home' style='color:#4CAF50; text-decoration;'>Home </a>"
    html += "<a href='/away' style='color:#4CAF50; text-decoration;'>Away </a>"
    html += "<a href='/live' style='color:#4CAF50; text-decoration;'>    GW</a><br>"
    html.append("</div>")

    html.append("</div>")  # /header

    # Table Container
    html.append("<div id='table-container'>")
    html.append("<table>")
    html.append("<tr>")
    html.append("<th class='highlight'>#</th>")
    html.append("<th class='highlight'>User ID</th>")
    html.append("<th class='highlight'>Player Name</th>")
    html.append("<th class='highlight'>Entry (Team)</th>")
    html.append("<th class='highlight'>Điểm tháng (Net)</th>")
    html.append("<th class='highlight'>Transfers</th>")
    html.append("<th class='highlight'>Hits</th>")
    html.append("</tr>")

    if rows:
        for idx, r in enumerate(rows, 1):
            user_id = r.get("user_id", "")
            player_name = r.get("player_name", "")
            entry_name  = r.get("entry_name", "")
            month_pts   = r.get("month_points", 0)
            month_trans = r.get("month_transfers", 0)
            month_hits  = r.get("month_hits", 0)

            html.append(f"<tr class='row-{(idx-1) % 3}'>")
            html.append(f"<td>{idx}</td>")
            html.append(f"<td>{user_id}</td>")
            html.append(f"<td>{player_name}</td>")
            html.append(f"<td>{entry_name}</td>")
            html.append(f"<td><b>{month_pts}</b></td>")
            html.append(f"<td>{month_trans}</td>")
            html.append(f"<td>{month_hits}</td>")
            html.append("</tr>")
    else:
        html.append("<tr class='row-0'><td colspan='7'>Không có dữ liệu</td></tr>")

    html.append("</table>")
    html.append("</div>")  # /table-container
    html.append("</body></html>")

    # Ghi file
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"month_{int(mon)}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(html))
    print(f"[OK] Wrote {out_path}")
    return out_path

def __render_month_points_to_file(mon: int, league_id: int, out_dir: str = "data") -> str:
    """
    Render bảng xếp hạng theo tháng ra HTML: data/month_<mon>.html
    Tie-break: nếu month_points bằng nhau → so vòng cuối tháng theo
    (last_event_points, last_event_goals, last_event_assists, -last_event_transfers) desc.
    """
    rows = compute_month_points(mon, league_id)

    # Sort theo yêu cầu
    try:
        rows = sorted(
            rows,
            key=lambda r: (
                int(r.get("month_points", 0)),
                int(r.get("last_event_points", 0)),
                int(r.get("last_event_goals", 0)),
                int(r.get("last_event_assists", 0)),
                -int(r.get("last_event_transfers", 0)),
            ),
            reverse=True
        )
    except Exception:
        pass

    league_name = get_league_name(league_id) if "get_league_name" in globals() else f"League {league_id}"
    events_list = get_event_by_mon(int(mon))
    events_str = ", ".join(str(e) for e in events_list) if events_list else "—"

    # Dải tháng của mùa (8 -> tháng hiện tại, có wrap qua năm)
    now = datetime.now()
    cur_mon = now.month
    months = list(range(8, cur_mon + 1)) if cur_mon >= 8 else list(range(8, 13)) + list(range(1, cur_mon + 1))

    # ---- HTML ----
    html = []
    html.append("<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    html.append(f"<title>FPL Month {int(mon)} — {league_name}</title>")
    html.append("<style>")
    html.append("body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;margin:0;padding:16px;}")
    html.append("h1{margin:0 0 8px} .sub{color:#666;margin:0 0 16px}")
    html.append("#nav{margin:8px 0 16px}")
    html.append("#nav a{display:inline-block;margin-right:8px;text-decoration:none;color:#0a7}")
    html.append("#nav a.active{font-weight:700;text-decoration:underline}")
    html.append("table{border-collapse:collapse;width:100%} th,td{border:1px solid #ddd;padding:8px;text-align:left}")
    html.append("th{background:#f6f6f6} tr:nth-child(even){background:#fafafa}")
    html.append("</style></head><body>")

    html.append(f"<h1>Tháng {int(mon)} — {league_name}</h1>")
    html.append(f"<p class='sub'>Gameweeks: {events_str}</p>")

    # Nav tháng
    html.append("<div id='nav'>")
    for m in months:
        cls = "active" if m == int(mon) else ""
        html.append(f"<a class='{cls}' href='/month?mon={m}'>Tháng {m}</a>")
    html.append(" · <a href='/'>Total</a> · <a href='/home'>Home</a> · <a href='/away'>Away</a> · <a href='/live'>GW</a>")
    html.append("</div>")

    # Bảng
    html.append("<div id='table-container'><table><thead><tr>")
    html.append("<th>#</th><th>User ID</th><th>Player</th><th>Team</th>")
    html.append("<th>Month Pts</th><th>Transfers</th><th>Hits</th>")
    html.append("<th>Last GW (pts/G/A/tr)</th>")
    html.append("</tr></thead><tbody>")

    if rows:
        for idx, r in enumerate(rows, start=1):
            user_id      = r.get("user_id", "")
            player_name  = r.get("player_name", "")
            entry_name   = r.get("entry_name", "")
            month_pts    = int(r.get("month_points", 0) or 0)
            month_trans  = int(r.get("month_transfers", 0) or 0)
            month_hits   = int(r.get("month_hits", 0) or 0)

            last_id      = r.get("last_event_id", "")
            lep          = int(r.get("last_event_points", 0) or 0)
            leg          = int(r.get("last_event_goals", 0) or 0)
            lea          = int(r.get("last_event_assists", 0) or 0)
            letf         = int(r.get("last_event_transfers", 0) or 0)

            html.append("<tr>")
            html.append(f"<td>{idx}</td>")
            html.append(f"<td>{user_id}</td>")
            html.append(f"<td>{player_name}</td>")
            html.append(f"<td>{entry_name}</td>")
            html.append(f"<td><b>{month_pts}</b></td>")
            html.append(f"<td>{month_trans}</td>")
            html.append(f"<td>{month_hits}</td>")
            html.append(f"<td>GW{last_id if last_id else '—'}: {lep} / {leg}/{lea}/{letf}</td>")
            html.append("</tr>")
    else:
        html.append("<tr><td colspan='8'>Không có dữ liệu</td></tr>")

    html.append("</tbody></table></div></body></html>")

    # Ghi file
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"month_{int(mon)}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(html))
    print(f"[OK] Wrote {out_path}")
    return out_path


def render_month_points_to_file(mon: int, league_id: int, out_dir: str = "data") -> str:
    """
    Render bảng xếp hạng theo tháng ra HTML: data/month_<mon>.html
    - Giao diện theo format đã yêu cầu (banner, màu nền các hàng, chữ trắng).
    - Có thanh điều hướng các tháng (8 -> tháng hiện tại), bôi đậm tháng đang xem.
    - Bảng hiển thị: #, User ID, Player, Team, Điểm tháng (Net),
      Transfers, Hits, và cột phụ: Last GW (pts/G/A/tr).
    """
    # Lấy dữ liệu
    rows = compute_month_points(mon, league_id)

    # Sort với tie-break vòng cuối tháng
    try:
        rows = sorted(
            rows,
            key=lambda r: (
                int(r.get("month_points", 0)),
                int(r.get("last_event_points", 0)),
                int(r.get("last_event_goals", 0)),
                int(r.get("last_event_assists", 0)),
                -int(r.get("last_event_transfers", 0)),
            ),
            reverse=True
        )
    except Exception:
        pass

    league_name = get_league_name(league_id) if "get_league_name" in globals() else f"League {league_id}"
    events_list = get_event_by_mon(int(mon))
    events_str = ", ".join(str(e) for e in events_list) if events_list else "—"

    # Tính dải tháng theo mùa (8 -> tháng hiện tại, có wrap qua năm)
    now = datetime.now()
    cur_mon = now.month
    if cur_mon >= 8:
        months = list(range(8, cur_mon + 1))
    else:
        months = list(range(8, 13)) + list(range(1, cur_mon + 1))

    # ---- HTML theo format yêu cầu ----
    html = []
    html.append("<html><head>")
    html.append("<meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'/>")
    html.append("<style>")
    html.append("body {")
    html.append("    margin: 0;")
    html.append("    padding: 0;")
    html.append("    font-family: Arial, sans-serif;")
    html.append("    background-image: url('https://www.ncfsc.co.uk/wp-content/uploads/2023/05/FPL_Banner.png');")
    html.append("    background-size: 20% auto;")
    html.append("    background-repeat: no-repeat;")
    html.append("    background-position: left top;")
    html.append("}")
    html.append("#header {")
    html.append("    background-color: transparent;")
    html.append("    text-align: center;")
    html.append("    padding: 20px;")
    html.append("    color: #4CAF50;")
    html.append("}")
    html.append("#nav { margin: 6px 0 0; }")
    html.append("#nav a { color: #4CAF50; text-decoration: none; margin: 0 6px; }")
    html.append("#nav a.active { font-weight: bold; text-decoration: underline; }")
    html.append("#table-container {")
    html.append("    background-color: transparent;")
    html.append("    padding: 20px;")
    html.append("    overflow-x: auto;")
    html.append("}")
    html.append("table {")
    html.append("    border-collapse: collapse;")
    html.append("    width: 100%;")
    html.append("    margin: 0 auto;")
    html.append("}")
    html.append("th, td {")
    html.append("    border: 1px solid white;")
    html.append("    padding: 10px;")
    html.append("    text-align: center;")
    html.append("    color: white;")
    html.append("}")
    html.append("th {")
    html.append("    font-weight: bold;")
    html.append("}")
    html.append("tr.row-0 td { background-color: #13174B; }")
    html.append("tr.row-1 td { background-color: #4CAF50; }")
    html.append("tr.row-2 td { background-color: #ED4D5E; }")
    html.append("th.highlight { background-color: #ED4D5E; }")
    html.append("</style>")
    html.append("</head><body>")

    # Header
    html.append("<div id='header'>")
    html.append(f"<h1>{league_name} — Tháng {int(mon)}</h1>")
    html.append(f"<div>Gameweeks: <b>{events_str}</b></div>")

    # Điều hướng theo THÁNG
    html.append("<div id='nav'>")
    for m in months:
        cls = "active" if m == int(mon) else ""
        # nếu phục vụ file tĩnh, có thể đổi href thành f'/month_{m}.html'
        html.append(f"<a class='{cls}' href='/month?mon={m}'>Tháng {m}</a>")
    html.append("<a href='/' style='color:#4CAF50; text-decoration;'>Total </a>")
    html.append("<a href='/home' style='color:#4CAF50; text-decoration;'>Home </a>")
    html.append("<a href='/away' style='color:#4CAF50; text-decoration;'>Away </a>")
    html.append("<a href='/live' style='color:#4CAF50; text-decoration;'>GW</a><br>")
    html.append("</div>")  # /nav

    html.append("</div>")  # /header

    # Table
    html.append("<div id='table-container'>")
    html.append("<table>")
    html.append("<tr>")
    html.append("<th class='highlight'>#</th>")
    html.append("<th class='highlight'>User ID</th>")
    html.append("<th class='highlight'>Player Name</th>")
    html.append("<th class='highlight'>Entry (Team)</th>")
    html.append("<th class='highlight'>Điểm tháng (Net)</th>")
    html.append("<th class='highlight'>Transfers</th>")
    html.append("<th class='highlight'>Hits</th>")
    html.append("<th class='highlight'>Last GW (pts/G/A/tr)</th>")
    html.append("</tr>")

    if rows:
        for idx, r in enumerate(rows, 1):
            user_id = r.get("user_id", "")
            player_name = r.get("player_name", "")
            entry_name  = r.get("entry_name", "")
            month_pts   = int(r.get("month_points", 0) or 0)
            month_trans = int(r.get("month_transfers", 0) or 0)
            month_hits  = int(r.get("month_hits", 0) or 0)

            last_id = r.get("last_event_id", "")
            lep = int(r.get("last_event_points", 0) or 0)
            leg = int(r.get("last_event_goals", 0) or 0)
            lea = int(r.get("last_event_assists", 0) or 0)
            letf = int(r.get("last_event_transfers", 0) or 0)

            html.append(f"<tr class='row-{(idx-1) % 3}'>")
            html.append(f"<td>{idx}</td>")
            html.append(f"<td>{user_id}</td>")
            html.append(f"<td>{player_name}</td>")
            html.append(f"<td>{entry_name}</td>")
            html.append(f"<td><b>{month_pts}</b></td>")
            html.append(f"<td>{month_trans}</td>")
            html.append(f"<td>{month_hits}</td>")
            html.append(f"<td>GW{last_id if last_id else '—'}: {lep} / {leg}/{lea}/{letf}</td>")
            html.append("</tr>")
    else:
        html.append("<tr class='row-0'><td colspan='8'>Không có dữ liệu</td></tr>")

    html.append("</table>")
    html.append("</div>")  # /table-container
    html.append("</body></html>")

    # Ghi file
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"month_{int(mon)}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("".join(html))
    print(f"[OK] Wrote {out_path}")
    return out_path
