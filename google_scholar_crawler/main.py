from scholarly import scholarly, ProxyGenerator
import jsonpickle
import json
from datetime import datetime
import os
import time

# 重试机制
max_retries = int(os.environ.get('MAX_RETRIES', '3'))
retry_delay = 10  # 秒

scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
if not scholar_id:
    raise ValueError("请设置环境变量 GOOGLE_SCHOLAR_ID")


def fetch():
    author: dict = scholarly.search_author_id(scholar_id)
    scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
    return author


def enable_free_proxies():
    """免费代理池质量很差，只在直连失败后当兜底用。"""
    try:
        pg = ProxyGenerator()
        if pg.FreeProxies():
            scholarly.use_proxy(pg)
            return True
        print("免费代理池没有可用节点。")
    except Exception as e:
        print(f"启用免费代理池失败: {e}")
    return False


author = None
for attempt in range(max_retries):
    try:
        print(f"正在尝试获取 Google Scholar 数据 (尝试 {attempt + 1}/{max_retries})...")
        author = fetch()
        print("成功获取数据！")
        break
    except Exception as e:
        print(f"尝试 {attempt + 1} 失败: {e}")
        if attempt < max_retries - 1:
            print(f"{retry_delay} 秒后重试...")
            time.sleep(retry_delay)

if author is None:
    # 直连全部失败，多半是出口 IP 被 Google Scholar 拦截（GitHub Actions 常见）。
    print("直连全部失败，尝试改用免费代理池...")
    if enable_free_proxies():
        try:
            author = fetch()
            print("通过代理成功获取数据！")
        except Exception as e:
            print(f"通过代理获取仍然失败: {e}")

if author is None:
    raise SystemExit(
        "所有尝试均失败。常见原因：Google Scholar 反爬虫拦截了当前出口 IP。\n"
        "在本机运行 ./update_scholar.sh 通常可以成功。"
    )

name = author['name']
author['updated'] = str(datetime.now())
author['publications'] = {v['author_pub_id']:v for v in author['publications']}
print(json.dumps(author, indent=2))
os.makedirs('results', exist_ok=True)
with open(f'results/gs_data.json', 'w') as outfile:
    json.dump(author, outfile, ensure_ascii=False)

shieldio_data = {
  "schemaVersion": 1,
  "label": "citations",
  "message": f"{author['citedby']}",
}
with open(f'results/gs_data_shieldsio.json', 'w') as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)
