from flask import Flask
import threading
import requests
import json
import time

app = Flask(__name__)

league_id = 169451

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

                # Kiểm tra xem danh sách kết quả có rỗng không
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
                            'cxc_event': cxc_event
                        })

                    # Sắp xếp theo tổng điểm từ cao đến thấp
                    user_info.sort(key=lambda x: x['total_points'], reverse=True)
    return render_user_info(user_info)

def render_user_info(user_info):
    # Tạo HTML cho bảng thông tin người dùng
    html = "<h1>KANAMA FANTASY</h1>"
    html += "<table border='1'>"
    html += "<tr><th>Entry Name</th><th>Player Name</th><th>Total Points</th><th>Home Points</th><th>Away Points</th><th>Event Transfers</th><th>Total Transfers Cost</th><th>WILDCARD</th><th>BBOOST</th><th>3CX</th></tr>"

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
        html += "</tr>"

    html += "</table>"
    return html

def generate_json_data_thread():
    while True:
        generate_json_data()
        time.sleep(60)  # Chờ 10 phút (600 giây) trước khi chạy lại

if __name__ == '__main__':
    thread = threading.Thread(target=generate_json_data_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    app.run(host='0.0.0.0',port=19999)
