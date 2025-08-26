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

league_id = 816786


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

def generate_json_data_with_priority():
    # Time trackers
    last_daily_run = None
    last_hourly_run = None
    while True:
        try:
            current_time = datetime.now()
            # Check and run the daily task
            if last_daily_run is None or current_time - last_daily_run >= timedelta(days=1):
                print("Running daily task...")
                generate_json_data_daily(league_id)
                last_daily_run = current_time
                continue  # Skip other tasks for this iteration to give priority to daily
            # Check and run the hourly task
            if last_hourly_run is None or current_time - last_hourly_run >= timedelta(hours=1):
                print("Running hourly task...")
                generate_json_data_hourly(league_id)
                last_hourly_run = current_time
                continue  # Skip live task for this iteration to give priority to hourly
            # Run the live task every 10 seconds
            print("Running live task...")
            generate_json_data_live(league_id)
            time.sleep(10)  # Wait 10 seconds before the next iteration
        except Exception as e:
            print(f"Error connecting to API: {e}")
            time.sleep(60)  # Wait 1 minute before retrying in case of errors

if __name__ == '__main__':
    render_live_gw_to_file_v2(league_id)
    thread = threading.Thread(target=generate_json_data_with_priority)
    thread.daemon = True  # Đặt thread thành daemon để nó tự động dừng khi ứng dụng Flask kết thúc
    thread.start()
    app.run(host='0.0.0.0',port=19999)
