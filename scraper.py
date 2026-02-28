import requests
import json
import time
from datetime import datetime, timedelta

def get_real_time():
    """دالة لجلب الوقت الحقيقي من الإنترنت لتجنب أخطاء السيرفر"""
    try:
        # نجلب التوقيت العالمي UTC
        response = requests.get("http://worldtimeapi.org/api/timezone/Etc/UTC", timeout=5)
        data = response.json()
        # نأخذ التاريخ فقط (أول 10 حروف YYYY-MM-DD)
        date_str = data['datetime'][:10]
        print(f"🌍 التوقيت الحقيقي من الإنترنت: {date_str}")
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception as e:
        print(f"⚠️ تعذر جلب التوقيت من الإنترنت، نستخدم توقيت السيرفر: {e}")
        return datetime.now()

def scrape_smart_calendar():
    # 1. إعدادات الدوريات (الأهم فالأهم)
    leagues = [
        {"name": "EPL", "url": "eng.1"},       # إنجليزي
        {"name": "La Liga", "url": "esp.1"},   # إسباني
        {"name": "Bundesliga", "url": "ger.1"},# ألماني
        {"name": "Serie A", "url": "ita.1"},   # إيطالي
        {"name": "Ligue 1", "url": "fra.1"},   # فرنسي
        {"name": "UCL", "url": "uefa.champions"}, # أبطال أوروبا
        {"name": "CAF CL", "url": "caf.champions"}, # أبطال أفريقيا
    ]
    
    # 2. تحديد "اليوم" بناءً على التوقيت الحقيقي
    today = get_real_time()
    
    # سنبحث في: 3 أيام ماضي + اليوم + 14 يوم مستقبل (لتقليل الضغط وضمان السرعة)
    # المجموع حوالي 18 يوم وهو كافي جداً للموقع
    days_priority = [0, -1, 1] 
    days_priority.extend(range(2, 15))   # أسبوعين قدام
    days_priority.extend(range(-2, -4, -1)) # يومين ورا زيادة
    
    all_matches = []
    processed_dates = set()

    print(f"🚀 بدء سحب المباريات بناءً على تاريخ: {today.strftime('%Y-%m-%d')}")

    for day_offset in days_priority:
        current_date = today + timedelta(days=day_offset)
        date_api = current_date.strftime("%Y%m%d")
        date_display = current_date.strftime("%Y-%m-%d")

        if date_display in processed_dates:
            continue
        processed_dates.add(date_display)

        print(f"📅 فحص تاريخ: {date_display} ...")
        
        matches_in_day = 0

        for league in leagues:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league['url']}/scoreboard?dates={date_api}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            try:
                response = requests.get(url, headers=headers, timeout=5)
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
                            match_status = status.get('shortDetail', '')
                            is_live = status.get('state') == 'in'
                            
                            all_matches.append({
                                "date": date_display,
                                "league": league['name'],
                                "home": home['team']['name'],
                                "away": away['team']['name'],
                                "home_score": home.get('score', '0'),
                                "away_score": away.get('score', '0'),
                                "home_logo": home['team'].get('logo', ''),
                                "away_logo": away['team'].get('logo', ''),
                                "status": match_status,
                                "live": is_live,
                                "timestamp": date_api
                            })
                            matches_in_day += 1
            except:
                continue
        
        if matches_in_day > 0:
            print(f"   ✅ تم العثور على {matches_in_day} مباراة.")

    # ترتيب حسب التاريخ
    all_matches.sort(key=lambda x: (x['timestamp'], x['league']))

    print(f"🏁 تم الانتهاء! إجمالي المباريات: {len(all_matches)}")
    
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_smart_calendar()
