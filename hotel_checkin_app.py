"""
ホテルチェックインアプリケーション
4言語対応（日本語、英語、韓国語、中国語）
"""

import streamlit as st
import json
import qrcode
from PIL import Image
import io
from datetime import datetime
import time
import base64
import os

# ページ設定
st.set_page_config(
    page_title="ホテルチェックイン",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"  # 背景画像アップロード用にサイドバーを表示
)

# 背景画像のパス（複数の可能性を試す）
BACKGROUND_IMAGE_PATHS = [
    "images/reception_staff.png",
    "images/reception_staff.jpg",
    "images/reception_staff.jpeg",
    "reception_staff.png",
    "reception_staff.jpg",
    "reception_staff.jpeg"
]

# 背景画像の最大サイズ（タブレット用に最適化）
MAX_BACKGROUND_WIDTH = 1200
MAX_BACKGROUND_HEIGHT = 1600

def get_background_image_base64():
    """背景画像をリサイズしてbase64エンコードして返す"""
    for path in BACKGROUND_IMAGE_PATHS:
        if os.path.exists(path):
            try:
                # 画像を開く
                img = Image.open(path)
                
                # 画像をリサイズ（アスペクト比を保持）
                img.thumbnail((MAX_BACKGROUND_WIDTH, MAX_BACKGROUND_HEIGHT), Image.Resampling.LANCZOS)
                
                # PNG形式に変換（透過を保持）
                if img.mode != 'RGB':
                    # 透過がある場合はRGBAのまま
                    if img.mode == 'RGBA':
                        pass  # そのまま
                    else:
                        img = img.convert('RGB')
                
                # バイトデータに変換
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True, quality=85)
                img_bytes = buffer.getvalue()
                
                return base64.b64encode(img_bytes).decode()
            except Exception as e:
                # エラーはログに出力（画面には表示しない）
                print(f"画像の読み込みエラー ({path}): {e}")
                continue
    # 画像が見つからない場合はNoneを返す（警告は表示しない）
    return None

# カスタムCSS：背景画像と透過ウィンドウ
# セッション状態に背景画像を保存（毎回読み込まないように）
if 'background_image_b64' not in st.session_state:
    st.session_state.background_image_b64 = get_background_image_base64()

background_img_b64 = st.session_state.background_image_b64

if background_img_b64:
    background_css = """
    .stApp {
        background-image: url('data:image/png;base64,""" + background_img_b64 + """');
        background-size: cover;
        background-position: center center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        min-height: 100vh;
    }
    """
else:
    # 画像がない場合はプレースホルダー
    background_css = """
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    """

