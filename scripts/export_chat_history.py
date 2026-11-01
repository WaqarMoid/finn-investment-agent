"""Export Antigravity JSONL transcripts into clean, readable Markdown and standalone HTML chat viewers."""

import html
import json
import os
import re
from pathlib import Path


def clean_user_text(text: str) -> str:
    if not text:
        return ""
    if "<USER_REQUEST>" in text:
        match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    # Strip system noise tags
    text = re.sub(r"<CONTEXT_SUMMARY>.*?</CONTEXT_SUMMARY>", "", text, flags=re.DOTALL)
    text = re.sub(r"<SYSTEM_MESSAGE>.*?</SYSTEM_MESSAGE>", "", text, flags=re.DOTALL)
    text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
    return text.strip()


def parse_transcript(jsonl_path: str):
    items = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except Exception:
                continue

            t = row.get("type")
            src = row.get("source")
            content = row.get("content") or ""
            ts = row.get("created_at", "")[:19].replace("T", " ")
            tool_calls = row.get("tool_calls", [])

            if t == "USER_INPUT":
                text = clean_user_text(content)
                if text:
                    items.append({"role": "user", "text": text, "ts": ts})
            elif src == "MODEL" and content.strip():
                items.append({"role": "assistant", "text": content.strip(), "ts": ts})
            elif src == "MODEL" and tool_calls:
                call_descs = []
                for tc in tool_calls:
                    name = tc.get("name") or tc.get("function", {}).get("name") or "tool"
                    args = tc.get("args") or tc.get("function", {}).get("arguments") or {}
                    summary = ""
                    if isinstance(args, dict):
                        summary = args.get("toolSummary") or args.get("CommandLine") or args.get("Path") or ""
                    elif isinstance(args, str):
                        summary = args[:80]
                    call_descs.append(f"{name}: {summary}" if summary else name)
                if call_descs:
                    items.append({"role": "tools", "text": " | ".join(call_descs[:4]), "ts": ts})
    return items


def generate_markdown(items, title, session_id):
    md = [f"# {title}\n", f"**Session ID:** `{session_id}`  \n", f"**Export Date:** November 1, 2026\n", "---\n"]
    for it in items:
        role = it["role"]
        ts = it["ts"]
        text = it["text"]
        if role == "user":
            md.append(f"### 👤 User ({ts})\n")
            md.append(f"> {text.replace(chr(10), chr(10) + '> ')}\n\n")
        elif role == "assistant":
            md.append(f"### 🤖 Antigravity Assistant ({ts})\n")
            md.append(f"{text}\n\n")
        elif role == "tools":
            md.append(f"<details><summary>🛠️ <em>Tools executed ({ts}): {html.escape(text[:100])}...</em></summary>\n\n```text\n{text}\n```\n\n</details>\n\n")
    return "\n".join(md)


