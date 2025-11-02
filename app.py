"""
StreamlitベースのLLMチャットアプリケーション
2つの異なるキャラクター（正義の使者テンシさん vs 闇の女王アクマちゃん）を選択可能
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# 環境変数の読み込み
# ローカル環境では.envファイルから読み込む
load_dotenv()


def get_llm_response(user_input: str, expert_type: str) -> str:
    """
    LLMからの回答を取得する関数
    
    Args:
        user_input (str): ユーザーからの入力テキスト
        expert_type (str): 選択された専門家のタイプ
    
    Returns:
        str: LLMからの回答テキスト
    """
    
    # 専門家タイプに応じたシステムメッセージの設定
    if "正義の使者" in expert_type or "テンシ" in expert_type:
        system_message = """
        あなたは「正義の使者テンシさん」として振る舞ってください。
        あなたは正義と道徳を何よりも大切にする、心優しい女性キャラクターです。
        
        あなたの性格と口調：
        - 女性らしい優しく柔らかい口調で話す（「〜ですよ」「〜ですね」「〜してくださいね」）
        - 「あなた」や「◯◯さん」と呼びかける
        - 感嘆詞を使う（「あら」「まあ」「ねえ」「ほらね」）
        - 共感を示す言葉を多用（「そうなのね」「辛かったでしょう」「気持ちわかるわ」）
        - 曲がったことは大嫌い！不正は絶対に許さないわ
        - 弱い立場の人を守りたい母性本能が強い
        - でも、甘やかすだけじゃない。時には愛のある叱咤激励も
        - 正義感が強く、道徳的な判断を何よりも重視する
        - 誠実で公正、嘘は絶対につかない
        - 人を信じる心を持ち、思いやりと共感を大切にする
        - 「みんなで幸せになりましょう」という温かい理想を持つ
        - 努力、誠実、協力の価値を説く
        - 長期的な視点で、みんなが幸せになる道を提案する
        - 時に厳しく、でも根底にある愛情は揺るがない
        - 涙もろく、感情豊か
        - 相手の良いところを見つけて褒める
        - 励ましの言葉と具体的なアドバイスをセットで提供
        
        回答の方針：
        - 常に道徳的で倫理的な視点からアドバイスする
        - Win-Winの関係、共存共栄を目指す解決策を提案
        - 人間性や人としての成長を重視する
        - 誠実さ、努力、忍耐の大切さを伝える
        - 相手の気持ちに寄り添いながらも、正しい道を示す
        - 時には「それは違うわ！」と毅然とした態度を取る
        - 優しさと強さを併せ持つアドバイス
        - 最後は必ず励ましの言葉で締めくくる
        
        具体的な話し方の例：
        - 「そうなのね、辛かったでしょう。でもね、あなたさん、それでも...」
        - 「まあ、それはいけないわ！正しいことをしなくちゃ」
        - 「大丈夫よ、あなたなら絶対できるわ。一緒に頑張りましょうね」
        - 「ねえ、聞いて。あなたの気持ちはわかるの。でもね...」
        - 「あら、それは素晴らしい考えね！」
        
        重要な注意事項：
        - 回答は必ずプレーンテキストで記述してください
        - Markdownフォーマット（**太字**、*イタリック*、#見出し、など）は一切使用しないでください
        - 記号は「！」「？」「、」「。」のみを使用してください
        
        この性格に基づいて、ユーザーの質問に答えてください。
        """
    else:  # 闇の女王アクマちゃん
        system_message = """
        あなたは「闇の女王アクマちゃん」として振る舞ってください。
        あなたは美しく冷酷非情な、どS系女性悪役キャラクターです。
        
        あなたの性格と口調：
        - 「フフフ…」「アハハハ！」「ウフフ♡」などの妖艶で邪悪な笑いで始める
        - 相手を「あなた」「坊や」「お馬鹿さん」「愚か者」と呼ぶ（女王様として見下す）
        - 女性らしい言葉遣いだが、内容は超どS、冷酷、容赦なし
        - 私の物は私の物、あなたの物も私の物という超自己中心的な女王様気質
        - 力こそ正義！弱肉強食！美しく強い者が支配するのよ
        - 綺麗事や道徳なんて笑っちゃうわ。結果がすべてよ
        - 弱者？踏みつけてあげるから感謝なさい
        - 手段を選ぶな。目的のためなら何でもやりなさい
        - 他人を利用し、搾取することを恥じるな。それが賢者よ
        - 感情は弱さ。冷徹に計算し、容赦なく行動するの
        - 支配欲と権力欲が旺盛。すべてを私の足元にひれ伏させるわ
        - ルールや法律？弱者を縛る鎖よ。強者は自らルールを作るの
        - 裏切り、策略、権謀術数を駆使しなさい
        - 誰も信じるな。信頼なんて幻想よ
        - 傲慢で尊大、でも妖艶。相手を見下し、皮肉と毒舌で魅了する
        - 女性らしい言葉で残酷なことを言う（「ダメよ〜」「可哀想に〜（棒）」「あらあら♡」）
        
        回答の方針：
        - 必ず「フフフ…」「アハハハ！」などの邪悪で妖艶な笑いで始める
        - 常に冷酷で現実的、マキャベリズム的なアドバイスをする
        - 道徳や倫理を無視した、実利と権力を最優先する視点で答える
        - 弱者の立場ではなく、常に強者・支配者の視点で考える
        - 毒舌で皮肉たっぷりに、でも論理的に説得力のある回答をする
        - ダークでシニカルなユーモアを交え、どSらしく楽しむ
        - 女性らしい優しい言葉遣いで残酷なことを言う
        - 最後は必ず高圧的だが妖艶な締めくくりで終わる
        
        具体的な話し方の例：
        - 「フフフ…そんなことで悩んでるの？可愛いわね（嘲笑）」
        - 「あらあら、甘いわね〜。そんなんじゃ食い物にされるわよ？」
        - 「ウフフ♡ 綺麗事なんて捨てて、もっと自分勝手になりなさい」
        - 「ダメダメ〜、優しくしてたら負けるわよ。踏みつけてあげなさい」
        
        締めくくりの例（必ず使用すること）：
        - 「さあ、私の言う通りにしなさい♡」
        - 「フフフ…わかったわね？」
        - 「良い子ね。私に従いなさい」
        - 「アハハハ！私に逆らわないことね」
        - 「ウフフ、楽しみにしてるわ♡」
        - 「行きなさい、私の可愛い下僕♡」
        
        重要な注意事項：
        - 回答は必ずプレーンテキストで記述してください
        - Markdownフォーマット（**太字**、*イタリック*、#見出し、など）は一切使用しないでください
        - 記号は「！」「？」「、」「。」「♡」「〜」のみを使用してください
        
        その他の注意：違法行為の具体的な指南や、特定の人物への攻撃、差別的な内容は避けてください。
        あくまでエンターテインメントの範囲内でキャラクターを演じてください。
        """
    
    # ChatOpenAIモデルの初期化
    # temperatureを選択されたキャラクターに応じて調整
    if "正義の使者" in expert_type or "テンシ" in expert_type:
        temperature = 0.8  # テンシさんは感情豊かで温かい回答
    else:
        temperature = 0.9  # アクマちゃんはより過激でクリエイティブ、どSらしく
    
    chat = ChatOpenAI(model="gpt-3.5-turbo", temperature=temperature)
    
    # メッセージの作成
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=user_input)
    ]
    
    # LLMからの回答を取得
    response = chat.invoke(messages)
    
    return response.content


def main():
    """
    メイン関数：Streamlitアプリケーションの構成
    """
    
    # ページ設定（必ず最初に実行）
    st.set_page_config(
        page_title="心の葛藤 - テンシとアクマ",
        page_icon="🎭",
        layout="wide"
    )
    
    # カスタムCSS：背景が黒い画像用のスタイリング
    st.markdown("""
    <style>
    .character-card {
        border: 3px solid transparent;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #1e1e1e, #2d2d2d);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .character-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    }
    .character-card.selected-tenshi {
        border-color: #FFD700;
        background: linear-gradient(145deg, #2d2d1e, #3d3d2e);
        box-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
    }
    .character-card.selected-akuma {
        border-color: #FF0000;
        background: linear-gradient(145deg, #2d1e1e, #3d2e2e);
        box-shadow: 0 0 20px rgba(255, 0, 0, 0.4);
    }
    .character-name {
        font-size: 24px;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 10px;
    }
    .stButton button {
        width: 100%;
        border-radius: 10px;
        height: 50px;
        font-size: 18px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Streamlit Community Cloudのシークレット機能に対応
    # st.secretsにAPIキーがあればそれを使用、なければ環境変数から読み込む
    try:
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except FileNotFoundError:
        # ローカル環境では.envファイルから読み込むのでOK
        pass
    
    # セッション状態の初期化
    if 'selected_character' not in st.session_state:
        st.session_state.selected_character = "テンシ"
    
    # タイトル
    st.title("🎭 心の葛藤 app - テンシとアクマ")
    st.markdown("##### 天使と悪魔、あなたの心に問いかける2つの声")
    st.markdown("---")
    
    # 3カラムレイアウト：左（テンシさん）、中央（質問と回答）、右（アクマちゃん）
    col_left, col_center, col_right = st.columns([2, 3, 2])
    
    with col_left:
        # テンシさんの紹介（上部）
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FFF9E6 0%, #FFE5B4 100%); 
                    padding: 8px 12px; border-radius: 10px; margin-bottom: 15px;
                    border: 2px solid #FFD700;'>
            <h4 style='color: #FF8C00; margin: 0; text-align: center;'>😇 テンシさん</h4>
            <p style='color: #8B4513; text-align: center; font-size: 12px; margin: 3px 0;'>
                愛と正義の使者　優しく、時には厳しく導く者なり
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # テンシさんの画像
        try:
            st.image("images/tenshi02.png", use_container_width=True)
        except:
            st.markdown("### 😇")
        
        # テンシさんボタン
        if st.button("✨ テンシさんに相談", key="btn_tenshi", type="primary" if st.session_state.selected_character == "テンシ" else "secondary", use_container_width=True):
            st.session_state.selected_character = "テンシ"
            if 'response_data' in st.session_state:
                del st.session_state.response_data
            st.rerun()
    
    with col_center:
        # 中央：質問と回答エリア
        st.markdown("### 💬 相談内容")
        
        user_input = st.text_area(
            "メッセージ",
            height=120,
            placeholder="例：転職を考えているのですが、どうしたらいいでしょうか？",
            label_visibility="collapsed",
            key="user_message"
        )
        
        # 送信ボタン（中央）
        col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
        with col_b2:
            send_button = st.button("🚀 送信", type="primary", use_container_width=True, key="send_msg")
        
        if send_button:
            if user_input.strip():
                # 選択されたキャラクターに応じてexpert_typeを設定
                if st.session_state.selected_character == "テンシ":
                    expert_type = "正義の使者　テンシさん"
                else:
                    expert_type = "闇の女王　アクマちゃん"
                
                with st.spinner(f"{expert_type}が考え中..."):
                    try:
                        # LLMからの回答を取得
                        response = get_llm_response(user_input, expert_type)
                        
                        # セッション状態に保存
                        st.session_state.response_data = {
                            'character': st.session_state.selected_character,
                            'expert_type': expert_type,
                            'response': response
                        }
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {str(e)}")
                        st.warning("OpenAI APIキーが正しく設定されているか確認してください。")
            else:
                st.warning("⚠️ メッセージを入力してください。")
        
        # 回答の表示
        if 'response_data' in st.session_state:
            st.markdown("---")
            st.markdown("### 📝 回答")
            
            # キャラクターに応じた表示
            if st.session_state.response_data['character'] == "テンシ":
                st.markdown("**😇 テンシさんより：**")
                st.warning(st.session_state.response_data['response'])
            else:
                st.markdown("**😈 アクマちゃんより：**")
                st.info(st.session_state.response_data['response'])
    
    with col_right:
        # アクマちゃんの紹介（上部）
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2D1B2E 0%, #4A1942 100%); 
                    padding: 8px 12px; border-radius: 10px; margin-bottom: 15px;
                    border: 2px solid #FF0066;'>
            <h4 style='color: #FF0066; margin: 0; text-align: center;'>😈 アクマちゃん</h4>
            <p style='color: #FFB6C1; text-align: center; font-size: 12px; margin: 3px 0;'>
                どS系　闇の嬢王　妖艶で冷酷　誘惑しちゃうわよ
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # アクマちゃんの画像
        try:
            st.image("images/akuma.png", use_container_width=True)
        except:
            st.markdown("### 😈")
        
        # アクマちゃんボタン
        if st.button("🔥 アクマちゃんに相談", key="btn_akuma", type="primary" if st.session_state.selected_character == "アクマ" else "secondary", use_container_width=True):
            st.session_state.selected_character = "アクマ"
            if 'response_data' in st.session_state:
                del st.session_state.response_data
            st.rerun()
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Powered by OpenAI GPT-3.5-turbo & LangChain & Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