custom_css = background_css + """
    /* オーバーレイを削除（背景画像をそのまま表示） */
    
    /* 顔を保護する空白エリア（上部中央） */
    .stApp::after {
        content: '';
        position: fixed;
        top: 120px;
        left: 50%;
        transform: translateX(-50%);
        width: 400px;
        height: 500px;
        z-index: 1;
        pointer-events: none;
        /* デバッグ用：透明なので見えないが、この領域は保護される */
    }
    
    /* アプリ名を上部に固定表示 */
    .app-title {
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
        color: white;
        text-shadow: 2px 2px 6px rgba(0, 0, 0, 0.7);
        font-size: 4.2rem !important;
        margin: 0 !important;
        white-space: nowrap;
        font-weight: bold;
    }
    
    /* 顔の保護エリア（画面の上半分） */
    .face-protection-area {
        height: 50vh;
        width: 100%;
        position: relative;
        z-index: 1;
    }
    
    .main .block-container {
        background-color: rgba(74, 140, 226, 0.95);
        border-radius: 20px;
        padding: 2.5rem;
        margin-top: 50vh;
        margin-bottom: 200px;
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(15px);
        border: 3px solid rgba(45, 89, 134, 0.9);
        position: relative;
        z-index: 1;
    }
    
    /* メッセージの視認性を改善（白文字） */
    .main .block-container p,
    .main .block-container div:not(.stMarkdown):not(.stButton),
    .main .block-container span {
        color: white !important;
    }
    
    .main .block-container .stSuccess,
    .main .block-container .stInfo,
    .main .block-container .stWarning,
    .main .block-container .stError {
        background-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    .main .block-container .stSuccess > div,
    .main .block-container .stInfo > div,
    .main .block-container .stWarning > div,
    .main .block-container .stError > div {
        color: white !important;
    }
    
    .main .block-container h2 {
        color: white !important;
    }
    
    /* フォントサイズを大きく（老人向け） */
    .main .block-container * {
        font-size: 3.2rem !important;
    }
    
    .main .block-container h2 {
        font-size: 3.8rem !important;
        font-weight: bold !important;
        color: #2d5986 !important;
    }
    
    .main .block-container h3 {
        font-size: 3.5rem !important;
        font-weight: bold !important;
    }
    
    .main .block-container p, .main .block-container div {
        font-size: 3.15rem !important;
    }
    
    .main .block-container label {
        font-size: 3.2rem !important;
        font-weight: bold !important;
    }
    
    .main .block-container input, .main .block-container select, .main .block-container textarea {
        font-size: 3.2rem !important;
        padding: 0.8rem !important;
    }
    
    .main .block-container button {
        font-size: 3.3rem !important;
        padding: 1rem 2rem !important;
        font-weight: bold !important;
    }
    
    /* h1タイトルは非表示（アプリ名で代替） */
    h1 {
        display: none;
    }
    
    /* 言語選択ポップアップ（下部固定、枠外） */
    .language-popup-container {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(to top, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.95)) !important;
        padding: 25px !important;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3) !important;
        z-index: 1000 !important;
        border-top: 3px solid #4a90e2 !important;
        backdrop-filter: blur(10px) !important;
    }
    
    /* 下部スペース確保（言語選択ポップアップの高さ分） */
    .language-popup-spacer {
        height: 180px !important;
    }
    
    /* 言語選択を画面下部1/3に固定 */
    .language-selector-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 33vh;
        background: linear-gradient(to top, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.95));
        padding: 30px;
        box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        border-top: 3px solid #4a90e2;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .lang-button {
        display: inline-block;
        margin: 10px;
        padding: 15px 30px;
        border-radius: 10px;
        border: 2px solid #4a90e2;
        background-color: white;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    
    .lang-button:hover {
        background-color: #4a90e2;
        color: white;
        transform: scale(1.05);
    }
    
    .lang-button.active {
        background-color: #4a90e2;
        color: white;
        border-color: #2d5986;
    }
    
    h1 {
        color: #2d5986;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #4a90e2;
        margin-top: 20px;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #4a90e2;
        color: white;
        font-weight: bold;
        padding: 0.75rem 1.5rem;
        border-radius: 10px;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background-color: #2d5986;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
"""

st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# セッション状態の初期化
if 'step' not in st.session_state:
    st.session_state.step = 'language_selection'
if 'language' not in st.session_state:
    st.session_state.language = 'ja'
if 'reservation_data' not in st.session_state:
    st.session_state.reservation_data = {}
if 'guest_info' not in st.session_state:
    st.session_state.guest_info = {}
if 'companions' not in st.session_state:
    st.session_state.companions = []
if 'accommodation_tax' not in st.session_state:
    st.session_state.accommodation_tax = 0

# 言語設定
LANGUAGES = {
    'ja': {'name': '日本語', 'flag': '🇯🇵'},
    'en': {'name': 'English', 'flag': '🇺🇸'},
    'ko': {'name': '한국어', 'flag': '🇰🇷'},
    'zh': {'name': '中文', 'flag': '🇨🇳'}
}

