#!/usr/bin/env python3
import requests
import json

# 現在のスポットライトAPIエンドポイントをテスト
print("Testing Spotlight API...")
api_url = 'https://arc.msn.com/v3/Delivery/Cache?pid=279978&fmt=json&cdm=1&lc=ja-JP&ctry=JP'

try:
    response = requests.get(api_url, timeout=10)
    print(f'Status Code: {response.status_code}')
    data = response.json()
    print(f'Response Keys: {list(data.keys())}')
    print(f'\nFull Response:')
    print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f'Error: {e}')

# Bing過去の壁紙API（より古い画像）もテスト
print("\n" + "="*50)
print("Testing Bing Archive API (idx=8)...")
api_url2 = 'https://www.bing.com/HPImageArchive.aspx?format=js&idx=8&n=8&mkt=ja-JP'

try:
    response = requests.get(api_url2, timeout=10)
    print(f'Status Code: {response.status_code}')
    data = response.json()
    print(f'Response Keys: {list(data.keys())}')
    if 'images' in data:
        print(f'Number of images: {len(data["images"])}')
        if data['images']:
            print(f'\nFirst image title: {data["images"][0].get("title", "N/A")}')
except Exception as e:
    print(f'Error: {e}')
