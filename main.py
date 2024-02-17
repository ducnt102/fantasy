from flask import Flask, render_template, request, redirect, url_for, send_from_directory
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
  try:
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
                        captain, vice_captain = get_captain_and_vice_captain(user_id, last_event['event'])
                        captain_name = get_web_name_by_element_id(captain)
                        captain_point = get_live_element_id(last_event['event'],captain) 
                        vice_point = get_live_element_id(last_event['event'],vice_captain)
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
    return render_live_info(user_info,get_league_name(league_id),event_selected['event'],last_event['event'])
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/live')
def live():
  try:
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
                        #last_event_points = last_event.get('points', 0) - last_event_transfers_cost
                        event_transfers = last_event.get('event_transfers', 0)
                        # Sử dụng hàm get_user_picks để lấy thông tin về các lựa chọn
                        user_picks = get_user_picks(user_id, last_event['event'])
                        captain, vice_captain = get_captain_and_vice_captain(user_id, last_event['event'])
                        captain_name = get_web_name_by_element_id(captain)
                        captain_point = get_live_element_id(last_event['event'],captain) 
                        vice_point = get_live_element_id(last_event['event'],vice_captain)
                        vice_name = get_web_name_by_element_id(vice_captain)
                        active_chip= get_active_chip(user_id, last_event['event'])
                        if user_picks:
                            # Sử dụng hàm get_live_player_stats để lấy thông tin về cầu thủ
                            total_goals_scored, total_assists, last_event_points  = get_live_player_stats(last_event['event'], user_picks)
                            last_event_points = last_event_points - last_event_transfers_cost + captain_point
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
                #user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], x['last_event_transfers_cost']), reverse=True)
                user_info.sort(key=lambda x: (x['last_event_points'], x['total_goals_scored'], x['total_assists'], -x['last_event_transfers_cost']), reverse=True)
    return render_live_info(user_info,get_league_name(league_id),last_event['event'],last_event['event'])
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))
# Thêm hàm render_live_info() để tạo HTML cho trang /live

@app.route('/')
def display_user_info():
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
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))    

@app.route('/away')
def display_away_info():
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
                    user_info.sort(key=lambda x: x['away_points'], reverse=True)
    return render_user_info(user_info,get_league_name(league_id))
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/error')
def serve_html():
    return send_from_directory('static', 'error.html')

def generate_json_data_thread():
    while True:
        try: 
            generate_json_data(league_id)
            time.sleep(600)  # Chờ 10 phút (600 giây) trước khi chạy lại
        except ConnectionError as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 10 phút trước khi thử lại
            continue
            time.sleep(600)

if __name__ == '__main__':
    thread = threading.Thread(target=generate_json_data_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    app.run(host='0.0.0.0',port=19999)
