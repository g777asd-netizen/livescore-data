import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# دالة لتنظيف النصوص
def clean_text(text):
    return text.strip() if text else ""

def scrape_scoreaxis():
    # الرابط المستهدف
    url = "https://www.scoreaxis.com/"
    
    # يجب وضع User-Agent لكي يظن الموقع أننا متصفح عادي ولسنا روبوت
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # للتأكد أن الصفحة فتحت بنجاح
        
        soup = BeautifulSoup(response.text, 'html.parser')
        matches_data = []

        # ملاحظة: هذه الـ Classes (مثل match-item) هي تخمينية وتعتمد على تحليل الموقع
        # ستحتاج لتغييرها بناء على ما نراه في "Inspect Element" للموقع الحقيقي
        # سنبدأ بسحب كل العناصر التي قد تحتوي على مباريات
        
        # لنفترض أن الموقع يضع المباريات في جدول أو div
        # هذا الجزء يحتاج لتجربة، سأكتب كوداً يبحث عن الهيكل العام
        
        # البحث عن حاويات المباريات (تحتاج لتحديث حسب كود الموقع الحالي)
        # في scoreaxis عادة تكون المباريات داخل روابط <a> أو div بأسماء معينة
        games = soup.find_all('div', class_='match-event') # مثال لاسم كلاس شائع

        if not games:
            # محاولة بديلة إذا كان الاسم مختلفاً
            games = soup.find_all('tr') # البحث في الجداول

        for game in games:
            try:
                # محاولة استخراج الفريقين والنتيجة
                # هذه الأسماء home-team, away-team يجب التأكد منها من الموقع
                home = clean_text(game.find(class_='home-team').text)
                away = clean_text(game.find(class_='away-team').text)
                score = clean_text(game.find(class_='score').text)
                
                # إضافة الوقت إن وجد
                time = clean_text(game.find(class_='match-time').text)

                if home and away:
                    matches_data.append({
                        "home": home,
                        "away": away,
                        "score": score if score else "VS",
                        "time": time
                    })
            except:
                continue

        # إذا لم نجد بيانات (بسبب اختلاف الكلاسات) نضع رسالة خطأ مؤقتة لنعرف
        if not matches_data:
            print("لم يتم العثور على مباريات، يجب مراجعة أسماء الـ Classes")
            # سنضيف بيانات وهمية للتجربة فقط حتى نضبط الكود
            matches_data.append({
                "home": "Scraper Test", 
                "away": "Check Logs", 
                "score": datetime.now().strftime("%H:%M")
            })

        # حفظ البيانات في ملف JSON
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(matches_data, f, ensure_ascii=False, indent=2)
            
        print("Done! Data saved to matches.json")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_scoreaxis()
