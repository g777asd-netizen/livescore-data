import requests
from bs4 import BeautifulSoup
import json

# هذا مجرد مثال توضيحي، ستحتاج لتحليل كود الموقع بدقة
url = "https://www.scoreaxis.com/" 
headers = {'User-Agent': 'Mozilla/5.0'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

matches = []

# هنا ستحتاج لمعرفة الـ Classes الخاصة بالموقع
# لنفترض أن المباريات موجودة داخل div اسمه match-container
for item in soup.find_all('div', class_='match-container'):
    home_team = item.find('span', class_='home').text
    away_team = item.find('span', class_='away').text
    score = item.find('span', class_='score').text
    
    matches.append({
        'home': home_team,
        'away': away_team,
        'score': score
    })

# حفظ البيانات كملف JSON
with open('matches.json', 'w', encoding='utf-8') as f:
    json.dump(matches, f, ensure_ascii=False)
