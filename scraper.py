import requests
import json
import email.utils as eut
from datetime import datetime

def get_google_time():
    """
    دالة ذكية لجلب التوقيت الحقيقي من سيرفرات جوجل
    لتجاهل توقيت سيرفر جيت هب الخاطئ (2026)
    """
    try:
        response = requests.head("https://www.google.com", timeout=5)
        date_str = response.headers['Date']
        # تحويل صيغة التاريخ من الهيدر إلى تاريخ بايثون
        real_time = eut.parsedate_to_datetime(date_str)
        print(f"✅ التوقيت الحقيقي من جوجل: {real_time.strftime('%Y-%m-%d')}")
        return real_time
    except Exception as e:
        print(f"⚠️ فشل جلب توقيت جوجل: {e}")
        # محاولة أخيرة مع موقع آخر
        return datetime.now()

def scrape_today_only():
    # 1. قائمة الدوريات الهامة
    leagues = [
        {"name": "EPL", "url": "eng.1"},       # إنجليزي
        {"name": "La Liga", "url": "esp.1"},   # إسباني
        {"name": "Bundesliga", "url": "ger.1"},# ألماني
        {"name": "Serie A", "url": "ita.1"},   # إيطالي
        {"name": "Ligue 1", "url": "fra.1"},   # فرنسي
        {"name": "UCL", "url": "uefa.champions"}, # أبطال أوروبا
        {"name": "CAF CL", "url": "caf.champions"}, # أبطال أفريقيا
        {"name": "KSA League", "url": "sau.1"}, # الدوري السعودي
        {"name": "EGY League", "url": "egy.1"}   # الدوري المصري
    ]
    
    # 2. الحصول على تاريخ اليوم الحقيقي
    today = get_google_time()
    date_api = today.strftime("%Y%m%d")      # الصيغة للرابط (20250125)
    date_display = today.strftime("%Y-%m-%d") # الصيغة للعرض (2025-01-25)

    print(f"🚀 جاري سحب مباريات اليوم فقط ({date_display})...")
    
    all_matches = []
    
    for league in leagues:
        # رابط ESPN لمباريات اليوم المحدد
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league['url']}/scoreboard?dates={date_api}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                for event in events:
                    competitions = event.get('competitions', [{}])[0]
                    competitors = competitions.get('competitions', [])
                    
                    home = next((t for t in competitors if t['homeAway'] == 'home'), None)
                    away = next((t for t in competitors if t['homeAway'] == 'away'), None)
                    
                    if home and away:
                        status = event.get('status', {}).get('type', {})
                        match_status = status.get('shortDetail', '') # النتيجة أو الوقت
                        state = status.get('state', '') # pre, in, post
                        is_live = (state == 'in')

                        # تجميع بيانات المباراة
                        match_data = {
                            "league": league['name'],
                            "date": date_display,
                            "home": home['team']['name'],
                            "away": away['team']['name'],
                            "home_score": home.get('score', '0'),
                            "away_score": away.get('score', '0'),
                            "home_logo": home['team'].get('logo', ''),
                            "away_logo": away['team'].get('logo', ''),
                            "status": match_status,
                            "live": is_live,
                            "timestamp": date_api
                        }
                        all_matches.append(match_data)
        except Exception as e:
            print(f"خطأ في دوري {league['name']}: {e}")
            continue

    # حفظ البيانات
    print(f"🏁 تم الانتهاء! عدد مباريات اليوم: {len(all_matches)}")
    
    if len(all_matches) == 0:
        # إضافة رسالة وهمية لكي لا يظهر الموقع فارغاً إذا لم تكن هناك مباريات
        all_matches.append({
            "league": "Info",
            "date": date_display,
            "home": "لا توجد مباريات",
            "away": "جارية الآن",
            "home_score": "-",
            "away_score": "-",
            "home_logo": "",
            "away_logo": "",
            "status": "No Matches",
            "live": False
        })

    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_today_only()
