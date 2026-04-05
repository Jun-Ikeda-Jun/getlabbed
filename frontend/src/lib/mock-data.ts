import type { MatchAnalysis } from "./types";

export const MOCK_ANALYSIS: MatchAnalysis = {
  summary:
    "全体的にいい試合でした！空中攻撃の当て方がうまく、特に空前のリーチ管理が光っていました。ただ、崖の攻防で同じパターンを繰り返してしまい、相手に読まれている場面が目立ちました。崖上がりのバリエーションを増やせば、もっと安定して勝てるようになりますよ。",
  score: 72,
  result: "win",
  stage: "戦場 / Battlefield",
  player_character: "yoshi",
  opponent_character: "mario",
  habits: [
    {
      habit: "崖上がりパターンの固定化",
      description: "その場上がりを3回連続で選択。相手に読まれてスマッシュを置かれた。",
      count: "3回中3回がその場上がり",
      impact: "相手がパターンを読んでスマッシュを合わせ、1ストック失った",
      fix: "その場・攻撃・回避・ジャンプの4択をランダムに使い分ける。同じ択は2回連続まで。",
    },
    {
      habit: "ガーキャン行動の遅延",
      description: "ガードを解いてから技を振る癖があり、反撃が間に合わない場面が複数あった。",
      count: "ガーキャンチャンス4回中3回で遅延",
      impact: "確定反撃を逃し、合計40%以上のダメージ機会を損失",
      fix: "ガード中に直接上スマッシュ入力。ガードボタンを離さずにスティック上+A。",
    },
  ],
  game_flow: [
    {
      game: 1,
      summary: "序盤はコンボで%リードを作ったが、中盤の崖攻防で読まれ始め、終盤に逆転勝利。",
      turning_point: "98秒の崖上がり3連続読まれから流れが変わりかけたが、210秒の空前→空上撃墜で取り返した。",
    },
  ],
  pro_comparison: "空中攻撃のリーチ管理はRon（ヨッシー使い上位）に通じるものがある。ただしRonは崖上がりの択を毎回変えており、崖の攻防での被弾率が圧倒的に低い。崖上がりの改善だけでワンランク上に行ける。",
  moments: [
    {
      timestamp: 23,
      description: "開幕の空Nからコンボを繋げて22%。いいスタート！",
      rating: "great",
      suggestion: null,
      practice_tip: null,
    },
    {
      timestamp: 43,
      description:
        "相手の着地を待って掴んだのはナイス！ここから下投げ→空上で20%取れるよ。",
      rating: "great",
      suggestion: "下投げ→空上のコンボルートを覚えよう",
      practice_tip:
        "トレモで掴み→下投げ→空上を低%・中%・高%で10回ずつ練習",
    },
    {
      timestamp: 67,
      description: "台上で待つ判断は悪くなかった。相手の動きを見れている。",
      rating: "good",
      suggestion: null,
      practice_tip: null,
    },
    {
      timestamp: 98,
      description:
        "崖でその場上がりを3回連続で選んでいる。相手がパターンを読んでスマッシュを置き始めた。",
      rating: "missed_opportunity",
      suggestion:
        "崖上がりは毎回変えよう：その場、攻撃、回避、ジャンプの4択をランダムに",
      practice_tip:
        "崖上がりの練習：相手に崖待ちさせて、4種類をランダムに使い分ける。10回中同じ択が3回以上出ないように",
    },
    {
      timestamp: 125,
      description:
        "空後を当てに行ったけど、反転が間に合わなくて空前が出てしまった。",
      rating: "mistake",
      suggestion: "反転空後は練習あるのみ。引きながらジャンプ→空後の入力を意識",
      practice_tip:
        "トレモでマリオを相手に、引き空後を20回連続で出す練習。安定したら実戦で使おう",
    },
    {
      timestamp: 156,
      description: "相手のファイアボールを卵で相殺しつつ接近。判断が良い。",
      rating: "good",
      suggestion: null,
      practice_tip: null,
    },
    {
      timestamp: 178,
      description:
        "復帰阻止に行ったのは良い判断！ただ技が当たらなくて自分も崖外に。リスクが高かった。",
      rating: "okay",
      suggestion:
        "マリオの復帰は上Bのルートが限られるから、崖で待つ方が安全。無理に外に出なくてOK",
      practice_tip: null,
    },
    {
      timestamp: 210,
      description:
        "相手120%で空前→空上で撃墜！コンボ火力が素晴らしい。",
      rating: "great",
      suggestion: null,
      practice_tip: null,
    },
    {
      timestamp: 245,
      description:
        "ガーキャンから上スマが出せなかった。ガードが解けてからスマッシュを振ったので遅れた。",
      rating: "critical_error",
      suggestion:
        "ガーキャン上スマはガード中に上スマ入力。ガードを解いてからだと遅い",
      practice_tip:
        "トレモでCPUの攻撃をガード→ガーキャン上スマを50回。反射的に出せるようになるまで",
    },
    {
      timestamp: 289,
      description:
        "最終ストックで冷静にタイムアウトを狙わず攻めたのは良い判断。",
      rating: "good",
      suggestion: null,
      practice_tip: null,
    },
  ],
  strengths: [
    "空中攻撃のリーチ管理がうまい。特に空前の先端当てが安定している",
    "コンボ火力が高い。掴みからのリターンをしっかり取れている",
    "相手の動きを見てから行動できている。読み合いの意識が良い",
    "台を使った立ち回りが上手。台上からのプレッシャーが効いている",
  ],
  weaknesses: [
    "崖上がりのパターンが単調。その場上がりに偏りすぎ",
    "ガーキャン行動が遅い。ガードを解いてから技を振る癖がある",
    "反転空後の精度が低い。とっさの場面で空前が出てしまう",
    "復帰阻止のリスク管理が甘い。無理に崖外に出て自分が危なくなる",
  ],
  practice_plan: [
    "トレモで掴み→下投げ→空上のコンボを低%・中%・高%で各10回（15分）",
    "崖上がり4択をランダムに使い分ける練習。相手に崖待ちさせて20回（10分）",
    "ガーキャン上スマの反復練習。CPU Lv3の攻撃をガードしてから反撃50回（15分）",
    "反転空後の入力練習。引きジャンプ→空後を安定させる20回連続（10分）",
    "実戦で意識すること：崖上がりを毎回変える、ガーキャンを意識する",
  ],
  matchup_tips: [
    "マリオのファイアボールは卵で相殺できる。焦って飛び込まないこと",
    "マリオの上Bは無敵が少ない。崖で待って復帰を狩るのが安全",
    "マリオの下投げ→空上のコンボに注意。ずらしを入れて抜けよう",
    "マリオはケープで飛び道具を反射するので、卵は近距離で使わない",
    "マリオの横スマッシュは発生が早いので、崖上がりでその場上がりは危険",
  ],
};

