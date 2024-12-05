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

league_id = 460675


@app.route('/gw')
def gw():
  try:
    selected_event = int(request.args.get('selected_event', 0))  # Lấy event từ request, mặc định là 0 nếu không có
    html_file_path = f"data/gw_{selected_event}.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: Gameweek {selected_event} not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/live')
def live():
  try:
    current_event_id, finished_status = get_current_event()
    html_file_path = f"data/gw_{current_event_id}.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: Gameweek {selected_event} not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

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
    return render_user_info(user_info,get_league_name(league_id))
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/error')
def serve_html():
    return send_from_directory('static', 'error.html')

def generate_json_data_daily_thread():
    while True:
        try: 
            render_old_gw_to_file(league_id)
            generate_json_data_daily(league_id)
            time.sleep(3600*24)  # Chờ 10 phút (600 giây) trước khi chạy lại
        except Exception as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 2 phút trước khi thử lại
            continue
            time.sleep(120)
def generate_json_data_live_thread():
    while True:
        try: 
            render_live_gw_to_file(league_id)
            generate_json_data_live(league_id)
            time.sleep(60)  # Chờ 10 phút (600 giây) trước khi chạy lại
        except Exception as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 10 phút trước khi thử lại
            continue
            time.sleep(120)

if __name__ == '__main__':
    #render_old_gw_to_file(league_id)
    thread = threading.Thread(target=generate_json_data_daily_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()

    thread2 = threading.Thread(target=generate_json_data_live_thread)
    thread2.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread2.start()
    app.run(host='0.0.0.0',port=19999)