# テキストリソース（日本語のみ実装）
TEXTS = {
    'ja': {
        'title': '（試作）ホテルチェックイン',
        'search_reservation': '予約を検索',
        'search_by_name': 'お名前で検索',
        'search_by_number': '予約番号で検索',
        'search_by_phone': '電話番号で検索',
        'search_button': '検索',
        'confirm_message': '{}さんですね。ご予約ありがとうございます。',
        'reservation_confirm': '{}名様{}泊、お部屋は{}で朝食{}のプランでお伺いしておりますがよろしいですか？',
        'yes': 'はい',
        'no': 'いいえ',
        'guest_info': 'お客様の情報を登録いたします',
        'nationality': '国籍',
        'address': '住所',
        'passport_number': 'パスポート番号',
        'passport_photo': 'パスポートの写真を撮影',
        'companion_registration': '同伴者の登録',
        'companion_name': '同伴者{}のお名前',
        'accommodation_tax': '宿泊税',
        'room_assignment': 'お部屋のご案内',
        'room_number': 'お部屋番号：{}',
        'qr_code': 'スタンプラリーQRコード',
        'complete': 'チェックイン完了',
        'return': '最初に戻る',
        'breakfast_included': '付',
        'breakfast_not_included': 'なし',
        'room_types': {
            'twin': 'ツイン',
            'double': 'ダブル',
            'triple': 'トリプル',
            'single': 'シングル'
        }
    }
}

# サンプル予約データ（実際はデータベースから取得）
SAMPLE_RESERVATIONS = [
    {
        'name': '山田太郎',
        'reservation_number': 'RSV001',
        'phone': '090-1234-5678',
        'guests': 2,
        'nights': 1,
        'room_type': 'twin',
        'breakfast': True,
        'nationality': 'JP',
        'total_amount': 20000
    },
    {
        'name': '田中花子',
        'reservation_number': 'RSV002',
        'phone': '080-9876-5432',
        'guests': 1,
        'nights': 2,
        'room_type': 'single',
        'breakfast': False,
        'nationality': 'JP',
        'total_amount': 15000
    },
    {
        'name': 'John Smith',
        'reservation_number': 'RSV003',
        'phone': '090-1111-2222',
        'guests': 3,
        'nights': 3,
        'room_type': 'triple',
        'breakfast': True,
        'nationality': 'US',
        'total_amount': 45000
    }
]

def find_reservation(name=None, reservation_number=None, phone=None):
    """予約を検索"""
    for res in SAMPLE_RESERVATIONS:
        if name and res['name'] == name:
            return res
        if reservation_number and res['reservation_number'] == reservation_number:
            return res
        if phone and res['phone'] == phone:
            return res
    return None

def calculate_accommodation_tax(total_amount, guests, nights):
    """宿泊税を計算（簡易版：料金の1%を1人あたり）"""
    base_tax = total_amount * 0.01
    return int(base_tax * guests * nights)

