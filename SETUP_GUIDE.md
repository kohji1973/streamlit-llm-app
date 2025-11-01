# 📘 セットアップガイド

## 🔧 ターミナルのフォントサイズを大きくする方法（VSCode）

ターミナルの文字が小さくて読みづらい場合、以下の方法でフォントサイズを変更できます。

### 方法1: 設定UIから変更（推奨）

1. **VSCodeを開く**

2. **設定を開く**
   - メニューバー: `ファイル` → `ユーザー設定` → `設定`
   - または、ショートカットキー: `Ctrl + ,`

3. **検索バーで「terminal font」と入力**

4. **「Terminal › Integrated: Font Size」を探す**

5. **数値を変更する**
   - デフォルト: 14
   - 推奨: 16〜20（お好みで調整）
   - 例: `18` に設定すると読みやすくなります

6. **変更は即座に反映されます**

### 方法2: settings.jsonから直接編集

1. **コマンドパレットを開く**
   - ショートカットキー: `Ctrl + Shift + P`

2. **「Preferences: Open Settings (JSON)」と入力して選択**

3. **以下の設定を追加または変更**

```json
{
    "terminal.integrated.fontSize": 18,
    "terminal.integrated.lineHeight": 1.2,
    "terminal.integrated.fontFamily": "Consolas, 'Courier New', monospace"
}
```

4. **ファイルを保存**（`Ctrl + S`）

### 方法3: ターミナルで一時的に拡大（ズーム）

- **拡大**: `Ctrl + Shift + +`（プラス記号）
- **縮小**: `Ctrl + Shift + -`（マイナス記号）
- **リセット**: `Ctrl + 0`（ゼロ）

⚠️ この方法は一時的で、VSCodeを再起動すると元に戻ります。

### おすすめの設定値

```json
{
    "terminal.integrated.fontSize": 18,
    "terminal.integrated.lineHeight": 1.2,
    "terminal.integrated.fontWeight": "normal",
    "terminal.integrated.fontFamily": "Consolas, 'Courier New', monospace"
}
```

これで、ターミナルがとても読みやすくなります！

---

## 🔑 .envファイルの作成方法

`.env`ファイルはセキュリティ上の理由で自動作成できないため、手動で作成してください。

### 手順

1. **VSCodeでプロジェクトを開く**

2. **新規ファイルを作成**
   - エクスプローラーで「streamlit-llm-app」フォルダを右クリック
   - 「新しいファイル」を選択
   - ファイル名: `.env`（ドットから始まることに注意）

3. **以下の内容を記述**

```
OPENAI_API_KEY=あなたのOpenAI APIキーをここに貼り付け
```

例:
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

4. **ファイルを保存**（`Ctrl + S`）

⚠️ **重要な注意点**:
- APIキーの前後に空白やクォーテーション（`"`や`'`）は不要です
- このファイルは絶対にGitHubにアップロードしないでください
- `.gitignore`に`.env`が含まれているか確認してください

---

## 🚀 アプリを起動する手順

### 1. 仮想環境の有効化

**PowerShellの場合:**
```powershell
cd C:\Users\ASUKA\Desktop\streamlit-llm-app
.\venv\Scripts\Activate.ps1
```

**もしエラーが出たら（実行ポリシーの問題）:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
その後、再度仮想環境を有効化してください。

### 2. パッケージのインストール

```powershell
pip install -r requirements.txt
```

### 3. アプリの起動

```powershell
streamlit run app.py
```

### 4. ブラウザでアクセス

自動的にブラウザが開きます。開かない場合は以下のURLにアクセス:
```
http://localhost:8501
```

---

## 📤 GitHubへのアップロード手順

### 初回セットアップ

```bash
# リポジトリの初期化（まだの場合）
git init

# リモートリポジトリの追加
git remote add origin https://github.com/YOUR_USERNAME/streamlit-llm-app.git

# 現在のブランチ名をmainに変更
git branch -M main

# ファイルをステージング
git add .

# コミット
git commit -m "Initial commit: Streamlit LLM app with character selection"

# GitHubにプッシュ
git push -u origin main
```

### 変更を追加する場合

```bash
# 変更をステージング
git add .

# コミット
git commit -m "変更内容の説明"

# プッシュ
git push
```

### プッシュ前の確認

```bash
# .envがステージングされていないか確認
git status

# .envが表示されないことを確認してください！
```

---

## 🐛 トラブルシューティング

### エラー: "ModuleNotFoundError: No module named 'streamlit'"

**解決策:** 仮想環境が有効化されているか確認し、パッケージを再インストール
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### エラー: "OpenAI API key not found"

**解決策:** 
1. `.env`ファイルが正しく作成されているか確認
2. `OPENAI_API_KEY=`の後にAPIキーが正しく記載されているか確認
3. VSCodeを再起動してみる

### PowerShellで仮想環境が有効化できない

**解決策:** 実行ポリシーを変更
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ターミナルのフォントが小さい

**解決策:** このガイドの最初のセクションを参照してください！

---

## ✅ チェックリスト

デプロイ前に以下を確認してください：

- [ ] `.env`ファイルが作成されている
- [ ] `.gitignore`に`.env`が含まれている
- [ ] `git status`で`.env`が表示されない
- [ ] `requirements.txt`が存在する
- [ ] `app.py`が正しく動作する
- [ ] ローカルで正常に起動できる
- [ ] GitHubリポジトリが作成されている
- [ ] リポジトリ名が`streamlit-llm-app`である

すべてチェックできたら、デプロイ準備完了です！🎉


