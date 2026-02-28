import requests
import json
import time
from datetime import datetime, timedelta

def scrape_smart_calendar():
    # 1. إعدادات الدوريات
    leagues = [
        {"name": "EPL", "url": "eng.1"},       # الدوري الإنجليزي
        {"name": "La Liga", "url": "esp.1"},   # الدوري الإسباني
        {"name": "Bundesliga", "url": "ger.1"},# الدوري الألماني
        {"name": "Serie A", "url": "ita.1"},   # الدوري الإيطالي
        {"name": "Ligue 1", "url": "fra.1"},   # الدوري الفرنسي
        {"name": "UCL", "url": "uefa.champions"}, # أبطال أوروبا
        {"name": "CAF CL", "url": "caf.champions"}, # دوري أبطال أفريقيا
        {"name": "FIFA WC", "url": "fifa.world"}    # تصفيات كأس العالم
    ]
    
    # 2. ضبط التواريخ بدقة
    today = datetime.now()
    print(f"🕒 تاريخ السيرفر الحالي: {today.strftime('%Y-%m-%d')}")

    # ترتيب الأيام حسب الأهمية:
    # الأولوية 1: اليوم (0)
    # الأولوية 2: أمس (-1) وغداً (+1)
    # الأولوية 3: الأيام القادمة (من +2 إلى +60)
    # الأولوية 4: الأيام الماضية (من -2 إلى -10)
    
    days_priority = [0, -1, 1] 
    days_priority.extend(range(2, 60))   # المستقبل
    days_priority.extend(range(-2, -11, -1)) # الماضي
    
    all_matches = []
    processed_dates = set() # لمنع التكرار

    print("🚀 بدء سحب المباريات (الأولوية لليوم)...")

    for day_offset in days_priority:
        current_date = today + timedelta(days=day_offset)
        date_api = current_date.strftime("%Y%m%d")      # للصيغة في الرابط
        date_display = current_date.strftime("%Y-%m-%d") # للعرض

        # تخطي التاريخ لو تم معالجته سابقاً
        if date_display in processed_dates:
            continue
        processed_dates.add(date_display)

        print(f"📅 جاري فحص: {date_display} ...")
        
        daily_matches_found = 0

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
                            
                            # تحديد حالة المباراة للعرض
                            match_status = status.get('shortDetail', '')
                            is_live = status.get('state') == 'in'
                            
                            # تجميع البيانات
                            all_matches.append({
                                "id": event.get('id'),
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
                                "timestamp": date_api # للترتيب لاحقاً
                            })
                            daily_matches_found += 1
            except Exception as e:
                # خطأ بسيط نتجاهله ونكمل
                continue
        
        # إذا وجدنا مباريات في هذا اليوم نطبع العدد
        if daily_matches_found > 0:
            print(f"   ✅ وجدنا {daily_matches_found} مباراة.")

        # راحة قصيرة جداً لتخفيف الحمل
        # time.sleep(0.1)

    # 3. الترتيب النهائي (مهم جداً لأننا سحبنا الأيام بشكل عشوائي)
    # نرتب حسب التاريخ ثم حسب الدوري
    all_matches.sort(key=lambda x: (x['timestamp'], x['league']))

    print(f"🏁 تم الانتهاء! المجموع الكلي: {len(all_matches)} مباراة.")
    
    # 4. حفظ الملف
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(all_matches, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    scrape_smart_calendar()
