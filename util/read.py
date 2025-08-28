import json
from typing import List, Dict, Any

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

def _get_live_player_stats(event, user_picks):
    file_name = f"data/events_{str(event)}.json"
    with open(file_name, "r") as file:
        data = json.load(file)        
        # Khởi tạo biến để lưu tổng số goals_scored và assists
    if data:
        total_goals_scored = 0
        total_assists = 0
        live_user_points = 0
        # Duyệt qua từng lựa chọn của người chơi
        for user_pick in user_picks['picks']:
            element_id = user_pick['element']
            multiplier = user_pick['multiplier']
            # Kiểm tra điều kiện multiplier !=0
            if multiplier == 1 or multiplier == 2 or multiplier == 3:
                # Tìm thông tin về cầu thủ trong response của API
                for player_info in data['elements']:
                    if player_info['id'] == element_id:
                        # Cộng dồn goals_scored và assists
                        total_goals_scored += player_info['stats']['goals_scored']
                        total_assists += player_info['stats']['assists']
                        live_user_points += player_info['stats']['total_points'] * int(multiplier)
                        break
        # Trả về tổng số goals_scored và assists
        return total_goals_scored, total_assists, live_user_points
    else:
        print(f"Yêu cầu không thành công cho event {event}")
        return None

def get_live_player_stats(event: int, user_picks: Dict[str, Any]):
    """
    Trả về (total_goals_scored, total_assists, live_user_points) cho cả đội.
    Hỗ trợ DGW bằng cách ưu tiên lấy từ 'stats' (đã cộng dồn), nếu thiếu thì cộng từ 'explain'.
    """
    file_name = f"data/events_{str(event)}.json"
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0, 0, 0

    elements = data.get("elements", []) if isinstance(data, dict) else []
    elements_by_id = {e.get("id"): e for e in elements if isinstance(e, dict)}

    total_goals_scored = 0
    total_assists = 0
    live_user_points = 0

    for pick in user_picks.get("picks", []):
        element_id = pick.get("element")
        multiplier = int(pick.get("multiplier", 0) or 0)

        # chỉ tính cầu thủ đang đá (multiplier 1/2/3)
        if multiplier not in (1, 2, 3):
            continue

        p = elements_by_id.get(element_id)
        if not p:
            continue

        stats = p.get("stats") or {}
        g = stats.get("goals_scored")
        a = stats.get("assists")
        tp = stats.get("total_points")

        # Nếu thiếu, tính từ explain
        if g is None or a is None or tp is None:
            g_sum = 0
            a_sum = 0
            tp_sum = 0
            for ex in p.get("explain", []) or []:
                for item in ex.get("stats", []) or []:
                    ident = item.get("identifier")
                    if ident == "goals_scored":
                        g_sum += int(item.get("value", 0) or 0)
                    elif ident == "assists":
                        a_sum += int(item.get("value", 0) or 0)
                    # 'points' là điểm cho từng chỉ tiêu ở 1 fixture
                    tp_sum += int(item.get("points", 0) or 0)
            if g is None:
                g = g_sum
            if a is None:
                a = a_sum
            if tp is None:
                tp = tp_sum

        total_goals_scored += int(g or 0)
        total_assists += int(a or 0)
        live_user_points += int(tp or 0) * multiplier

    return total_goals_scored, total_assists, live_user_points

