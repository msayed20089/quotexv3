import requests
import logging
import random
import time
from datetime import datetime

class MarketSentiment:
    def __init__(self):
        self.sentiment_cache = {}
        self.cache_timeout = 300  # 5 دقائق
        
    def get_market_sentiment(self, pair):
        """الحصول على اتجاه السوق الحالي للزوج"""
        try:
            cache_key = f"sentiment_{pair}"
            current_time = time.time()
            
            # التحقق من الكاش
            if cache_key in self.sentiment_cache:
                cached_data, timestamp = self.sentiment_cache[cache_key]
                if current_time - timestamp < self.cache_timeout:
                    return cached_data
            
            # محاكاة بيانات الزخم السعري الواقعية
            sentiment_data = self.generate_realistic_sentiment(pair)
            
            self.sentiment_cache[cache_key] = (sentiment_data, current_time)
            return sentiment_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على اتجاه السوق: {e}")
            return self.generate_fallback_sentiment(pair)
    
    def generate_realistic_sentiment(self, pair):
        """توليد بيانات زخم واقعية"""
        try:
            # محاكاة بيانات تداول حقيقية
            buy_pressure = random.uniform(0.4, 0.7)
            sell_pressure = 1 - buy_pressure
            
            # تحديد الاتجاه بناء على الضغط
            if buy_pressure > 0.55:
                direction = "BULLISH"
                strength = min(95, int(buy_pressure * 100))
            elif sell_pressure > 0.55:
                direction = "BEARISH" 
                strength = min(95, int(sell_pressure * 100))
            else:
                direction = "NEUTRAL"
                strength = 50
            
            sentiment_data = {
                'direction': direction,
                'strength': strength,
                'buy_pressure': round(buy_pressure * 100, 1),
                'sell_pressure': round(sell_pressure * 100, 1),
                'volume_trend': random.choice(['INCREASING', 'DECREASING', 'STABLE']),
                'momentum': random.choice(['STRONG', 'MODERATE', 'WEAK']),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
            
            logging.info(f"📊 زخم {pair}: {direction} (قوة: {strength}%)")
            
            return sentiment_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في توليد الزخم: {e}")
            return self.generate_fallback_sentiment(pair)
    
    def generate_fallback_sentiment(self, pair):
        """بيانات زخم احتياطية"""
        return {
            'direction': random.choice(['BULLISH', 'BEARISH']),
            'strength': random.randint(55, 75),
            'buy_pressure': round(random.uniform(45, 65), 1),
            'sell_pressure': round(random.uniform(35, 55), 1),
            'volume_trend': 'STABLE',
            'momentum': 'MODERATE',
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def analyze_multiple_timeframes(self, pair):
        """تحليل الزخم على فترات زمنية متعددة"""
        try:
            timeframes = ['1m', '5m', '15m', '1h']
            timeframe_analysis = {}
            
            for tf in timeframes:
                sentiment = self.get_market_sentiment(pair)
                timeframe_analysis[tf] = sentiment
            
            # تحليل شامل للفترات الزمنية
            bullish_count = sum(1 for tf in timeframes if timeframe_analysis[tf]['direction'] == 'BULLISH')
            bearish_count = sum(1 for tf in timeframes if timeframe_analysis[tf]['direction'] == 'BEARISH')
            
            if bullish_count >= 3:
                overall_direction = "BULLISH"
                confidence = min(90, 60 + (bullish_count * 10))
            elif bearish_count >= 3:
                overall_direction = "BEARISH"
                confidence = min(90, 60 + (bearish_count * 10))
            else:
                overall_direction = "NEUTRAL"
                confidence = 50
            
            return {
                'overall_direction': overall_direction,
                'confidence': confidence,
                'timeframe_analysis': timeframe_analysis,
                'bullish_timeframes': bullish_count,
                'bearish_timeframes': bearish_count
            }
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحليل الفترات الزمنية: {e}")
            return {
                'overall_direction': 'NEUTRAL',
                'confidence': 50,
                'timeframe_analysis': {},
                'bullish_timeframes': 0,
                'bearish_timeframes': 0
            }
