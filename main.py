import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def initial_fda(source_file: str) -> list[str]:
    """อ่านไฟล์ .txt และลบ '-' ออก"""
    with open(source_file, 'r', encoding='utf-8') as file:
        return [fda.strip().replace('-', '') for fda in file if fda.strip()]

def get_cmt_detail(fda: str, retries: int = 3) -> str | None:
    """ดึงลิงก์ดูข้อมูลจากเว็บ FDA พร้อม retry"""
    url = f'https://www.fda.moph.go.th/?op=kwssl&lang=1&skin=s&db=Main&ww={fda}'
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find(id='table_list')
            if table:
                link_tag = table.find('a')
                if link_tag and link_tag.get('href'):
                    return link_tag.get('href')
            print(f'⚠️ {fda}: Table or link not found')
            return None
        except requests.RequestException as e:
            print(f'🔴 {fda} Attempt {attempt} failed: {e}')
            time.sleep(2 + random.random())  # delay แบบสุภาพ
    return None

if __name__ == "__main__":
    fda_list = initial_fda('fda_list.txt')
    cmt_detail_urls: dict[str, str | None] = {}

    for fda in fda_list:
        print(f'🐈 {fda} Processing...')
        url = get_cmt_detail(fda)
        cmt_detail_urls[fda] = url
        if url:
            print(f'✅ {fda} Completed')
        else:
            print(f'🔴 {fda} Failed')
        time.sleep(1 + random.random())  # delay แบบสุภาพ

    # Save to Excel
    df = pd.DataFrame(list(cmt_detail_urls.items()), columns=['FDA', 'URL'])
    df.to_excel('fda_list.xlsx', index=False)
    print("💾 Save fda_list.xlsx success\n")

    # Summary
    print('🦢 Summary')
    for fda, url in cmt_detail_urls.items():
        print(f'{fda}: {url}')