def _get_pick_live_players_v2(
    event: int, 
    user_picks: Dict[str, Any], 
    all_bonus_points: Dict[int, Dict[int, float]], 
    player_info_path: str = "data/player_full_info.json"
) -> List[Dict[str, Any]]:
    file_name = f"data/events_{str(event)}.json"
    try:
        try:
            with open(file_name, "r", encoding="utf-8") as event_file:
                event_data = json.load(event_file)
        except Exception as e:
            print(f"[WARN] Cannot load {file_name}: {e}")
            event_data = {}

        try:
            with open(player_info_path, "r", encoding="utf-8") as player_file:
                player_info_dict = json.load(player_file)
        except Exception as e:
            print(f"[WARN] Cannot load {player_info_path}: {e}")
            player_info_dict = {}

        picks = []
        if isinstance(user_picks, dict):
            picks = user_picks.get("picks") or []
            if not isinstance(picks, list):
                picks = []

        elements = event_data.get("elements") or []
        if not isinstance(elements, list):
            elements = []

        players_info: List[Dict[str, Any]] = []

        for user_pick in picks:
            element_id = (user_pick or {}).get("element", 0) or 0
            # BỎ QUA pick không hợp lệ (0 hoặc thiếu)
            if not isinstance(element_id, int) or element_id <= 0:
                continue

            multiplier = (user_pick or {}).get("multiplier", 0) or 0
            is_captain = bool((user_pick or {}).get("is_captain", False))
            is_vice_captain = bool((user_pick or {}).get("is_vice_captain", False))
            position = (user_pick or {}).get("position", 0) or 0

            info_from_dict = player_info_dict.get(str(element_id), {}) if isinstance(player_info_dict, dict) else {}
            player_details = {
                "ID": element_id,
                "web_name": info_from_dict.get("web_name", "Unknown"),
                "point": 0,
                "bonus": 0,
                "expected_bonus": 0,
                "element_type": info_from_dict.get("element_type", 0) or 0,
                "minutes": 0,
                "multiplier": multiplier,
                "is_captain": is_captain,
                "is_vice_captain": is_vice_captain,
                "running": False,
                "position": position,
                "fixture": 0
            }

            # Tìm player trong event_data
            player_obj = None
            for p in elements:
                try:
                    if p.get("id") == element_id:
                        player_obj = p
                        break
                except Exception:
                    continue

            # Nếu không có trong events_<gw>.json -> bỏ qua để tránh out-of-index ở explain
            if not player_obj:
                continue

            stats = player_obj.get("stats") or {}
            player_details["point"] = stats.get("total_points", 0) or 0
            player_details["bonus"] = stats.get("bonus", 0) or 0
            player_details["minutes"] = stats.get("minutes", 0) or 0

            # explain có thể rỗng
            fixture_id = 0
            explain_data = player_obj.get("explain")
            if isinstance(explain_data, list) and len(explain_data) > 0:
                first_exp = explain_data[0] or {}
                fixture_id = first_exp.get("fixture", 0) or 0
            player_details["fixture"] = fixture_id

            # Bonus kỳ vọng + running
            fixture_key_int = fixture_id
            fixture_key_str = str(fixture_id)
            abp_entry = (
                all_bonus_points.get(fixture_key_int)
                or all_bonus_points.get(fixture_key_str)
                or {}
            )
            bonus_points_map = abp_entry.get("bonus_points") or {}
            if not isinstance(bonus_points_map, dict):
                bonus_points_map = {}
            player_details["expected_bonus"] = bonus_points_map.get(element_id, 0) or 0
            player_details["running"] = bool(abp_entry.get("running", False))

            players_info.append(player_details)

        return players_info

    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return []

