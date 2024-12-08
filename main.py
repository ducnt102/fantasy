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
    html_file_path = f"data/live.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: Gameweek {current_event_id} not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/')
def display_user_info():
  try:
    html_file_path = f"data/total.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: file not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/away')
def display_away_info():
  try:
    html_file_path = f"data/away.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: file not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/home')
def display_home_info():
  try:
    html_file_path = f"data/home.html"
    with open(html_file_path, "r") as html_file:
        html_content = html_file.read()
        return html_content  # Return the HTML content as the response
  except FileNotFoundError:
    # If the file does not exist, return a 404 error
    return f"<h1>Error 404: file not found.</h1>", 404
  except Exception as e:
    print(e)
    return redirect(url_for('serve_html'))

@app.route('/error')
def serve_html():
    return send_from_directory('static', 'error.html')

def generate_json_data_daily_thread():
    while True:
        try:
            generate_json_data_daily(league_id)
            time.sleep(3600*24)  # Chờ 1 ngày trước khi chạy lại
        except Exception as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 2 phút trước khi thử lại
            continue
            time.sleep(120)

def generate_json_data_hourly_thread():
    while True:
        try:
            generate_json_data_hourly(league_id)
            time.sleep(3600)  # Chờ 1h
        except Exception as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 1 phút trước khi thử lại
            continue
            time.sleep(60)

def generate_json_data_live_thread():
    while True:
        try:
            #render_live_gw_to_file(league_id)
            generate_json_data_live(league_id)
            time.sleep(10)  # Chờ 10 s
        except Exception as e:
            print(f"Error connecting to API: {e}")
            # Nếu gặp lỗi kết nối, chờ 1 phút trước khi thử lại
            continue
            time.sleep(60)

if __name__ == '__main__':
    #get_events_file_live(15)
    #save_fixtures_to_file()
    #save_all_players_full_to_file()
    #render_live_gw_to_file_v2(league_id)
    thread = threading.Thread(target=generate_json_data_daily_thread)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    thread3 = threading.Thread(target=generate_json_data_hourly_thread)
    thread3.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread3.start()
    time.sleep(10)
    thread2 = threading.Thread(target=generate_json_data_live_thread)
    thread2.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread2.start()
    app.run(host='0.0.0.0',port=19999)
