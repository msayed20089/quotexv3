import random
import logging
from datetime import datetime
from config import UTC3_TZ, TRADING_PAIRS

class TradingEngine:
    def __init__(self, candle_analyzer, technical_analyzer):
        self.pairs = TRADING_PAIRS
        self.candle_analyzer = candle_analyzer
        self.technical_analyzer = technical_analyzer
        
        # استيراد المحلل المتقدم
        from advanced_analyzer import AdvancedAnalyzer
        self.advanced_analyzer = AdvancedAnalyzer()
        
        self.last_analysis = {}
    
    def analyze_and_decide(self):
        """تحليل متقدم واتخاذ قرار التداول"""
        try:
            # اختيار زوج عشوائي
            pair = random.choice(self.pairs)
            
            # الحصول على شموع تاريخية للتحليل
            historical_candles = self.candle_analyzer.get_historical_candles(pair, 25)
            
            if historical_candles and len(historical_candles) >= 15:
                # استخدام التحليل المتقدم
                analysis_result = self.advanced_analyzer.comprehensive_analysis(pair, historical_candles)
                
                trade_data = {
                    'pair': pair,
                    'direction': analysis_result['direction'],
                    'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
                    'duration': 30,
                    'confidence': analysis_result['confidence'],
                    'analysis_method': analysis_result['analysis_method'],
                    'indicators': analysis_result['technical_analysis'].get('indicators', {}),
                    'news_impact': analysis_result['news_analysis'],
                    'market_sentiment': analysis_result['sentiment_analysis'],
                    'points_breakdown': analysis_result['points_breakdown']
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
    
    # باقي الدوال تبقى كما هي...
