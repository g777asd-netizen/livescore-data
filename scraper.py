import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_scoreaxis_direct():
    # الرابط المباشر لموقع Scoreaxis
    url = "https://www.scoreaxis.com/"
    
    print("🚀 جاري الاتصال بموقع Scoreaxis...")

    # رؤوس مخصصة للخداع (كأننا متصفح لابتوب حقيقي)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }

    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        
        # التأكد إن الموقع فتح ومش عامل بلوك
        if response.status_code == 403:
            print("❌ للأسف: موقع Scoreaxis حظر الاتصال (Error 403 Cloudflare).")
            # هنا بنحاول نجرب رابط تاني احتياطي جوه الموقع
            url = "https://www.scoreaxis.com/fixtures-results"
            print("🔄 جاري المحاولة مع رابط النتائج...")
            response = session.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"⚠️ فشل الاتصال، الكود: {response.status_code}")
            return

        print("✅ تم فتح الموقع بنجاح! جاري تحليل البيانات...")

        soup = BeautifulSoup(response.text, 'html.parser')
        all_matches = []

        # تحليل كود HTML الخاص بـ Scoreaxis
        # بنبحث عن حاويات المباريات (تختلف الكلاسات أحياناً لذا نبحث عن النمط العام)
        
        # عادة المباريات تكون داخل جدول أو ديفات بأسماء فرق
        match_containers = soup.find_all('div', class_=re.compile('match|fixture')) 
        
        # لو ملقاش، نجرب ندور على أسماء فرق
        if not match_containers:
            match_containers = soup.find_all('tr')

        count = 0
        for item in match_containers:
            try:
                # محاولة استخراج البيانات بناء على هيكل Scoreaxis
                # هذه الكلاسات تقريبية وتحتاج تطابق مع الموقع الحي
                home_elem = item.find(class_=re.compile('home|team-1'))
                away_elem = item.find(class_=re.compile('away|team-2'))
                score_elem = item.find(class_=re.compile('score|result'))
                status_elem = item.find(class_=re.compile('time|status'))

                if home_elem and away_elem:
                    home = home_elem.get_text(strip=True)
                    away = away_elem.get_text(strip=True)
                    
                    # تنظيف النتيجة
                    score = score_elem.get_text(strip=True) if score_elem else "VS"
                    status = status_elem.get_text(strip=True) if status_elem else "-"

                    # تخطي المباريات الفارغة
                    if not home or not away:
                        continue

                    all_matches.append({
                        "league": "Scoreaxis", # الموقع لا يسهل استخراج اسم الدوري بسهولة من القائمة المختصرة
                        "date": "Today",
                        "home": home,
                        "away": away,
                        "home_score": score.split('-')[0].strip() if '-' in score else score,
                        "away_score": score.split('-')[1].strip() if '-' in score else "",
                        "home_logo": "", # صور اللوجو تحتاج كود معقد لسحبها من الخلفية
                        "away_logo": "",
                        "status": status,
                        "live": "Live" in status or "'" in status
                    })
                    count += 1
            except:
                continue

        print(f"🏁 تم العثور على {len(all_matches)} مباراة من Scoreaxis.")
        
        # حفظ الملف
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(all_matches, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ حدث خطأ غير متوقع: {e}")

if __name__ == "__main__":
    scrape_scoreaxis_direct()
