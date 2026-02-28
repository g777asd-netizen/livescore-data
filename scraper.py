import requests
import json
from datetime import datetime, timedelta

def scrape_calendar():
    # قائمة الدوريات التي نريد سحبها (يمكنك إضافة المزيد بحذر)
    leagues = [
        {"name": "EPL", "url": "eng.1"},       # الدوري الإنجليزي
        {"name": "La Liga", "url": "esp.1"},   # الدوري الإسباني
        {"name": "Bundesliga", "url": "ger.1"},# الدوري الألماني
        {"name": "Serie A", "url": "ita.1"},   # الدوري الإيطالي
        {"name": "Ligue 1", "url": "fra.1"},   # الدوري الفرنسي
        {"name": "UCL", "url": "uefa.champions"} # أبطال أوروبا
    ]
    
    # تحديد النطاق الزمني: 10 أيام ماضي + اليوم + 49 يوم مستقبل
    today = datetime.now()
    start_date = today - timedelta(days=10)
    total_days = 60
    
    all_matches = []
    
    print(f"🔄 جاري سحب جدول المباريات لمدة {total_days} يوماً...")

    # حلقة تكرارية لكل يوم
    for i in range(total_days):
        current_date = start_date + timedelta(days=i)
        date_str = current_date.strftime("%Y%m%d") # صيغة التاريخ للرابط
        display_date = current_date.strftime("%Y-%m-%d") # صيغة التاريخ للعرض
        
        print(f"📅 معالجة تاريخ: {display_date}")

        # حلقة تكرارية لكل دوري في هذا اليوم
        for league in leagues:
            url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/{league['url']}/scoreboard?dates={date_str}"
            
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
                        
                        home_team = next((t for t in competitors if t['homeAway'] == 'home'), None)
                        away_team = next((t for t in competitors if t['homeAway'] == 'away'), None)
                        
                        if home_team and away_team:
                            status_type = event.get('status', {}).get('type', {})
                            state = status_type.get('state', '') # pre, in, post
                            short_detail = status_type.get('shortDetail', '') # FT, 90', 14:00

                            match_data = {
                                "league": league['name'],
                                "date": display_date,
                                "home": home_team['team']['name'],
                                "away": away_team['team']['name'],
                                "home_score": home_team.get('score', '0'),
                                "away_score": away_team.get('score', '0'),
                                "logo_home": home_team['team'].get('logo', ''),
                                "logo_away": away_team['team'].get('logo', ''),
                                "status": short_detail, # الوقت أو النتيجة النهائية
                                "state": state # حالة المباراة للفرز (مباشر أو انتهى)
                            }
                            all_matches.append(match_data)
            except Exception as e:
                print(f"⚠️ خطأ في {league['name']} بتاريخ {display_date}: {e}")
                continue

    # حفظ البيانات
    print(f"✅ تم جمع {len(all_matches)} مباراة.")
    
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_calendar()
