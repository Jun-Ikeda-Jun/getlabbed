# NEXT: GetLabbed（スマブラAIコーチ）

> この NEXT.md は次のアクションだけを書く最小ファイル。
> 詳細な経緯は PROGRESS.md を参照。

## 最優先タスク
Railway Hobby Planへのアップグレード→本番E2Eテストで「Anthropic Connection error」の解消確認。

## 次のステップ（順番）
1. Railway Hobby Plan ($5/月) アップグレード
2. `/api/debug/anthropic` で接続確認
3. 本番E2Eテスト: YouTube URL → フレーム抽出 → Claude Vision → レポート生成
4. ファイルアップロード方式（`/api/analyze-upload`）でのE2Eテスト
5. ベータユーザー募集・フィードバック収集

## 前提・注意
- モデル: claude-opus-4-6（1Mコンテキスト）
- フレーム: 600枚上限、640x360 Q25、2秒おき
- リクエスト32MB上限、10分超はストリーミング必須
- コスト: ~$3.40/回
- プレイヤーキャラ側視点のみでコーチング（相手側アドバイス除外）

## Context（詳細が必要な時だけ参照）
- PROGRESS.md: 「デプロイ済み」「E2Eテスト結果」
- BUSINESS_PLAN.md
- API制限: ~/.claude/rules/common/feedback_claude_api_vision_limits.md

## 最終更新
2026-04-08