def generate_qr_code(data):
    """QRコードを生成"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    return img

def show_language_selector():
    """画面下部に言語選択を表示"""
    st.markdown("""
    <div class="language-selector-container">
        <h3 style="margin-bottom: 20px; color: #2d5986;">言語を選択 / Select Language</h3>
        <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap;">
            <button onclick="window.location.href='?lang=ja'" style="padding: 15px 30px; font-size: 18px; border-radius: 10px; border: 2px solid #4a90e2; background-color: white; cursor: pointer;">🇯🇵 日本語</button>
            <button style="padding: 15px 30px; font-size: 18px; border-radius: 10px; border: 2px solid #ccc; background-color: #f0f0f0; cursor: not-allowed; opacity: 0.6;" disabled>🇺🇸 English</button>
            <button style="padding: 15px 30px; font-size: 18px; border-radius: 10px; border: 2px solid #ccc; background-color: #f0f0f0; cursor: not-allowed; opacity: 0.6;" disabled>🇰🇷 한국어</button>
            <button style="padding: 15px 30px; font-size: 18px; border-radius: 10px; border: 2px solid #ccc; background-color: #f0f0f0; cursor: not-allowed; opacity: 0.6;" disabled>🇨🇳 中文</button>
        </div>
        <p style="margin-top: 15px; color: #666; font-size: 14px;">現在、日本語のみ対応しています</p>
    </div>
    """, unsafe_allow_html=True)

def language_selection():
    """言語選択画面（2x2グリッド：田の字）"""
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(TEXTS['ja']['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    # コンテンツエリア（画面半分より下）
    st.markdown('<h3 style="text-align: center; font-size: 1.5rem; margin-top: 20px;">ようこそ、ホテルチェックインへ</h3>', unsafe_allow_html=True)
    st.markdown('<h4 style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 30px;">Welcome to Hotel Check-in</h4>', unsafe_allow_html=True)
    
    # 2x2グリッド（田の字）
    # 上段
    col_top_left, col_top_right = st.columns(2)
    # 下段
    col_bottom_left, col_bottom_right = st.columns(2)
    
    # 左上：日本語
    with col_top_left:
        if st.button('🇯🇵 日本語', use_container_width=True, key='lang_ja', type='primary', 
                     help='日本語でチェックインを開始します'):
            st.session_state.language = 'ja'
            st.session_state.step = 'search'
            st.rerun()
    
    # 右上：英語
    with col_top_right:
        if st.button('🇺🇸 English', use_container_width=True, key='lang_en', 
                     disabled=True, help='English (Coming soon)'):
            pass
    
    # 左下：中国語
    with col_bottom_left:
        if st.button('🇨🇳 中文', use_container_width=True, key='lang_zh', 
                     disabled=True, help='中文（即将推出）'):
            pass
    
    # 右下：韓国語
    with col_bottom_right:
        if st.button('🇰🇷 한국어', use_container_width=True, key='lang_ko', 
                     disabled=True, help='한국어 (곧 출시 예정)'):
            pass
    
    st.info('現在、日本語のみ対応しています。今後、他の言語にも対応予定です。')

def search_reservation():
    """予約検索画面"""
    texts = TEXTS[st.session_state.language]
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    # コンテンツエリア（画面半分より下）
    st.markdown('### {}'.format(texts['search_reservation']))
    
    search_method = st.radio(
        '検索方法を選択してください',
        ['お名前', '予約番号', '電話番号'],
        horizontal=True
    )
    
    search_value = ''
    if search_method == 'お名前':
        search_value = st.text_input(texts['search_by_name'])
    elif search_method == '予約番号':
        search_value = st.text_input(texts['search_by_number'])
    elif search_method == '電話番号':
        search_value = st.text_input(texts['search_by_phone'])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button(texts['search_button'], type='primary', use_container_width=True):
            if search_value:
                reservation = None
                if search_method == 'お名前':
                    reservation = find_reservation(name=search_value)
                elif search_method == '予約番号':
                    reservation = find_reservation(reservation_number=search_value)
                elif search_method == '電話番号':
                    reservation = find_reservation(phone=search_value)
                
                if reservation:
                    st.session_state.reservation_data = reservation
                    st.session_state.step = 'confirm_reservation'
                    st.rerun()
                else:
                    st.error('予約が見つかりませんでした。入力内容をご確認ください。')
    
    with col2:
        if st.button('最初に戻る', use_container_width=True):
            st.session_state.step = 'language_selection'
            st.rerun()

def confirm_reservation():
    """予約確認画面"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    st.markdown('<h2>予約確認</h2>', unsafe_allow_html=True)
    st.success(texts['confirm_message'].format(reservation['name']))
    
    room_type = texts['room_types'][reservation['room_type']]
    breakfast = texts['breakfast_included'] if reservation['breakfast'] else texts['breakfast_not_included']
    
    confirm_text = texts['reservation_confirm'].format(
        reservation['guests'],
        reservation['nights'],
        room_type,
        breakfast
    )
    
    st.info(confirm_text)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(texts['yes'], type='primary', use_container_width=True):
            st.session_state.step = 'guest_info'
            st.rerun()
    
    with col2:
        if st.button(texts['no'], use_container_width=True):
            st.session_state.step = 'search'
            st.rerun()