def get_pick_live_players_v2(
    event: int, 
    user_picks: Dict[str, Any], 
    all_bonus_points: Dict[int, Dict[int, float]], 
    player_info_path: str = "data/player_full_info.json"
) -> List[Dict[str, Any]]:
    """
    Đọc data/events_<gw>.json và trả về danh sách các cầu thủ trong đội hình của user
    (đã gộp bonus dự kiến cho tất cả các fixture nếu là Double/Triple GW).
    all_bonus_points: dict[fixture_id] -> {"bonus_points": {element_id: bonus}, "running": bool}
    """
    file_name = f"data/events_{str(event)}.json"

    # Tải event live
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            event_data = json.load(f)
    except Exception:
        event_data = {}

    elements = event_data.get("elements", []) if isinstance(event_data, dict) else []
    elements_by_id = {e.get("id"): e for e in elements if isinstance(e, dict)}

    # Thông tin tên cầu thủ, vị trí
    try:
        with open(player_info_path, "r", encoding="utf-8") as f:
            player_info_dict = json.load(f) or {}
    except Exception:
        player_info_dict = {}

    players_info: List[Dict[str, Any]] = []

    for user_pick in user_picks.get("picks", []):
        element_id = user_pick.get("element")
        multiplier = int(user_pick.get("multiplier", 0) or 0)
        is_captain = bool(user_pick.get("is_captain", False))
        is_vice_captain = bool(user_pick.get("is_vice_captain", False))
        position = user_pick.get("position")

        info_from_dict = player_info_dict.get(str(element_id), {})

        player_details: Dict[str, Any] = {
            "ID": element_id,
            "web_name": info_from_dict.get("web_name", "Unknown"),
            "point": 0,
            "bonus": 0,
            "expected_bonus": 0,
            "element_type": info_from_dict.get("element_type", 0) or 0,
            "minutes": 0,
            "multiplier": multiplier,
            "is_captain": is_captain,
            "is_vice_captain": is_vice_captain,
            "running": False,
            "position": position,
            "fixture": 0,   # giữ nguyên field cũ để không phá UI hiện có
        }

        player_obj = elements_by_id.get(element_id)
        if not player_obj:
            players_info.append(player_details)
            continue

        stats = player_obj.get("stats") or {}
        player_details["point"] = int(stats.get("total_points", 0) or 0)
        player_details["bonus"] = int(stats.get("bonus", 0) or 0)
        player_details["minutes"] = int(stats.get("minutes", 0) or 0)

        # Lấy tất cả fixture_id mà cầu thủ xuất hiện trong GW này (DGW/TGW)
        explain = player_obj.get("explain") or []
        fixture_ids: List[int] = []
        for ex in explain:
            try:
                fid = ex.get("fixture")
                if isinstance(fid, int):
                    fixture_ids.append(fid)
            except Exception:
                continue

        if fixture_ids:
            # Giữ lại fixture cuối cùng để tương thích với UI cũ
            player_details["fixture"] = fixture_ids[-1]

            # Tổng expected_bonus trên tất cả fixture trong GW
            expected_bonus_sum = 0
            running_any = False
            for fid in fixture_ids:
                # all_bonus_points có thể dùng key int hoặc str
                abp_entry = (
                    all_bonus_points.get(fid)
                    or all_bonus_points.get(str(fid))
                    or {}
                )
                bp_map = abp_entry.get("bonus_points") or {}
                expected_bonus_sum += int(bp_map.get(element_id, 0) or 0)
                running_any = running_any or bool(abp_entry.get("running", False))

            player_details["expected_bonus"] = expected_bonus_sum
            player_details["running"] = running_any

        players_info.append(player_details)

    return players_info

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

def _get_live_element_id(event, element_id):
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
        return 

def get_live_element_id(event: int, element_id: int) -> int:
    """
    Trả về tổng điểm live của 1 cầu thủ trong GW (đã cộng dồn nếu là DGW).
    Ưu tiên lấy từ field 'stats.total_points'. Nếu không có, fallback tính từ 'explain'.
    """
    file_name = f"data/events_{str(event)}.json"
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0

    elements = data.get("elements", []) if isinstance(data, dict) else []
    for p in elements:
        try:
            if p.get("id") != element_id:
                continue

            # 1) Có sẵn tổng ở 'stats'
            stats = p.get("stats") or {}
            if "total_points" in stats:
                return int(stats.get("total_points", 0) or 0)

            # 2) Fallback: cộng điểm từ explain
            total_points = 0
            for ex in p.get("explain", []) or []:
                for item in ex.get("stats", []) or []:
                    # FPL trả về 'points' cho từng chỉ tiêu ở fixture; cộng tất cả lại
                    total_points += int(item.get("points", 0) or 0)
            return total_points
        except Exception:
            continue

    return 0