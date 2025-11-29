from scholarly import scholarly
import jsonpickle
import json
from datetime import datetime
import os
import time

# 重试机制
max_retries = 3
retry_delay = 10  # 秒

scholar_id = os.environ.get('GOOGLE_SCHOLAR_ID')
if not scholar_id:
    raise ValueError("请设置环境变量 GOOGLE_SCHOLAR_ID")

for attempt in range(max_retries):
    try:
        print(f"正在尝试获取 Google Scholar 数据 (尝试 {attempt + 1}/{max_retries})...")
        author: dict = scholarly.search_author_id(scholar_id)
        scholarly.fill(author, sections=['basics', 'indices', 'counts', 'publications'])
        print("成功获取数据！")
        break
    except Exception as e:
        if attempt < max_retries - 1:
            print(f"尝试 {attempt + 1} 失败: {str(e)}")
            print(f"{retry_delay} 秒后重试...")
            time.sleep(retry_delay)
        else:
            print(f"所有尝试均失败。可能是 Google Scholar 的反爬虫限制或网络问题。")
            raise
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
