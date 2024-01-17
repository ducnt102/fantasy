from flask import Flask
import threading
import requests
import json
import time
from flask import request


app = Flask(__name__)

league_id = 169451

def get_league_name(id):
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
        print(f"Yêu cầu không thành công cho id {id}. Status code:", response.status_code)    
        return None

def generate_json_data():

    url = f"https://fantasy.premierleague.com/api/leagues-classic/{league_id}/standings/"

    # Gửi yêu cầu GET đến API
    response = requests.get(url)

    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        data = response.json()
        with open("league_id.json", "w") as file:
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
                          with open(f"{user_id}.json", "w") as file:
                            json.dump(user_data, file)
                          print(f"Dữ liệu cho user_id {user_id} đã được lưu vào file {user_id}.json")
                          user_events = get_user_events_x(user_id)
                          last_event = user_events[-1] if user_events else None
                          get_user_picks_file(user_id,last_event['event'])
                    user_events = get_user_events_x(user_id)
                    last_event = user_events[-1] if user_events else None
                    get_events_file(last_event['event'])
                # Kiểm tra xem danh sách kết quả có rỗng không                          
                else:
                    print(f"Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)


def calculate_total_transfers_cost(user_id):
    total_transfers_cost = 0
    user_events = get_user_events(user_id)

    # Lặp qua từng sự kiện và tính tổng event_transfers_cost
    for event in user_events:
        event_transfers_cost = event.get('event_transfers_cost', 0)
        total_transfers_cost += event_transfers_cost
    return total_transfers_cost

def get_user_events(user_id):
    with open(f"{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'current' in user_data:
        return user_data['current']
    return []

# Hàm để lấy dữ liệu từ tệp JSON về chip của người dùng
def get_user_chips(user_id):
    with open(f"{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'chips' in user_data:
        return user_data['chips']
    return []

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
    for chip in user_chips:
        if chip['name'].lower() == chip_name.lower():
            return chip.get('event', '')
    return ''

def get_user_chips_x(user_id):
    user_chips = []
    url = f"https://fantasy.premierleague.com/api/entry/{user_id}/history/"

    # Gửi yêu cầu GET đến API
    response = requests.get(url)

    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if response.status_code == 200:
        # Lấy dữ liệu JSON từ phản hồi
        user_data = response.json()

        # Kiểm tra và lấy thông tin sự kiện của người dùng
        if 'chips' in user_data:
            user_chips = user_data['chips']
    else:
        print(f"Yêu cầu không thành công cho user_id {user_id}. Status code:", response.status_code)
    return user_chips

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

def get_events_file(gw_id):
    for event in range(1, gw_id + 1):
        file_name = f"events_{event}.json"
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

def get_active_chip(user_id, event):
    file_name = f"{user_id}_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
    if 'active_chip' in data:
        chip = data['active_chip']
        return chip
    else:
        print(f"Yêu cầu get chip không thành công cho {user_id} event {event}")
        return None

def get_live_player_stats(event, user_picks):
    file_name = f"events_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
        # Khởi tạo biến để lưu tổng số goals_scored và assists
    if data:
        total_goals_scored = 0
        total_assists = 0
        
        # Duyệt qua từng lựa chọn của người chơi
        for user_pick in user_picks['picks']:
            element_id = user_pick['element']
            multiplier = user_pick['multiplier']
            
            # Kiểm tra điều kiện multiplier !=0
            if multiplier == 1 or multiplier == 2:
                # Tìm thông tin về cầu thủ trong response của API
                for player_info in data['elements']:
                    if player_info['id'] == element_id:
                        # Cộng dồn goals_scored và assists
                        total_goals_scored += player_info['stats']['goals_scored']
                        total_assists += player_info['stats']['assists']
                        break
        
        # Trả về tổng số goals_scored và assists
        return total_goals_scored, total_assists
    else:
        print(f"Yêu cầu không thành công cho event {event}")
        return None
def get_user_picks_file(user_id, event):
    for gw_id in range(1, int(event)+1):
        url = f"https://fantasy.premierleague.com/api/entry/{user_id}/event/{gw_id}/picks/"
        # Gửi yêu cầu GET đến API
        response = requests.get(url)
        # Kiểm tra xem yêu cầu có thành công không (status code 200)
        if response.status_code == 200:
            # Lấy dữ liệu JSON từ phản hồi
            data = response.json()
            with open(f"{user_id}_{gw_id}.json", "w") as file:
                json.dump(data, file)
        else:
            print(f"Yêu cầu không thành công cho user_id {user_id}, event {gw_id}. Status code:", response.status_code)

def get_user_picks(user_id, event):
    with open(f"{user_id}_{event}.json", "r") as file:
        data = json.load(file)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if data:
        # Lấy dữ liệu JSON từ phản hồi
        #data = response.json()
        return data
    else:
        print(f"Yêu cầu không thành công cho user_id {user_id}, event {event}")
        return None


@app.route('/gw')
def gw():
    with open("league_id.json", "r") as file:
        data = json.load(file)
    
    user_info = []
    selected_event = int(request.args.get('selected_event', 0))  # Lấy event từ request, mặc định là 0 nếu không có
    
    if 'standings' in data:
        standings_info = data['standings']
        
        if 'results' in standings_info:
            results = standings_info['results']
            
            if results:
                for result in results:
                    user_id = result['entry']
                    user_events = get_user_events_x(user_id)
                    event_selected = user_events[selected_event-1] if user_events else None
                    
                    if event_selected:
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        total_points = calculate_total_points(user_id)
                        last_event_transfers_cost = event_selected.get('event_transfers_cost', 0)
                        last_event_points = event_selected.get('points', 0) - last_event_transfers_cost
                        event_transfers = event_selected.get('event_transfers', 0)

                        # Sử dụng hàm get_user_picks để lấy thông tin về các lựa chọn
                        user_picks = get_user_picks(user_id, event_selected['event'])
                        active_chip= get_active_chip(user_id, event_selected['event'])
                        if user_picks:
                            # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                            total_goals_scored, total_assists  = get_live_player_stats(event_selected['event'], user_picks)
                            
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
                                'event_transfers': event_transfers
                            })
                # Sắp xếp theo điểm của sự kiện cuối cùng từ cao đến thấp
                #user_info.sort(key=lambda x: x['last_event_points'], reverse=True)
                user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['event_transfers']), reverse=True)
    return render_live_info(user_info,get_league_name(league_id),event_selected['event'])

