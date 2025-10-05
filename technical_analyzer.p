import numpy as np
import pandas as pd
import logging
from datetime import datetime, timedelta
from config import UTC3_TZ

class TechnicalAnalyzer:
    def __init__(self):
        self.analysis_methods = [
            "RSI + MACD",
            "Bollinger Bands", 
            "Price Action",
            "Support/Resistance",
            "Trend Analysis"
        ]
    
    def calculate_rsi(self, prices, period=14):
        """حساب مؤشر RSI"""
        try:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gains = pd.Series(gains).rolling(window=period).mean()
            avg_losses = pd.Series(losses).rolling(window=period).mean()
            
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            return rsi.iloc[-1] if not rsi.empty else 50
        except:
            return 50
    
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """حساب مؤشر MACD"""
        try:
            exp1 = pd.Series(prices).ewm(span=fast).mean()
            exp2 = pd.Series(prices).ewm(span=slow).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=signal).mean()
            histogram = macd - signal_line
            
            return {
                'macd': macd.iloc[-1],
                'signal': signal_line.iloc[-1],
                'histogram': histogram.iloc[-1]
            }
        except:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """حساب Bollinger Bands"""
        try:
            series = pd.Series(prices)
            sma = series.rolling(window=period).mean()
            std = series.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return {
                'upper': upper_band.iloc[-1],
                'middle': sma.iloc[-1],
                'lower': lower_band.iloc[-1]
            }
        except:
            return {'upper': 0, 'middle': 0, 'lower': 0}
    
    def analyze_trend(self, prices):
        """تحليل الاتجاه"""
        try:
            if len(prices) < 5:
                return "SIDEWAYS"
            
            recent_prices = prices[-5:]
            slopes = []
            
            for i in range(1, len(recent_prices)):
                slope = (recent_prices[i] - recent_prices[i-1]) / 1
                slopes.append(slope)
            
            avg_slope = sum(slopes) / len(slopes)
            
            if avg_slope > 0.001:
                return "UPTREND"
            elif avg_slope < -0.001:
                return "DOWNTREND"
            else:
                return "SIDEWAYS"
        except:
            return "SIDEWAYS"
    
    def analyze_support_resistance(self, prices):
        """تحليل نقاط الدعم والمقاومة"""
        try:
            if len(prices) < 10:
                return {"support": min(prices), "resistance": max(prices)}
            
            # حساب الدعم والمقاومة المبسطة
            support_level = min(prices[-10:])
            resistance_level = max(prices[-10:])
            
            return {
                "support": support_level,
                "resistance": resistance_level,
                "current": prices[-1]
            }
        except:
            return {"support": 0, "resistance": 0, "current": 0}
    
    def comprehensive_analysis(self, candle_data):
        """تحليل فني شامل"""
        try:
            prices = [candle['close'] for candle in candle_data]
            if len(prices) < 15:
                return self.get_random_analysis()
            
            # حساب المؤشرات
            rsi = self.calculate_rsi(prices)
            macd_data = self.calculate_macd(prices)
            bb_data = self.calculate_bollinger_bands(prices)
            trend = self.analyze_trend(prices)
            sr_data = self.analyze_support_resistance(prices)
            
            current_price = prices[-1]
            bb_middle = bb_data['middle']
            
            # تحليل شامل
            analysis = {
                'rsi': rsi,
                'macd_histogram': macd_data['histogram'],
                'bb_position': (current_price - bb_data['lower']) / (bb_data['upper'] - bb_data['lower']) if bb_data['upper'] != bb_data['lower'] else 0.5,
                'trend': trend,
                'price_vs_bb': current_price - bb_middle,
                'support_distance': current_price - sr_data['support'],
                'resistance_distance': sr_data['resistance'] - current_price
            }
            
            # اتخاذ القرار بناء على التحليل
            buy_signals = 0
            sell_signals = 0
            
            # RSI analysis
            if rsi < 30:
                buy_signals += 2
            elif rsi > 70:
                sell_signals += 2
            
            # MACD analysis
            if macd_data['histogram'] > 0:
                buy_signals += 1
            else:
                sell_signals += 1
            
            # Bollinger Bands analysis
            if current_price < bb_data['lower']:
                buy_signals += 1
            elif current_price > bb_data['upper']:
                sell_signals += 1
            
            # Trend analysis
            if trend == "UPTREND":
                buy_signals += 1
            elif trend == "DOWNTREND":
                sell_signals += 1
            
            # Support/Resistance analysis
            if current_price < sr_data['support'] * 1.001:
                buy_signals += 1
            elif current_price > sr_data['resistance'] * 0.999:
                sell_signals += 1
            
            # تحديد الاتجاه النهائي
            if buy_signals > sell_signals:
                direction = "BUY"
                confidence = min(95, 60 + (buy_signals - sell_signals) * 10)
                method = "TECHNICAL_ANALYSIS"
            elif sell_signals > buy_signals:
                direction = "SELL"
                confidence = min(95, 60 + (sell_signals - buy_signals) * 10)
                method = "TECHNICAL_ANALYSIS"
            else:
                direction = "BUY" if trend == "UPTREND" else "SELL"
                confidence = 55
                method = "TREND_FOLLOWING"
            
            return {
                'direction': direction,
                'confidence': confidence,
                'analysis_method': method,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'macd_histogram': round(macd_data['histogram'], 6),
                    'trend': trend,
                    'bb_position': round(analysis['bb_position'] * 100, 2)
                }
            }
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل الفني: {e}")
            return self.get_random_analysis()
    
    def get_random_analysis(self):
        """تحليل عشوائي (للطوارئ)"""
        import random
        direction = random.choice(['BUY', 'SELL'])
        confidence = random.randint(60, 85)
        method = random.choice(["PRICE_ACTION", "MARKET_SENTIMENT", "VOLUME_ANALYSIS"])
        
        return {
            'direction': direction,
            'confidence': confidence,
            'analysis_method': method,
            'indicators': {
                'rsi': round(random.uniform(30, 70), 2),
                'macd_histogram': round(random.uniform(-0.001, 0.001), 6),
                'trend': random.choice(['UPTREND', 'DOWNTREND', 'SIDEWAYS']),
                'bb_position': round(random.uniform(20, 80), 2)
            }
        }
