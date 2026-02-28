import requests
from bs4 import BeautifulSoup
import json
import random
import time
from datetime import datetime

def scrape_scoreaxis():
    url = "https://www.scoreaxis.com/"
    
    # قائمة بمتصفحات مختلفة للخداع
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
    ]
    
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        # ننتظر ثانية عشوائية لتقليل الشك
        time.sleep(2)
        
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        if response.status_code == 403:
            print("❌ الموقع لا يزال يحظر الاتصال (Error 403).")
            # محاولة احتياطية: استخدام رابط Widget مباشر (أسهل في السحب)
            url = "https://www.scoreaxis.com/widget/live-matches/8920" 
            print("🔄 جاري المحاولة مع رابط الـ Widget...")
            response = session.get(url, headers=headers, timeout=15)

        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        matches_data = []

        # البحث في الـ Widget (بنية مختلفة قليلاً وأسهل)
        match_rows = soup.find_all('div', class_='match-row') # محاولة 1
        
        if not match_rows:
            match_rows = soup.select('.match-container, .event-row') # محاولة 2

        print(f"✅ تم العثور على {len(match_rows)} عنصر محتمل.")

        for item in match_rows:
            try:
                # استخراج الأسماء بناء على الكلاسات الشائعة في الودجت
                home = item.find(class_='home').text.strip()
                away = item.find(class_='away').text.strip()
                score = item.find(class_='score').text.strip()
                
                # تنظيف النتيجة
                if not score: score = "VS"
                
                matches_data.append({
                    "home": home,
                    "away": away,
                    "score": score,
                    "time": "LIVE"
                })
            except:
                continue

        # إذا لم نجد بيانات، نضع رسالة حالة
        if not matches_data:
            print("⚠️ لم يتم استخراج مباريات، قد تكون الكلاسات تغيرت.")
            matches_data.append({
                "home": "No Live Matches",
                "away": "Try Later",
                "score": "-",
                "time": datetime.now().strftime("%H:%M")
            })
        else:
            print(f"✅ تم سحب {len(matches_data)} مباراة بنجاح.")

        # حفظ الملف
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(matches_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Error: {e}")
        # تسجيل الخطأ في الملف لنراه
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump([{"home": "Error", "away": str(e), "score": "X"}], f)

if __name__ == "__main__":
    scrape_scoreaxis()
