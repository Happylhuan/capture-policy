import argparse
import re
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup

urls = {
    "TYPE1": {
        "https://xxx": "class"
    },
    "TYPE2": {
        "https://xxx": "class"
    },
    "TYPE3": {
        "https://xxx": "class"
    }
}

parser = argparse.ArgumentParser(description="Fetch data from the last N days.")
parser.add_argument('--days', type=int, default=30, help="Number of days to look back (default: 30)")
args = parser.parse_args()
days = args.days
thirty_days_ago = datetime.now() - timedelta(days)
TYPE1 = "<div><li>"
TYPE2 = "<div><dl><dd>"
TYPE3 = "<div><li><span>match'"

documents = []
date_pattern = re.compile(r'\b\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])\b')
for category, url_list in urls.items():
    for url, url_class in url_list.items():
        documents.append({'title': f"Source: {url}", 'link': "", 'date': ""})
        response = requests.get(url)
        response.encoding = response.apparent_encoding
        soup = BeautifulSoup(response.text, 'html.parser')
        class_div = soup.find('div', class_=url_class)
        if not class_div:
            continue
        if category == "TYPE1":
            items = class_div.find_all('li')
            for item in items:
                title_tag = item.find('a')
                title = title_tag.text.strip() if title_tag else None
                if not title:
                    continue
                date_tag = item.find('span')
                date = date_tag.text.strip() if date_tag else None
                link = title_tag['href'] if title_tag else None
                if link:
                    link = link if link.startswith('http') else url + link
                if datetime.strptime(date, '%Y-%m-%d') >= thirty_days_ago:
                    documents.append({'title': title, 'link': link, 'date': date})
            documents.append({'title': "", 'link': "", 'date': ""})
        elif category == "TYPE2":
            items = class_div.find_all('dl')
            for item in items:
                a_tag = item.find('dd', class_='trt-col-10 trt-col-sm-24 slb-trt-col-24')
                title_tag = a_tag.find('a') if a_tag else None
                title = title_tag.text.strip() if title_tag else None
                if not title:
                    continue
                link = title_tag.get('href') if title_tag else None
                if link:
                    link = link if link.startswith('http') else url + link
                date_tag = item.find('dd', class_='trt-col-3 none_sm slb_none')
                date = date_tag.text.strip() if date_tag else None
                if datetime.strptime(date, '%Y-%m-%d') >= thirty_days_ago:
                    documents.append({'title': title, 'link': link, 'date': date})
            documents.append({'title': "", 'link': "", 'date': ""})
        elif category == "TYPE3":
            items = class_div.find_all('li')  # 查找所有 <li> 标签
            for item in items:
                title_tag = item.find('a')  # 假设标题在 a 标签中
                title = title_tag.text.strip() if title_tag else None
                if not title:
                    continue
                link = title_tag['href'] if title_tag else None
                if link:
                    link = link if link.startswith('http') else url + link
                date_pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
                date = None
                spans = item.find_all('span')
                for span in spans:
                    text = span.text.strip() if span else ""
                    match = date_pattern.search(text)
                    if match:
                        date = match.group()
                        break
                if datetime.strptime(date, '%Y-%m-%d') >= thirty_days_ago:
                    documents.append({'title': title, 'link': link, 'date': date})
            documents.append({'title': "", 'link': "", 'date': ""})
output_directory = '/Users/xxx/Desktop/Ai自动识别xx网站'
output_file = f"{output_directory}/AI识别xx网站_{datetime.now().strftime('%Y-%m-%d %H:%M')}.xlsx"
df = pd.DataFrame(documents)
df.to_excel(output_file, index=False, sheet_name='Policy')
