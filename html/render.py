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
    html += "<a href='/' style='color:#4CAF50; text-decoration;'>Home </a>"
    html += "<a href='/away' style='color:#4CAF50; text-decoration;'>Away </a>"
    html += "<a href='/live' style='color:#4CAF50; text-decoration;'>    GW</a><br>"
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


def render_live_info(user_info, league_name, gw_id, last_gw):
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
    html += "    position: relative;"
    html += "    z-index: 1;"
    html += "}"
    html += "#table-container {"
    html += "    background-color: #4CAF50;"
    html += "    padding: 20px;"
    html += "    overflow-x: auto; /* Allow horizontal scrolling */"
    html += "    position: relative;"
    html += "    z-index: 0;"
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
    # Header
    html += "<div id='header'>"
    html += "<h1>" + league_name + " - GW " + str(gw_id) + "</h1>"
    html += "<a href='/' style='color:#4CAF50; text-decoration;'> Home </a>"
    html += "<a href='/away' style='color:#4CAF50; text-decoration;'> Away</a><br>"
    for event_id in range(1, last_gw + 1):
        html += "<a href='/gw?selected_event=" + str(event_id) + "' style='color:#4CAF50; text-decoration;'>" + str(
            event_id) + "</a> "
    html += "</div>"
    # Table Container
    html += "<div id='table-container'>"
    # Bổ sung thông tin về các lựa chọn, event_transfers và live_player_stats vào trang HTML
    html += "<table>"
    html += "<tr><th>Entry Name</th><th>Player Name</th><th>Total Points</th><th>Points</th><th>Active Chip</th><th>Event Transfers</th><th>Transfers Cost</th><th>Total Goals(Not Bench)</th><th>Total Assists(Not Bench)</th><th>Captain</th><th>Vice</th><th>Captain Point</th></tr>"
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
        captain_name = user['captain_name']
        vice_name = user['vice_name']
        captain_point = user['captain_point']
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
        html += f"<td>{captain_name}</td>"
        html += f"<td>{vice_name}</td>"
        html += f"<td>{captain_point}</td>"
        html += "</tr>"
    html += "</table>"
    html += "</body></html>"
    return html

