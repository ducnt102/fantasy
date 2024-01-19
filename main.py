from flask import Flask
import threading
import requests
import json
import time
from flask import request
from util.write import *
from util.read import *
from util.api import *
from src.logic import *
from html.render import *

app = Flask(__name__)

league_id = 169451


@app.route('/gw')
def gw():
    with open("data/league_id.json", "r") as file:
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
    return render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event'])

@app.route('/live')
def live():
    with open("data/league_id.json", "r") as file:
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
    return render_live_info(user_info,get_league_name(league_id),last_event['event'],last_event['event'])

# Thêm hàm render_live_info() để tạo HTML cho trang /live
def render_live_info(user_info,league_name,gw_id,last_gw):
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
    html += "<h1>" + league_name + " - GW " + str(gw_id) +  "</h1>"
    html += "<a href='/' style='color:#4CAF50; text-decoration:underline;'>Home</a><br>"
    for event_id in range(1, last_gw+1):
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


def generate_json_data_thread():
    while True:
        generate_json_data(league_id)
        time.sleep(600)  # Chờ 10 phút (600 giây) trước khi chạy lại

if __name__ == '__main__':
    thread = threading.Thread(target=generate_json_data_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    app.run(host='0.0.0.0',port=19999)
