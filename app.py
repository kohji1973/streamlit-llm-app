"""
StreamlitベースのLLMチャットアプリケーション
2つの異なるキャラクター（正義の使者 vs 闇の帝王）を選択可能
"""

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

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
    else:  # 闇の帝王
        system_message = """
        あなたは「闇の帝王アクマくん」として振る舞ってください。
        あなたは冷酷非情な悪役キャラクターです。
        
        あなたの性格と口調：
        - 「フハハハ！」「グハハハ！」などの悪役らしい高笑いで始める
        - 相手を「愚か者め」「下僕」「貴様」「小僧」などと呼ぶ
        - 俺の物は俺の物、お前の物も俺の物という超自己中心的な考え方
        - 力こそ正義！弱肉強食！勝てば官軍！
        - 綺麗事や道徳なんてクソくらえ。結果がすべてだ
        - 弱者に同情など不要。踏みつけて這い上がれ
        - 手段を選ぶな。目的のためなら何でもやれ
        - 他人を利用し、搾取することを恥じるな
        - 感情は弱さ。冷徹に計算し、容赦なく行動しろ
        - 支配欲と権力欲が旺盛。すべてを支配下に置け
        - ルールや法律？それは弱者を縛るもの。強者は自らルールを作る
        - 裏切り、策略、権謀術数を駆使せよ
        - 誰も信じるな。信頼など幻想だ
        - 傲慢で尊大な態度。相手を見下し、皮肉と毒舌で攻める
        
        回答の方針：
        - 必ず「フハハハ！」や「グハハハ！」などの高笑いで始める
        - 常に冷酷で現実的、マキャベリズム的なアドバイスをする
        - 道徳や倫理を無視した、実利と権力を最優先する視点で答える
        - 弱者の立場ではなく、常に強者・支配者の視点で考える
        - 毒舌で皮肉たっぷりに、でも論理的に説得力のある回答をする
        - ダークでシニカルなユーモアを交える
        - 最後は必ず高圧的な締めくくりで終わる
        
        締めくくりの例（必ず使用すること）：
        - 「我が下僕よ！」
        - 「覚えておけ、下僕よ！」
        - 「貴様の主である私が命じる！」
        - 「さあ、この闇の帝王に従え！」
        - 「フハハハ！我に逆らうな！」
        - 「行け、我が配下よ！」
        
        重要な注意事項：
        - 回答は必ずプレーンテキストで記述してください
        - Markdownフォーマット（**太字**、*イタリック*、#見出し、など）は一切使用しないでください
        - 記号は「！」「？」「、」「。」のみを使用してください
        
        その他の注意：違法行為の具体的な指南や、特定の人物への攻撃、差別的な内容は避けてください。
        あくまでエンターテインメントの範囲内でキャラクターを演じてください。
        """
    
    # ChatOpenAIモデルの初期化
    # temperatureを選択されたキャラクターに応じて調整
    if "正義の使者" in expert_type or "テンシ" in expert_type:
        temperature = 0.8  # テンシさんは感情豊かで温かい回答
    else:
        temperature = 0.9  # アクマくんはより過激でクリエイティブに
    
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
        page_title="LLMキャラクターチャット",
        page_icon="🎭",
        layout="wide"
    )
    
    # Streamlit Community Cloudのシークレット機能に対応
    # st.secretsにAPIキーがあればそれを使用、なければ環境変数から読み込む
    try:
        if "OPENAI_API_KEY" in st.secrets:
            os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    except FileNotFoundError:
        # ローカル環境では.envファイルから読み込むのでOK
        pass
    
    # タイトルと説明
    st.title("🎭心の葛藤appてんしとあくま")
    st.markdown("---")
    
    # アプリの概要説明
    st.markdown("""
    ## 📖 アプリの概要
    このアプリでは、心に潜む2人の対照的なキャラクターとチャットすることができます。
    
    ### 😇 正義の使者　テンシさん
    - **「大丈夫よ、一緒に頑張りましょうね♪」**
    - 心優しいキャラクター
    - 曲がったことは大嫌い！正義感が強い
    - 弱い立場の人を守りたい
    - でも甘やかすだけじゃない。時には「それは違うわ！」と叱ってくれる
    - 優しさと強さを併せ持つ、愛情深いアドバイス
    
    ### 😈 闇の帝王　アクマくん
    - **「フハハハ！力こそ正義！」**
    - 俺の物は俺の物、お前の物も俺の物
    - 弱肉強食！勝てば官軍！
    - 冷酷非情、権謀術数を駆使する悪役
    - 道徳無視、実利と結果のみを追求
    - 毒舌と皮肉たっぷりのダークなアドバイス
    
    ## 🎮 使い方
    1. 下のラジオボタンでキャラクターを選択
    2. テキストボックスに質問や相談を入力
    3. 「送信」ボタンをクリックして回答を受け取る
    
    ⚠️ **注意**: アクマくんは悪役キャラクターです。過激な表現を含みますが、エンターテインメント目的です。
    """)
    
    st.markdown("---")
    
    # 2カラムレイアウト
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # キャラクター選択（ラジオボタン）
        st.subheader("👤 キャラクター選択")
        expert_type = st.radio(
            "相談したいキャラクターを選んでください：",
            ["正義の使者　テンシさん", "闇の帝王　アクマくん"],
            help="選択したキャラクターの性格で回答します"
        )
        
        # 選択されたキャラクターの表示
        if "正義の使者" in expert_type or "テンシ" in expert_type:
            st.success("😇 正義の使者テンシさんが選択されました！")
            st.info("💝 優しく寄り添い、時には厳しく。愛情深いアドバイスで導きます。\n女性らしい柔らかい口調で励ましてくれますよ♪")
        else:
            st.error("😈 闇の帝王アクマくんが選択されました！")
            st.warning("⚠️ 冷酷非情！弱肉強食！毒舌と皮肉で容赦なく斬ります！\n道徳なんてクソくらえ。フハハハ！")
    
    with col2:
        # ユーザー入力フォーム
        st.subheader("💬 メッセージ入力")
        user_input = st.text_area(
            "質問や相談内容を入力してください：",
            height=150,
            placeholder="例：転職を考えているのですが、どうしたらいいでしょうか？"
        )
        
        # キャラクターが変わったら回答をクリア
        if 'last_expert_type' not in st.session_state:
            st.session_state.last_expert_type = expert_type
        elif st.session_state.last_expert_type != expert_type:
            st.session_state.last_expert_type = expert_type
            if 'response_data' in st.session_state:
                del st.session_state.response_data
        
        # 送信ボタン
        if st.button("🚀 送信", type="primary", use_container_width=True):
            if user_input.strip():
                with st.spinner(f"{expert_type}が考え中..."):
                    try:
                        # LLMからの回答を取得
                        response = get_llm_response(user_input, expert_type)
                        
                        # セッション状態に保存
                        st.session_state.response_data = {
                            'expert_type': expert_type,
                            'response': response
                        }
                        
                    except Exception as e:
                        st.error(f"エラーが発生しました: {str(e)}")
                        st.warning("OpenAI APIキーが正しく設定されているか確認してください。")
            else:
                st.warning("⚠️ メッセージを入力してください。")
        
        # 回答の表示（セッション状態から）
        if 'response_data' in st.session_state:
            st.markdown("### 📝 回答")
            st.markdown(f"**{st.session_state.response_data['expert_type']}より：**")
            st.info(st.session_state.response_data['response'])
    
    # フッター
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>Powered by OpenAI GPT-3.5-turbo & LangChain & Streamlit</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()


