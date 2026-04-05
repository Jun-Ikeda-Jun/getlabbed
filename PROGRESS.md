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

- **フェーズ**: MVP完成 + E2Eテスト完了、プロダクト品質の最終調整中
- **サービス名**: GetLabbed（getlabbed.com、Xserver Domainで1円、池田さん購入予定）
- **コア体験が確認済み**: Opus 4.6でYoshidora vs Asimoの試合を600フレーム分析 → 癖6件検出 + 30場面分析 + ゲームフロー + 練習メニュー（$3.40/回、217秒）

### 技術仕様（確定）

| 項目 | 値 |
|---|---|
| モデル | claude-opus-4-6（1Mコンテキスト） |
| フレーム | 600枚上限、640x360 Q20-30、2秒おき |
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

### E2Eテスト結果

- テスト動画: Supernova 2024 TOP 8 - Yoshidora (Yoshi) vs Asimo (Ryu)
- 結果ファイル: `data/e2e_opus_full.txt`（13,053文字の完全分析）
- 癖検出6件（セービング依存、復帰ルート単調、昇龍ぶっぱ等）
- 30場面の詳細分析 + 5ゲームのフロー + プロ比較

### アナライザーの現状

- `backend/app/analyzer.py` はまだ旧方式（フレームdict → _select_key_frames）のまま
- E2Eテストはスクリプト直書きで実行した
- **次セッションで analyzer.py を Opus 4.6 + 600フレーム方式に正式リファクタリングする必要あり**
- `backend/app/config.py` のモデルは `claude-sonnet-4-20250514` のまま → `claude-opus-4-6` に変更必要

### マーケティング戦略

- YouTube チャンネルでプロの試合分析動画を投稿（宣伝）→ Claudeサブスクで分析（コスト固定）
- ベータユーザーは無料で分析、アウトプット掲載許可をもらう
- r/CrazyHand、Twitter/X @GetLabbed で展開

### API制限メモ（重要）

- 画像600枚上限（1Mコンテキストモデルのみ。200Kモデルは100枚）
- リクエスト32MB上限（base64で1.33倍になるので注意）
- 10分超のリクエストはストリーミング必須
- 詳細: `~/.claude/rules/common/feedback_claude_api_vision_limits.md`

---

## 次にやること

1. **analyzer.pyをOpus 4.6 + 600フレーム方式にリファクタリング**
   - config.pyのモデルを`claude-opus-4-6`に変更
   - フレーム抽出を640x360 Q20-30に
   - ストリーミング対応
   - E2Eテストスクリプトのロジックをanalyzer.pyに統合

2. **デプロイ**
   - Vercel（フロントエンド）
   - Fly.io or Railway（バックエンド）
   - ドメイン設定（getlabbed.com）

3. **YouTube宣伝チャンネル準備**
   - @GetLabbed アカウント作成
   - プロの試合分析動画を1本作成
   - r/CrazyHand に投稿

4. **ベータユーザー募集**
   - 無料分析 → アウトプット掲載許可