@app.route('/live')
def live():
    with open("league_id.json", "r") as file:
        data = json.load(file)
    
    user_info = []
    
    if 'standings' in data:
        standings_info = data['standings']
        
        if 'results' in standings_info:
            results = standings_info['results']
            
            if results:
                for result in results:
                    user_id = result['entry']
                    user_events = get_user_events_x(user_id)
                    last_event = user_events[-1] if user_events else None
                    
                    if last_event:
                        player_name = result.get('player_name', '')
                        entry_name = result.get('entry_name', '')
                        total_points = calculate_total_points(user_id)
                        last_event_transfers_cost = last_event.get('event_transfers_cost', 0)
                        last_event_points = last_event.get('points', 0) - last_event_transfers_cost
                        event_transfers = last_event.get('event_transfers', 0)

                        # Sử dụng hàm get_user_picks để lấy thông tin về các lựa chọn
                        user_picks = get_user_picks(user_id, last_event['event'])
                        active_chip= get_active_chip(user_id, last_event['event'])
                        if user_picks:
                            # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                            total_goals_scored, total_assists  = get_live_player_stats(last_event['event'], user_picks)
                            
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
                                'event_transfers': event_transfers
                            })
                # Sắp xếp theo điểm của sự kiện cuối cùng từ cao đến thấp
                #user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], x['last_event_transfers_cost']), reverse=True)
                user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['last_event_transfers_cost']), reverse=True)
    return render_live_info(user_info,get_league_name(league_id),last_event['event'])

