# Streamlit LLM App

このリポジトリには複数のStreamlitアプリケーションが含まれています。

## アプリケーション

### ホテルチェックインアプリ (`hotel_checkin_app.py`)

ホテルのチェックイン用タブレットアプリケーションです。

**機能:**
- 4言語対応（日本語、英語、韓国語、中国語）- 現在日本語のみ動作
- 予約検索（名前、予約番号、電話番号）
- 予約確認
- お客様情報登録
- 同伴者登録
- 宿泊税計算・徴収
- QRコード表示（日本人客のみ）
- 部屋番号表示

**起動方法:**
```bash
streamlit run hotel_checkin_app.py
```

詳細は `HOTEL_CHECKIN_README.md` を参照してください。

## その他のアプリ

- `app.py` - LLMチャットアプリ
- `taxi_app.py` - タクシーアプリ

## セットアップ

```bash
pip install -r requirements.txt
```

## デプロイ

Streamlit Cloudでデプロイする場合、各アプリのファイル名を指定してください。
