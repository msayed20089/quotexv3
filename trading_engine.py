import random
import logging
from datetime import datetime
from config import UTC3_TZ, TRADING_PAIRS

class TradingEngine:
    def __init__(self):
        self.pairs = TRADING_PAIRS
        
        # استيراد المحللين داخل الدالة
        from candle_analyzer import CandleAnalyzer
        from technical_analyzer import TechnicalAnalyzer
        
        self.candle_analyzer = CandleAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
        self.last_analysis = {}
        self.recent_directions = []  # تتبع الاتجاهات الحديثة
    
    def analyze_and_decide(self):
        """تحليل متقدم واتخاذ قرار التداول"""
        try:
            # اختيار زوج عشوائي
            pair = random.choice(self.pairs)
            
            # الحصول على شموع تاريخية للتحليل
            historical_candles = self.candle_analyzer.get_historical_candles(pair, 25)
            
            if historical_candles and len(historical_candles) >= 15:
                # استخدام التحليل الفني الأساسي فقط
                analysis_result = self.technical_analyzer.comprehensive_analysis(historical_candles)
                
                # تطبيق توازن إضافي على الاتجاهات
                balanced_direction = self.apply_direction_balance(analysis_result['direction'])
                
                trade_data = {
                    'pair': pair,
                    'direction': balanced_direction,
                    'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
                    'duration': 30,
                    'confidence': analysis_result['confidence'],
                    'analysis_method': analysis_result['analysis_method'],
                    'indicators': analysis_result['indicators'],
                    'news_impact': {'direction': 'NEUTRAL', 'score': 0, 'events_count': 0},
                    'market_sentiment': {'overall_direction': 'NEUTRAL', 'confidence': 50},
                    'points_breakdown': analysis_result.get('points_analysis', {'buy_points': 0, 'sell_points': 0})
                }
                
                # حفظ آخر تحليل
                self.last_analysis[pair] = trade_data
                
            else:
                # تحليل بسيط إذا فشل التحليل المتقدم
                trade_data = self.get_smart_fallback_analysis(pair)
            
            logging.info(f"🎯 قرار التداول النهائي لـ {pair}: {trade_data['direction']} (ثقة: {trade_data['confidence']}%)")
            return trade_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل واتخاذ القرار: {e}")
            return self.get_smart_fallback_analysis(random.choice(self.pairs))
    
    def apply_direction_balance(self, direction):
        """تطبيق توازن على الاتجاهات لمنع التكرار"""
        # حفظ آخر 5 اتجاهات
        self.recent_directions.append(direction)
        if len(self.recent_directions) > 5:
            self.recent_directions.pop(0)
        
        # إذا كانت 3 اتجاهات متتالية نفس النوع، نغير الاتجاه
        if len(self.recent_directions) >= 3:
            last_three = self.recent_directions[-3:]
            if all(d == 'BUY' for d in last_three):
                logging.info("⚖️ تصحيح توازن: تحويل من BUY إلى SELL")
                return 'SELL'
            elif all(d == 'SELL' for d in last_three):
                logging.info("⚖️ تصحيح توازن: تحويل من SELL إلى BUY")
                return 'BUY'
        
        return direction
    
    def get_smart_fallback_analysis(self, pair):
        """تحليل احتياطي ذكي مع توازن"""
        # توزيع 50/50 بين BUY و SELL
        direction = random.choice(['BUY', 'SELL'])
        confidence = random.randint(60, 80)
        
        # تطبيق التوازن
        balanced_direction = self.apply_direction_balance(direction)
        
        return {
            'pair': pair,
            'direction': balanced_direction,
            'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
            'duration': 30,
            'confidence': confidence,
            'analysis_method': 'FALLBACK_ANALYSIS',
            'indicators': {},
            'news_impact': {'direction': 'NEUTRAL', 'score': 0},
            'market_sentiment': {'overall_direction': 'NEUTRAL', 'confidence': 50},
            'points_breakdown': {'buy_points': 0, 'sell_points': 0}
        }