# Thêm hàm render_live_info() để tạo HTML cho trang /live
def render_live_info(user_info,league_name,gw_id):
    html = "<html><head>"
    html += "<style>"
    html += "body {"
    html += "    margin: 0; /* Loại bỏ margin mặc định của body */"
    html += "    padding: 0; /* Loại bỏ padding mặc định của body */"
    html += "    font-family: Arial, sans-serif; /* Lựa chọn font chữ */"
    html += "    background-image: url('https://www.ncfsc.co.uk/wp-content/uploads/2023/05/FPL_Banner.png');"
    html += "    background-size: 20% auto;"
    html += "    background-repeat: no-repeat;"
    html += "    background-position: left top; /* Đặt vị trí ảnh nền ở bên trái trên */"
    html += "}"
    html += "#header {"
    html += "    background-color: transparent; /* Đặt màu nền của header là trong suốt */"
    html += "    text-align: center; /* Căn lề giữa */"
    html += "    padding: 20px; /* Khoảng cách giữa nội dung và mép */"
    html += "    color: black; /* Màu chữ đen */"
    html += "}"
    html += "#table-container {"
    html += "    background-color: #4CAF50; /* Màu nền của table container */"
    html += "    padding: 20px; /* Khoảng cách giữa nội dung và mép */"
    html += "}"
    html += "table {"
    html += "    border-collapse: collapse;"
    html += "    width: 100%;"
    html += "    margin: 0 auto; /* Căn lề giữa */"
    html += "}"
    html += "th, td {"
    html += "    border: 1px solid white;"
    html += "    padding: 10px;"
    html += "    text-align: center;"
    html += "    color: white;"
    html += "}"
    html += "</style>"
    html += "</head><body>"

    # Header
    html += "<div id='header'>"
    html += "<h1>" + league_name + " - GW " + str(gw_id) +  " - Live</h1>"
    html += "<a href='/' style='color:#4CAF50; text-decoration:underline;'>Home</a><br>"
    for event_id in range(1, gw_id+1):
        html += "<a href='/gw?selected_event=" + str(event_id) + "' style='color:#4CAF50; text-decoration:underline;'>" + str(event_id) + "</a> "
    html += "</div>"
    html += "</div>"

    # Table Container
    html += "<div id='table-container'>"
    # Bổ sung thông tin về các lựa chọn, event_transfers và live_player_stats vào trang HTML
    html += "<table>"
    html += "<tr><th>Entry Name</th><th>Player Name</th><th>Total Points</th><th>Points</th><th>Active Chip</th><th>Event Transfers</th><th>Transfers Cost</th><th>Total Goals(Not Bench)</th><th>Total Assisst(Not Bench)</th><th>User Picks</th></tr>"
    
    for user in user_info:
        player_name = user['player_name']
        entry_name = user['entry_name']
        total_points = user['total_points']
        last_event_points = user['last_event_points']
        last_event_transfers_cost = user['last_event_transfers_cost']
        event_transfers = user['user_picks']['entry_history'].get('event_transfers', 0)
        total_goals_scored = user['total_goals_scored']
        total_assists = user['total_assists']
        user_picks = user['user_picks']
        active_chip = user['active_chip']
    
        html += "<tr>"
        html += f"<td>{entry_name}</td>"
        html += f"<td>{player_name}</td>"
        html += f"<td>{total_points}</td>"
        html += f"<td>{last_event_points}</td>"
        html += f"<td>{active_chip}</td>"        
        html += f"<td>{event_transfers}</td>"
        html += f"<td>{last_event_transfers_cost}</td>"        
        html += f"<td>{total_goals_scored}</td>"
        html += f"<td>{total_assists}</td>"
        
        # Hiển thị thông tin về các lựa chọn
        html += "<td>"
        for pick in user_picks['picks']:
            element_id = pick['element']
            html += f"{element_id}, "
        html += "</td>"
        
        html += "</tr>"
    
    html += "</table>"
    html += "</body></html>"
    return html


