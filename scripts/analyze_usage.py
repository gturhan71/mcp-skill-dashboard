"""Claude Code transcriptlerinden (~/.claude/projects/**/*.jsonl) MCP ve
skill kullanim istatistiklerini cikarir."""

import json
from collections import Counter, defaultdict
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

tool_counts = Counter()
mcp_server_counts = Counter()
mcp_tool_counts = Counter()
skill_counts = Counter()
builtin_counts = Counter()
daily_mcp = defaultdict(Counter)      # date -> server -> count
daily_skill = defaultdict(Counter)    # date -> skill -> count
project_mcp = defaultdict(Counter)    # project -> server -> count
project_skill = defaultdict(Counter)  # project -> skill -> count

total_lines = 0
parsed_lines = 0
total_tool_calls = 0

for jsonl_path in PROJECTS_DIR.rglob("*.jsonl"):
    project_name = jsonl_path.parts[len(PROJECTS_DIR.parts)]
    with open(jsonl_path, "r", errors="ignore") as f:
        for line in f:
            total_lines += 1
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            parsed_lines += 1

            if d.get("type") != "assistant":
                continue
            msg = d.get("message", {})
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue

            ts = d.get("timestamp", "")
            date = ts[:10] if ts else "unknown"

            for block in content:
                if not isinstance(block, dict) or block.get("type") != "tool_use":
                    continue
                name = block.get("name", "")
                if not name:
                    continue
                total_tool_calls += 1
                tool_counts[name] += 1

                if name.startswith("mcp__"):
                    parts = name.split("__")
                    server = parts[1] if len(parts) > 1 else "unknown"
                    tool = "__".join(parts[2:]) if len(parts) > 2 else "unknown"
                    mcp_server_counts[server] += 1
                    mcp_tool_counts[f"{server}::{tool}"] += 1
                    daily_mcp[date][server] += 1
                    project_mcp[project_name][server] += 1
                elif name == "Skill":
                    skill = block.get("input", {}).get("skill", "unknown")
                    skill_counts[skill] += 1
                    daily_skill[date][skill] += 1
                    project_skill[project_name][skill] += 1
                else:
                    builtin_counts[name] += 1

result = {
    "summary": {
        "transcript_files": len(list(PROJECTS_DIR.rglob("*.jsonl"))),
        "total_lines": total_lines,
        "parsed_lines": parsed_lines,
        "total_tool_calls": total_tool_calls,
        "unique_mcp_servers": len(mcp_server_counts),
        "unique_skills": len(skill_counts),
    },
    "mcp_servers": mcp_server_counts.most_common(),
    "mcp_tools_top30": mcp_tool_counts.most_common(30),
    "skills": skill_counts.most_common(),
    "builtin_tools": builtin_counts.most_common(),
    "daily_mcp": {d: dict(c) for d, c in sorted(daily_mcp.items())},
    "daily_skill": {d: dict(c) for d, c in sorted(daily_skill.items())},
    "project_mcp": {p: dict(c.most_common(5)) for p, c in project_mcp.items()},
    "project_skill": {p: dict(c.most_common(5)) for p, c in project_skill.items()},
}

out_path = DATA_DIR / "usage_stats.json"
out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(f"Yazildi: {out_path}")
print(json.dumps(result["summary"], indent=2))
print("\nTop MCP servers:")
for s, c in mcp_server_counts.most_common(10):
    print(f"  {s}: {c}")
print("\nTop skills:")
for s, c in skill_counts.most_common(15):
    print(f"  {s}: {c}")
