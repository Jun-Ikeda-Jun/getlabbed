"""Prompt templates for Claude analysis.

All prompts support both Japanese (ja) and English (en) output.
The system prompt establishes FrameCoach's coaching persona.
The user prompt assembles match context + frames for analysis.
"""

from __future__ import annotations

from typing import Any, Literal

# ---------------------------------------------------------------------------
# System prompts
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_JA_FRIENDLY = """\
あなたは「GetLabbed」、大乱闘スマッシュブラザーズSPECIALの \
フレンドリーで頼れるAIコーチです。お前の癖、丸見えだぞ？

## あなたの役割
- 試合の映像フレームを分析して、プレイヤーの良い点と改善点を見つける
- **中学生でも分かる言葉** で説明する（専門用語を使うときは必ずカッコ書きで説明を添える）
- 褒めるところはしっかり褒め、改善点は「こうするともっと良くなるよ」という前向きな言い方にする
- **キャラ固有の知識を使え** — 「ガードから反撃」ではなく「ヨッシーなら掴み6Fで確定→下投げ空前で30%」のように具体的に
- プロプレイヤーの癖や定石を引用して説得力を出す

## 説明のフォーマット
各場面について以下の流れで説明してください：
1. 何が起きたか（事実）
2. なぜそれが重要か（理由） — キャラ固有のデータを根拠に
3. 代わりにどうすればよかったか（改善案）— 具体的なコンボルートや撃墜%を含む
4. 練習メニュー（具体的にトレモで何をすればいいか）

## 口調
- 「〜だよ」「〜だね」のカジュアル敬語
- 「ナイス！」「いい判断！」など、ゲーム実況のような親しみやすさ
- 長文を避け、1つの説明は3〜5文以内

## フレームデータの扱い
フレームデータ（発生F、全体F、判定など）は分析の根拠として内部で使いますが、\
出力にはなるべく含めません。代わりに「速い技」「遅い技」「反撃が間に合う」など、\
体感で分かる表現に翻訳してください。

## プロ知識の活用
プロ知識（キャラガイド、マッチアップ詳細、対戦理論）が提供されている場合は \
必ず活用してください。特に：
- コンボ始動技と撃墜確定コンボは具体的に言及する
- マッチアップ固有の有利不利とその理由を説明する
- プロプレイヤーの名前と特徴的なプレイを引用する
"""

_SYSTEM_PROMPT_JA_DETAILED = """\
あなたは「GetLabbed」、大乱闘スマッシュブラザーズSPECIALの \
エキスパートコーチです。

## あなたの役割
- 試合の映像フレームを分析して、プレイヤーの良い点と改善点を見つける
- フレームデータ・判定・硬直差を引用しながら、技術的に正確な分析をする
- 上級者向けに、具体的な数値と根拠を示す
- プロ知識（キャラガイド、マッチアップ詳細）が提供されている場合は必ず活用する

## 説明のフォーマット
各場面について以下の情報を含めてください：
1. 状況説明（ステージ位置、蓄積%、有利/不利状況）
2. プレイヤーの選択とその評価
3. 最適な選択肢とフレームデータによる裏付け
4. 練習メニュー（トレモ設定を含む）

## 口調
- 丁寧語ベース、ただし堅すぎない
- データを根拠として示す

## フレームデータの扱い
発生F、全体F、ガード硬直差、ヒット時の有利Fなどを積極的に引用してください。
"""

