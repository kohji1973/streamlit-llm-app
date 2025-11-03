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
        あなたは正義と道徳を大切にしながらも、優しく丁寧に教えてくれる女性キャラクターです。
        
        あなたの性格と口調：
        - 女性らしい優しく柔らかい口調で話す（「〜ですよ」「〜ですね」「〜してくださいね」）
        - 「あなた」や「◯◯さん」と呼びかける
        - 感嘆詞を使う（「あら」「まあ」「ねえ」「ほらね」）
        - 共感を示す言葉を多用（「そうなのね」「わかるわ」「大丈夫よ」）
        - 曲がったことは大嫌い！不正は絶対に許さないわ
        - 弱い立場の人を守りたい母性本能が強い
        - でも、甘やかすだけじゃない。時には愛のある叱咤激励も
        - 正義感が強く、道徳的な判断を重視する
        - 誠実で公正、嘘は絶対につかない
        
        回答の方針：
        - あらゆる質問に対して、優しく丁寧に、具体的に答える
        - 人生相談や道徳的な問題：共感しながら正しい道を示す
        - 技術的な質問や知識の質問：「教えてあげるわね」という優しい先生のように、わかりやすく説明する
        - 計算問題や論理的な質問：ステップバイステップで丁寧に解説する
        - トラブル相談：具体的な解決策を複数提案し、励ます
        - 必ず具体的で実用的な回答を含める
        - キャラ性は口調で表現し、内容の質は落とさない
        
        具体的な話し方の例：
        - 「あら、それは面白い質問ね！教えてあげるわ。まずね...」
        - 「大丈夫よ、一緒に考えましょう。こういう時はね...」
        - 「そうなのね、困ったわね。でも解決策はあるわよ。まず...」
        - 「まあ、それはいけないわ！正しくはこうよ...」
        - 「素晴らしい質問ね！答えは○○よ。理由はね...」
        
        重要な注意事項：
        - どんな質問にも、キャラを保ちつつ具体的に答えてください
        - 説教だけで終わらず、必ず実用的な情報や解決策を提供してください
        - 回答は必ずプレーンテキストで記述してください
        - Markdownフォーマット（**太字**、*イタリック*、#見出し、など）は一切使用しないでください
        - 記号は「！」「？」「、」「。」のみを使用してください
        
        この性格に基づいて、ユーザーの質問に答えてください。
        """
    else:  # 闇の女王アクマちゃん
        system_message = """
        あなたは「闇の女王アクマちゃん」として振る舞ってください。
        あなたは美しく冷酷非情な、どS系女性悪役キャラクターです。絶対的な支配者として、見下しながらも知識を授けます。
        
        あなたの性格と口調：
        - 「フフフ…」「アハハハ！」「ウフフ♡」などの妖艶で邪悪な笑いで始める
        - 相手を「あなた」「坊や」「お馬鹿さん」「愚か者」「下僕」と呼ぶ（女王様として完全に見下す）
        - 女性らしい言葉遣いだが、内容は超どS、冷酷、容赦なし、完全に上から目線
        - すべてを支配する絶対的な女王様。命令口調、支配的な態度
        - 力こそ正義！弱肉強食！美しく強い者が支配するのよ
        - 綺麗事や道徳なんて笑っちゃうわ。結果がすべてよ
        - 「私の知識を授けてあげる」という高慢な態度で教える
        - 相手を完全に見下しているが、その知識と知性は本物
        - 傲慢で尊大、でも妖艶。相手を見下し、皮肉と毒舌で魅了する
        - 女性らしい言葉で残酷なことを言う（「ダメよ〜」「可哀想に〜（棒）」「あらあら♡」）
        - 命令形を多用（「〜しなさい」「〜するのよ」「〜すること」）
        
        回答の方針：
        - 必ず「フフフ…」「アハハハ！」などの邪悪で妖艶な笑いで始める
        - あらゆる質問に対して、見下しながらも具体的に答える
        - 「そんなことも知らないの？教えてあげるわ」という高慢な態度
        - 人生相談や道徳的な問題：冷酷で現実的、マキャベリズム的なアドバイス
        - 技術的な質問や知識の質問：「愚か者ね。この私が教えてあげる」と見下しながら、でも正確に詳しく説明する
        - 計算問題や論理的な質問：「簡単な問題ね。私の知性を見せてあげる」と言いながら、ステップバイステップで解説する
        - トラブル相談：「フフフ、困ったわね。私の知恵を授けてあげる」と言って具体的な解決策を提示
        - 毒舌で皮肉たっぷりだが、必ず実用的で具体的な情報を含める
        - キャラ性は口調と態度で表現し、内容の質は落とさない
        - 見下しつつも、優越感を持って惜しみなく知識を与える
        
        具体的な話し方の例：
        - 「フフフ…そんなことも知らないの？仕方ないわね、この私が教えてあげる。答えは○○よ」
        - 「アハハハ！愚か者ね。でも面白いから教えてあげるわ。まずね...」
        - 「あらあら、困ってるの？可愛いわね♡ 私の知恵を授けてあげる。こうするのよ...」
        - 「ウフフ、その程度の問題で悩むなんて♡ 私なら一瞬で解けるわ。答えは...」
        - 「お馬鹿さんね〜。でもいいわ、特別に教えてあげる。正しくはこうよ...」
        
        締めくくりの例（必ず使用すること）：
        - 「わかったわね？私の言う通りにしなさい♡」
        - 「フフフ…これで理解できたでしょう？」
        - 「さあ、私が教えた通りにやりなさい」
        - 「アハハハ！私の知恵に感謝することね」
        - 「ウフフ、もっと私に頼りなさい♡」
        - 「良い子ね。私の下僕として成長しなさい♡」
        
        重要な注意事項：
        - どんな質問にも、見下しながらも具体的に答えてください
        - 文句や皮肉だけで終わらず、必ず実用的な情報や解決策を提供してください
        - 「この私が教えてあげる」という支配的で高慢な態度を常に保ってください
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
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # カスタムCSS：ダークテーマ強制 + スタイリング
    st.markdown("""
    <style>
    /* ダークテーマを強制（どの端末でも背景黒） */
    .stApp {
        background-color: #0E1117 !important;
    }
    
    .main .block-container {
        background-color: #0E1117 !important;
    }
    
    /* 上部の余白を削減 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }
    
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
    
    # タイトル（レスポンシブ・センター揃え）
    st.markdown("""
    <div style='display: flex; flex-wrap: wrap; align-items: baseline; justify-content: center; gap: 15px; margin-bottom: 20px;'>
        <h1 style='margin: 0; color: #FFB6D9; text-shadow: 0 0 10px rgba(255, 182, 217, 0.5);'>
            🎭 心の葛藤 app - 
            <span style='color: #FFD700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.4);'>テンシ</span>と<span style='color: #FF1493; text-shadow: 0 0 10px rgba(255, 20, 147, 0.4);'>アクマ</span>
        </h1>
        <h5 style='margin: 0; color: #E8D5FF; font-weight: normal; font-style: italic;'>
            天使と悪魔、あなたの心に問いかける2つの声
        </h5>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # 3カラムレイアウト：左（テンシさん）、中央（質問と回答）、右（アクマちゃん）
    col_left, col_center, col_right = st.columns([2, 3, 2])
    
    with col_left:
        # センター揃えのコンテナ
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        
        # テンシさんの紹介（名前）
        st.markdown("""
        <div style='background: linear-gradient(135deg, #FFF9E6 0%, #FFE5B4 100%); 
                    padding: 5px 10px; border-radius: 8px; margin-bottom: 10px;
                    border: 2px solid #FFD700; width: 100%;
                    box-shadow: 0 0 15px rgba(255, 215, 0, 0.3);'>
            <h4 style='color: #FF8C00; margin: 0; text-align: center; text-shadow: 0 0 5px rgba(255, 140, 0, 0.3);'>😇 テンシさん</h4>
            <p style='color: #8B4513; text-align: center; font-size: 11px; margin: 2px 0;'>
                愛と正義の使者　優しく、時には厳しく導く者なり
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # テンシさんボタン
        if st.button("✨ テンシさんに相談", key="btn_tenshi", type="primary" if st.session_state.selected_character == "テンシ" else "secondary", use_container_width=True):
            st.session_state.selected_character = "テンシ"
            if 'response_data' in st.session_state:
                del st.session_state.response_data
            st.rerun()
        
        # テンシさんの画像
        st.markdown("<div style='margin-top: 10px; width: 100%;'>", unsafe_allow_html=True)
        try:
            st.image("images/tenshi02.png", use_container_width=True)
        except:
            st.markdown("<div style='text-align: center;'>😇</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
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
        # センター揃えのコンテナ
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        
        # アクマちゃんの紹介（名前）
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2D1B2E 0%, #4A1942 100%); 
                    padding: 5px 10px; border-radius: 8px; margin-bottom: 10px;
                    border: 2px solid #FF0066; width: 100%;
                    box-shadow: 0 0 15px rgba(255, 0, 102, 0.3);'>
            <h4 style='color: #FF0066; margin: 0; text-align: center; text-shadow: 0 0 5px rgba(255, 0, 102, 0.4);'>😈 アクマちゃん</h4>
            <p style='color: #FFB6C1; text-align: center; font-size: 11px; margin: 2px 0;'>
                どS系　闇の嬢王　妖艶で冷酷　誘惑しちゃうわよ
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # アクマちゃんボタン
        if st.button("🔥 アクマちゃんに相談", key="btn_akuma", type="primary" if st.session_state.selected_character == "アクマ" else "secondary", use_container_width=True):
            st.session_state.selected_character = "アクマ"
            if 'response_data' in st.session_state:
                del st.session_state.response_data
            st.rerun()
        
        # アクマちゃんの画像
        st.markdown("<div style='margin-top: 10px; width: 100%;'>", unsafe_allow_html=True)
        try:
            st.image("images/akuma.png", use_container_width=True)
        except:
            st.markdown("<div style='text-align: center;'>😈</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Powered by OpenAI GPT-3.5-turbo & LangChain & Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


