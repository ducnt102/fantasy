import json
# Hàm để lấy dữ liệu từ tệp JSON về chip của người dùng
def get_user_chips(user_id):
    with open(f"data/{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'chips' in user_data:
        return user_data['chips']
    return []

def get_active_chip(user_id, event):
    file_name = f"data/{user_id}_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
    if 'active_chip' in data:
        chip = data['active_chip']
        return chip
    else:
        print(f"Yêu cầu get chip không thành công cho {user_id} event {event}")
        return None

def get_live_player_stats(event, user_picks):
    file_name = f"data/events_{str(event)}.json"
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

def get_user_picks(user_id, event):
    with open(f"data/{user_id}_{event}.json", "r") as file:
        data = json.load(file)
    # Kiểm tra xem yêu cầu có thành công không (status code 200)
    if data:
        # Lấy dữ liệu JSON từ phản hồi
        #data = response.json()
        return data
    else:
        print(f"Yêu cầu không thành công cho user_id {user_id}, event {event}")
        return None

def get_user_events(user_id):
    with open(f"data/{user_id}.json", "r") as file:
        user_data = json.load(file)
    if 'current' in user_data:
        return user_data['current']
    return []

def get_live_element_id(event, element_id):
    file_name = f"data/events_{str(event)}.json"
    total_point = 0
    with open(file_name, "r") as file:
        data = json.load(file)        
    if data:
        for player_info in data['elements']:
                    if player_info['id'] == element_id:
                        # Cộng dồn goals_scored và assists
                        total_point = player_info['stats']['total_points']
                        break
        # Trả về tổng số goals_scored và assists
        return total_point
    else:
        print(f"Yêu cầu không thành công cho event {event}")
        return None