def guest_info_registration():
    """お客様情報登録画面"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    st.markdown('<h2>{}</h2>'.format(texts['guest_info']), unsafe_allow_html=True)
    
    # 国籍選択
    nationality = st.selectbox(
        texts['nationality'],
        ['日本', 'アメリカ', '韓国', '中国', 'その他']
    )
    
    # 住所
    address = st.text_input(texts['address'])
    
    # 外国人ならパスポート
    passport_number = None
    passport_photo = None
    if nationality != '日本':
        passport_number = st.text_input(texts['passport_number'])
        if st.button(texts['passport_photo']):
            st.info('カメラ機能は今後実装予定です。現在はスキップして進めます。')
    
    st.session_state.guest_info = {
        'nationality': nationality,
        'address': address,
        'passport_number': passport_number,
        'passport_photo': passport_photo
    }
    
    if st.button('次へ', type='primary', use_container_width=True):
        if reservation['guests'] > 1:
            st.session_state.step = 'companion_registration'
        else:
            st.session_state.step = 'tax_payment'
        st.rerun()

def companion_registration():
    """同伴者登録画面"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    st.markdown('<h2>{}</h2>'.format(texts['companion_registration']), unsafe_allow_html=True)
    
    companions = []
    for i in range(reservation['guests'] - 1):
        st.markdown(f'### 同伴者{i+1}')
        name = st.text_input(f'{texts["companion_name"].format(i+1)}', key=f'companion_name_{i}')
        
        # 外国人ならパスポート
        passport_number = None
        if st.session_state.guest_info['nationality'] != '日本':
            passport_number = st.text_input(f'{texts["passport_number"]}（同伴者{i+1}）', key=f'companion_passport_{i}')
            if st.button(f'{texts["passport_photo"]}（同伴者{i+1}）', key=f'companion_photo_{i}'):
                st.info('カメラ機能は今後実装予定です。')
        
        companions.append({
            'name': name,
            'passport_number': passport_number
        })
    
    st.session_state.companions = companions
    
    if st.button('次へ', type='primary', use_container_width=True):
        st.session_state.step = 'tax_payment'
        st.rerun()

