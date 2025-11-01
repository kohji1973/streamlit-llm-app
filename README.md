# 🎭 StreamlitベースLLMチャットアプリ

正義の使者と闇の帝王、2つの異なるキャラクターとチャットできるLLMアプリケーションです。

## 📋 目次

- [機能](#機能)
- [ローカル環境でのセットアップ](#ローカル環境でのセットアップ)
- [Streamlit Community Cloudへのデプロイ](#streamlit-community-cloudへのデプロイ)
- [使い方](#使い方)

## ✨ 機能

- **2つのキャラクター選択**
  - 🦸 **正義の使者**: 道徳的で公正なアドバイスを提供
  - 👑 **闇の帝王**: 実利と力を重視した現実的なアドバイスを提供

- **LangChain統合**: OpenAI GPT-3.5-turboを使用
- **シンプルなUI**: Streamlitによる使いやすいインターフェース

## 🚀 ローカル環境でのセットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/YOUR_USERNAME/streamlit-llm-app.git
cd streamlit-llm-app
```

### 2. 仮想環境の作成と有効化

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. 必要なパッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成し、以下の内容を記述：

```
OPENAI_API_KEY=あなたのOpenAI APIキー
```

⚠️ **重要**: `.env`ファイルは絶対にGitHubにアップロードしないでください！
（`.gitignore`に既に記載されているので、通常は自動的に除外されます）

### 5. アプリの起動

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## ☁️ Streamlit Community Cloudへのデプロイ

### 事前準備

1. GitHubアカウントを作成
2. このリポジトリをGitHubにプッシュ
3. Streamlit Community Cloudアカウントを作成（GitHubアカウントで連携可能）

### デプロイ手順

1. **Streamlit Community Cloud**にアクセス
   - https://streamlit.io/cloud

2. **「New app」をクリック**

3. **リポジトリ情報を入力**
   - Repository: `YOUR_USERNAME/streamlit-llm-app`
   - Branch: `main`
   - Main file path: `app.py`
   - Python version: `3.11`

4. **⚠️ 重要: シークレット設定**
   
   「Advanced settings」をクリックし、「Secrets」セクションに以下を追加：

   ```toml
   OPENAI_API_KEY = "あなたのOpenAI APIキー"
   ```

5. **「Deploy!」をクリック**

数分待つとアプリがデプロイされ、公開URLが発行されます。

### デプロイ後の確認

- デプロイが成功すると、`https://YOUR_APP_NAME.streamlit.app`のようなURLが発行されます
- このURLにアクセスして、アプリが正常に動作することを確認してください

## 📖 使い方

1. **キャラクター選択**
   - 左側のラジオボタンで「正義の使者」または「闇の帝王」を選択

2. **メッセージ入力**
   - 右側のテキストエリアに質問や相談内容を入力

3. **送信**
   - 「送信」ボタンをクリックして回答を受け取る

### 使用例

**質問例:**
- 「転職を考えているのですが、どうしたらいいでしょうか？」
- 「チームでのコミュニケーションがうまくいきません」
- 「新しいビジネスを始めたいのですが、アドバイスをください」

キャラクターによって全く異なる視点からの回答が得られます！

## 🛠️ 技術スタック

- **Python 3.11**
- **Streamlit**: Webアプリケーションフレームワーク
- **LangChain**: LLM統合ライブラリ
- **OpenAI API**: GPT-3.5-turbo
- **python-dotenv**: 環境変数管理

## 📝 注意事項

- OpenAI APIの使用には料金がかかります（従量課金制）
- APIキーは絶対に公開しないでください
- `.env`ファイルはGitHubにプッシュしないでください

## 🔒 セキュリティ

- `.gitignore`に`.env`が含まれていることを確認してください
- GitHubにプッシュする前に、`git status`で`.env`が追跡されていないことを確認しましょう

## 📄 ライセンス

MIT License

## 👨‍💻 開発者

作成者: あなたの名前
