import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "data"
usage = json.loads((HERE / "usage_stats.json").read_text())
local = json.loads((HERE / "local_inventory.json").read_text())

FRIENDLY_MCP_NAMES = {
    "1a59c906-04da-521d-bda7-7f71b9f9e01c": "Claude Docs",
    "860b4205-5e62-4606-9d51-223bbc4d6a52": "Vercel",
    "3cfb093a-4dbb-48e8-aceb-fa96695332c2": "Canva",
    "449d861d-10a5-4c29-9b84-80be5ecf890e": "Medya Uretim Paketi (gorsel/video/ses)",
    "Claude_Browser": "Built-in Browser",
    "Claude_Code_iOS_Simulator": "iOS Simulator",
    "ccd_turn": "Turn/Plan Yonetimi (ccd_turn)",
    "ccd_session": "Session Yonetimi (ccd_session)",
    "ccd_pr": "PR Yonetimi (ccd_pr)",
    "ccd_session_mgmt": "Session Yonetimi v2",
    "visualize": "Visualize Widget",
    "terminal": "Terminal",
    "transcript-api": "YouTube Transcript API (3. parti)",
    "scheduled-tasks": "Zamanlanmis Gorevler",
    "claude-in-chrome": "Claude in Chrome",
    "Code_placeholder": "Code (placeholder)",
}

# Yerel disk/bagimlilik verisiyle eslesen MCP/skill isimleri (manuel eslestirme)
LOCAL_MATCH = {
    "graphify": ["graphify", "graphifyy (graphify motoru)"],
    "kill-ai-slop": ["kill-ai-slop"],
}

mcp_servers = []
for name, count in usage["mcp_servers"]:
    mcp_servers.append({
        "id": name,
        "label": FRIENDLY_MCP_NAMES.get(name, name),
        "calls": count,
        "is_remote": True,  # tumu bu makinede bir .claude disk izine sahip degil (connector/app-bundled)
    })
mcp_servers.sort(key=lambda x: -x["calls"])

skills = []
for name, count in usage["skills"]:
    local_items = LOCAL_MATCH.get(name, [])
    local_size = sum(c["size_bytes"] for c in local if c["name"] in local_items)
    skills.append({
        "name": name,
        "calls": count,
        "local_size_bytes": local_size,
        "has_local_footprint": bool(local_items),
    })
skills.sort(key=lambda x: -x["calls"])

dashboard = {
    "summary": usage["summary"],
    "mcp_servers": mcp_servers,
    "mcp_tools_top30": usage["mcp_tools_top30"],
    "skills": skills,
    "builtin_tools": usage["builtin_tools"],
    "daily_mcp": usage["daily_mcp"],
    "daily_skill": usage["daily_skill"],
    "project_mcp": usage["project_mcp"],
    "project_skill": usage["project_skill"],
    "local_inventory": local,
    "local_total_bytes": sum(c["size_bytes"] for c in local),
}

out = HERE / "dashboard_data.json"
out.write_text(json.dumps(dashboard, ensure_ascii=False, indent=2))
print(f"Yazildi: {out}")
print(f"Toplam yerel disk kullanimi: {dashboard['local_total_bytes']/1024/1024:.1f} MB")
