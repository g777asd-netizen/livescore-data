import requests
import json
from datetime import datetime

def scrape_espn():
    # رابط API الخاص بـ ESPN (الدوري الإنجليزي + أهم المباريات)
    # يمكن تغيير الرابط لجلب دوريات أخرى
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        matches_data = []

        # الدخول في تفاصيل ملف الـ JSON الخاص بـ ESPN
        events = data.get('events', [])
        
        print(f"✅ وجدنا {len(events)} مباريات في القائمة.")

        for event in events:
            try:
                competitions = event.get('competitions', [{}])[0]
                competitors = competitions.get('competitors', [])
                
                # استخراج الفريقين
                home_team = next((team for team in competitors if team['homeAway'] == 'home'), None)
                away_team = next((team for team in competitors if team['homeAway'] == 'away'), None)
                
                if home_team and away_team:
                    home_name = home_team['team']['name']
                    away_name = away_team['team']['name']
                    
                    # استخراج النتيجة
                    home_score = home_team.get('score', '0')
                    away_score = away_team.get('score', '0')
                    
                    # حالة المباراة (مباشر - انتهت - لم تبدأ)
                    status = event.get('status', {}).get('type', {}).get('shortDetail', '')

                    matches_data.append({
                        "home": home_name,
                        "away": away_name,
                        "score": f"{home_score} - {away_score}",
                        "time": status
                    })
            except Exception as e:
                print(f"خطأ في مباراة واحدة: {e}")
                continue

        # إذا لم تكن هناك مباريات (مثل أوقات الصباح الباكر)، نضع رسالة
        if not matches_data:
            matches_data.append({
                "home": "No Matches",
                "away": "Right Now",
                "score": "-",
                "time": datetime.now().strftime("%H:%M")
            })

        # حفظ البيانات بنفس التنسيق اللي بلوجر مستنيه
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump(matches_data, f, ensure_ascii=False, indent=2)
            
        print("✅ تم تحديث البيانات بنجاح!")

    except Exception as e:
        print(f"❌ Error: {e}")
        # تسجيل الخطأ
        with open('matches.json', 'w', encoding='utf-8') as f:
            json.dump([{"home": "Error", "away": "Check Logs", "score": "X", "time": "Err"}], f)

if __name__ == "__main__":
    scrape_espn()
