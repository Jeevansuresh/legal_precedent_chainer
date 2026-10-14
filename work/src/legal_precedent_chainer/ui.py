from __future__ import annotations


def render_home_page() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Legal Precedent Chainer | Legal Intelligence Platform</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --bg-dark: #090d16;
      --bg-card: rgba(17, 24, 39, 0.7);
      --bg-card-hover: rgba(24, 34, 53, 0.85);
      --bg-card-solid: #0f172a;
      --bg-input: rgba(15, 23, 42, 0.6);
      
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-glow: rgba(59, 130, 246, 0.3);
      --border-accent: rgba(245, 158, 11, 0.4);
      
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      
      --primary: #3b82f6;
      --primary-glow: rgba(59, 130, 246, 0.25);
      --primary-hover: #60a5fa;
      
      --gold: #f59e0b;
      --gold-glow: rgba(245, 158, 11, 0.2);
      
      --emerald: #10b981;
      --rose: #f43f5e;
      --amber: #fbbf24;
      --sky: #38bdf8;
      
      --radius-sm: 8px;
      --radius-md: 12px;
      --radius-lg: 18px;
      --radius-full: 9999px;
      
      --shadow-glow: 0 0 25px rgba(59, 130, 246, 0.15);
      --shadow-gold: 0 0 25px rgba(245, 158, 11, 0.15);
      --glass-backdrop: blur(16px) saturate(180%);
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      color: var(--text-main);
      background-color: var(--bg-dark);
      background-image: 
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(59, 130, 246, 0.15), transparent),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(245, 158, 11, 0.08), transparent),
        radial-gradient(circle at 10% 40%, rgba(14, 165, 233, 0.05), transparent);
      background-attachment: fixed;
      min-height: 100vh;
      overflow-x: hidden;
      line-height: 1.5;
    }

    /* Ambient Background Mesh */
    .bg-mesh {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      pointer-events: none;
      z-index: 0;
      background-size: 40px 40px;
      background-image: 
        linear-gradient(to right, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
      mask-image: radial-gradient(circle at 50% 30%, black 40%, transparent 80%);
    }

    .page {
      position: relative;
      z-index: 1;
      max-width: 1360px;
      margin: 0 auto;
      padding: 32px 24px 60px;
    }

    /* Header & Branding */
    .head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
      margin-bottom: 32px;
      padding-bottom: 24px;
      border-bottom: 1px solid var(--border-subtle);
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .brand-icon {
      width: 48px;
      height: 48px;
      border-radius: var(--radius-md);
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(59, 130, 246, 0.2));
      border: 1px solid var(--border-accent);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: var(--shadow-gold);
    }

    h1 {
      margin: 0;
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 2.2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      background: linear-gradient(135deg, #ffffff 40%, #cbd5e1 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .sub {
      margin: 4px 0 0;
      color: var(--text-muted);
      font-size: 0.95rem;
      font-weight: 400;
    }

    /* Stats Grid */
    .stats {
      display: flex;
      gap: 12px;
    }

    .stat {
      background: var(--bg-card);
      backdrop-filter: var(--glass-backdrop);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 12px 18px;
      min-width: 120px;
      transition: all 0.25s ease;
    }

    .stat:hover {
      border-color: var(--border-glow);
      transform: translateY(-2px);
      box-shadow: var(--shadow-glow);
    }

    .stat .k {
      font-size: 0.7rem;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 700;
    }

    .stat .v {
      margin-top: 4px;
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--text-main);
      font-family: 'JetBrains Mono', monospace;
    }

    /* Cards & Layout */
    .card {
      background: var(--bg-card);
      backdrop-filter: var(--glass-backdrop);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-lg);
      padding: 28px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
      margin-bottom: 24px;
      transition: border-color 0.3s ease;
    }

    .card:hover {
      border-color: rgba(255, 255, 255, 0.12);
    }

    .card-title {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .card h2 {
      margin: 0;
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .card h2 span.icon {
      font-size: 1.2rem;
    }

    /* Form Controls */
    .field-group {
      margin-bottom: 16px;
    }

    label {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-muted);
      font-size: 0.82rem;
      font-weight: 600;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    input, select, textarea {
      width: 100%;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 12px 14px;
      background: var(--bg-input);
      color: var(--text-main);
      font-size: 0.95rem;
      font-family: inherit;
      outline: none;
      transition: all 0.2s ease;
    }

    textarea {
      min-height: 90px;
      resize: vertical;
      line-height: 1.6;
    }

    input:focus, select:focus, textarea:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
      background: rgba(15, 23, 42, 0.85);
    }

    select option {
      background: #0f172a;
      color: #fff;
    }

    .form-grid-3 { display: grid; grid-template-columns: 1.2fr 1.2fr 1fr; gap: 14px; }
    .form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

    /* Buttons */
    .actions {
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-top: 20px;
      align-items: center;
    }

    .btn {
      border: none;
      border-radius: var(--radius-md);
      padding: 12px 20px;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      letter-spacing: 0.01em;
    }

    .btn.primary {
      background: linear-gradient(135deg, var(--primary), #1d4ed8);
      color: #ffffff;
      box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
    }

    .btn.primary:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(59, 130, 246, 0.6);
      filter: brightness(1.1);
    }

    .btn.secondary {
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.2));
      color: var(--gold);
      border: 1px solid var(--border-accent);
    }

    .btn.secondary:hover {
      background: rgba(245, 158, 11, 0.3);
      transform: translateY(-1px);
    }

    .btn.ghost {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
    }

    .btn.ghost:hover {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text-main);
    }

    .btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none !important;
    }

    /* Details styling */
    details {
      margin-top: 14px;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.2);
    }

    summary {
      cursor: pointer;
      font-weight: 600;
      color: var(--sky);
      font-size: 0.88rem;
      user-select: none;
    }

    /* Toast Notification */
    .toast-container {
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 1000;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .toast {
      background: var(--bg-card-solid);
      border: 1px solid var(--border-subtle);
      border-left: 4px solid var(--primary);
      padding: 14px 20px;
      border-radius: var(--radius-md);
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
      color: var(--text-main);
      font-size: 0.9rem;
      display: flex;
      align-items: center;
      gap: 12px;
      animation: slideIn 0.3s ease;
    }

    .toast.error { border-left-color: var(--rose); }
    .toast.success { border-left-color: var(--emerald); }

    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* Results Section Styling */
    .results-wrapper {
      display: none;
      animation: fadeIn 0.5s ease forwards;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(12px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .chip {
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: var(--sky);
      border-radius: var(--radius-full);
      padding: 6px 14px;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.5px;
    }

    /* IRAC Brief Section */
    .irac-brief {
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
      border: 1px solid var(--border-glow);
      border-radius: var(--radius-md);
      padding: 20px;
      margin-bottom: 20px;
    }

    .irac-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      margin-top: 12px;
    }

    .irac-item {
      background: rgba(0, 0, 0, 0.25);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: var(--radius-sm);
      padding: 12px 14px;
    }

    .irac-item .tag {
      font-size: 0.72rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 4px;
    }

    .tag.issue { color: var(--sky); }
    .tag.rule { color: var(--gold); }
    .tag.application { color: var(--emerald); }
    .tag.conclusion { color: #a855f7; }

    .irac-item p {
      margin: 0;
      font-size: 0.9rem;
      color: var(--text-main);
    }

    /* Radial Scorecards */
    .scorecard-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin: 20px 0;
    }

    .score-gauge {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    .gauge-svg {
      width: 80px;
      height: 80px;
      transform: rotate(-90deg);
    }

    .gauge-bg { fill: none; stroke: rgba(255, 255, 255, 0.06); stroke-width: 6; }
    .gauge-fill {
      fill: none;
      stroke-width: 6;
      stroke-linecap: round;
      transition: stroke-dashoffset 1s ease-in-out;
    }

    .score-val {
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      font-size: 1.1rem;
      margin-top: -52px;
      margin-bottom: 26px;
      color: var(--text-main);
    }

    .score-lbl {
      font-size: 0.75rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .score-explain {
      margin: 4px auto 20px;
      max-width: 980px;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      background: rgba(15, 23, 42, 0.45);
      padding: 12px 14px;
    }

    .score-explain-title {
      margin: 0 0 6px;
      color: var(--text-main);
      font-size: 0.84rem;
      font-weight: 700;
      letter-spacing: 0.2px;
    }

    .score-explain-list {
      margin: 0;
      padding-left: 18px;
    }

    .score-explain-list li {
      margin-bottom: 4px;
      color: var(--text-muted);
      font-size: 0.8rem;
      line-height: 1.5;
    }

    /* Animated Citation Chain Graph Flow */
    .chain-flow {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      align-items: center;
      padding: 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
    }

    .chain-node {
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(30, 58, 138, 0.3));
      border: 1px solid var(--border-glow);
      color: var(--text-main);
      padding: 8px 14px;
      border-radius: var(--radius-full);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem;
      font-weight: 600;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
      transition: all 0.2s ease;
    }

    .chain-node:hover {
      border-color: var(--gold);
      box-shadow: var(--shadow-gold);
      transform: scale(1.04);
    }

    .chain-arrow {
      color: var(--gold);
      font-size: 1.1rem;
      display: flex;
      align-items: center;
      opacity: 0.8;
    }

    /* Content Box Layouts */
    .grid-2col {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
    }

    .box {
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 16px 18px;
    }

    .box h3 {
      margin: 0 0 12px;
      font-size: 0.8rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.8px;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .bullet {
      margin: 0;
      padding-left: 20px;
    }

    .bullet li {
      margin-bottom: 8px;
      color: var(--text-main);
      font-size: 0.9rem;
      line-height: 1.6;
    }

    /* Draft blocks */
    .draft-block {
      background: rgba(0, 0, 0, 0.3);
      border-left: 3px solid var(--primary);
      padding: 12px 16px;
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      margin-top: 8px;
      font-size: 0.92rem;
      line-height: 1.65;
    }

    .draft-block.petitioner { border-left-color: var(--gold); }
    .draft-block.respondent { border-left-color: var(--rose); }

    /* Risk Flags */
    .risk-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    .risk-card {
      border: 1px solid var(--border-subtle);
      border-left: 4px solid var(--amber);
      background: rgba(251, 191, 36, 0.05);
      border-radius: var(--radius-sm);
      padding: 12px;
    }

    .risk-card.sev-high { border-left-color: var(--rose); background: rgba(244, 63, 94, 0.05); }
    .risk-card.sev-low { border-left-color: var(--emerald); background: rgba(16, 185, 129, 0.05); }

    .risk-card h4 {
      margin: 0 0 4px;
      font-size: 0.88rem;
      font-weight: 700;
    }

    .risk-card p {
      margin: 4px 0;
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    /* Alternatives grid */
    .alt-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 12px;
    }

    .alt-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 14px;
      transition: border-color 0.2s ease;
    }

    .alt-card:hover { border-color: var(--border-glow); }

    .alt-card h4 {
      margin: 0 0 6px;
      font-size: 0.9rem;
      color: var(--sky);
    }

    .alt-card p {
      margin: 4px 0;
      font-size: 0.82rem;
      color: var(--text-muted);
    }

    /* Tables */
    .table-container {
      overflow-x: auto;
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      text-align: left;
    }

    th {
      background: rgba(15, 23, 42, 0.8);
      color: var(--text-muted);
      font-weight: 700;
      padding: 10px 14px;
      border-bottom: 1px solid var(--border-subtle);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-size: 0.75rem;
    }

    td {
      padding: 10px 14px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-main);
    }

    tr:last-child td { border-bottom: none; }
    tr:hover td { background: rgba(255, 255, 255, 0.02); }

    /* Loading Overlay */
    .loading-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(9, 13, 22, 0.8);
      backdrop-filter: blur(8px);
      z-index: 999;
      display: none;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }

    .scales-spinner {
      font-size: 48px;
      animation: pulseScales 1.5s ease-in-out infinite alternate;
    }

    @keyframes pulseScales {
      0% { transform: scale(0.9); opacity: 0.6; }
      100% { transform: scale(1.15); opacity: 1; filter: drop-shadow(0 0 15px rgba(245, 158, 11, 0.6)); }
    }

    .loading-text {
      margin-top: 16px;
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-main);
      letter-spacing: 0.5px;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .head { flex-direction: column; align-items: flex-start; }
      .stats { width: 100%; justify-content: space-between; }
      .form-grid-3, .form-grid-2, .grid-2col, .irac-grid, .scorecard-grid, .risk-grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
<div class="bg-mesh"></div>

<!-- Loading Overlay -->
<div id="loadingOverlay" class="loading-overlay">
  <div class="scales-spinner">⚖️</div>
  <div class="loading-text">Analyzing Precedent Chain & Synthesizing Argument...</div>
</div>

<!-- Toast Notifications -->
<div id="toastContainer" class="toast-container"></div>

<div class="page">
  <!-- Top Navigation / Header -->
  <header class="head">
    <div class="brand">
      <div class="brand-icon">⚖️</div>
      <div>
        <h1>Legal Precedent Chainer</h1>
        <p class="sub">Autonomous legal argument synthesizer & precedent chain optimizer.</p>
      </div>
    </div>
    
    <div class="stats">
      <div class="stat">
        <div class="k">Indexed Cases</div>
        <div id="statCases" class="v">—</div>
      </div>
      <div class="stat">
        <div class="k">Citations</div>
        <div id="statCitations" class="v">—</div>
      </div>
      <div class="stat">
        <div class="k">Coverage</div>
        <div id="statCoverage" class="v">—</div>
      </div>
    </div>
  </header>

  <!-- Query & Configuration Card -->
  <section class="card">
    <div class="card-title">
      <h2><span class="icon">🎯</span> Build My Argument Strategy</h2>
      <button class="btn ghost" onclick="loadDemo()" title="Load synthetic India legal demonstration data">
        <span>✨</span> Load Demo Query
      </button>
    </div>

    <div class="field-group">
      <label for="question">Natural Language Legal Issue / Question</label>
      <textarea id="question" placeholder="e.g. Does privacy jurisprudence under Article 21 support statutory marriage-equality claims?"></textarea>
    </div>

    <div class="actions" style="margin-bottom: 20px;">
      <button class="btn secondary" onclick="suggestFromQuestion()">
        <span>🧠</span> Infer Case Authorities From Question
      </button>
      <span id="suggestionHint" class="sub" style="margin:0; font-size:0.85rem"></span>
    </div>

    <div class="form-grid-3">
      <div class="field-group">
        <label for="source">Anchor Precedent (Source)</label>
        <input id="source" list="caseList" value="IN-SC-2023-SAME-SEX-MARRIAGE"/>
      </div>
      <div class="field-group">
        <label for="target">Target Matter Case</label>
        <input id="target" list="caseList" value="IN-SC-1950-AKM-GOPALAN"/>
      </div>
      <div class="field-group">
        <label for="practice">Practice Domain</label>
        <select id="practice">
          <option selected>Constitutional law</option>
          <option>Criminal law</option>
          <option>Commercial law</option>
          <option>Administrative law</option>
          <option>General litigation</option>
        </select>
      </div>
    </div>

    <div class="form-grid-3" style="margin-top: 6px;">
      <div class="field-group">
        <label for="jurisdiction">Jurisdiction</label>
        <input id="jurisdiction" value="India Supreme Court"/>
      </div>
      <div class="field-group">
        <label for="mode">Reasoning Mode</label>
        <select id="mode">
          <option value="best" selected>Best Legal Relevance (Bellman-Ford)</option>
          <option value="fast">Most Direct Route (BFS)</option>
          <option value="comprehensive">Comprehensive Review (Floyd-Warshall)</option>
        </select>
      </div>
      <div class="field-group">
        <label for="draftLength">Argument Depth</label>
        <select id="draftLength">
          <option value="short">Short (Executive Brief)</option>
          <option value="standard" selected>Standard (Pleading Depth)</option>
          <option value="long">Long (Full Filing Style)</option>
        </select>
      </div>
    </div>

    <datalist id="caseList"></datalist>

    <div class="actions">
      <button id="runBtn" class="btn primary" onclick="runSingle()">
        <span>⚡</span> Synthesize Legal Argument
      </button>
      <button id="compareBtn" class="btn secondary" onclick="runCompare()">
        <span>📊</span> Compare Alternative Routes
      </button>
      <button class="btn ghost" onclick="exportMemo()">
        <span>📄</span> Export Argument Memo (.md)
      </button>
    </div>

    <details id="technical">
      <summary>Advanced Graph Parameters (Algorithm Tuning)</summary>
      <div class="form-grid-3" style="margin-top:12px">
        <div class="field-group">
          <label for="algorithm">Graph Algorithm</label>
          <select id="algorithm">
            <option value="bellman_ford" selected>Bellman-Ford</option>
            <option value="bfs">BFS</option>
            <option value="floyd">Floyd-Warshall</option>
            <option value="dijkstra">Dijkstra (Extension)</option>
            <option value="astar">A* (Extension)</option>
          </select>
        </div>
        <div class="field-group">
          <label for="alpha">Citation Weight (&alpha;)</label>
          <input id="alpha" type="number" min="0" max="10" step="0.1" value="1.0"/>
        </div>
        <div class="field-group">
          <label for="beta">Semantic Distance (&beta;)</label>
          <input id="beta" type="number" min="0" max="10" step="0.1" value="2.0"/>
        </div>
      </div>
    </details>
  </section>

  <!-- Output Results Panel -->
  <main id="resultsWrapper" class="results-wrapper">
    <!-- Header Banner for Output -->
    <section class="card" style="border-color: var(--border-glow);">
      <div class="card-title">
        <h2><span class="icon">📜</span> Recommended Argument Strategy</h2>
        <span id="modeChip" class="chip">Bellman-Ford Optimised</span>
      </div>

      <!-- IRAC Synthesis -->
      <div class="irac-brief">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <h3 style="margin:0; font-family:'Playfair Display', serif; color:var(--gold); font-size:1.1rem;">
            Core Legal Brief (IRAC Structure)
          </h3>
        </div>
        <div class="irac-grid">
          <div class="irac-item"><div class="tag issue">Issue</div><p id="issue">—</p></div>
          <div class="irac-item"><div class="tag rule">Rule</div><p id="rule">—</p></div>
          <div class="irac-item"><div class="tag application">Application</div><p id="application">—</p></div>
          <div class="irac-item"><div class="tag conclusion">Conclusion</div><p id="conclusion">—</p></div>
        </div>
      </div>

      <!-- Radial Scorecards -->
      <div class="scorecard-grid">
        <div class="score-gauge">
          <svg class="gauge-svg" viewBox="0 0 36 36">
            <path class="gauge-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path id="gaugeAuth" class="gauge-fill" stroke="var(--primary)" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div id="scoreAuthVal" class="score-val">0.00</div>
          <div class="score-lbl">Authority Strength</div>
        </div>

        <div class="score-gauge">
          <svg class="gauge-svg" viewBox="0 0 36 36">
            <path class="gauge-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path id="gaugeCoh" class="gauge-fill" stroke="var(--emerald)" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div id="scoreCohVal" class="score-val">0.00</div>
          <div class="score-lbl">Coherence Score</div>
        </div>

        <div class="score-gauge">
          <svg class="gauge-svg" viewBox="0 0 36 36">
            <path class="gauge-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path id="gaugeRisk" class="gauge-fill" stroke="var(--rose)" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div id="scoreRiskVal" class="score-val">0.00</div>
          <div class="score-lbl">Risk Rating</div>
        </div>

        <div class="score-gauge">
          <svg class="gauge-svg" viewBox="0 0 36 36">
            <path class="gauge-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path id="gaugeRead" class="gauge-fill" stroke="var(--gold)" stroke-dasharray="0, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
          </svg>
          <div id="scoreReadVal" class="score-val">0.00</div>
          <div class="score-lbl">Draft Readiness</div>
        </div>
      </div>
      <p id="scoreNote" class="sub" style="text-align:center; margin-bottom: 8px;"></p>
      <div class="score-explain">
        <p id="scoreCalcTitle" class="score-explain-title">How this scorecard is calculated (0–100 scale)</p>
        <ul id="scoreCalcList" class="score-explain-list"></ul>
      </div>

      <!-- Citation Flow Visualization -->
      <div class="field-group">
        <label>Precedent Citation Chain Flow</label>
        <div id="chainFlow" class="chain-flow"></div>
        <p id="persuasive" class="sub" style="margin-top:10px; font-size:0.88rem; color:var(--text-main);"></p>
      </div>
    </section>

    <!-- Key Authorities & Draft Language -->
    <div class="grid-2col">
      <div class="box">
        <h3><span>📚</span> Key Authorities to Read First</h3>
        <ul id="authorities" class="bullet"></ul>
      </div>
      <div class="box">
        <h3><span>✅</span> Verification Checklist</h3>
        <ul id="checklist" class="bullet"></ul>
      </div>
    </div>

    <!-- Generated Draft Blocks -->
    <section class="card">
      <h2><span class="icon">✍️</span> Filing-Ready Draft Blocks</h2>
      
      <div style="margin-top:14px;">
        <label>Neutral Judicial Synthesis Paragraph</label>
        <div id="neutralDraft" class="draft-block"></div>
      </div>

      <div class="grid-2col" style="margin-top:16px;">
        <div>
          <label style="color:var(--gold);">Petitioner / Appellant Submission Block</label>
          <div id="petitionerDraft" class="draft-block petitioner"></div>
        </div>
        <div>
          <label style="color:var(--rose);">Respondent Submission Block</label>
          <div id="respondentDraft" class="draft-block respondent"></div>
        </div>
      </div>
    </section>

    <!-- Risk Analysis & Counter-Arguments -->
    <div class="grid-2col">
      <div class="box">
        <h3><span>⚠️</span> Precedent Risk Flags</h3>
        <div id="risks" class="risk-grid"></div>
      </div>

      <div class="box">
        <h3><span>🛡️</span> Counter-Argument Strategy</h3>
        <p style="margin:4px 0; font-size:0.85rem;"><strong>Likely Opposing Chain:</strong> <span id="oppChain" style="font-family:'JetBrains Mono'; color:var(--rose);"></span></p>
        <p style="margin:8px 0; font-size:0.88rem;"><strong>Opposing Position:</strong> <span id="oppArg"></span></p>
        <div class="draft-block" style="border-left-color: var(--emerald); margin-top:8px;">
          <strong>Recommended Rebuttal:</strong> <span id="rebuttal"></span>
        </div>
      </div>
    </div>

    <!-- Alternative Routes Panel -->
    <section class="card">
      <h2><span class="icon">🔀</span> Alternative Precedent Strategies</h2>
      <div id="alternatives" class="alt-grid" style="margin-top:14px;"></div>
    </section>

    <!-- Evidence Tables -->
    <section class="card">
      <h2><span class="icon">🔍</span> Sentence-Level Citation Trace</h2>
      <div class="table-container" style="margin-top:14px;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Sentence Excerpt</th>
              <th>Supporting Precedent</th>
            </tr>
          </thead>
          <tbody id="sentenceRows"></tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2><span class="icon">🔗</span> Graph Hop Evidence & Snippets</h2>
      <div class="table-container" style="margin-top:14px;">
        <table>
          <thead>
            <tr>
              <th>From</th>
              <th>To</th>
              <th>Rationale</th>
              <th>Source Excerpt</th>
              <th>Target Excerpt</th>
            </tr>
          </thead>
          <tbody id="hopRows"></tbody>
        </table>
      </div>
    </section>

    <p id="disclaimer" class="sub" style="text-align:center; font-size:0.8rem; margin-top:20px;"></p>
  </main>
</div>

<script>
const MODE_CONFIG = {
  best: { algorithm: 'bellman_ford', alpha: 1.0, beta: 2.2, label: 'Best Legal Relevance' },
  fast: { algorithm: 'bfs', alpha: 1.0, beta: 0.0, label: 'Most Direct Route' },
  comprehensive: { algorithm: 'floyd', alpha: 1.0, beta: 2.0, label: 'Comprehensive Review' }
};

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'error' ? '❌' : type === 'success' ? '✅' : 'ℹ️'}</span> <div>${escapeHtml(message)}</div>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

