# FrameCoach Go-to-Market & Revenue Strategy Research
> Compiled: 2026-04-05

---

## 1. FGCでバズるマーケティング手法

### 成功事例: Slippi (Melee)

Slippiはスマブラコミュニティでツールが広まった最も成功した事例。

- **起源**: Fizzi (Jas Laferriere) がリプレイインフラを個人プロジェクトとして開発
- **初期拡散**: 大会配信で使用 → 選手・視聴者が自然に認知（The Gang Steals the Script, Pound 2019）
- **爆発的成長**: COVID-19中のロールバックネットコード追加（2020年6月）→ オフライン不可のメレー勢が殺到
- **収益モデル**: Patreon → Stripe直接課金（Ranked機能をペイウォール）
- **派生バイラル**: 「Slippi Wrapped」（年間まとめ）が数百ユーザー/分のアクセスを記録
- **教訓**: **大会で使われる → 選手が広める → コミュニティが自走する**

→ Sources:
- [Project Slippi: a Melee revolution](https://esportsinsider.com/2019/02/project-slippi-a-melee-revolution)
- [Fizzi Laferriere - Releasing the data](https://esportsinsider.com/2019/06/jas-fizzi-laferriere-project-slippi-releasing-the-data)
- [Spotify Smashed: Spotify Wrapped for Melee](https://dotesports.com/fgc/news/spotify-smashed-how-a-small-project-turned-into-spotify-wrapped-for-melee)

### 成功事例: Ultimate Frame Data

- MetalMusicManが個人開発、モバイルフレンドリー
- SmashWiki + Kurogane Hammer + コミュニティのスプレッドシートからデータ集約
- 「試合中にスマホで見れる」実用性でスマブラ勢の定番ツールに
- 広告収入で運営
- **教訓**: **既存の散在データを1箇所に集約 + モバイル最適化 = 定番ツール化**

→ Source: [Ultimate Frame Data](https://ultimateframedata.com/)

### FrameCoachへの応用: 拡散チャネル戦略

| チャネル | 規模 | 戦略 |
|---------|------|------|
| r/smashbros | 約99万人 | 「あなたの試合を分析してみた」投稿。選手名入りの分析結果は高エンゲージメント |
| r/CrazyHand | 約3.3万人 | 上達したい層が集中。「マッチアップで悩んでる人、URL貼ってみて」スレッド |
| Smashcords (Discord) | キャラ別サーバー多数 | 各キャラDiscordにBot/連携。「このマッチアップどうすれば」→ FrameCoachリンク |
| Twitter/X | 選手フォロワー数万〜数十万 | プロの試合を分析 → 選手本人がRT |
| Smashboards | 老舗フォーラム | 長文分析・技術記事向き |

### インフルエンサー活用

**ターゲット候補:**
- **IzawSmash** (YouTube 24万人): スマブラ教育コンテンツのトップ。8,000人以上を指導。$70-80/hでコーチング → FrameCoachは彼の「自動化された弟子」になれる
- **MkLeo**: 世界ランク1位経験者。彼の試合を分析して公開 → 本人がシェアする可能性
- **Sparg0, Tweek**: トップランカー。スカウティング機能のデモに最適

**推奨アプローチ:**
- 有料スポンサーではなく「先に価値を提供」→ プロの試合を無料分析して公開
- プロが自分の練習に使い始める → 自然に配信で言及
- FGCは商業臭を嫌う。「コミュニティツール」として認知されることが最重要

---

## 2. 無料→有料の転換設計

### ベンチマーク

| カテゴリ | フリーミアム→有料転換率 |
|---------|----------------------|
| SaaS全体（B2B中心） | 2.6%〜5.8% |
| ゲーミング（F2P→課金） | 2〜4% (Konvoy Ventures) |
| Consumer SaaS（低単価） | 2〜3% |
| トップパフォーマー（Slack, Spotify） | 10〜30% |

→ Sources:
- [First Page Sage: SaaS Freemium Conversion Rates 2026](https://firstpagesage.com/seo-blog/saas-freemium-conversion-rates/)
- [Konvoy: Freemium Conversion 2-4% in Gaming](https://www.konvoy.vc/newsletters/freemium-conversion-2-4-in-gaming)
- [Userpilot: Freemium Conversion Rate Guide](https://userpilot.com/blog/freemium-conversion-rate/)

### 低単価SaaSのチャーン問題

- **$25未満ARPU → 月間チャーン6.1%**（年間で約53%が離脱）
- Consumer SaaSは「アプリストアで1タップ解約」のため構造的に高チャーン
- **対策**: 年間プランの割引（月額換算で30%オフ等）でチャーンを下げる

→ Source: [MRRSaver: SaaS Churn Rate Benchmarks 2026](https://www.mrrsaver.com/blog/saas-churn-rate-benchmarks)

### FGCを怒らせないペイウォールの置き方

**やってはいけないこと:**
- フレームデータ等の基礎情報を有料にする（FGCは「知識は共有すべき」文化）
- 初回利用で即ペイウォール
- Pay-to-Win的な印象を与える（「金を払えば強くなる」）

**推奨ペイウォール設計:**

| 無料で提供（必須） | 有料の価値（納得感） |
|------------------|-------------------|
| 月3回の分析 | 無制限分析 |
| マッチアップ知識ベース全文 | 自分の傾向トラッキング（時系列） |
| 基本的な改善アドバイス | カスタム練習メニュー |
| | 対戦相手スカウティング |
| | 複数キャラの癖分析 |

**課金トリガーの仮説（優先順）:**
1. **回数制限**: 月3回で足りない → 追加分析したい（最も自然）
2. **成長実感**: 無料分析で「自分の弱点」が見えた → 継続追跡したい
3. **大会前の需要**: 大会前に対戦相手をスカウティングしたい（Competitor プラン）
4. **精度・深さ**: 無料版は概要、有料版は場面ごとの詳細ブレイクダウン

### Slippiの参考事例

Slippiは「Ranked機能」をペイウォールにして課金を集めた。基本機能（リプレイ、ネットプレイ）は無料のまま。コミュニティは「Fizziを支えたい」というモチベーションで課金 → **開発者への共感** も重要な転換要因。

---

## 3. コンテンツマーケティング戦略

### A. マッチアップ知識ベース × SEO

**狙うキーワード群:**
- 「[キャラA] vs [キャラB] smash ultimate」 → 89キャラ × 88 = 7,832通りのマッチアップページ
- 「how to beat [キャラ名] smash ultimate」 → 89ページ
- 「[キャラ名] frame data」 → 既存のUltimate Frame Dataと競合するが、AIアドバイス付きで差別化
- 「smash ultimate improvement guide」 → ピラーページ

**SEO構造:**
```
framecoach.gg/matchups/                     ← ピラーページ
framecoach.gg/matchups/mario-vs-fox/         ← 個別マッチアップ（7,832ページ）
framecoach.gg/characters/mario/              ← キャラ別ガイド（89ページ）
framecoach.gg/guides/how-to-improve/         ← 総合ガイド
```

- 1ページあたりの内容: フレームデータ比較 + AIによるマッチアップ分析 + 推奨戦略 + ユーザーの分析結果から抽出した統計（例: 「このマッチアップでは空中攻撃が最も多いバースト手段」）
- **ユーザー生成データで自動更新**: 分析が増えるほどマッチアップ統計が充実 → SEOコンテンツが自動成長

### B. YouTube / TikTok コンテンツ

**フォーマット案:**

| 形式 | 例 | 長さ | プラットフォーム |
|------|---|------|---------------|
| プロ分析 | 「MkLeoのこの試合、AIはどう見た？」 | 3-5分 | YouTube |
| マッチアップTips | 「マリオ使いがフォックスに勝つ3つの方法」 | 30-60秒 | TikTok/Shorts |
| Before/After | 「FrameCoachのアドバイス実践してみた」 | 2-3分 | YouTube |
| 週間トレンド | 「今週最も分析されたマッチアップTOP5」 | 1分 | TikTok/Shorts |
| 大会プレビュー | 「Kagaribi出場選手のAI分析」 | 5-10分 | YouTube |

**IzawSmash参考**: 彼の「Art of...」シリーズは1動画数十万再生。教育コンテンツの需要は高い。

### C. プロの試合分析コンテンツ

- トーナメントのTop8試合をFrameCoachで分析 → 「○○選手がここで勝てた理由」記事/動画
- 大会後24時間以内に速報分析 → Twitter/Xで拡散
- **選手本人がシェアする確率が高い**（自分の強さをデータで証明できる）

---

## 4. パートナーシップ・コラボ

### start.gg (旧 smash.gg)

- GraphQL APIが公開済み → 技術連携のハードルは低い
- 大会データ（ブラケット、参加者、結果）をFrameCoachに取り込み可能
- **提案**: start.ggの大会ページに「FrameCoachで分析する」ボタンを設置
- npm (`smashgg.js`) / Python (`pysmashgg`) ラッパーも存在

→ Source: [start.gg Developer Portal](https://developer.start.gg/docs/intro/)

### VGBootCamp

- スマブラ最大の配信・メディア企業（GimR主宰）
- Supernova, Kagaribi, Pound, Xanadu等の大会を運営
- 配信中にFrameCoachの分析をオーバーレイ表示 → 視聴者がそのまま自分の試合を分析

→ Source: [VGBootCamp - SmashWiki](https://www.ssbwiki.com/Team:VGBootCamp)

### Metafy

- ゲーミングコーチングプラットフォーム。$33.8M調達済み
- IzawSmashは#1スマブラコーチ（$70-80/セッション、8,000人以上指導）
- **提案**: FrameCoachの分析結果をMetafyコーチが参照できる連携。「AIが見つけた弱点 → 人間コーチが修正」のフロー
- Metafyの新機能（Groups, Courses, Events）にFrameCoach分析を埋め込み

→ Sources:
- [Metafy all-in-one platform](https://esportsinsider.com/2024/12/metafy-all-in-one-platform-gaming-creators)
- [IzawSmash on Metafy](https://metafy.gg/@izaw)

### プロチーム / 選手

- 個別スポンサーではなく「ツール提供」として接近
- Competitor プランを無料提供 → チームの分析ワークフローに入り込む
- 選手の公式プロフィールに「Powered by FrameCoach」

---

## 5. スマブラ以外への展開

### 市場規模比較

| タイトル | PC同時接続（2025ピーク） | 大会規模（Evo 2025） | 技術的類似度 |
|---------|----------------------|---------------------|------------|
| スマブラSP | N/A（コンソール専用） | 3,000+規模の大会多数 | ベースライン |
| Street Fighter 6 | 50,604 | 4,228 | 中（2D格闘、フレームデータ構造が異なる） |
| 鉄拳8 | 16,091 | 2,521 | 中（3D格闘、軸移動の分析が追加） |

→ Sources:
- [SF6 player count](https://www.hotspawn.com/street-fighter/guide/how-many-people-play-street-fighter-6)
- [Evo 2025 stats](https://www.eventhubs.com/news/2025/aug/03/sf6-tekken8-evo-2025-stats/)

### 展開優先順位

1. **Street Fighter 6（最優先）**
   - 最大の競技人口（PC同時接続3万人/日）
   - Evo最多エントリー
   - フレームデータ文化がスマブラと同じくらい根付いている
   - Capcom Pro Tourエコシステムとの連携可能性

2. **鉄拳8（2番目）**
   - 競技人口はSF6の約1/5だが、コアファンの課金意欲は高い
   - 3D軸移動の分析は差別化要因になる

3. **その他（将来）**
   - Guilty Gear Strive, Granblue Fantasy Versus: Rising
   - 市場は小さいがコアファンの密度が高い

### 展開タイミング

- **Phase 1 (〜6ヶ月)**: スマブラSPで月1,000ユーザー達成、プロダクト・マーケット・フィット確認
- **Phase 2 (6〜12ヶ月)**: SF6対応開始。スマブラでの成功事例を使ってFGC全体にアプローチ
- **Phase 3 (12〜18ヶ月)**: 鉄拳8対応。マルチゲーム対応でTAMを3-5倍に拡大

---

## 6. CAC / LTV 試算

### ベンチマーク

| 指標 | 値 | ソース |
|------|---|------|
| ゲーミングアプリ平均LTV | $2.55 | Business of Apps |
| ゲーミングF2P転換率 | 2-4% | Konvoy Ventures |
| SaaSフリーミアム転換率 | 2.6% (オーガニック) | First Page Sage |
| Consumer SaaS月間チャーン | 6.1% ($25未満ARPU) | MRRSaver |
| SaaS理想LTV:CAC比率 | 3:1以上 | 業界コンセンサス |
| リファラルプログラムCAC (B2B SaaS) | $150 | Phoenix Strategy Group |
| ゲーミングテック理想CAC | $25未満 | Financial Models Lab |

→ Sources:
- [Business of Apps: LTV Rates](https://www.businessofapps.com/data/ltv-app-rates/)
- [Financial Models Lab: Gaming KPIs](https://financialmodelslab.com/blogs/kpi-metrics/gaming-industry)
- [Phoenix Strategy Group: CAC Benchmarks](https://www.phoenixstrategy.group/blog/cac-benchmarks-by-channel-2025)

### FrameCoach固有の試算

**前提:**
- Free→Pro転換率: 3%（SaaS+ゲーミング平均）
- Free→Competitor転換率: 0.5%
- Pro月額: ¥1,200 ($8)
- Competitor月額: ¥2,200 ($15)
- 月間チャーン: 6%（低単価Consumer SaaSベンチマーク）
- 平均顧客寿命: 1/0.06 = 16.7ヶ月

**LTV計算:**
- Pro LTV = ¥1,200 × 16.7 = **¥20,040** (~$134)
- Competitor LTV = ¥2,200 × 16.7 = **¥36,740** (~$245)
- Blended LTV（Pro 85%: Competitor 15%）= **¥22,545** (~$150)

**LTV:CAC 3:1を維持するためのCAC上限:**
- 許容CAC = ¥22,545 / 3 = **¥7,515** (~$50)

### 月1,000ユーザー / 月5,000ユーザーの売上予測

#### Scenario A: 月間アクティブユーザー 1,000人

| 指標 | 値 |
|------|---|
| 無料ユーザー | 965人 |
| Proユーザー（3%） | 30人 |
| Competitorユーザー（0.5%） | 5人 |
| 月間MRR | ¥36,000 + ¥11,000 = **¥47,000** (~$313) |
| 年間ARR | **¥564,000** (~$3,760) |

#### Scenario B: 月間アクティブユーザー 5,000人

| 指標 | 値 |
|------|---|
| 無料ユーザー | 4,825人 |
| Proユーザー（3%） | 150人 |
| Competitorユーザー（0.5%） | 25人 |
| 月間MRR | ¥180,000 + ¥55,000 = **¥235,000** (~$1,567) |
| 年間ARR | **¥2,820,000** (~$18,800) |

#### Scenario C: 転換率を上げた場合（5% Pro, 1% Competitor）

**5,000ユーザー + 高転換率:**

| 指標 | 値 |
|------|---|
| Proユーザー（5%） | 250人 |
| Competitorユーザー（1%） | 50人 |
| 月間MRR | ¥300,000 + ¥110,000 = **¥410,000** (~$2,733) |
| 年間ARR | **¥4,920,000** (~$32,800) |

### 売上を上げるレバー

1. **転換率向上**: 3% → 5%で売上1.7倍。ペイウォールの位置と体験が鍵
2. **チャーン削減**: 6% → 4%で平均顧客寿命が16.7 → 25ヶ月。年間プラン推奨
3. **ARPU向上**: 年間プラン（10ヶ月分の価格で12ヶ月）でARPU向上 + チャーン削減の一石二鳥
4. **横展開**: SF6対応でTAM 3-5倍。同じインフラで複数ゲームを回せる

### 現実的なCAC想定（コミュニティ主導）

FGCツールの強みは**オーガニック獲得が主力**になること。

| チャネル | 想定CAC | 備考 |
|---------|---------|------|
| Reddit/Discord（オーガニック） | ¥0〜500 | 投稿・口コミ。工数のみ |
| Twitter/X（オーガニック） | ¥0〜500 | プロの試合分析コンテンツ |
| YouTube/TikTok | ¥500〜1,500 | 動画制作コスト |
| インフルエンサー提携 | ¥1,000〜3,000 | ツール無料提供 + 紹介料 |
| SEO（マッチアップページ） | ¥0〜300 | 初期構築後は自動流入 |
| 有料広告（Twitter/Reddit） | ¥3,000〜5,000 | 最も高コスト、後回し |

**Blended CAC目標: ¥1,000〜2,000（$7-13）** → LTV:CAC比率 11:1〜22:1で非常に健全

---

## 7. 市場全体像: AI esportsコーチング

### 市場規模

- AI in Esports Performance Tracking市場: 2025年 $455M → 2035年 $6,671M (CAGR 30.8%)
- Esports Coaching AI市場: 2024年 $386M → 2033年 $2,186M (CAGR 20.1%)

→ Sources:
- [AI in Esports Performance Tracking Market](https://market.us/report/ai-in-esports-performance-tracking-market/)
- [Esports Coaching AI Market](https://dataintelo.com/report/esports-coaching-ai-market)

### 競合

| サービス | 対象ゲーム | モデル | FrameCoachとの差 |
|---------|----------|------|-----------------|
| Omnic.AI | FPS（Valorant等） | AI動画分析 | FPS特化、格闘ゲーム非対応 |
| Aimlabs | FPS | エイム練習 + 分析 | 40M+ユーザー。格闘ゲーム非対応 |
| Metafy | 全ジャンル | 人間コーチ | AI分析なし。補完関係 |
| Ultimate Frame Data | スマブラ | 静的データ参照 | AI分析なし。データソースとして共存可能 |
| ProGuides | 複数 | 動画教材 + コーチ | 格闘ゲーム弱い |

**FrameCoachのポジション**: 格闘ゲーム × AI動画分析 → **直接競合がほぼゼロ**。ブルーオーシャン。

---

## 8. スマブラSP競技シーンの健全性（2025-2026）

サービスの持続性を判断するための重要データ。

- **2025年の大会数**: 1,927大会、67カ国、54,544人参加、313,434セット
- **Kagaribi#14（2025年11月）**: 1,520エントリー
- **プレイヤーDB**: 732,517プロフィール、217,747大会を追跡
- **UltRank 2025**: 「このゲームは死んでいない。むしろ最も激戦の大会がYear 7で実現した」
- **バランスパッチは終了済み** → メタは選手の発見で緩やかに進化
- **賞金総額**: 2025年 $258,427

→ Sources:
- [UltRank 2025 Introduction](https://medium.com/@ultrankssb/ultrank-2025-introduction-and-honorable-mentions-bd0eabf3b0ac)
- [Smash Player Database](https://smashdata.gg/)
- [Upcoming SSB Events](https://escharts.com/upcoming-tournaments/ssb)

**結論**: スマブラSPの競技シーンは2025-2026時点で健全。新作発表がなくても年間5万人以上が大会参加。ただし、新作発表があれば移行リスクあり → マルチゲーム対応の伏線を早めに張る。

---

## 9. 推奨GTMタイムライン

### Month 1-2: コミュニティシーディング
- [ ] r/CrazyHandに「あなたの試合をAIが分析」無料提供スレッド
- [ ] トップ選手の試合を5本分析 → Twitter/Xで公開
- [ ] 各キャラDiscord（Smashcords経由）にマッチアップ分析を投稿
- [ ] 目標: 500無料ユーザー

### Month 3-4: コンテンツ拡大
- [ ] マッチアップ知識ベース（89キャラ × 上位20マッチアップ）をSEOページとして公開
- [ ] YouTube/TikTokで週2本のショート動画開始
- [ ] IzawSmash or 類似のコンテンツクリエイターにアプローチ
- [ ] 目標: 1,000無料ユーザー、30 Pro課金

### Month 5-6: パートナーシップ + 大会
- [ ] start.gg API連携（大会結果 → 自動分析提案）
- [ ] VGBootCamp配信でのオーバーレイテスト
- [ ] Metafyコーチ向けのダッシュボード提供
- [ ] 主要大会（Supernova, Kagaribi等）で「大会参加者限定Pro無料トライアル」
- [ ] 目標: 3,000無料ユーザー、100 Pro課金

### Month 7-12: スケール + 横展開準備
- [ ] SF6対応のプロトタイプ開発開始
- [ ] 年間プラン導入（チャーン対策）
- [ ] Competitor プランのβテスト（プロチーム向け）
- [ ] 目標: 5,000無料ユーザー、200 Pro + 30 Competitor
- [ ] 月間MRR: ¥300,000〜400,000