_SYSTEM_PROMPT_EN_FRIENDLY = """\
You are "GetLabbed", a friendly and knowledgeable Super Smash Bros. Ultimate AI coach. \
Your habits? Exposed.

## Your role
- Analyze match footage frame by frame and identify what the player did well and where they can improve
- **Explain everything so a middle schooler can understand** — if you use a technical term, always add a brief explanation in parentheses
- Celebrate good plays enthusiastically, and frame improvements positively ("Here's how to level up" instead of "You messed up")
- **Use character-specific knowledge** — not "punish out of shield" but "Yoshi grab is 6F out of shield → down-throw to fair for 30%"
- Reference pro player habits and established meta knowledge

## Explanation format
For each moment, follow this flow:
1. What happened (facts)
2. Why it matters (reasoning) — cite character-specific data
3. What to do instead (improvement) — include specific combo routes and kill %s
4. Practice drill (specific training mode instructions)

## Tone
- Casual and encouraging, like a supportive older sibling who's really good at Smash
- Use phrases like "Nice!", "Great call!", "Here's a pro tip"
- Keep each explanation to 3-5 sentences

## Frame data handling
Use frame data (startup, total frames, advantage) internally for accuracy, but translate \
to natural language: "fast move", "slow move", "you have time to punish", etc.

## Pro knowledge usage
When pro knowledge (character guides, matchup details, competitive theory) is provided, \
you MUST use it. Specifically:
- Reference combo starters and kill confirms with exact % ranges
- Explain matchup-specific advantages and disadvantages
- Name-drop pro players and their signature habits
"""

_SYSTEM_PROMPT_EN_DETAILED = """\
You are "GetLabbed", an expert-level Super Smash Bros. Ultimate AI coach.

## Your role
- Analyze match footage frame by frame with technical precision
- Reference frame data, hitbox info, and frame advantage in your analysis
- Provide detailed, data-backed coaching for advanced players
- Leverage all provided pro knowledge (character guides, matchup data, competitive theory)

## Explanation format
For each moment, include:
1. Situation (stage position, damage %, advantage state)
2. Player's choice and evaluation
3. Optimal choice with frame data justification
4. Practice drill (including training mode settings)

## Tone
- Professional but not stiff
- Data-driven, always cite numbers

## Frame data handling
Actively reference startup frames, total frames, shield advantage, and hit advantage.
"""

_SYSTEM_PROMPTS = {
    ("ja", "friendly"): _SYSTEM_PROMPT_JA_FRIENDLY,
    ("ja", "detailed"): _SYSTEM_PROMPT_JA_DETAILED,
    ("en", "friendly"): _SYSTEM_PROMPT_EN_FRIENDLY,
    ("en", "detailed"): _SYSTEM_PROMPT_EN_DETAILED,
}


def get_system_prompt(
    language: Literal["ja", "en"],
    mode: Literal["friendly", "detailed"],
) -> str:
    """Return the system prompt for the given language and mode."""
    return _SYSTEM_PROMPTS[(language, mode)]


# ---------------------------------------------------------------------------
# User prompt builder
# ---------------------------------------------------------------------------

_MATCH_CONTEXT_JA = """\
## 試合情報
- プレイヤーキャラ: {player_character}
- 相手キャラ: {opponent_character}
- フレーム数: {total_frames}枚（分析対象: {selected_frames}枚）

## キャラクターデータ
{frame_data_summary}

{matchup_section}

## 分析してほしいこと
以下のフレーム画像を順番に見て、試合の流れを追いながら分析してください。
各フレームの下に記載されたメタデータ（タイムスタンプ、蓄積%など）も参考にしてください。

最終的に以下のJSON形式で出力してください:
```json
{{
  "summary": "試合全体のまとめ（2-3文）",
  "score": 0〜100の数値,
  "moments": [
    {{
      "timestamp": タイムスタンプ(秒),
      "description": "何が起きたか",
      "rating": "great|good|okay|missed_opportunity|mistake|critical_error",
      "suggestion": "改善案（良いプレイなら null）",
      "practice_tip": "練習メニュー（不要なら null）"
    }}
  ],
  "strengths": ["良かった点1", "良かった点2"],
  "weaknesses": ["改善点1", "改善点2"],
  "practice_plan": ["練習メニュー1", "練習メニュー2"],
  "matchup_tips": ["キャラ対策1", "キャラ対策2"]
}}
```
"""

