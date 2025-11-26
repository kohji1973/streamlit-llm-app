"""
タクシー配車アプリケーション
- フロント端末（ホテルなど）：リクエスト送信
- ドライバー端末：リクエスト受信・承認
- 位置情報ベースの距離計算とマッチング
"""

import streamlit as st
import math
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

# ページ設定
st.set_page_config(
    page_title="takutakutaxi",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# データファイルのパス
# ⚠️ Streamlit Cloudでは、ファイルシステムへの書き込みは一時的です
# 本番環境では、データベース（SQLite、PostgreSQL、Firebase等）の使用を推奨します
DATA_DIR = "taxi_data"
REQUESTS_FILE = os.path.join(DATA_DIR, "requests.json")
DRIVERS_FILE = os.path.join(DATA_DIR, "drivers.json")

# データディレクトリの作成
os.makedirs(DATA_DIR, exist_ok=True)


def load_requests() -> Dict:
    """JSONファイルからリクエストを読み込む"""
    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # datetime文字列をdatetimeオブジェクトに変換
                for req_id, req_data in data.items():
                    if 'created_at' in req_data and isinstance(req_data['created_at'], str):
                        req_data['created_at'] = datetime.fromisoformat(req_data['created_at'])
                    if 'assigned_at' in req_data and req_data['assigned_at'] and isinstance(req_data['assigned_at'], str):
                        req_data['assigned_at'] = datetime.fromisoformat(req_data['assigned_at'])
                    if 'arrived_at' in req_data and req_data['arrived_at'] and isinstance(req_data['arrived_at'], str):
                        req_data['arrived_at'] = datetime.fromisoformat(req_data['arrived_at'])
                    if 'departed_at' in req_data and req_data['departed_at'] and isinstance(req_data['departed_at'], str):
                        req_data['departed_at'] = datetime.fromisoformat(req_data['departed_at'])
                    if 'completed_at' in req_data and req_data['completed_at'] and isinstance(req_data['completed_at'], str):
                        req_data['completed_at'] = datetime.fromisoformat(req_data['completed_at'])
                return data
        except json.JSONDecodeError:
            # JSONファイルが壊れている場合は空の辞書を返す
            return {}
        except Exception as e:
            # エラーはログに記録するが、UIには表示しない（初期化時は表示できないため）
            print(f"データ読み込みエラー: {e}")
            return {}
    return {}


def save_requests(requests: Dict):
    """リクエストをJSONファイルに保存"""
    try:
        # datetimeオブジェクトを文字列に変換
        data_to_save = {}
        for req_id, req_data in requests.items():
            req_copy = req_data.copy()
            if 'created_at' in req_copy and req_copy['created_at']:
                if isinstance(req_copy['created_at'], datetime):
                    req_copy['created_at'] = req_copy['created_at'].isoformat()
            if 'assigned_at' in req_copy and req_copy['assigned_at']:
                if isinstance(req_copy['assigned_at'], datetime):
                    req_copy['assigned_at'] = req_copy['assigned_at'].isoformat()
            if 'arrived_at' in req_copy and req_copy['arrived_at']:
                if isinstance(req_copy['arrived_at'], datetime):
                    req_copy['arrived_at'] = req_copy['arrived_at'].isoformat()
            if 'departed_at' in req_copy and req_copy['departed_at']:
                if isinstance(req_copy['departed_at'], datetime):
                    req_copy['departed_at'] = req_copy['departed_at'].isoformat()
            if 'completed_at' in req_copy and req_copy['completed_at']:
                if isinstance(req_copy['completed_at'], datetime):
                    req_copy['completed_at'] = req_copy['completed_at'].isoformat()
            data_to_save[req_id] = req_copy
        
        with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"データ保存エラー: {e}")