@app.route('/')
def display_user_info():
    with open("league_id.json", "r") as file:
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
                            'last_bank' : last_bank
                        })

                    # Sắp xếp theo tổng điểm từ cao đến thấp
                    user_info.sort(key=lambda x: x['total_points'], reverse=True)
    return render_user_info(user_info,get_league_name(league_id))

def render_user_info(user_info, league_name):
    # Tạo HTML cho trang
    html = "<html><head>"
    html += "<style>"
    html += "body {"
    html += "    margin: 0;"
    html += "    padding: 0;"
    html += "    font-family: Arial, sans-serif;"
    html += "    background-image: url('https://www.ncfsc.co.uk/wp-content/uploads/2023/05/FPL_Banner.png');"
    html += "    background-size: 20% auto;"
    html += "    background-repeat: no-repeat;"
    html += "    background-position: left top;"
    html += "}"
    html += "#header {"
    html += "    background-color: transparent;"
    html += "    text-align: center;"
    html += "    padding: 20px;"
    html += "    color: black;"
    html += "}"
    html += "#table-container {"
    html += "    background-color: #4CAF50;"
    html += "    padding: 20px;"
    html += "    overflow-x: auto;"  # Thêm thuộc tính overflow-x để tạo thanh cuộn ngang nếu cần
    html += "}"
    html += "table {"
    html += "    border-collapse: collapse;"
    html += "    width: 100%;"
    html += "    margin: 0 auto;"
    html += "}"
    html += "th, td {"
    html += "    border: 1px solid white;"
    html += "    padding: 10px;"
    html += "    text-align: center;"
    html += "    color: white;"
    html += "}"
    html += "</style>"
    html += "</head><body>"

    html += "<div id='header'>"
    html += "<h1>" + league_name + "</h1>"
    html += "<a href='/live' style='color:#4CAF50; text-decoration:underline;'>LIVE</a>"
    html += "</div>"

    # Table Container
    html += "<div id='table-container'>"
    html += "<table>"
    html += "<tr><th>Entry Name</th><th>Player Name</th><th>Total Points</th><th>Home Points</th><th>Away Points</th><th>Event Transfers</th><th>Total Transfers Cost</th><th>WILDCARD</th><th>BBOOST</th><th>3CX</th><th>Last_value</th><th>Last_bank</th></tr>"

    for user in user_info:
        player_name = user['player_name']
        entry_name = user['entry_name']
        total_points = user['total_points']
        home_points = user['home_points']
        away_points = user['away_points']
        event_note = user['event_note']
        total_transfers_cost = user['total_transfers_cost']
        wildcard_event = user['wildcard_event']
        bboost_event = user['bboost_event']
        cxc_event = user['cxc_event']
        last_bank = user['last_bank']
        last_value = user['last_value']

        # Thêm thông tin người dùng vào bảng
        html += "<tr>"
        html += f"<td>{entry_name}</td>"
        html += f"<td>{player_name}</td>"
        html += f"<td>{total_points}</td>"
        html += f"<td>{home_points}</td>"
        html += f"<td>{away_points}</td>"
        html += f"<td>{event_note}</td>"
        html += f"<td>{total_transfers_cost}</td>"
        html += f"<td>{wildcard_event}</td>"
        html += f"<td>{bboost_event}</td>"
        html += f"<td>{cxc_event}</td>"
        html += f"<td>{last_value}</td>"
        html += f"<td>{last_bank}</td>"
        html += "</tr>"

    html += "</table>"
    html += "</body></html>"
    return html


def generate_json_data_thread():
    while True:
        generate_json_data()
        time.sleep(3600)  # Chờ 10 phút (600 giây) trước khi chạy lại

if __name__ == '__main__':
    thread = threading.Thread(target=generate_json_data_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    app.run(host='0.0.0.0',port=19999)
