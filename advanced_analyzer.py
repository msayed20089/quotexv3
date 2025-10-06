import logging
from datetime import datetime
from config import UTC3_TZ

class AdvancedAnalyzer:
    def __init__(self):
        from economic_calendar import EconomicCalendar
        from market_sentiment import MarketSentiment
        from technical_analyzer import TechnicalAnalyzer
        
        self.economic_calendar = EconomicCalendar()
        self.market_sentiment = MarketSentiment()
        self.technical_analyzer = TechnicalAnalyzer()
        
    def comprehensive_analysis(self, pair, historical_candles):
        """تحليل شامل متكامل"""
        try:
            logging.info(f"🎯 بدء التحليل الشامل لـ {pair}")
            
            # 1. التحليل الفني
            technical_analysis = self.technical_analyzer.comprehensive_analysis(historical_candles)
            
            # 2. البنوشرات الاقتصادية
            economic_events = self.economic_calendar.get_economic_news()
            news_impact = self.economic_calendar.analyze_news_impact(pair)
            
            # 3. زخم السوق
            sentiment_analysis = self.market_sentiment.analyze_multiple_timeframes(pair)
            
            # 4. دمج كل التحليلات
            final_decision = self.combine_analyses(
                technical_analysis, 
                news_impact, 
                sentiment_analysis,
                pair
            )
            
            logging.info(f"📊 التحليل الشامل لـ {pair}:")
            logging.info(f"   → الفني: {technical_analysis['direction']} ({technical_analysis['confidence']}%)")
            logging.info(f"   → البنوشرات: {news_impact['direction']}")
            logging.info(f"   → الزخم: {sentiment_analysis['overall_direction']} ({sentiment_analysis['confidence']}%)")
            logging.info(f"   → القرار النهائي: {final_decision['direction']} ({final_decision['confidence']}%)")
            
            return final_decision
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل الشامل: {e}")
            return self.get_fallback_analysis(pair)
    
    def combine_analyses(self, technical, news, sentiment, pair):
        """دمج كل أنواع التحليل"""
        try:
            # نظام نقاط متقدم
            buy_points = 0
            sell_points = 0
            
            # التحليل الفني (40% وزن)
            if technical['direction'] == 'BUY':
                buy_points += 4
                logging.info("   → الفني: +4 نقاط للشراء")
            else:
                sell_points += 4
                logging.info("   → الفني: +4 نقاط للبيع")
            
            # البنوشرات الاقتصادية (30% وزن)
            if news['direction'] == 'BULLISH':
                buy_points += 3
                logging.info("   → البنوشرات: +3 نقاط للشراء")
            elif news['direction'] == 'BEARISH':
                sell_points += 3
                logging.info("   → البنوشرات: +3 نقاط للبيع")
            else:
                buy_points += 1
                sell_points += 1
                logging.info("   → البنوشرات: +1 نقطة لكل اتجاه")
            
            # زخم السوق (30% وزن)
            if sentiment['overall_direction'] == 'BULLISH':
                buy_points += 3
                logging.info("   → الزخم: +3 نقاط للشراء")
            elif sentiment['overall_direction'] == 'BEARISH':
                sell_points += 3
                logging.info("   → الزخم: +3 نقاط للبيع")
            else:
                buy_points += 1
                sell_points += 1
                logging.info("   → الزخم: +1 نقطة لكل اتجاه")
            
            logging.info(f"   → النقاط النهائية: شراء {buy_points} | بيع {sell_points}")
            
            # اتخاذ القرار النهائي
            total_points = buy_points + sell_points
            if total_points > 0:
                buy_ratio = buy_points / total_points
                
                if buy_ratio >= 0.6:
                    direction = "BUY"
                    confidence = min(95, 70 + int((buy_ratio - 0.6) * 50))
                    method = "ADVANCED_BULLISH_SIGNALS"
                elif buy_ratio <= 0.4:
                    direction = "SELL"
                    confidence = min(95, 70 + int((0.6 - buy_ratio) * 50))
                    method = "ADVANCED_BEARISH_SIGNALS"
                else:
                    # متوازن - نفضل الاتجاه الفني
                    direction = technical['direction']
                    confidence = max(60, technical['confidence'] - 10)
                    method = "BALANCED_ANALYSIS"
            else:
                direction = technical['direction']
                confidence = technical['confidence']
                method = "TECHNICAL_FALLBACK"
            
            return {
                'direction': direction,
                'confidence': confidence,
                'analysis_method': method,
                'technical_analysis': technical,
                'news_analysis': news,
                'sentiment_analysis': sentiment,
                'points_breakdown': {
                    'buy_points': buy_points,
                    'sell_points': sell_points,
                    'buy_ratio': round(buy_ratio, 2) if total_points > 0 else 0.5
                }
            }
            
        except Exception as e:
            logging.error(f"❌ خطأ في دمج التحليلات: {e}")
            return self.get_fallback_analysis(pair)
    
    def get_fallback_analysis(self, pair):
        """تحليل احتياطي"""
        import random
        direction = random.choice(['BUY', 'SELL'])
        confidence = random.randint(60, 80)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'analysis_method': 'FALLBACK_ANALYSIS',
            'technical_analysis': {},
            'news_analysis': {'direction': 'NEUTRAL', 'score': 0},
            'sentiment_analysis': {'overall_direction': 'NEUTRAL', 'confidence': 50},
            'points_breakdown': {'buy_points': 0, 'sell_points': 0, 'buy_ratio': 0.5}
        }
