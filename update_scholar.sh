#!/usr/bin/env bash
# 本地刷新 Google Scholar 引用数据（本机 IP 通常不会被 Google 拦截，
# 而 GitHub Actions 的出口 IP 经常被拒，所以手动跑这个脚本最稳妥）。
set -euo pipefail

cd "$(dirname "$0")"

# main.py 把结果写到「当前工作目录/results/」；在 crawler 目录下运行，避免写到错误路径
(
  cd google_scholar_crawler
  GOOGLE_SCHOLAR_ID=amozZDkAAAAJ python3 main.py > /dev/null
)

cp google_scholar_crawler/results/gs_data.json gs_data.json
cp google_scholar_crawler/results/gs_data_shieldsio.json gs_data_shieldsio.json

python3 - <<'PY'
import json
d = json.load(open('gs_data.json'))
print(f"citedby={d['citedby']}  h-index={d['hindex']}  publications={len(d['publications'])}  updated={d['updated']}")
PY

echo "已更新 gs_data.json / gs_data_shieldsio.json，记得 commit 并 push 到 master（线上 badge 读 GitHub raw）。"
