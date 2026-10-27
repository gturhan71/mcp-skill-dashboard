import json
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent.parent / "data"
d = json.loads((HERE / "dashboard_data.json").read_text())

OUT = HERE / "rows"
OUT.mkdir(exist_ok=True)


def write(name, rows):
    (OUT / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"{name}: {len(rows)} rows")


# 1. mcp_usage
mcp_rows = [{"id": s["id"], "label": s["label"], "calls": s["calls"]} for s in d["mcp_servers"]]
write("mcp_usage", mcp_rows)

# 2. skill_usage
skill_rows = [
    {
        "name": s["name"],
        "calls": s["calls"],
        "local_size_mb": round(s["local_size_bytes"] / 1024 / 1024, 2),
        "has_local_footprint": s["has_local_footprint"],
    }
    for s in d["skills"]
]
write("skill_usage", skill_rows)

# 3. mcp_tools (top 30 individual tools)
tool_rows = [{"tool": name, "calls": c} for name, c in d["mcp_tools_top30"]]
write("mcp_tools", tool_rows)

# 4. local_components (disk + dependencies)
comp_rows = []
for c in d["local_inventory"]:
    comp_rows.append({
        "name": c["name"],
        "type": c["type"],
        "size_mb": round(c["size_bytes"] / 1024 / 1024, 2),
        "dependencies": "; ".join(c["dependencies"]) if c["dependencies"] else "—",
        "notes": c.get("notes") or "—",
    })
comp_rows.sort(key=lambda r: -r["size_mb"])
write("local_components", comp_rows)

# 5. daily_trend (mcp + skill calls combined per day)
totals = defaultdict(int)
for date, counts in d["daily_mcp"].items():
    totals[date] += sum(counts.values())
for date, counts in d["daily_skill"].items():
    totals[date] += sum(counts.values())
daily_rows = [{"date": date, "calls": calls} for date, calls in sorted(totals.items())]
write("daily_trend", daily_rows)

# 6. project_breakdown
projects = set(d["project_mcp"].keys()) | set(d["project_skill"].keys())
proj_rows = []
for p in projects:
    mcp_calls = sum(d["project_mcp"].get(p, {}).values())
    skill_calls = sum(d["project_skill"].get(p, {}).values())
    # strip the long home-path prefix for readability
    short = p.replace("-Users-gokhan-turhan-", "").replace("-Projects-", "")
    proj_rows.append({
        "project": short,
        "mcp_calls": mcp_calls,
        "skill_calls": skill_calls,
        "total_calls": mcp_calls + skill_calls,
    })
proj_rows.sort(key=lambda r: -r["total_calls"])
write("project_breakdown", proj_rows)

print("\nTumu yazildi:", OUT)