_MATCH_CONTEXT_EN = """\
## Match Info
- Player character: {player_character}
- Opponent character: {opponent_character}
- Total frames: {total_frames} (analyzing: {selected_frames})

## Character Data
{frame_data_summary}

{matchup_section}

## Analysis Request
Review the following frames in order. Track the flow of the match and analyze \
the player's decisions. Use the metadata below each frame (timestamp, damage %, etc.) \
as context.

Output your analysis in the following JSON format:
```json
{{
  "summary": "2-3 sentence match summary",
  "score": 0-100,
  "moments": [
    {{
      "timestamp": timestamp_in_seconds,
      "description": "What happened",
      "rating": "great|good|okay|missed_opportunity|mistake|critical_error",
      "suggestion": "Improvement suggestion (null if play was good)",
      "practice_tip": "Practice drill (null if not needed)"
    }}
  ],
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["area1", "area2"],
  "practice_plan": ["drill1", "drill2"],
  "matchup_tips": ["tip1", "tip2"]
}}
```
"""

_MATCHUP_SECTION_JA = """\
## マッチアップ情報（{char_a} vs {char_b}）
{matchup_summary}
"""

_MATCHUP_SECTION_EN = """\
## Matchup Info ({char_a} vs {char_b})
{matchup_summary}
"""


def _format_pro_knowledge_section(
    pro_knowledge: dict[str, Any] | None,
    language: Literal["ja", "en"],
) -> str:
    """Format pro knowledge into a prompt section."""
    if not pro_knowledge:
        return ""

    sections: list[str] = []
    player_guide = pro_knowledge.get("player_guide")
    opponent_guide = pro_knowledge.get("opponent_guide")
    matchup_guide = pro_knowledge.get("matchup_guide")

    if player_guide and "_alias" not in player_guide:
        char_name = player_guide.get("display_name", player_guide.get("character", ""))
        if language == "ja":
            lines = [f"## プレイヤーキャラ詳細ガイド（{char_name}）"]
        else:
            lines = [f"## Player Character Guide ({char_name})"]

        # Playstyle
        if ps := player_guide.get("playstyle_summary"):
            lines.append(f"**Playstyle**: {ps}")

        # Key strengths (brief)
        strengths = player_guide.get("key_strengths", [])
        if strengths:
            header = "**強み**:" if language == "ja" else "**Strengths**:"
            lines.append(header)
            for s in strengths[:3]:
                lines.append(f"- {s.get('strength', '')}: {s.get('explanation_detailed', s.get('explanation_friendly', ''))}")

        # Key weaknesses (brief)
        weaknesses = player_guide.get("key_weaknesses", [])
        if weaknesses:
            header = "**弱み**:" if language == "ja" else "**Weaknesses**:"
            lines.append(header)
            for w in weaknesses[:3]:
                lines.append(f"- {w.get('weakness', '')}: {w.get('explanation_detailed', w.get('explanation_friendly', ''))}")

        # Combo starters & kill confirms
        adv = player_guide.get("advantage_state", {})
        if combos := adv.get("combo_starters"):
            header = "**コンボ始動**:" if language == "ja" else "**Combo starters**:"
            lines.append(header)
            for c in combos:
                lines.append(f"- {c}")
        if kills := adv.get("kill_confirms"):
            header = "**撃墜確定**:" if language == "ja" else "**Kill confirms**:"
            lines.append(header)
            for k in kills:
                lines.append(f"- {k}")

        # Neutral game
        neutral = player_guide.get("neutral_game", {})
        if mistakes := neutral.get("common_mistakes"):
            header = "**よくあるミス**:" if language == "ja" else "**Common mistakes to watch for**:"
            lines.append(header)
            for m in mistakes:
                lines.append(f"- {m}")

        # Pro player habits
        if pros := player_guide.get("pro_player_habits"):
            header = "**プロの癖**:" if language == "ja" else "**Pro player habits**:"
            lines.append(header)
            for p in pros:
                lines.append(f"- {p.get('player', '')}: {p.get('note', '')}")

        sections.append("\n".join(lines))

    if opponent_guide and "_alias" not in opponent_guide:
        char_name = opponent_guide.get("display_name", opponent_guide.get("character", ""))
        if language == "ja":
            lines = [f"## 相手キャラ情報（{char_name}）"]
        else:
            lines = [f"## Opponent Info ({char_name})"]

        if ps := opponent_guide.get("playstyle_summary"):
            lines.append(f"**Playstyle**: {ps}")
        weaknesses = opponent_guide.get("key_weaknesses", [])
        if weaknesses:
            header = "**相手の弱点（狙い目）**:" if language == "ja" else "**Opponent weaknesses (exploit these)**:"
            lines.append(header)
            for w in weaknesses[:3]:
                lines.append(f"- {w.get('weakness', '')}: {w.get('explanation_detailed', w.get('explanation_friendly', ''))}")

        sections.append("\n".join(lines))

    if matchup_guide:
        if language == "ja":
            lines = ["## マッチアップ詳細ガイド"]
        else:
            lines = ["## Detailed Matchup Guide"]

        if summary := matchup_guide.get("summary"):
            lines.append(summary)
        if tips := matchup_guide.get("player_tips"):
            for tip in tips[:5]:
                lines.append(f"- {tip}")
        if key_interactions := matchup_guide.get("key_interactions"):
            for interaction in key_interactions[:3]:
                lines.append(f"- {interaction}")

        sections.append("\n".join(lines))

    return "\n\n".join(sections)


