# GetLabbed — スマブラAIコーチ

> 過去ログ: [archive/PROGRESS_research_and_design.md](archive/PROGRESS_research_and_design.md)

## 過去の経緯（要約）

- リサーチ: 格ゲーAIコーチは世界にゼロ。FPS向けOmnic.AI($9.99/月)が参考モデル
- MVP設計: YouTube URL → フレーム抽出 → Claude Vision分析 → コーチングレポート
- サービス名「GetLabbed」に決定。フロントエンド（Next.js）リブランド済み
- 知識ベース構築完了（89キャラフレームデータ + 87キャラプロ知識 + YouTube字幕50本）
- RAG統合完了（プロ知識がClaudeプロンプトに注入される）
- ビジネスプラン: [BUSINESS_PLAN.md](BUSINESS_PLAN.md)

---

## 現在の状態

- **フェーズ**: E2Eテスト中（Railway Hobbyプランへのアップグレード待ち）
- **サービス名**: GetLabbed
- **GitHub**: https://github.com/Jun-Ikeda-Jun/getlabbed (public)

### デプロイ済み

1. **Railwayバックエンド**: Online（US Westリージョン）
   - URL: https://getlabbed-production.up.railway.app
   - 修正内容: Dockerfileの$PORT対応、mainブランチをproduction環境に接続、yt-dlp iOSクライアント対応、Anthropicタイムアウト15分、`/api/analyze-upload`追加

2. **Vercelフロントエンド**: Online
   - URL: https://getlabbed.vercel.app（リネーム完了）
   - 環境変数: `NEXT_PUBLIC_API_URL=https://getlabbed-production.up.railway.app`, `NEXT_PUBLIC_MOCK_MODE=false`

3. **API動作確認済み**（基本機能）
   - /api/health OK
   - 89キャラ読み込みOK
   - キャラ選択ドロップダウン動作確認済み

### E2Eテスト結果

- **ローカル**: 成功（72秒のHungrybox vs JustASnowball動画 → スコア92点、12モーメント、プロ比較で「これはHungrybox本人」と正しく認識。約1分7秒で完了）
- **Railway**: Anthropic APIへのConnection error
  - 原因: Trial PlanのRAM 0.5GB制限 + 制限されたアウトバウンドネットワーク
  - 解決策: **Hobby Plan ($5/月、8GB RAM、ネットワーク制限なし) にアップグレード中**
  - デバッグエンドポイント: `/api/debug/anthropic` で接続確認可能

### YouTube直接DLの問題

- yt-dlpがクラウドサーバーIPでYouTubeに「Sign in to confirm you're not a bot」とブロックされる
- iOSクライアント (`extractor_args` で `player_client=ios`) で**ローカルでは回避可能**だが、Railway上では不安定
- 対策: ファイルアップロード方式（`/api/analyze-upload`）を追加。フロントから動画ファイル直接送信

### 過去の実装サマリ

1. **analyzer.pyリファクタリング完了**
   - config.py: モデル `claude-opus-4-6`、枚数上限600
   - frame_extractor.py: 640x360 Q25、0.5fps（2秒おき）
   - analyzer.py: `_select_key_frames`削除（全フレーム送信）、ストリーミング対応、max_tokens 16384
   - pipeline.py: デフォルトfps=0.5に変更

2. **分析品質の改善**
   - プレイヤーキャラ側の視点のみでコーチング（相手側アドバイス除外）
   - タイムスタンプはフレーム画像の値をそのまま使用する指示
   - スコア0-100のルーブリック追加（プロ/上級/中級/初中級/初心者）
   - habits（癖検出）, game_flow, pro_comparison フィールド追加
   - フロントエンドに癖・ゲームフロー・プロ比較セクション追加
   - models.pyにPlayerHabit, GameFlow追加、analyzer.pyパーサー対応

3. **デプロイ設定**
   - Dockerfile作成（プロジェクトルート。cv2 + tesseract + ffmpeg）
   - railway.toml作成
   - .gitignore作成
   - GitHubリポ作成 + push済み

### 技術仕様（確定）

| 項目 | 値 |
|---|---|
| モデル | claude-opus-4-6（1Mコンテキスト） |
| フレーム | 600枚上限、640x360 Q25、2秒おき |
| リクエスト | ~15-20MB（32MB制限内） |
| 出力 | 8K-16Kトークン |
| コスト | ~$3.40/回 |
| APIキー | → credential_microsoft365.md参照（Anthropic APIセクション） |

### 知識ベース

- [x] フレームデータ（89キャラ） → `data/frame_data/`
- [x] キャラプロフィール（89キャラ） → `data/characters.json`
- [x] プロ知識（87ファイル = 89キャラ全カバー） → `data/pro_knowledge/`
- [x] マッチアップチャート → `data/matchup_data/`
- [x] YouTube字幕（50本、872KB） → `data/youtube_transcripts/`
- [x] RAGとしてバックエンドに統合済み

### API制限メモ（重要）

- 画像600枚上限（1Mコンテキストモデルのみ。200Kモデルは100枚）
- リクエスト32MB上限（base64で1.33倍になるので注意）
- 10分超のリクエストはストリーミング必須
- 詳細: `~/.claude/rules/common/feedback_claude_api_vision_limits.md`

---

## 次にやること

1. **Railway Hobbyプラン課金完了** ← ユーザー操作待ち
   - Subscribe画面でカード情報入力 → Subscribe実行
   - 完了後、デプロイ自動再起動

2. **Hobbyプラン稼働後のE2E再テスト**
   - `/api/debug/anthropic` でAnthropic接続確認
   - `/api/analyze-upload` で `/tmp/test_match.mp4` を投げて全工程テスト
   - 想定: ローカル同様、約1分で分析完了

3. **フロントエンドのファイルアップロード対応**
   - 現在のフロントはYouTube URL専用 → ファイルアップロードUIを追加
   - もしくはYouTube URL方式を諦めて完全にアップロード方式に切り替え

4. **YouTube宣伝チャンネル準備**
   - @GetLabbed アカウント作成
   - プロの試合分析動画を1本作成

5. **ベータユーザー募集**
   - r/CrazyHand に投稿
   - 無料分析 → アウトプット掲載許可