function showLoading(show) {
  document.getElementById('loadingOverlay').style.display = show ? 'flex' : 'none';
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = String(str || '');
  return div.innerHTML;
}

function applyMode() {
  const cfg = MODE_CONFIG[document.getElementById('mode').value] || MODE_CONFIG.best;
  if (!document.getElementById('technical').open) {
    document.getElementById('algorithm').value = cfg.algorithm;
    document.getElementById('alpha').value = cfg.alpha;
    document.getElementById('beta').value = cfg.beta;
  }
}

function payload(overAlgo = null) {
  const cfg = MODE_CONFIG[document.getElementById('mode').value] || MODE_CONFIG.best;
  const tech = document.getElementById('technical').open;
  return {
    source_case_id: document.getElementById('source').value.trim(),
    target_case_id: document.getElementById('target').value.trim(),
    user_question: document.getElementById('question').value.trim() || null,
    practice_context: document.getElementById('practice').value,
    jurisdiction: document.getElementById('jurisdiction').value,
    draft_length: document.getElementById('draftLength').value,
    algorithm: overAlgo || (tech ? document.getElementById('algorithm').value : cfg.algorithm),
    alpha: tech ? Number(document.getElementById('alpha').value) : cfg.alpha,
    beta: tech ? Number(document.getElementById('beta').value) : cfg.beta,
    max_depth: 25
  };
}

