"""Yerelde diskte gercekten yer kaplayan skill/plugin bilesenlerinin
boyutunu ve bagimliliklarini cikarir. Uzak/MCP servisler (app-bundled
connector'lar) burada N/A olarak isaretlenir cunku bu makinede dosya
izleri yoktur.
"""

import json
import subprocess
from pathlib import Path

HOME = Path.home()
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def du(path: Path) -> int:
    if not path.exists():
        return 0
    out = subprocess.run(["du", "-sk", str(path)], capture_output=True, text=True)
    try:
        kb = int(out.stdout.split()[0])
        return kb * 1024
    except (ValueError, IndexError):
        return 0


components = []

# --- Yerel skiller (~/.claude/skills altinda gercek klasor olanlar) ---
skills_dir = HOME / ".claude" / "skills"
for entry in sorted(skills_dir.iterdir()):
    if not entry.is_dir() or entry.name in {".trash", "synced"}:
        continue
    size = du(entry)
    deps = []
    notes = ""
    if entry.name == "graphify":
        deps = ["Python (uv tool / pip)", "PyPI: graphifyy (ayri kurulum, ~129MB)", "opsiyonel: GEMINI_API_KEY, Neo4j, FalkorDB"]
        notes = "SKILL.md disinda calisan asil motor (graphifyy) ayri bir uv tool ortaminda."
    elif entry.name == "kill-ai-slop":
        deps = ["Node.js (script calistirmak icin)"]
        notes = "Kendi ifadesiyle 'dependency-free' - sadece Node.js built-in modulleri kullaniyor."
    components.append({
        "name": entry.name,
        "type": "skill (yerel)",
        "path": str(entry),
        "size_bytes": size,
        "dependencies": deps,
        "notes": notes,
    })

# --- graphifyy ayri paket (skill'in calistirdigi asil motor) ---
graphifyy_path = HOME / ".local" / "share" / "uv" / "tools" / "graphifyy"
if graphifyy_path.exists():
    components.append({
        "name": "graphifyy (graphify motoru)",
        "type": "uv tool paketi",
        "path": str(graphifyy_path),
        "size_bytes": du(graphifyy_path),
        "dependencies": ["Python 3.x", "networkx, sentence-transformers ve benzeri PyPI paketleri (uv tool venv icinde)"],
        "notes": "graphify skill'i bu CLI'yi cagirir; skill klasorunun kendisi kucuk ama motor ~129MB.",
    })

# --- Yerel plugin cache (ruflo marketplace) ---
plugins_cache = HOME / ".claude" / "plugins" / "cache"
for marketplace_dir in sorted(plugins_cache.iterdir()):
    if not marketplace_dir.is_dir():
        continue
    if marketplace_dir.name.startswith("temp_local"):
        components.append({
            "name": "temp_local plugin cache (gecici)",
            "type": "plugin (gecici staging)",
            "path": str(marketplace_dir),
            "size_bytes": du(marketplace_dir),
            "dependencies": ["Node.js/TypeScript"],
            "notes": "Plugin kurulum/senkronizasyon sirasinda birakilan gecici staging klasoru, aktif kullanilan ayri bir plugin degil.",
        })
        continue
    for plugin_dir in sorted(marketplace_dir.iterdir()):
        if not plugin_dir.is_dir():
            continue
        for version_dir in sorted(plugin_dir.iterdir()):
            if not version_dir.is_dir():
                continue
            manifest_path = version_dir / ".claude-plugin" / "plugin.json"
            mcp_path = version_dir / ".mcp.json"
            name = plugin_dir.name
            version = version_dir.name
            deps = ["Node.js (plugin script/MCP server calistirmak icin)"]
            notes = ""
            if mcp_path.exists():
                try:
                    mcp_cfg = json.loads(mcp_path.read_text())
                    servers = list(mcp_cfg.get("mcpServers", {}).keys())
                    if servers:
                        notes = f"MCP server(lar): {', '.join(servers)}"
                except json.JSONDecodeError:
                    pass
            if name in {"ruflo-core", "ruflo-console"}:
                deps.append("npx ile cekilen @claude-flow/cli (ayri npm cache, bu olcume dahil degil)")
            components.append({
                "name": f"{name} ({version})",
                "type": "plugin (yerel cache)",
                "path": str(version_dir),
                "size_bytes": du(version_dir),
                "dependencies": deps,
                "notes": notes,
            })

out_path = DATA_DIR / "local_inventory.json"
out_path.write_text(json.dumps(components, ensure_ascii=False, indent=2))
print(f"Yazildi: {out_path}")
for c in components:
    print(f"{c['name']}: {c['size_bytes']/1024/1024:.1f} MB | {c['dependencies']}")