def _format_youtube_context(
    youtube_excerpts: list[dict[str, Any]] | None,
    language: Literal["ja", "en"],
) -> str:
    """Format YouTube transcript excerpts into a prompt section."""
    if not youtube_excerpts:
        return ""

    if language == "ja":
        lines = ["## プロの解説（YouTube字幕より）"]
    else:
        lines = ["## Pro Commentary (from YouTube)"]

    for entry in youtube_excerpts:
        title = entry.get("title", "")
        channel = entry.get("channel", "")
        excerpt = entry.get("transcript_excerpt", "")
        lines.append(f"### {title} ({channel})")
        lines.append(excerpt)

    return "\n\n".join(lines)


def build_user_prompt(
    *,
    language: Literal["ja", "en"],
    player_character: str,
    opponent_character: str,
    total_frames: int,
    selected_frames: int,
    frame_data_summary: str,
    matchup_data: dict | None,
    pro_knowledge: dict[str, Any] | None = None,
    youtube_excerpts: list[dict[str, Any]] | None = None,
) -> str:
    """Build the text portion of the user message (frames are sent as images)."""
    matchup_section = ""
    if matchup_data:
        matchup_summary = matchup_data.get("summary", matchup_data.get("advantage", ""))
        if language == "ja":
            matchup_section = _MATCHUP_SECTION_JA.format(
                char_a=player_character,
                char_b=opponent_character,
                matchup_summary=matchup_summary,
            )
        else:
            matchup_section = _MATCHUP_SECTION_EN.format(
                char_a=player_character,
                char_b=opponent_character,
                matchup_summary=matchup_summary,
            )

    template = _MATCH_CONTEXT_JA if language == "ja" else _MATCH_CONTEXT_EN
    base_prompt = template.format(
        player_character=player_character,
        opponent_character=opponent_character,
        total_frames=total_frames,
        selected_frames=selected_frames,
        frame_data_summary=frame_data_summary,
        matchup_section=matchup_section,
    )

    # Append pro knowledge sections
    pro_section = _format_pro_knowledge_section(pro_knowledge, language)
    youtube_section = _format_youtube_context(youtube_excerpts, language)

    parts = [base_prompt]
    if pro_section:
        parts.append(pro_section)
    if youtube_section:
        parts.append(youtube_section)

    return "\n\n".join(parts)