async function callPath(overAlgo = null) {
  const res = await fetch('/path/find', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload(overAlgo))
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

async function loadStats() {
  const res = await fetch('/api/stats');
  if (!res.ok) return;
  const s = await res.json();
  document.getElementById('statCases').textContent = s.case_count;
  document.getElementById('statCitations').textContent = s.citation_edge_count;
  document.getElementById('statCoverage').textContent = `${s.year_min}–${s.year_max}`;
}

async function loadCases() {
  const res = await fetch('/api/cases');
  if (!res.ok) return;
  const data = await res.json();
  const dl = document.getElementById('caseList');
  dl.innerHTML = '';
  for (const c of data) {
    const o = document.createElement('option');
    o.value = c.id;
    o.label = `${c.id} — ${c.title} (${c.year})`;
    dl.appendChild(o);
  }
}

async function suggestFromQuestion() {
  const q = document.getElementById('question').value.trim();
  if (!q) {
    showToast('Please enter a natural language legal question first.', 'error');
    return;
  }
  showLoading(true);
  try {
    const res = await fetch('/api/query/suggest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: q,
        practice_context: document.getElementById('practice').value,
        jurisdiction: document.getElementById('jurisdiction').value
      })
    });
    if (!res.ok) throw new Error('Could not infer authority cases from question.');
    const data = await res.json();
    document.getElementById('source').value = data.inferred_source_case;
    document.getElementById('target').value = data.inferred_target_case;
    document.getElementById('suggestionHint').textContent = data.reasoning;
    showToast('Authorities inferred successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

function setGauge(gaugeId, valId, scoreVal) {
  const val = typeof scoreVal === 'number' ? scoreVal : 0;
  const clamped = Math.min(Math.max(val, 0), 100);
  const strokeDash = `${clamped.toFixed(1)}, 100`;
  document.getElementById(gaugeId).setAttribute('stroke-dasharray', strokeDash);
  document.getElementById(valId).textContent = clamped.toFixed(1);
}

function renderScorecard(score) {
  const authority = typeof score?.authority_strength === 'number' ? score.authority_strength : 0;
  const coherence = typeof score?.coherence_score === 'number' ? score.coherence_score : 0;
  const risk = typeof score?.risk_score === 'number' ? score.risk_score : 0;
  const readiness = typeof score?.draft_readiness === 'number' ? score.draft_readiness : 0;

  setGauge('gaugeAuth', 'scoreAuthVal', authority);
  setGauge('gaugeCoh', 'scoreCohVal', coherence);
  setGauge('gaugeRisk', 'scoreRiskVal', risk);
  setGauge('gaugeRead', 'scoreReadVal', readiness);

  document.getElementById('scoreNote').textContent = score.notes || '';

  const lines = [
    'Authority Strength = clamp(35 + 6.5 × avg inbound citations across cases in this chain).',
    'Coherence Score = clamp(((avg hop similarity + 1) / 2) × 100).',
    'Risk Rating = clamp(12 + high-flag penalties + medium-flag penalties + long-chain penalty − low-flag credits).',
    'Draft Readiness = clamp(0.45 × Authority + 0.40 × Coherence + 0.15 × (100 − Risk)).',
    `Current run values → Authority ${authority.toFixed(1)}, Coherence ${coherence.toFixed(1)}, Risk ${risk.toFixed(1)}, Draft Readiness ${readiness.toFixed(1)}.`
  ];

  document.getElementById('scoreCalcList').innerHTML = lines
    .map((line) => `<li>${escapeHtml(line)}</li>`)
    .join('');
}

function renderChain(path) {
  const container = document.getElementById('chainFlow');
  if (!path || !path.length) {
    container.innerHTML = '<span class="sub">No citation chain discovered.</span>';
    return;
  }
  const elements = [];
  path.forEach((node, i) => {
    elements.push(`<div class="chain-node">${escapeHtml(node)}</div>`);
    if (i < path.length - 1) {
      elements.push(`<div class="chain-arrow">➔</div>`);
    }
  });
  container.innerHTML = elements.join('');
}

function renderList(id, items) {
  const el = document.getElementById(id);
  if (!items || !items.length) {
    el.innerHTML = '<li>None recorded.</li>';
    return;
  }
  el.innerHTML = items.map(x => `<li>${escapeHtml(x)}</li>`).join('');
}

function renderRisks(flags) {
  const container = document.getElementById('risks');
  if (!flags || !flags.length) {
    container.innerHTML = '<div class="risk-card sev-low"><h4>No Major Risk Flags</h4><p>Current precedent chain exhibits high statutory and ratio continuity.</p></div>';
    return;
  }
  container.innerHTML = flags.map(f => `
    <div class="risk-card sev-${escapeHtml(f.severity)}">
      <h4>${escapeHtml(f.title)} (${escapeHtml(f.severity).toUpperCase()})</h4>
      <p>${escapeHtml(f.reason)}</p>
      <p style="color:var(--text-main); margin-top:4px;"><strong>Recommended Check:</strong> ${escapeHtml(f.recommended_check)}</p>
    </div>
  `).join('');
}

function renderAlts(alts) {
  const container = document.getElementById('alternatives');
  if (!alts || !alts.length) {
    container.innerHTML = '<div class="alt-card"><p>No alternative strategy routes found.</p></div>';
    return;
  }
  container.innerHTML = alts.map(a => `
    <div class="alt-card">
      <h4>${escapeHtml(a.strategy_label)}</h4>
      <p><strong>When to Prefer:</strong> ${escapeHtml(a.when_to_prefer)}</p>
      <p style="font-family:'JetBrains Mono'; font-size:0.78rem; color:var(--sky);">
        ${escapeHtml((a.path || []).join(' ➔ '))}
      </p>
      <p><strong>Cost Metric:</strong> ${Number(a.metrics.total_cost).toFixed(4)} | <strong>Hops:</strong> ${a.metrics.hop_count}</p>
    </div>
  `).join('');
}

function renderSentence(rows) {
  const el = document.getElementById('sentenceRows');
  if (!rows || !rows.length) {
    el.innerHTML = '<tr><td colspan="3">No sentence citations available.</td></tr>';
    return;
  }
  el.innerHTML = rows.map(r => `
    <tr>
      <td style="font-family:'JetBrains Mono';">${escapeHtml(r.sentence_id)}</td>
      <td>${escapeHtml(r.text)}</td>
      <td style="font-family:'JetBrains Mono'; color:var(--sky);">${escapeHtml((r.supports || []).join(', '))}</td>
    </tr>
  `).join('');
}

function renderHopRows(hops) {
  const el = document.getElementById('hopRows');
  if (!hops || !hops.length) {
    el.innerHTML = '<tr><td colspan="5">No hop evidence available.</td></tr>';
    return;
  }
  el.innerHTML = hops.map(h => `
    <tr>
      <td style="font-family:'JetBrains Mono';">${escapeHtml(h.from)}</td>
      <td style="font-family:'JetBrains Mono';">${escapeHtml(h.to)}</td>
      <td>${escapeHtml(h.why_hop)}</td>
      <td style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(h.from_summary_snippet)}</td>
      <td style="font-size:0.8rem; color:var(--text-muted);">${escapeHtml(h.to_summary_snippet)}</td>
    </tr>
  `).join('');
}

function renderResult(data) {
  document.getElementById('resultsWrapper').style.display = 'block';
  document.getElementById('modeChip').textContent = (MODE_CONFIG[document.getElementById('mode').value] || MODE_CONFIG.best).label;
  
  document.getElementById('issue').textContent = data.lawyer_brief.issue;
  document.getElementById('rule').textContent = data.lawyer_brief.rule;
  document.getElementById('application').textContent = data.lawyer_brief.application;
  document.getElementById('conclusion').textContent = data.lawyer_brief.conclusion;

  renderScorecard(data.chain_scorecard);
  renderChain(data.recommended_chain.path || []);
  document.getElementById('persuasive').textContent = data.recommended_chain.persuasive_reason || '';

  document.getElementById('neutralDraft').textContent = data.lawyer_brief.suggested_paragraph || '';
  document.getElementById('petitionerDraft').textContent = data.lawyer_brief.petitioner_paragraph || '';
  document.getElementById('respondentDraft').textContent = data.lawyer_brief.respondent_paragraph || '';

  renderList('authorities', data.lawyer_brief.authorities_to_read_first || []);
  renderList('checklist', data.verification_checklist || []);
  renderRisks(data.risk_flags || []);
  renderAlts(data.alternatives || []);

  document.getElementById('oppChain').textContent = (data.counter_argument_pack.likely_opposing_chain || []).join(' ➔ ');
  document.getElementById('oppArg').textContent = data.counter_argument_pack.opposing_argument || '';
  document.getElementById('rebuttal').textContent = data.counter_argument_pack.rebuttal_strategy || '';

  renderSentence(data.sentence_citations || []);
  renderHopRows(data.hops || []);
  document.getElementById('disclaimer').textContent = data.lawyer_brief.disclaimer || '';

  document.getElementById('resultsWrapper').scrollIntoView({ behavior: 'smooth' });
}

async function runSingle() {
  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  showLoading(true);
  try {
    const data = await callPath();
    renderResult(data);
    showToast('Legal argument synthesized successfully.', 'success');
  } catch (err) {
    showToast(err.message || String(err), 'error');
  } finally {
    btn.disabled = false;
    showLoading(false);
  }
}

async function runCompare() {
  const btn = document.getElementById('compareBtn');
  btn.disabled = true;
  showLoading(true);
  try {
    const methods = ['bfs', 'bellman_ford', 'floyd'];
    const outputs = [];
    for (const method of methods) {
      try {
        outputs.push(await callPath(method));
      } catch (_) {}
    }
    if (!outputs.length) throw new Error('No valid path found across algorithms.');
    outputs.sort((a, b) => a.metrics.total_cost - b.metrics.total_cost);
    renderResult(outputs[0]);
    showToast(`Compared ${outputs.length} algorithm paths. Optimal strategy rendered.`, 'success');
  } catch (err) {
    showToast(err.message || String(err), 'error');
  } finally {
    btn.disabled = false;
    showLoading(false);
  }
}

async function exportMemo() {
  showLoading(true);
  try {
    const res = await fetch('/argument/export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload())
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Export failed' }));
      throw new Error(err.detail || 'Export failed');
    }
    const data = await res.json();
    const blob = new Blob([data.memo_markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'legal_precedent_argument_memo.md';
    a.click();
    URL.revokeObjectURL(url);
    showToast('Argument Memo exported as Markdown.', 'success');
  } catch (err) {
    showToast(err.message || String(err), 'error');
  } finally {
    showLoading(false);
  }
}

function loadDemo() {
  document.getElementById('question').value = 'How have Indian courts built digital privacy and accountability doctrine over time?';
  document.getElementById('source').value = 'IN-SC-2021-DIGITAL-RIGHTS-ACCOUNTABILITY';
  document.getElementById('target').value = 'IN-SC-2013-DIGITAL-PRIVACY-BASELINE';
  document.getElementById('practice').value = 'Constitutional law';
  document.getElementById('jurisdiction').value = 'Supreme Court of India';
  document.getElementById('mode').value = 'best';
  document.getElementById('draftLength').value = 'long';
  applyMode();
  showToast('Demo values loaded into form.', 'info');
}

document.getElementById('mode').addEventListener('change', applyMode);
(async function boot() {
  await Promise.all([loadStats(), loadCases()]);
  loadDemo();
})();
</script>
</body>
</html>"""