def load_drivers() -> Dict:
    """JSONファイルからドライバー情報を読み込む"""
    if os.path.exists(DRIVERS_FILE):
        try:
            with open(DRIVERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # datetime文字列をdatetimeオブジェクトに変換
                for driver_id, driver_data in data.items():
                    if 'updated_at' in driver_data and isinstance(driver_data['updated_at'], str):
                        driver_data['updated_at'] = datetime.fromisoformat(driver_data['updated_at'])
                return data
        except json.JSONDecodeError:
            # JSONファイルが壊れている場合は空の辞書を返す
            return {}
        except Exception as e:
            # エラーはログに記録するが、UIには表示しない（初期化時は表示できないため）
            print(f"データ読み込みエラー: {e}")
            return {}
    return {}


def save_drivers(drivers: Dict):
    """ドライバー情報をJSONファイルに保存"""
    try:
        # datetimeオブジェクトを文字列に変換
        data_to_save = {}
        for driver_id, driver_data in drivers.items():
            driver_copy = driver_data.copy()
            if 'updated_at' in driver_copy:
                driver_copy['updated_at'] = driver_copy['updated_at'].isoformat()
            data_to_save[driver_id] = driver_copy
        
        with open(DRIVERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"データ保存エラー: {e}")


# セッション状態の初期化（ファイルから読み込み）
if 'requests' not in st.session_state:
    st.session_state.requests = load_requests()

if 'drivers' not in st.session_state:
    st.session_state.drivers = load_drivers()

if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

if 'auto_refresh_enabled' not in st.session_state:
    st.session_state.auto_refresh_enabled = False

if 'driver_has_active_request' not in st.session_state:
    st.session_state.driver_has_active_request = False


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    2点間の距離を計算（ハーバーサイン公式）
    戻り値: キロメートル
    """
    R = 6371  # 地球の半径（km）
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def estimate_arrival_time(distance_km: float) -> int:
    """
    距離から到着時間を推定（分）
    平均速度: 30km/h（市街地想定）
    """
    speed_kmh = 30
    time_hours = distance_km / speed_kmh
    return int(time_hours * 60)


def find_nearest_drivers(request_lat: float, request_lon: float, 
                        available_drivers: Dict) -> List[tuple]:
    """
    利用可能なドライバーを距離順にソート
    戻り値: [(ドライバーID, 距離, ドライバー情報), ...]
    """
    driver_distances = []
    
    for driver_id, driver_info in available_drivers.items():
        if driver_info.get('status') == 'available':
            distance = calculate_distance(
                request_lat, request_lon,
                driver_info['lat'], driver_info['lon']
            )
            driver_distances.append((driver_id, distance, driver_info))
    
    # 距離でソート
    driver_distances.sort(key=lambda x: x[1])
    return driver_distances


def frontend_page():
    """フロント端末（ホテルなど）のページ"""
    try:
        # 最新データを読み込み（フロント側は常に最新状態を表示）
        # ファイルから最新のデータを読み込んでセッション状態を更新
        latest_requests = load_requests()
        # セッション状態を最新データで完全に更新
        if latest_requests:
            st.session_state.requests = latest_requests
        st.session_state.last_update = time.time()

        # ポップなデザインのCSS
        st.markdown("""
        <style>
        /* Streamlitのデフォルト余白を削減 */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
        }
        .taxi-main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 0.5rem 1rem;
            min-height: auto;
        }
        .taxi-title {
            font-size: 3rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        .taxi-button-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 1.5rem 0;
        }
        .taxi-circle-button {
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            border: none;
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            cursor: pointer;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        .taxi-circle-button:hover {
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.6);
        }
        .taxi-circle-button:active {
            transform: scale(0.95);
        }
        .taxi-circle-button::before {
            content: '🚕';
            font-size: 4rem;
            position: absolute;
            top: 20%;
            animation: bounce 2s ease-in-out infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .taxi-status-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 20px;
            padding: 1rem;
            margin: 0.5rem auto;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 800px;
        }
        .taxi-success {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            color: #2d3748;
            padding: 0.8rem 1rem;
            border-radius: 15px;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            margin: 0.3rem 0;
            line-height: 1.4;
        }
        .taxi-success-info {
            background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
            color: #2d3748;
            padding: 0.8rem 1rem;
            border-radius: 15px;
            font-size: 1rem;
            text-align: center;
            margin: 0.3rem 0;
        }
        .taxi-arrived {
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
            color: #ffffff;
            padding: 0.8rem 1rem;
            border-radius: 15px;
            font-size: 1rem;
            font-weight: bold;
            text-align: center;
            margin: 0.3rem 0;
            line-height: 1.4;
            border: 2px solid #4caf50;
        }
        .request-info-line {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 1rem;
            margin: 0.3rem 0;
            flex-wrap: wrap;
        }
        .request-info-item {
            display: inline-block;
        }
        /* 「最新状況を更新」ボタンをリクエストカードと同じ幅に、赤枠で */
        .refresh-button-wrapper {
            max-width: 800px;
            margin: 0.5rem auto;
            text-align: center;
        }
        .refresh-button-wrapper button {
            width: 100% !important;
            max-width: 800px !important;
            border: 2px solid #dc3545 !important;
            background-color: white !important;
            color: #dc3545 !important;
            font-weight: bold;
        }
        .refresh-button-wrapper button:hover {
            background-color: #dc3545 !important;
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # 現在地の設定（非表示、デフォルト値を使用）
        if 'front_lat' not in st.session_state:
            st.session_state.front_lat = 35.6762  # 東京駅の例
        if 'front_lon' not in st.session_state:
            st.session_state.front_lon = 139.6503  # 東京駅の例
        
        # メインコンテナ（上部に配置、中央揃え）
        st.markdown('<div class="taxi-main-container">', unsafe_allow_html=True)
        st.markdown('<div class="taxi-title">🚕 takutakutaxi</div>', unsafe_allow_html=True)
        
        # 中央の大きなボタン
        st.markdown('<div class="taxi-button-container">', unsafe_allow_html=True)
        
        # カスタムボタンの実装（Streamlitのボタンを使用）
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            button_clicked = st.button(
                "taxiを呼ぶ",
                type="primary",
                use_container_width=True,
                key="call_taxi_button"
            )
            # ボタンのスタイルをカスタマイズ（拡大アニメーション付き、ホバーでピンク調）
            st.markdown("""
            <style>
            @keyframes buttonScale {
                0% {
                    transform: scale(1.0);
                }
                30% {
                    transform: scale(1.03);
                }
                31% {
                    transform: scale(1.0);
                }
                100% {
                    transform: scale(1.0);
                }
            }
            div[data-testid="stButton"] > button[kind="primary"] {
                width: 100%;
                height: 200px;
                border-radius: 100px;
                font-size: 3rem;
                font-weight: bold;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                border: 2px solid #cccccc;
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
                position: relative;
                transition: background 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
                animation: buttonScale 3s ease-in-out infinite;
            }
            div[data-testid="stButton"] > button[kind="primary"]::before {
                content: '🚕 ';
            }
            div[data-testid="stButton"] > button[kind="primary"]::after {
                content: '';
                position: absolute;
                top: 3%;
                left: 3%;
                right: 3%;
                bottom: 3%;
                border-radius: 100px;
                background: rgba(255, 255, 255, 0.03);
                pointer-events: none;
                box-shadow: inset 0 0 20px rgba(255, 255, 255, 0.03);
            }
            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #f093fb 100%);
                box-shadow: 0 15px 40px rgba(245, 87, 108, 0.6);
                border-color: #dddddd;
                animation-play-state: paused;
            }
            </style>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ボタンがクリックされたときの処理
        if button_clicked:
            # 新しいリクエストを作成
            request_id = str(uuid.uuid4())
            request_data = {
                'id': request_id,
                'front_lat': st.session_state.front_lat,
                'front_lon': st.session_state.front_lon,
                'destination': 'フロント',  # デフォルト値
                'passenger_name': '',
                'special_requests': '',
                'status': 'pending',  # pending, assigned, arrived, departed, completed
                'created_at': datetime.now(),
                'assigned_driver': None,
                'driver_name': None,
                'estimated_arrival': None,
                'car_number': None,
                'arrived_at': None,
                'departed_at': None,
                'completed_at': None
            }
            
            st.session_state.requests[request_id] = request_data
            save_requests(st.session_state.requests)  # ファイルに保存
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('<div class="taxi-success">✅ リクエストを送信しました！<br>ドライバーを探しています...</div>', unsafe_allow_html=True)
            time.sleep(0.5)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 「最新状況を更新」ボタンを「taxiを呼ぶ」ボタンの直下に配置（リクエストカードと同じ横幅、赤枠）
        st.markdown('<div class="refresh-button-wrapper">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            refresh_clicked = st.button("最新状況を更新", use_container_width=True, key="refresh_status_button")
            if refresh_clicked:
                try:
                    # 最新データを読み込んでセッション状態を確実に更新
                    latest_requests = load_requests()
                    if latest_requests:
                        st.session_state.requests = latest_requests.copy()
                    st.session_state.last_update = time.time()
                    st.success("✅ 最新状況を更新しました")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"更新エラー: {e}")
                    # データを再読み込み
                    try:
                        st.session_state.requests = load_requests()
                    except:
                        pass
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 現在のリクエスト状況（古い順に表示、departedとcompleted状態は除外）
        active_requests = []
        if st.session_state.requests:
            # pending、assigned、arrived状態のリクエストを取得（departedとcompleted状態は除外）
            for req_id, req_data in st.session_state.requests.items():
                status = req_data.get('status')
                if status in ['pending', 'assigned', 'arrived']:
                    active_requests.append((req_id, req_data))
            
            # 状態優先順位でソート（到着済み > 向かっています > 待機中）、同じ状態内では古い順
            status_priority = {'arrived': 0, 'assigned': 1, 'pending': 2}
            active_requests.sort(key=lambda x: (status_priority.get(x[1].get('status'), 99), x[1]['created_at']))
        
        if active_requests:
            st.markdown('<div class="taxi-status-card">', unsafe_allow_html=True)
            st.markdown("### 📋 現在のリクエスト状況")
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            
            # リクエストを古い順に表示
            for idx, (req_id, req_data) in enumerate(active_requests, 1):
                if idx > 1:
                    st.markdown('<div style="margin: 0.2rem 0;"></div>', unsafe_allow_html=True)
                
                if req_data['status'] == 'pending':
                    st.markdown(f"""
                    <div class="taxi-success-info">
                        📋 リクエスト #{idx} - リクエスト時刻: {req_data['created_at'].strftime('%H:%M:%S')}<br>
                        ⏳ ドライバーを探しています...
                    </div>
                    """, unsafe_allow_html=True)
                elif req_data['status'] == 'assigned':
                    driver_name_display = req_data.get('driver_name', '未設定')
                    car_number_display = req_data.get('car_number', '未設定')
                    arrival_time_display = req_data.get('estimated_arrival', 0)
                    st.markdown(f"""
                    <div class="taxi-success">
                        🚕 リクエスト #{idx} - タクシーが向かっています<br>
                        📅 リクエスト時刻: {req_data['created_at'].strftime('%H:%M:%S')}<br>
                        <div class="request-info-line">
                            <span class="request-info-item">👤 {driver_name_display}</span>
                            <span class="request-info-item">🚗 {car_number_display}</span>
                            <span class="request-info-item">⏰ 到着予定: {arrival_time_display}分後</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                elif req_data['status'] == 'arrived':
                    driver_name_display = req_data.get('driver_name', '未設定')
                    car_number_display = req_data.get('car_number', '未設定')
                    st.markdown(f"""
                    <div class="taxi-arrived">
                        ✅ リクエスト #{idx} - 到着しました<br>
                        📅 リクエスト時刻: {req_data['created_at'].strftime('%H:%M:%S')}<br>
                        <div class="request-info-line">
                            <span class="request-info-item">👤 {driver_name_display}</span>
                            <span class="request-info-item">🚗 {car_number_display}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="taxi-status-card">', unsafe_allow_html=True)
            st.markdown("### 📋 現在のリクエスト状況")
            st.info("現在、アクティブなリクエストはありません")
            st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.exception(e)


def driver_page():
    """ドライバー端末のページ"""
    try:
        # カスタムCSS（運転に集中できるシンプルなデザイン）
        st.markdown("""
        <style>
        .driver-main-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        .driver-info-small {
            font-size: 0.8rem;
            color: #666;
            margin: 0.5rem 0;
        }
        .driver-big-button {
            height: 150px;
            font-size: 2rem;
            font-weight: bold;
            border-radius: 15px;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.title("🚗 ドライバー端末")
        
        # ドライバーIDを取得（最初に設定）
        # 前回のIDを保持（IDが変更されたときに検知するため）
        if 'previous_driver_id' not in st.session_state:
            st.session_state.previous_driver_id = 'driver_001'
        
        previous_driver_id = st.session_state.previous_driver_id
        
        # 前回のIDでassigned、arrived、departed状態のリクエストがあるか確認（完了まで変更不可）
        has_active_assignment_previous = False
        if previous_driver_id:
            for rid, rinfo in st.session_state.requests.items():
                if rinfo.get('assigned_driver') == previous_driver_id and rinfo.get('status') in ['assigned', 'arrived', 'departed']:
                    has_active_assignment_previous = True
                    break
        
        driver_id = st.text_input(
            "ドライバーID",
            value=previous_driver_id,
            key="driver_id_input",
            disabled=has_active_assignment_previous
        )
        
        # ドライバーIDが変更されたか確認（リクエスト処理中でない場合のみ）
        if driver_id != previous_driver_id and not has_active_assignment_previous:
            # IDが変更された場合、選択されたIDの情報のみをファイルから読み込む
            file_drivers = load_drivers()
            # 選択されたIDの情報のみをファイルから読み込んで更新（他のドライバー情報は保持）
            if driver_id in file_drivers:
                st.session_state.drivers[driver_id] = file_drivers[driver_id]
            # 他のドライバーIDの情報もファイルから読み込む（存在する場合のみ）
            for did, dinfo in file_drivers.items():
                if did not in st.session_state.drivers:
                    st.session_state.drivers[did] = dinfo
            st.session_state.previous_driver_id = driver_id
        elif driver_id != previous_driver_id and has_active_assignment_previous:
            # リクエスト処理中（assigned、arrived、departed状態）の場合、ID変更を防ぐ
            st.warning("⚠️ リクエスト処理中はドライバーIDを変更できません。送迎完了後に変更してください。")
            driver_id = previous_driver_id  # 元のIDに戻す
            st.rerun()
        
        # 現在のドライバー情報を取得
        current_driver = st.session_state.drivers.get(driver_id) if driver_id else None
        
        # このドライバーにassigned、arrived、departed状態のリクエストがあるか確認（完了まで変更不可）
        has_active_assignment = False
        if driver_id:
            for rid, rinfo in st.session_state.requests.items():
                if rinfo.get('assigned_driver') == driver_id and rinfo.get('status') in ['assigned', 'arrived', 'departed']:
                    has_active_assignment = True
                    break
        
        # ドライバー情報の設定（折りたたみ可能、コンパクト）
        with st.expander("👤 ドライバー情報設定", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                driver_name = st.text_input("名前", placeholder="例：佐藤", key="driver_name_input", value=current_driver.get('name', '') if current_driver else '')
            
            with col2:
                car_number = st.text_input("車番", placeholder="例：品川 あ 1234", key="car_number_input", value=current_driver.get('car_number', '') if current_driver else '')
            
            with col3:
                driver_lat = st.number_input(
                    "緯度",
                    value=current_driver.get('lat', 35.6812) if current_driver else 35.6812,
                    format="%.4f",
                    step=0.0001,
                    key="driver_lat"
                )
            
            col4, col5, col6 = st.columns(3)
            with col4:
                driver_lon = st.number_input(
                    "経度",
                    value=current_driver.get('lon', 139.7671) if current_driver else 139.7671,
                    format="%.4f",
                    step=0.0001,
                    key="driver_lon"
                )
            
            with col5:
                status = st.radio(
                    "ステータス",
                    ["available", "busy"],
                    index=0 if not current_driver or current_driver.get('status') == 'available' else 1,
                    horizontal=True,
                    key="driver_status"
                )
            
            with col6:
                st.write("")  # スペーサー
                if st.button("💾 更新", type="primary"):
                    if not driver_id:
                        st.error("ドライバーIDを入力してください")
                    elif not car_number:
                        st.error("車番を入力してください")
                    else:
                        # このドライバーの情報のみを更新（他のドライバーには影響しない）
                        # 最新のドライバー情報を読み込んでマージ
                        latest_drivers = load_drivers()
                        # ファイルから読み込んだ情報と現在のセッション状態をマージ
                        for did, dinfo in latest_drivers.items():
                            if did not in st.session_state.drivers:
                                st.session_state.drivers[did] = dinfo
                        
                        # このドライバーの情報のみを更新
                        st.session_state.drivers[driver_id] = {
                            'id': driver_id,
                            'name': driver_name,
                            'car_number': car_number,
                            'lat': driver_lat,
                            'lon': driver_lon,
                            'status': status,
                            'updated_at': datetime.now()
                        }
                        save_drivers(st.session_state.drivers)
                        st.success(f"✅ ドライバーID: {driver_id}の情報を更新しました")
                        time.sleep(0.5)
                        st.rerun()
        
        st.markdown("---")
        
        # 最新のリクエストデータを読み込み（他のセッションからの更新を取得）
        latest_requests = load_requests()
        st.session_state.requests = latest_requests
        
        # このドライバーに割り当てられたassigned、arrived、departed状態のリクエストを取得（完了まで保持）
        my_active_assignment = None
        if driver_id:
            for rid, rinfo in st.session_state.requests.items():
                if rinfo.get('assigned_driver') == driver_id and rinfo.get('status') in ['assigned', 'arrived', 'departed']:
                    my_active_assignment = (rid, rinfo)
                    break
        
        # リクエスト受諾後の状態をセッション状態に保存（サイドバーのボタン無効化に使用）
        st.session_state.driver_has_active_request = (my_active_assignment is not None)
        
        # このドライバーに割り当てられたリクエストがある場合、それを優先表示
        if my_active_assignment:
            request_id, request_data = my_active_assignment
            
            st.markdown('<div class="driver-main-card">', unsafe_allow_html=True)
            st.markdown(f"### 🚕 現在のリクエスト")
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**リクエストID:** {request_id[:8]}...")
                st.markdown(f"**リクエスト時刻:** {request_data['created_at'].strftime('%H:%M:%S')}")
                st.markdown(f"**リクエスト元:** フロント")
            with col2:
                st.markdown(f"**車番:** {request_data.get('car_number', '未設定')}")
                if request_data.get('estimated_arrival'):
                    st.markdown(f"**到着予定:** {request_data['estimated_arrival']}分後")
            
            st.markdown("---")
            
            # メインボタン：到着、出発、完了の順に横に並べる
            col1, col2, col3 = st.columns(3)
            
            # 現在の状態を確認
            current_status = request_data.get('status', 'assigned')
            has_arrived = current_status in ['arrived', 'departed', 'completed']
            has_departed = current_status in ['departed', 'completed']
            is_completed = current_status == 'completed'
            
            with col1:
                if st.button(
                    "✅ 到着",
                    key=f"arrive_{request_id}",
                    type="primary",
                    use_container_width=True,
                    disabled=(current_status != 'assigned' or has_arrived)
                ):
                    # 到着ボタン（assigned状態の時のみ有効）
                    try:
                        latest_requests = load_requests()
                        target_request = latest_requests.get(request_id)
                        
                        if target_request and target_request.get('status') == 'assigned':
                            # 最新のデータを更新（コピーを作成）
                            target_request = target_request.copy()
                            target_request['status'] = 'arrived'
                            target_request['arrived_at'] = datetime.now()
                            latest_requests[request_id] = target_request
                            
                            # セッション状態を完全に更新
                            st.session_state.requests = latest_requests.copy()
                            
                            # ファイルに保存
                            save_requests(st.session_state.requests)
                            
                            st.success("✅ 到着を記録しました")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("⚠️ リクエストが見つからないか、既に処理済みです。")
                            st.session_state.requests = load_requests()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                        st.session_state.requests = load_requests()
                        time.sleep(1)
                        st.rerun()
            
            with col2:
                if st.button(
                    "✅ 出発",
                    key=f"depart_{request_id}",
                    type="primary",
                    use_container_width=True,
                    disabled=(current_status != 'arrived' or has_departed)
                ):
                    # 出発ボタン（arrived状態の時のみ有効）
                    try:
                        latest_requests = load_requests()
                        target_request = latest_requests.get(request_id)
                        
                        if target_request and target_request.get('status') == 'arrived':
                            # 最新のデータを更新（コピーを作成）
                            target_request = target_request.copy()
                            target_request['status'] = 'departed'
                            target_request['departed_at'] = datetime.now()
                            latest_requests[request_id] = target_request
                            
                            # セッション状態を完全に更新
                            st.session_state.requests = latest_requests.copy()
                            
                            # ファイルに保存
                            save_requests(st.session_state.requests)
                            
                            st.success("✅ 出発を記録しました")
                            time.sleep(0.5)
                            st.rerun()
                        else:
                            st.error("⚠️ リクエストが見つからないか、到着ボタンが押されていません。")
                            st.session_state.requests = load_requests()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                        st.session_state.requests = load_requests()
                        time.sleep(1)
                        st.rerun()
            
            with col3:
                if st.button(
                    "✅ 完了",
                    key=f"complete_{request_id}",
                    type="primary",
                    use_container_width=True,
                    disabled=(current_status != 'departed' or is_completed)
                ):
                    # 完了ボタン（departed状態の時のみ有効）
                    try:
                        latest_requests = load_requests()
                        latest_drivers = load_drivers()
                        target_request = latest_requests.get(request_id)
                        
                        if target_request and target_request.get('status') == 'departed':
                            # 最新のデータを更新（コピーを作成）
                            target_request = target_request.copy()
                            target_request['status'] = 'completed'
                            target_request['completed_at'] = datetime.now()
                            latest_requests[request_id] = target_request
                            
                            # ドライバーのステータスをavailableに更新（完了後は稼働可能に戻す）
                            if driver_id in latest_drivers:
                                latest_drivers[driver_id] = latest_drivers[driver_id].copy()
                                latest_drivers[driver_id]['status'] = 'available'  # 完了後は稼働可能に戻す
                            
                            # セッション状態を完全に更新
                            st.session_state.requests = latest_requests.copy()
                            st.session_state.drivers = latest_drivers.copy()
                            
                            # ファイルに保存
                            save_requests(st.session_state.requests)
                            save_drivers(st.session_state.drivers)
                            
                            # 完了後はリクエスト処理が終了したので、手動更新と自動更新を有効化
                            st.session_state.driver_has_active_request = False
                            
                            st.success("✅ 送迎完了として記録しました")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("⚠️ リクエストが見つからないか、出発ボタンが押されていません。")
                            st.session_state.requests = load_requests()
                            st.session_state.drivers = load_drivers()
                            time.sleep(1)
                            st.rerun()
                    except Exception as e:
                        st.error(f"エラーが発生しました: {e}")
                        st.session_state.requests = load_requests()
                        st.session_state.drivers = load_drivers()
                        time.sleep(1)
                        st.rerun()
            
            # 状態に応じたメッセージ表示
            if current_status == 'assigned':
                st.info("💡 「到着」ボタンを押してください")
            elif current_status == 'arrived':
                st.info("💡 「出発」ボタンを押してください")
            elif current_status == 'departed':
                st.info("💡 「完了」ボタンを押してください")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.info("⚠️ 現在、リクエストを処理中です。送迎完了まで新しいリクエストは表示されません。")
        
        # このドライバーに割り当てられたassigned状態のリクエストがない場合のみ、待機中のリクエストを表示
        if not my_active_assignment:
            # 待機中のリクエスト一覧（available状態のドライバーのみ表示可能）
            if current_driver and current_driver.get('status') == 'available':
                st.markdown("### 📋 待機中のリクエスト")
                
                # 待機中のリクエストを取得（複数のリクエストを同時に管理）
                # 最新のデータを読み込んで、statusが'pending'のものだけを取得（他のドライバーが受諾済みのものは除外）
                st.session_state.requests = load_requests()  # 最新状態を取得
                pending_requests = {
                    rid: rinfo for rid, rinfo in st.session_state.requests.items()
                    if rinfo.get('status') == 'pending'
                }
                
                if not pending_requests:
                    st.info("現在、待機中のリクエストはありません")
                else:
                    st.info(f"📊 現在、{len(pending_requests)}件のリクエストが待機中です")
                    
                    # 各リクエストまでの距離を計算してソート
                    request_distances = []
                    
                    for req_id, req_data in pending_requests.items():
                        distance = calculate_distance(
                            current_driver['lat'], current_driver['lon'],
                            req_data['front_lat'], req_data['front_lon']
                        )
                        request_distances.append((req_id, distance, req_data))
                    
                    # 距離でソート（近い順）
                    request_distances.sort(key=lambda x: x[1])
                    
                    # リクエスト選択用のセレクトボックス
                    if request_distances:
                        request_options = [
                            f"リクエスト #{idx} - 距離: {distance:.2f}km ({req_data['created_at'].strftime('%H:%M:%S')})"
                            for idx, (req_id, distance, req_data) in enumerate(request_distances, 1)
                        ]
                        selected_index = st.selectbox(
                            "📋 受諾するリクエストを選択してください",
                            range(len(request_options)),
                            format_func=lambda x: request_options[x],
                            key="request_selector"
                        )
                        
                        # 選択されたリクエストの詳細を表示
                        selected_req_id, selected_distance, selected_req_data = request_distances[selected_index]
                        estimated_minutes = estimate_arrival_time(selected_distance)
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**リクエストID:** {selected_req_id[:8]}...")
                            st.write(f"**リクエスト時刻:** {selected_req_data['created_at'].strftime('%H:%M:%S')}")
                            st.write(f"**距離:** {selected_distance:.2f}km")
                        
                        with col2:
                            st.write(f"**推定到着時間:** {estimated_minutes}分")
                            st.write("**ステータス:** 待機中")
                            st.write("**受諾可能:** ✅")
                        
                        # 受諾ボタン（一つだけ）
                        if st.button(
                            "✅ このリクエストを受ける",
                            key="accept_selected_request",
                            type="primary",
                            use_container_width=True
                        ):
                            req_id = selected_req_id
                            req_data = selected_req_data
                            distance = selected_distance
                            estimated_minutes = estimate_arrival_time(distance)
                            
                            # 二重受諾防止：最新データを再取得して、まだpending状態か確認
                            latest_requests = load_requests()
                            target_request = latest_requests.get(req_id)
                            
                            if target_request and target_request.get('status') == 'pending':
                                # リクエストを割り当て（このドライバーに割り当て）
                                target_request['status'] = 'assigned'
                                target_request['assigned_driver'] = driver_id
                                target_request['driver_name'] = current_driver.get('name', '')  # ドライバー名を保存
                                target_request['car_number'] = current_driver['car_number']
                                target_request['estimated_arrival'] = estimated_minutes + 3
                                target_request['assigned_at'] = datetime.now()
                                target_request['arrived_at'] = None  # 到着時刻を初期化
                                target_request['departed_at'] = None  # 出発時刻を初期化
                                
                                # ドライバーのステータスはavailableのまま維持（リクエスト処理中でも稼働可能としてカウント）
                                # 必要に応じて手動でbusyに変更可能
                                # current_driver['status'] = 'busy'  # コメントアウト：リクエスト処理中でもavailableとしてカウント
                                st.session_state.drivers[driver_id] = current_driver
                                
                                # 最新のデータを更新
                                st.session_state.requests = latest_requests
                                st.session_state.requests[req_id] = target_request
                                
                                # ファイルに保存
                                save_requests(st.session_state.requests)
                                save_drivers(st.session_state.drivers)
                                
                                st.success(f"✅ リクエストを受諾しました！\n車番: {current_driver['car_number']}\n到着予定: {estimated_minutes + 3}分後")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("⚠️ このリクエストは既に他のドライバーが受諾済みです。")
                                time.sleep(1)
                                st.rerun()
            else:
                if current_driver:
                    st.warning("⚠️ ステータスを「available」に設定してください")
                else:
                    st.info("💡 ドライバー情報を設定してください")
        
        # 自動更新の制御（このドライバーにリクエストがある場合は無効化）
        if my_active_assignment:
            # リクエストがある場合、自動更新を無効化（完了まで）
            st.session_state.auto_refresh_enabled = False
    
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.exception(e)


def main():
    """メイン関数"""
    # サイドバーでページ選択
    page = st.sidebar.selectbox(
        "ページを選択",
        ["フロント端末", "ドライバー端末"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 システム状況")
    
    # システム状況を表示（ファイルから直接読み込んで確実に表示）
    try:
        sidebar_requests = load_requests()
        sidebar_drivers = load_drivers()
        st.sidebar.write(f"**リクエスト数:** {len(sidebar_requests)}")
        
        # 稼働可能状態（available）のドライバーのみをカウント（busyは休憩中なので除外）
        # リクエスト処理中（assigned, arrived, departed状態）でもavailableならカウント
        available_drivers_count = sum(1 for d in sidebar_drivers.values() 
                                      if d.get('status') == 'available')
        
        # 稼働中ドライバー数 = リクエスト処理中（assigned, arrived, departed状態）のドライバー数
        active_driver_ids = set()
        for r in sidebar_requests.values():
            status = r.get('status')
            if status in ['assigned', 'arrived', 'departed']:
                driver_id = r.get('assigned_driver')
                if driver_id:
                    active_driver_ids.add(driver_id)
        
        # リクエスト処理中のドライバーのみをカウント（busy状態は除外）
        active_drivers_count = sum(1 for driver_id in active_driver_ids 
                                   if driver_id in sidebar_drivers 
                                   and sidebar_drivers[driver_id].get('status') == 'available')
        
        st.sidebar.write(f"**稼働可能ドライバー数:** {available_drivers_count}")
        st.sidebar.write(f"**稼働中ドライバー数:** {active_drivers_count}")
        
        pending_count = sum(1 for r in sidebar_requests.values() 
                           if r.get('status') == 'pending')
        assigned_count = sum(1 for r in sidebar_requests.values() 
                            if r.get('status') == 'assigned')
        st.sidebar.write(f"**待機中リクエスト:** {pending_count}")
        st.sidebar.write(f"**割り当て済みリクエスト:** {assigned_count}")
    except Exception as e:
        st.sidebar.error(f"システム状況の取得エラー: {e}")
        # エラー時は最新データを再読み込み
        try:
            sidebar_requests = load_requests()
            sidebar_drivers = load_drivers()
            st.sidebar.write(f"**リクエスト数:** {len(sidebar_requests)}")
            
            # 稼働可能状態（available）のドライバーのみをカウント（busyは休憩中なので除外）
            available_drivers_count = sum(1 for d in sidebar_drivers.values() 
                                          if d.get('status') == 'available')
            
            # 稼働中ドライバー数 = リクエスト処理中（assigned, arrived, departed状態）のドライバー数
            active_driver_ids = set()
            for r in sidebar_requests.values():
                status = r.get('status')
                if status in ['assigned', 'arrived', 'departed']:
                    driver_id = r.get('assigned_driver')
                    if driver_id:
                        active_driver_ids.add(driver_id)
            
            # リクエスト処理中のドライバーのみをカウント（busy状態は除外）
            active_drivers_count = sum(1 for driver_id in active_driver_ids 
                                       if driver_id in sidebar_drivers 
                                       and sidebar_drivers[driver_id].get('status') == 'available')
            
            st.sidebar.write(f"**稼働可能ドライバー数:** {available_drivers_count}")
            st.sidebar.write(f"**稼働中ドライバー数:** {active_drivers_count}")
            
            pending_count = sum(1 for r in sidebar_requests.values() 
                               if r.get('status') == 'pending')
            assigned_count = sum(1 for r in sidebar_requests.values() 
                                if r.get('status') == 'assigned')
            st.sidebar.write(f"**待機中リクエスト:** {pending_count}")
            st.sidebar.write(f"**割り当て済みリクエスト:** {assigned_count}")
            
            # セッション状態も更新
            st.session_state.requests = sidebar_requests
            st.session_state.drivers = sidebar_drivers
        except Exception as e2:
            st.sidebar.error(f"リカバリも失敗: {e2}")
            st.sidebar.write(f"**リクエスト数:** {len(st.session_state.requests)}")
            st.sidebar.write(f"**ドライバー数:** {len(st.session_state.drivers)}")
    
    st.sidebar.markdown("---")
    
    # ドライバー側で、このドライバー自身にassigned状態のリクエストがあるか確認
    has_active_assignment = False
    if page == "ドライバー端末":
        # サイドバーでドライバーIDを取得するための一時的な処理
        # 実際のドライバーIDはドライバーページ内で設定される
        # ここでは、assigned状態のリクエストの総数をチェック
        # ただし、実際の無効化は各ドライバーごとに行う
        pass  # 個別のドライバーIDを取得できないため、ページ内で制御
    
    # 手動更新ボタン（リクエスト受諾後は無効化）
    driver_has_active_request = st.session_state.get('driver_has_active_request', False)
    if st.sidebar.button(
        "🔄 手動更新", 
        type="secondary",
        disabled=(page == "ドライバー端末" and driver_has_active_request)
    ):
        # リクエスト情報のみを更新（ドライバー情報は完全に保持）
        st.session_state.requests = load_requests()
        # ドライバー情報は現在のセッション状態を完全に保持（上書きしない）
        st.session_state.last_update = time.time()
        st.sidebar.success("リクエスト情報を更新しました（ドライバー情報は保持されています）")
        st.rerun()
    
    # 自動更新の設定（リクエスト受諾後は無効化）
    st.sidebar.markdown("### ⚙️ 更新設定")
    auto_refresh_disabled = (page == "ドライバー端末" and driver_has_active_request)
    auto_refresh = st.sidebar.checkbox(
        "🔄 自動更新（30秒間隔）", 
        value=st.session_state.auto_refresh_enabled,
        disabled=auto_refresh_disabled
    )
    if not auto_refresh_disabled:
        st.session_state.auto_refresh_enabled = auto_refresh
    if auto_refresh:
        st.sidebar.caption("💡 自動更新はリソースを消費します。必要時のみONにしてください")
    
    # デバッグ用：全リクエストをクリア（フロント端末側のみ表示）
    if page == "フロント端末":
        if st.sidebar.button("🗑️ 全リクエストをクリア", type="secondary"):
            st.session_state.requests = {}
            save_requests({})  # ファイルもクリア
            st.session_state.last_update = time.time()
            if 'last_auto_refresh' in st.session_state:
                st.session_state.last_auto_refresh = time.time()
            st.success("リクエストをクリアしました")
            st.rerun()
    
    # ページに応じて表示
    try:
        if page == "フロント端末":
            frontend_page()
        else:
            driver_page()
    except Exception as e:
        st.error(f"エラーが発生しました: {e}")
        st.exception(e)
    
    # 自動更新の処理（ページ表示後に実行）
    if st.session_state.auto_refresh_enabled:
        # 自動更新が有効な場合、定期的にデータを再読み込み
        current_time = time.time()
        
        # 初回または前回の更新時刻を初期化
        if 'last_auto_refresh' not in st.session_state:
            st.session_state.last_auto_refresh = current_time
        
        time_since_last_refresh = current_time - st.session_state.last_auto_refresh
        
        # 30秒以上経過した場合に更新
        if time_since_last_refresh >= 30:
            # 最新データを読み込んでセッション状態を更新
            try:
                latest_requests = load_requests()
                latest_drivers = load_drivers()
                if latest_requests:
                    st.session_state.requests = latest_requests.copy()
                if latest_drivers:
                    st.session_state.drivers = latest_drivers.copy()
                st.session_state.last_auto_refresh = current_time
                st.session_state.last_update = current_time
                # 自動更新の場合は即座に再実行
                st.rerun()
            except Exception as e:
                st.error(f"自動更新エラー: {e}")
        else:
            # 30秒経過していない場合、JavaScriptで自動リロードを設定
            remaining_time = 30 - time_since_last_refresh
            st.markdown(
                f"""
                <script>
                    setTimeout(function() {{
                        window.location.reload();
                    }}, {int(remaining_time * 1000)});
                </script>
                """,
                unsafe_allow_html=True
            )


if __name__ == "__main__":
    main()