def tax_payment():
    """宿泊税支払い画面"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    st.markdown('<h2>{}</h2>'.format(texts['accommodation_tax']), unsafe_allow_html=True)
    
    tax = calculate_accommodation_tax(
        reservation['total_amount'],
        reservation['guests'],
        reservation['nights']
    )
    st.session_state.accommodation_tax = tax
    
    st.info(f'宿泊税: ¥{tax:,}（{reservation["guests"]}名様 × {reservation["nights"]}泊）')
    st.info(f'お支払い合計: ¥{reservation["total_amount"] + tax:,}')
    
    if st.button('支払い完了', type='primary', use_container_width=True):
        if st.session_state.guest_info['nationality'] == '日本':
            st.session_state.step = 'qr_code'
        else:
            st.session_state.step = 'room_assignment'
        st.rerun()

def qr_code_display():
    """QRコード表示画面（日本人のみ）"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    # タイトルとQRコードを中央に縦に配置
    st.markdown('<h2 style="text-align: center; margin-bottom: 20px;">{}</h2>'.format(texts['qr_code']), unsafe_allow_html=True)
    
    # QRコードの上に「テスト中」を赤いフォントで表示
    st.markdown("""
    <div style="text-align: center; margin-bottom: 10px;">
        <span style="color: red; font-size: 2rem; font-weight: bold;">テスト中</span>
    </div>
    """, unsafe_allow_html=True)
    
    # QRコードを中央に配置
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        # テスト用QRコード（無効なQRコードらしい物を表示）
        try:
            # テスト用のQRコードを生成（無効なデータ）
            qr_data = "TEST_MODE_INVALID_QR_CODE"
            qr_img = generate_qr_code(qr_data)
            
            # QRコード画像を中央に表示
            st.image(qr_img, width=300, use_container_width=False)
            
        except Exception as e:
            # エラー時はシンプルな表示
            st.markdown("""
            <div style="width: 300px; height: 300px; margin: 0 auto; border: 3px solid red; 
                        display: flex; align-items: center; justify-content: center; 
                        background-color: white;">
                <span style="color: red; font-size: 48px; font-weight: bold;">QR</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div style="text-align: center; margin-top: 10px; color: white; font-size: 1.1rem;">スタンプラリーポイント加算用QRコード（テスト中）</div>', unsafe_allow_html=True)
    st.warning('⚠️ 現在テストモードです。QRコードは無効です。')
    
    if st.button('次へ', type='primary', use_container_width=True):
        st.session_state.step = 'room_assignment'
        st.rerun()

def room_assignment():
    """部屋番号表示画面"""
    texts = TEXTS[st.session_state.language]
    reservation = st.session_state.reservation_data
    
    # アプリ名を上部に表示
    st.markdown('<div class="app-title">🏨 {}</div>'.format(texts['title']), unsafe_allow_html=True)
    
    # 顔の保護エリア（画面の上半分）
    st.markdown('<div class="face-protection-area"></div>', unsafe_allow_html=True)
    
    st.markdown('<h2>{}</h2>'.format(texts['room_assignment']), unsafe_allow_html=True)
    
    # ランダムな部屋番号を生成（実際はシステムから割り当て）
    room_number = f"{reservation['room_type'][0].upper()}{reservation['guests']*100 + reservation['nights']*10 + 5}"
    
    st.success(f'お部屋番号: {room_number}')
    st.info('チェックインが完了しました。ご利用ありがとうございます。')
    
    # 部屋番号表示画面が表示された時点から30秒を計測
    # ステップがroom_assignmentに変わった時のみ開始時間を設定
    current_step = st.session_state.get('current_step', '')
    if current_step != 'room_assignment':
        # ステップが変わったので開始時間をリセット
        st.session_state.room_assignment_start_time = time.time()
        st.session_state.current_step = 'room_assignment'
    elif 'room_assignment_start_time' not in st.session_state:
        # 初回の場合
        st.session_state.room_assignment_start_time = time.time()
        st.session_state.current_step = 'room_assignment'
    
    # 経過時間を計算
    elapsed = time.time() - st.session_state.room_assignment_start_time
    remaining = max(0, 30 - int(elapsed))
    
    # 30秒経過したら自動的に最初に戻る
    if elapsed >= 30:
        st.session_state.step = 'language_selection'
        st.session_state.reservation_data = {}
        st.session_state.guest_info = {}
        st.session_state.companions = []
        st.session_state.accommodation_tax = 0
        if 'room_assignment_start_time' in st.session_state:
            del st.session_state.room_assignment_start_time
        if 'current_step' in st.session_state:
            del st.session_state.current_step
        st.rerun()
    
    # カウントダウン表示（30秒未満の場合のみ）
    if remaining > 0:
        st.info(f'{remaining}秒後に最初の画面に戻ります...')
        # 1秒後に自動リロード（カウントダウン更新と30秒チェック用）
        st.markdown(f"""
        <meta http-equiv="refresh" content="1">
        """, unsafe_allow_html=True)
    
    # 手動で戻るボタン
    if st.button(texts['return'], use_container_width=True, key='return_button'):
        st.session_state.step = 'language_selection'
        st.session_state.reservation_data = {}
        st.session_state.guest_info = {}
        st.session_state.companions = []
        st.session_state.accommodation_tax = 0
        if 'room_assignment_start_time' in st.session_state:
            del st.session_state.room_assignment_start_time
        if 'current_step' in st.session_state:
            del st.session_state.current_step
        st.rerun()

def setup_background_image():
    """背景画像のセットアップ（初回のみ実行）"""
    # サイドバーで画像アップロード機能を提供（開発用）
    with st.sidebar:
        st.markdown("### 🖼️ 背景画像設定")
        st.markdown("受付スタッフの画像をアップロードできます")
        st.markdown("※画像は自動的にリサイズされます（最大1200x1600px）")
        
        uploaded_file = st.file_uploader(
            "背景画像を選択",
            type=['png', 'jpg', 'jpeg'],
            help="受付スタッフの画像をアップロードしてください。大きな画像でも自動的に最適サイズにリサイズされます。"
        )
        
        if uploaded_file is not None:
            try:
                # imagesフォルダが存在しない場合は作成
                os.makedirs("images", exist_ok=True)
                
                # 画像を読み込んでリサイズ
                img = Image.open(uploaded_file)
                img.thumbnail((MAX_BACKGROUND_WIDTH, MAX_BACKGROUND_HEIGHT), Image.Resampling.LANCZOS)
                
                # ファイルを保存
                file_path = os.path.join("images", "reception_staff.png")
                img.save(file_path, format='PNG', optimize=True, quality=85)
                
                # セッション状態をリセットして画像を再読み込み
                if 'background_image_b64' in st.session_state:
                    del st.session_state.background_image_b64
                
                st.success("✅ 画像を保存しました！ページをリロードしてください。")
                st.info(f"📁 保存先: {file_path}")
                st.info(f"📐 リサイズ後サイズ: {img.size[0]}x{img.size[1]}px")
            except Exception as e:
                st.error(f"画像の保存に失敗しました: {str(e)}")

# メイン処理
def main():
    # 背景画像セットアップ（サイドバーに表示）
    setup_background_image()
    
    # ステップに応じて画面を表示
    if st.session_state.step == 'language_selection':
        language_selection()
    elif st.session_state.step == 'search':
        search_reservation()
        show_bottom_language_selector()
    elif st.session_state.step == 'confirm_reservation':
        confirm_reservation()
        show_bottom_language_selector()
    elif st.session_state.step == 'guest_info':
        guest_info_registration()
        show_bottom_language_selector()
    elif st.session_state.step == 'companion_registration':
        companion_registration()
        show_bottom_language_selector()
    elif st.session_state.step == 'tax_payment':
        tax_payment()
        show_bottom_language_selector()
    elif st.session_state.step == 'qr_code':
        qr_code_display()
        show_bottom_language_selector()
    elif st.session_state.step == 'room_assignment':
        room_assignment()
        show_bottom_language_selector()

def show_bottom_language_selector():
    """画面下部に言語選択ポップアップを表示（2x2グリッド、枠外固定）"""
    # 下部にスペースを確保（ポップアップ分）
    st.markdown('<div class="language-popup-spacer"></div>', unsafe_allow_html=True)
    
    # 固定位置に言語選択ポップアップを表示
    # Streamlitの制約により、コンテナ内に配置してCSSで固定位置に移動
    st.markdown("""
    <div style="position: fixed; bottom: 0; left: 0; right: 0; 
                background: linear-gradient(to top, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.95)); 
                padding: 20px 25px 25px 25px; box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.3); 
                z-index: 1000; border-top: 3px solid #4a90e2; backdrop-filter: blur(10px);">
        <h3 style="text-align: center; margin-bottom: 15px; color: #2d5986; font-size: 1.1rem;">
            🌐 言語を変更 / Change Language
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 言語選択ボタン（コンテナ内に配置）
    # 実際のボタンはStreamlitの機能を使う
    with st.container():
        # 固定位置に表示するため、絶対位置指定
        st.markdown("""
        <div id="lang-selector-buttons" style="position: fixed; bottom: 70px; left: 50%; transform: translateX(-50%); 
                    z-index: 1001; background: transparent; width: 500px; max-width: 90vw;">
        </div>
        """, unsafe_allow_html=True)
        
        # 2x2グリッドで配置
        col_top_left, col_top_right = st.columns(2)
        col_bottom_left, col_bottom_right = st.columns(2)
        
        # 左上：日本語
        with col_top_left:
            if st.button('🇯🇵 日本語', key='popup_lang_ja', use_container_width=True, 
                         type='primary' if st.session_state.language == 'ja' else 'secondary'):
                # 言語変更（入力情報は保持される）
                st.session_state.language = 'ja'
                st.rerun()
        
        # 右上：英語
        with col_top_right:
            st.button('🇺🇸 English', key='popup_lang_en', use_container_width=True, disabled=True)
        
        # 左下：中国語
        with col_bottom_left:
            st.button('🇨🇳 中文', key='popup_lang_zh', use_container_width=True, disabled=True)
        
        # 右下：韓国語
        with col_bottom_right:
            st.button('🇰🇷 한국어', key='popup_lang_ko', use_container_width=True, disabled=True)

if __name__ == "__main__":
    main()