def generate_html(items, title, session_id):
    chat_bubbles = []
    for it in items:
        role = it["role"]
        ts = it["ts"]
        text = it["text"]
        if role == "user":
            esc = html.escape(text).replace("\n", "<br>")
            chat_bubbles.append(f"""
            <div class="message user">
                <div class="meta"><span>👤 User</span><span>{ts}</span></div>
                <div class="bubble">{esc}</div>
            </div>""")
        elif role == "assistant":
            # Basic markdown replacement for paragraphs and code blocks
            esc = html.escape(text)
            esc = re.sub(r"```(.*?)\n(.*?)```", r"<pre><code>\2</code></pre>", esc, flags=re.DOTALL)
            esc = re.sub(r"`([^`]+)`", r"<code>\1</code>", esc)
            esc = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", esc)
            esc = esc.replace("\n", "<br>")
            chat_bubbles.append(f"""
            <div class="message assistant">
                <div class="meta"><span>🤖 Antigravity Agent</span><span>{ts}</span></div>
                <div class="bubble">{esc}</div>
            </div>""")
        elif role == "tools":
            esc = html.escape(text)
            chat_bubbles.append(f"""
            <div class="message tools">
                <details>
                    <summary>🛠️ Tool Executions ({ts}): {esc[:90]}...</summary>
                    <pre class="tool-content">{esc}</pre>
                </details>
            </div>""")

    body = "\n".join(chat_bubbles)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #e6edf3;
            --text-muted: #8b949e;
            --user-bg: #1f3a5f;
            --agent-bg: #21262d;
            --accent: #58a6ff;
            --code-bg: #090d12;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        header {{
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
        }}
        header h1 {{ font-size: 1.6rem; font-weight: 700; color: #fff; }}
        header p {{ font-size: 0.9rem; color: var(--text-muted); margin-top: 6px; }}
        .nav-links {{ margin-top: 12px; }}
        .nav-links a {{ color: var(--accent); text-decoration: none; font-size: 0.9rem; margin-right: 16px; font-weight: 500; }}
        .nav-links a:hover {{ text-decoration: underline; }}
        .chat {{ display: flex; flex-direction: column; gap: 16px; }}
        .message {{ display: flex; flex-direction: column; width: 100%; }}
        .meta {{ display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-muted); margin-bottom: 4px; padding: 0 4px; }}
        .bubble {{
            padding: 14px 18px;
            border-radius: 12px;
            border: 1px solid var(--border);
            font-size: 0.95rem;
            word-break: break-word;
        }}
        .user .bubble {{
            background: var(--user-bg);
            border-color: #2b578c;
            align-self: flex-end;
            max-width: 90%;
        }}
        .assistant .bubble {{
            background: var(--agent-bg);
            align-self: flex-start;
            max-width: 100%;
        }}
        .tools {{
            font-size: 0.85rem;
            color: var(--text-muted);
            background: var(--surface);
            border: 1px dashed var(--border);
            border-radius: 8px;
            padding: 10px 14px;
        }}
        .tools summary {{ cursor: pointer; font-weight: 500; }}
        .tool-content {{
            margin-top: 8px;
            padding: 8px;
            background: var(--code-bg);
            border-radius: 6px;
            font-family: monospace;
            font-size: 0.8rem;
            white-space: pre-wrap;
            color: #7ee787;
        }}
        pre {{
            background: var(--code-bg);
            padding: 12px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 10px 0;
            border: 1px solid var(--border);
        }}
        code {{
            background: rgba(110, 118, 129, 0.2);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            <p>Session ID: <code>{session_id}</code> · ENAM AI Engineer Build Challenge</p>
            <div class="nav-links">
                <a href="./index.html">← All Sessions</a>
                <a href="https://finn-investment-agent.onrender.com" target="_blank">Live Prototype ↗</a>
                <a href="https://github.com/WaqarMoid/finn-investment-agent" target="_blank">GitHub Repo ↗</a>
            </div>
        </header>
        <div class="chat">
            {body}
        </div>
    </div>
</body>
</html>
"""


def generate_index_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FINN - AI Build History Transcripts</title>
    <style>
        :root {
            --bg: #0d1117;
            --surface: #161b22;
            --border: #30363d;
            --text: #e6edf3;
            --text-muted: #8b949e;
            --accent: #58a6ff;
            --card-hover: #1f242c;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 40px 20px;
            min-height: 100vh;
        }
        .container { max-width: 800px; margin: 0 auto; }
        header { margin-bottom: 32px; border-bottom: 1px solid var(--border); padding-bottom: 20px; }
        h1 { font-size: 2rem; font-weight: 700; color: #fff; margin-bottom: 8px; }
        p { color: var(--text-muted); font-size: 1rem; }
        .grid { display: flex; flex-direction: column; gap: 16px; margin-top: 24px; }
        .card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            gap: 8px;
            transition: all 0.2s ease;
        }
        .card:hover {
            background: var(--card-hover);
            border-color: var(--accent);
            transform: translateY(-2px);
        }
        .card-header { display: flex; justify-content: space-between; align-items: center; }
        .card-title { font-size: 1.2rem; font-weight: 600; color: var(--accent); }
        .card-tag { font-size: 0.75rem; background: rgba(88, 166, 255, 0.15); color: var(--accent); padding: 4px 8px; border-radius: 6px; font-weight: 600; }
        .card-desc { font-size: 0.95rem; color: var(--text-muted); line-height: 1.5; }
        .card-meta { font-size: 0.8rem; color: var(--text-muted); margin-top: 4px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>FINN · AI Build History</h1>
            <p>Interactive logs and agent thought transcripts recorded during the ENAM challenge.</p>
        </header>
        <div class="grid">
            <a href="./session-1.html" class="card">
                <div class="card-header">
                    <span class="card-title">Session 1 · Architecture & Foundations</span>
                    <span class="card-tag">Interactive Log</span>
                </div>
                <div class="card-desc">Initial discovery, verification of seed data, setup of mobile shell layout, test suite establishment, and primary filing parsers.</div>
                <div class="card-meta">Recorded: October 30–31, 2026 · Format: Clean Web View</div>
            </a>
            <a href="./session-2.html" class="card">
                <div class="card-header">
                    <span class="card-title">Session 2 · Universal Resolver, 8 Deep Modules & Live Render Deploy</span>
                    <span class="card-tag">Interactive Log</span>
                </div>
                <div class="card-desc">Comprehensive reference app analysis, dynamic exchange lookups (WIPRO, TATAMOTORS, SBIN, ITC), 8 research modules, evidence grounding, Render Docker deployment, and sub-2-second latency optimization.</div>
                <div class="card-meta">Recorded: October 31 – November 1, 2026 · Format: Clean Web View</div>
            </a>
        </div>
    </div>
</body>
</html>
"""


def main():
    p1 = "docs/ai_build_logs/antigravity_chat_session_1.jsonl"
    p2 = "docs/ai_build_logs/antigravity_chat_session_2.jsonl"

    items1 = parse_transcript(p1)
    items2 = parse_transcript(p2)

    # 1. Markdown files for GitHub reading
    md1 = generate_markdown(items1, "Antigravity Chat Session 1: Foundation & Architecture", "d03bdcac-d84a-4b29-bea0-ade2f314cf8e")
    md2 = generate_markdown(items2, "Antigravity Chat Session 2: Universal Engine & Production Deployment", "bdb8edb2-1281-43dc-8e15-4cd41ab2b762")

    Path("docs/ai_build_logs/ANTIGRAVITY_SESSION_1.md").write_text(md1, encoding="utf-8")
    Path("docs/ai_build_logs/ANTIGRAVITY_SESSION_2.md").write_text(md2, encoding="utf-8")

    # 2. Standalone HTML viewers for public web serving
    out_dir = Path("apps/web/public/build-history")
    out_dir.mkdir(parents=True, exist_ok=True)

    html1 = generate_html(items1, "FINN Build Session 1: Architecture & Foundations", "d03bdcac-d84a-4b29-bea0-ade2f314cf8e")
    html2 = generate_html(items2, "FINN Build Session 2: Universal Resolver & Deployment", "bdb8edb2-1281-43dc-8e15-4cd41ab2b762")
    idx_html = generate_index_html()

    (out_dir / "session-1.html").write_text(html1, encoding="utf-8")
    (out_dir / "session-2.html").write_text(html2, encoding="utf-8")
    (out_dir / "index.html").write_text(idx_html, encoding="utf-8")

    # Also keep copy in docs/ai_build_logs/ for offline inspection
    Path("docs/ai_build_logs/session-1.html").write_text(html1, encoding="utf-8")
    Path("docs/ai_build_logs/session-2.html").write_text(html2, encoding="utf-8")
    Path("docs/ai_build_logs/index.html").write_text(idx_html, encoding="utf-8")

    print(f"Generated Markdown: ANTIGRAVITY_SESSION_1.md ({len(items1)} items), ANTIGRAVITY_SESSION_2.md ({len(items2)} items)")
    print(f"Generated HTML viewers in apps/web/public/build-history and docs/ai_build_logs")


if __name__ == "__main__":
    main()
