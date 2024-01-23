from util.read import *

def calculate_total_transfers_cost(user_id):
    total_transfers_cost = 0
    user_events = get_user_events(user_id)
    # Lặp qua từng sự kiện và tính tổng event_transfers_cost
    for event in user_events:
        event_transfers_cost = event.get('event_transfers_cost', 0)
        total_transfers_cost += event_transfers_cost
    return total_transfers_cost

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
    if chip_name.lower() != 'wildcard':
        for chip in user_chips:
            if chip['name'].lower() == chip_name.lower():
                return chip.get('event', '')
    else:
        event_note=""
        for chip in user_chips:
            if chip['name'].lower() == chip_name.lower():
                event_number=chip.get('event', '0')
                event_note +=f"{event_number} "
        return event_note
    return ''

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