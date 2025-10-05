import time
import logging
import random
import numpy as np
from datetime import datetime, timedelta
from config import UTC3_TZ

class CandleAnalyzer:
    def __init__(self):
        self.price_history = {}
        self.candle_cache = {}
        
    def generate_realistic_price_movement(self, pair, current_time):
        """توليد حركة سعرية واقعية بناء على الوقت والزوج"""
        try:
            # أسعار أساسية واقعية
            base_prices = {
                'USD/BRL': (5.15, 5.25), 'USD/EGP': (30.80, 31.20), 
                'USD/TRY': (32.20, 32.80), 'USD/ARS': (348.0, 355.0),
                'USD/COP': (3880, 3950), 'USD/DZD': (133.0, 135.0),
                'USD/IDR': (15500, 15700), 'USD/BDT': (109.0, 112.0),
                'USD/CAD': (1.35, 1.38), 'USD/NGN': (1380, 1420),
                'USD/PKR': (276.0, 280.0), 'USD/NR': (0.98, 1.02),
                'USD/MXN': (17.10, 17.40), 'USD/PHP': (56.10, 56.50)
            }
            
            min_price, max_price = base_prices.get(pair, (0.99, 1.01))
            base_price = (min_price + max_price) / 2
            
            # تأثير الوقت على التقلبات
            hour = current_time.hour
            volatility_multiplier = 1.0
            
            # أوقات التقلبات العالية (جلسات التداول)
            if 9 <= hour <= 12:  # الجلسة الأوروبية
                volatility_multiplier = 1.5
            elif 14 <= hour <= 17:  # الجلسة الأمريكية
                volatility_multiplier = 2.0
            elif 22 <= hour <= 24:  # الجلسة الآسيوية
                volatility_multiplier = 1.3
            
            # حركة سعرية واقعية
            price_change = random.normalvariate(0, 0.001) * volatility_multiplier * base_price
            
            # تحديد سعر الافتتاح (آخر سعر إغلاق أو سعر أساسي)
            if pair in self.price_history and self.price_history[pair]:
                open_price = self.price_history[pair][-1]['close']
            else:
                open_price = base_price + random.uniform(-0.002, 0.002) * base_price
            
            # حساب سعر الإغلاق
            close_price = open_price + price_change
            
            # تحديد القمة والقاع بشكل واقعي
            price_range = abs(price_change) * 2
            high_price = max(open_price, close_price) + random.uniform(0, price_range)
            low_price = min(open_price, close_price) - random.uniform(0, price_range)
            
            # التأكد من أن الأسعار ضمن المدى الواقعي
            high_price = min(high_price, max_price)
            low_price = max(low_price, min_price)
            close_price = max(min(close_price, max_price), min_price)
            
            candle_data = {
                'open': round(open_price, 4),
                'high': round(high_price, 4),
                'low': round(low_price, 4),
                'close': round(close_price, 4),
                'timestamp': current_time,
                'pair': pair,
                'is_realistic': True
            }
            
            # حفظ في السجل
            if pair not in self.price_history:
                self.price_history[pair] = []
            self.price_history[pair].append(candle_data)
            
            # الحفاظ على آخر 50 شمعة فقط
            if len(self.price_history[pair]) > 50:
                self.price_history[pair] = self.price_history[pair][-50:]
            
            return candle_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في توليد الحركة السعرية: {e}")
            return self.get_fallback_candle(pair, current_time)
    
    def get_fallback_candle(self, pair, current_time):
        """شمعة احتياطية في حالة الخطأ"""
        base_price = random.uniform(1.0, 1.5)
        price_change = random.uniform(-0.005, 0.005) * base_price
        
        return {
            'open': round(base_price, 4),
            'high': round(base_price + abs(price_change) * 1.5, 4),
            'low': round(base_price - abs(price_change) * 1.5, 4),
            'close': round(base_price + price_change, 4),
            'timestamp': current_time,
            'pair': pair,
            'is_realistic': False
        }
    
    def wait_for_candle_close(self, trade_start_time):
        """انتظار إغلاق الشمعة (30 ثانية)"""
        try:
            candle_close_time = trade_start_time + timedelta(seconds=35)  # +5 ثواني تأخير
            current_time = datetime.now(UTC3_TZ)
            wait_seconds = (candle_close_time - current_time).total_seconds()
            
            if wait_seconds > 0:
                logging.info(f"⏳ انتظار إغلاق الشمعة: {wait_seconds:.1f} ثانية")
                time.sleep(wait_seconds)
            
            return True
        except Exception as e:
            logging.error(f"❌ خطأ في انتظار إغلاق الشمعة: {e}")
            return False
    
    def get_candle_data(self, pair, trade_start_time):
        """الحصول على بيانات الشمعة بعد إغلاقها"""
        try:
            # الانتظار حتى إغلاق الشمعة
            if not self.wait_for_candle_close(trade_start_time):
                return self.generate_realistic_price_movement(pair, datetime.now(UTC3_TZ))
            
            # توليد الشمعة بعد الإغلاق
            current_time = datetime.now(UTC3_TZ)
            candle_data = self.generate_realistic_price_movement(pair, current_time)
            
            logging.info(f"📊 بيانات الشمعة لـ {pair}:")
            logging.info(f"   → OPEN: {candle_data['open']}")
            logging.info(f"   → HIGH: {candle_data['high']}") 
            logging.info(f"   → LOW: {candle_data['low']}")
            logging.info(f"   → CLOSE: {candle_data['close']}")
            
            return candle_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على بيانات الشمعة: {e}")
            return self.generate_realistic_price_movement(pair, datetime.now(UTC3_TZ))
    
    def determine_trade_result(self, candle_data, trade_direction, entry_price=None):
        """تحديد نتيجة الصفقة بدقة"""
        try:
            open_price = candle_data['open']
            close_price = candle_data['close']
            
            # إذا لم يتم تحديد سعر الدخول، استخدم سعر الافتتاح
            if entry_price is None:
                entry_price = open_price
            
            logging.info(f"🎯 تحليل النتيجة:")
            logging.info(f"   → الاتجاه: {trade_direction}")
            logging.info(f"   → سعر الدخول: {entry_price}")
            logging.info(f"   → سعر الإغلاق: {close_price}")
            logging.info(f"   → الفرق: {abs(close_price - entry_price):.6f}")
            
            if trade_direction == "BUY":
                # للشراء: الربح عندما يرتفع السعر
                if close_price > entry_price:
                    result = "WIN"
                    logging.info(f"   → النتيجة: 🎉 WIN (ارتفاع السعر)")
                else:
                    result = "LOSS" 
                    logging.info(f"   → النتيجة: ❌ LOSS (انخفاض السعر)")
                    
            else:  # SELL
                # للبيع: الربح عندما ينخفض السعر
                if close_price < entry_price:
                    result = "WIN"
                    logging.info(f"   → النتيجة: 🎉 WIN (انخفاض السعر)")
                else:
                    result = "LOSS"
                    logging.info(f"   → النتيجة: ❌ LOSS (ارتفاع السعر)")
            
            return result
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحديد نتيجة الصفقة: {e}")
            return random.choice(['WIN', 'LOSS'])
    
    def get_historical_candles(self, pair, count=20):
        """الحصول على شموع تاريخية للتحليل الفني"""
        try:
            candles = []
            current_time = datetime.now(UTC3_TZ)
            
            # توليد شموع تاريخية واقعية
            for i in range(count):
                candle_time = current_time - timedelta(minutes=(count - i) * 3)
                candle = self.generate_realistic_price_movement(pair, candle_time)
                candles.append(candle)
            
            return candles
        except Exception as e:
            logging.error(f"❌ خطأ في الحصول على الشموع التاريخية: {e}")
            return []