export const MOCK_ANALYSIS_EN: MatchAnalysis = {
  ...MOCK_ANALYSIS,
  habits: MOCK_ANALYSIS.habits.map((h) => ({ ...h })),
  game_flow: MOCK_ANALYSIS.game_flow.map((g) => ({ ...g })),
  pro_comparison: "Your aerial spacing is reminiscent of Ron (top Yoshi player). However, Ron varies his ledge options every time, keeping his ledge vulnerability extremely low. Fixing your ledge habits alone would take you to the next level.",
  summary:
    "Overall a great match! Your aerial spacing was excellent, especially with forward air range management. However, you kept choosing the same ledge options repeatedly and your opponent started reading you. Adding variety to your ledge getups will make you much more consistent.",
  moments: MOCK_ANALYSIS.moments.map((m) => ({ ...m })),
  strengths: [
    "Excellent aerial spacing, especially forward air tipper",
    "Strong combo game with good grab follow-ups",
    "Good patience - waiting and reacting rather than rushing",
    "Smart use of platforms for pressure and mixups",
  ],
  weaknesses: [
    "Ledge options are too predictable - favoring neutral getup too much",
    "Out-of-shield options are slow - dropping shield before acting",
    "Reverse back air accuracy needs work - getting forward air instead",
    "Edgeguard risk management is loose - going offstage unnecessarily",
  ],
  practice_plan: [
    "Training mode: grab > down throw > up air combos at low/mid/high % (15 min)",
    "Ledge mixup practice: use all 4 options randomly, 20 reps (10 min)",
    "Out-of-shield up smash drill: shield CPU attacks then punish, 50 reps (15 min)",
    "Reverse back air practice: retreat jump > back air, 20 consecutive (10 min)",
    "In-game focus: vary ledge options every time, stay conscious of OOS punishes",
  ],
  matchup_tips: [
    "Mario's fireball can be traded with egg. Don't panic approach",
    "Mario's up B has little invincibility. Wait at ledge to punish recovery",
    "Watch out for Mario's down throw > up air. DI away to escape",
    "Mario can cape your eggs, so don't throw them at close range",
    "Mario's forward smash is fast - neutral getup at ledge is risky",
  ],
};
