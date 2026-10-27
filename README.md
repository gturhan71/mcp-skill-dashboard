# MCP & Skill Kullanım Dashboard

Bu makinedeki Claude Code transkript dosyalarını (`~/.claude/projects/**/*.jsonl`) analiz edip
en çok kullanılan MCP sunucularını, skilleri ve yerel disk/bağımlılık envanterini gösteren
bir dashboard üretir.

Yayınlanan dashboard: https://claude.ai/artifact/4wMnXSFPGw3X3xbX53wdPo

## Nasıl çalışır

Veri bir connector'dan değil, bu makinedeki transkript dosyalarının yerel analizinden gelir —
canlı değildir, her çalıştırmada yeni bir anlık görüntü (snapshot) üretir.

```bash
python3 scripts/analyze_usage.py       # transkriptlerden MCP/skill cagri sayilari -> data/usage_stats.json
python3 scripts/local_inventory.py     # yerel skill/plugin disk + bagimlilik envanteri -> data/local_inventory.json
python3 scripts/build_dashboard_data.py  # ikisini birlestirir -> data/dashboard_data.json
python3 scripts/prep_dashboard_rows.py   # dashboard'un okuyacagi row-array JSON'lari -> data/rows/*.json
```

Üretilen `data/rows/*.json` dosyaları, yayınlanmış dashboard artifact'ının veri kümeleri
(`datasets/*`) olarak yüklü; dashboard'u güncellemek için bu dosyaları artifact'in asset
deposuna tekrar yükleyip `datasets/<id>` belgelerindeki `updated` alanını değiştirmek gerekir.

`data/dashboard_page.html` dashboard'un `files/index.html` içeriğinin bir kopyasıdır (referans amaçlı).

## Yalnızca stdlib

Dört script de Python stdlib dışında bağımlılık kullanmaz (`json`, `pathlib`, `collections`,
`subprocess`) — sanal ortam veya `pip install` gerekmez, doğrudan `python3` ile çalışır.
