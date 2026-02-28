import requests
import json
from datetime import datetime

def scrape_auto_live():
    # قائمة الدوريات
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
    
    print("🚀 جاري سحب المباريات الحالية (تجاهل التاريخ)...")
    
    all_matches = []
    current_display_date = datetime.now().strftime("%Y-%m-%d") # للتسجيل فقط

    for league in leagues:
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # التغيير الجوهري: حذفنا جزء (?dates=...)
        # هذا يجبر الموقع على إرسال مباريات "اليوم" الحالية
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league['url']}/scoreboard"
        
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                
                # طباعة للتأكد من وجود بيانات
                if len(events) > 0:
                    print(f"   ✅ وجدنا {len(events)} مباراة في {league['name']}")

                for event in events:
                    competitions = event.get('competitions', [{}])[0]
                    competitors = competitions.get('competitions', [])
                    
                    home = next((t for t in competitors if t['homeAway'] == 'home'), None)
                    away = next((t for t in competitors if t['homeAway'] == 'away'), None)
                    
                    if home and away:
                        status = event.get('status', {}).get('type', {})
                        match_status = status.get('shortDetail', '')
                        state = status.get('state', '') # pre, in, post
                        is_live = (state == 'in')
                        
                        # نستخدم التاريخ القادم من المباراة نفسها لضمان الدقة
                        match_date = event.get('date', '')[:10] # 2026-02-28
                        
                        all_matches.append({
                            "league": league['name'],
                            "date": match_date, # تاريخ المباراة الفعلي من المصدر
                            "home": home['team']['name'],
                            "away": away['team']['name'],
                            "home_score": home.get('score', '0'),
                            "away_score": away.get('score', '0'),
                            "home_logo": home['team'].get('logo', ''),
                            "away_logo": away['team'].get('logo', ''),
                            "status": match_status,
                            "live": is_live
                        })
        except Exception as e:
            print(f"⚠️ خطأ في {league['name']}: {e}")
            continue

    print(f"🏁 النتيجة النهائية: {len(all_matches)} مباراة.")
    
    # حفظ الملف
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_auto_live()
