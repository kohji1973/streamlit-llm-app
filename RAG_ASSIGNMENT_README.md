# 中間課題：RAGシステムの開発 - 解答

## 概要

この課題では、Google Driveに保存された「オンラインMTG議事録」を外部参照するRAG（Retrieval-Augmented Generation）システムを開発します。

## 主な機能

1. **再帰的ファイル処理**
   - Google Drive内の複数階層のフォルダ構造から議事録ファイル（.docx）を自動的に読み込み
   - 「データベース化前」フォルダから「データベース化済み」フォルダへの自動コピー

2. **ベクターストアの管理**
   - 各テーマごとのベクターストア作成（営業、マーケティング、開発など）
   - 全テーマ横断のベクターストア作成
   - 増分更新対応（既存のベクターストアへのデータ追加）

3. **RAGシステムの実装**
   - LangChainを使用したConversationalRetrievalChainの構築
   - 会話履歴の記憶機能
   - ストリーミング出力対応

4. **対話機能**
   - 会話履歴を考慮した質問応答
   - インタラクティブな対話ループ
   - 参照元ドキュメントの確認

## ファイル構成

- `rag_assignment_solution.ipynb` - メインのJupyter Notebookファイル

## 使用方法

### 1. Google Colabでの実行

1. `rag_assignment_solution.ipynb` をGoogle Colabにアップロード
2. OpenAI APIキーをGoogle Colabのシークレットに設定
   - 左側メニューの「🔑」アイコンをクリック
   - `OPENAI_API_KEY` という名前でAPIキーを追加
3. セルを順番に実行

### 2. 事前準備

Google Driveに以下の構造でフォルダを作成してください：

```
オンラインMTG議事録/
├── 営業/
│   ├── データベース化前/
│   │   └── 議事録1.docx
│   └── データベース化済み/
├── マーケティング/
│   ├── データベース化前/
│   └── データベース化済み/
├── 開発/
│   ├── データベース化前/
│   └── データベース化済み/
└── ... (その他のテーマ)
```

### 3. 主要なコンポーネント

#### ヒント①：再帰的ファイル読み込み
- `recursive_file_check()` 関数で階層構造を再帰的に処理
- `file_load()` 関数でDocxファイルを読み込み、テーマ別に整理

#### ヒント②：ベクターストア作成の事前準備
- `CharacterTextSplitter` でドキュメントをチャンク分割
- `OpenAIEmbeddings` でテキストのベクトル化

#### ヒント③：ベクターストアの作成と管理
- Chromaを使用したベクターストアの作成
- 既存のベクターストアへの増分追加
- テーマごとと全テーマ横断の2種類のベクターストア管理

#### ヒント④：RAGシステムの構築（最重要）
- `ConversationalRetrievalChain` による会話履歴を考慮したRAG
- `ConversationBufferMemory` による会話履歴の管理
- ストリーミング出力による応答性の向上

## 技術スタック

- **LangChain**: RAGシステムの構築
- **OpenAI API**: GPT-3.5-turboによる回答生成
- **Chroma**: ベクターストアの管理
- **python-docx / docx2txt**: Word文書の読み込み
- **tiktoken**: トークン数の計算

## 主要な実装ポイント

### 1. ベクターストアの増分更新

```python
if os.path.isdir(f"{dir_path}/.db/.{theme_name}_chromadb"):
    # 既存のベクターストアを読み込んでデータを追加
    db = Chroma(persist_directory=f"{dir_path}/.db/.{theme_name}_chromadb", embedding_function=embeddings)
    db.add_documents(documents=splitted_docs)
else:
    # 新規にベクターストアを作成
    db = Chroma.from_documents(splitted_docs, embeddings, persist_directory=f"{dir_path}/.db/.{theme_name}_chromadb")
```

### 2. 会話履歴の記憶機能

```python
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"
)

qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=retriever,
    memory=memory,
    return_source_documents=True
)
```

### 3. ストリーミング出力

```python
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)
```

## トラブルシューティング

### よくある問題

1. **Google Driveのマウントエラー**
   - Google Colabでドライブへのアクセスを許可してください

2. **APIキーエラー**
   - OpenAI APIキーが正しく設定されているか確認してください

3. **メモリ不足エラー**
   - 大量のドキュメントを処理する場合、チャンクサイズを調整してください

4. **ベクターストアの読み込みエラー**
   - リセット処理を実行して、ベクターストアを再作成してください

## 学習ポイント

この課題を通じて以下のスキルを習得できます：

1. **再帰処理の理解**: 複雑なフォルダ構造の処理
2. **ベクターストアの管理**: 増分更新と複数ストアの管理
3. **RAGの実装**: LangChainを使った実践的なRAGシステム
4. **会話履歴の管理**: 文脈を考慮した対話システム
5. **エラー処理**: 実用的なエラーハンドリング

## 発展課題

1. 特定のテーマに絞った質問応答システムの実装
2. 複数のベクターストアを横断的に検索する機能
3. 回答の根拠となるドキュメントの引用表示
4. ユーザー評価システムの追加
5. Streamlitを使ったWebアプリ化

## ライセンス

このコードは学習目的で提供されています。

## 注意事項

- OpenAI APIの使用には料金が発生します
- Google Driveの容量に注意してください
- 個人情報を含むドキュメントの取り扱いには十分注意してください




