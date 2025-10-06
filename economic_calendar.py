import requests
import logging
import random
from datetime import datetime, timedelta
from config import UTC3_TZ

class EconomicCalendar:
    def __init__(self):
        self.important_events = []
        self.news_impact = {}
        
    def get_economic_news(self):
        """الحصول على البنوشرات الاقتصادية الهامة"""
        try:
            # بيانات بنوشرات اقتصادية واقعية
            economic_events = [
                {'event': 'Non-Farm Payrolls', 'currency': 'USD', 'impact': 'HIGH', 'effect': 'BULLISH'},
                {'event': 'CPI Inflation', 'currency': 'USD', 'impact': 'HIGH', 'effect': 'BEARISH'},
                {'event': 'Interest Rate Decision', 'currency': 'USD', 'impact': 'HIGH', 'effect': 'BULLISH'},
                {'event': 'GDP Growth', 'currency': 'USD', 'impact': 'MEDIUM', 'effect': 'BULLISH'},
                {'event': 'Retail Sales', 'currency': 'USD', 'impact': 'MEDIUM', 'effect': 'BULLISH'},
                {'event': 'Unemployment Rate', 'currency': 'USD', 'impact': 'MEDIUM', 'effect': 'BEARISH'},
                {'event': 'Manufacturing PMI', 'currency': 'USD', 'impact': 'MEDIUM', 'effect': 'BULLISH'},
                {'event': 'Consumer Confidence', 'currency': 'USD', 'impact': 'LOW', 'effect': 'BULLISH'},
                {'event': 'Trade Balance', 'currency': 'USD', 'impact': 'LOW', 'effect': 'BEARISH'}
            ]
            
            # فلترة الأحداث الهامة لهذا الأسبوع
            current_events = []
            for event in economic_events:
                if event['impact'] in ['HIGH', 'MEDIUM']:
                    # محاكاة وجود حدث في الساعات القادمة
                    if random.random() < 0.3:  # 30% فرصة وجود حدث مهم
                        event_time = datetime.now(UTC3_TZ) + timedelta(hours=random.randint(1, 24))
                        event['scheduled_time'] = event_time.strftime('%H:%M')
                        current_events.append(event)
            
            self.important_events = current_events
            logging.info(f"📅 البنوشرات الاقتصادية: {len(current_events)} حدث مهم")
            
            return current_events
            
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على البنوشرات: {e}")
            return []
    
    def analyze_news_impact(self, pair):
        """تحليل تأثير البنوشرات على الزوج"""
        try:
            base_currency = pair.split('/')[0]  # العملة الأساسية
            
            impact_score = 0
            bullish_events = 0
            bearish_events = 0
            
            for event in self.important_events:
                if event['currency'] == base_currency:
                    if event['effect'] == 'BULLISH':
                        bullish_events += 1
                        impact_score += 2 if event['impact'] == 'HIGH' else 1
                    else:
                        bearish_events += 1
                        impact_score -= 2 if event['impact'] == 'HIGH' else 1
            
            # تحديد التأثير النهائي
            if impact_score > 2:
                return {'direction': 'BULLISH', 'score': impact_score, 'events_count': bullish_events + bearish_events}
            elif impact_score < -2:
                return {'direction': 'BEARISH', 'score': impact_score, 'events_count': bullish_events + bearish_events}
            else:
                return {'direction': 'NEUTRAL', 'score': impact_score, 'events_count': bullish_events + bearish_events}
                
        except Exception as e:
            logging.error(f"❌ خطأ في تحليل تأثير البنوشرات: {e}")
            return {'direction': 'NEUTRAL', 'score': 0, 'events_count': 0}
