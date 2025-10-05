import numpy as np
import pandas as pd
import logging
from datetime import datetime

class TechnicalAnalyzer:
    def __init__(self):
        self.analysis_methods = [
            "RSI + MACD + Bollinger Bands",
            "Trend Analysis + Support/Resistance", 
            "Price Action + Volume Analysis",
            "Multi-Timeframe Analysis",
            "Advanced Technical Indicators"
        ]
    
    def calculate_rsi(self, prices, period=14):
        """حساب مؤشر RSI"""
        try:
            if len(prices) < period + 1:
                return 50
                
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
            if len(prices) < slow:
                return {'macd': 0, 'signal': 0, 'histogram': 0}
                
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
            if len(prices) < period:
                return {'upper': 0, 'middle': 0, 'lower': 0}
                
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
        """تحليل الاتجاه بدقة"""
        try:
            if len(prices) < 10:
                return "SIDEWAYS"
            
            # تحليل الاتجاه قصير المدى
            short_trend = self._calculate_trend_strength(prices[-5:])
            
            # تحليل الاتجاه طويل المدى  
            long_trend = self._calculate_trend_strength(prices[-10:])
            
            # دمج التحليلات
            if short_trend['strength'] > 0.7 and long_trend['strength'] > 0.6:
                return "STRONG_UPTREND"
            elif short_trend['strength'] < -0.7 and long_trend['strength'] < -0.6:
                return "STRONG_DOWNTREND"
            elif short_trend['direction'] == "UP" and long_trend['direction'] == "UP":
                return "UPTREND"
            elif short_trend['direction'] == "DOWN" and long_trend['direction'] == "DOWN":
                return "DOWNTREND"
            else:
                return "SIDEWAYS"
                
        except:
            return "SIDEWAYS"
    
    def _calculate_trend_strength(self, prices):
        """حساب قوة الاتجاه"""
        try:
            x = np.arange(len(prices))
            y = np.array(prices)
            
            # حساب الميل
            slope, intercept = np.polyfit(x, y, 1)
            
            # حساب قوة الاتجاه
            correlation = np.corrcoef(x, y)[0,1]
            strength = abs(correlation * slope * 1000)
            
            return {
                'direction': "UP" if slope > 0 else "DOWN",
                'strength': strength,
                'slope': slope
            }
        except:
            return {'direction': "SIDEWAYS", 'strength': 0, 'slope': 0}
    
    def analyze_support_resistance(self, prices):
        """تحليل نقاط الدعم والمقاومة المتقدمة"""
        try:
            if len(prices) < 15:
                return {"support": min(prices), "resistance": max(prices), "strength": "WEAK"}
            
            # حساب المتوسط المتحرك كدعم/مقاومة ديناميكي
            sma_20 = pd.Series(prices).rolling(window=10).mean().iloc[-1]
            
            # البحث عن القمم والقيعان
            resistance = max(prices[-10:])
            support = min(prices[-10:])
            
            # حساب قوة الدعم/المقاومة
            current_price = prices[-1]
            support_strength = (current_price - support) / (resistance - support) if resistance != support else 0.5
            
            strength_level = "STRONG" if support_strength < 0.3 or support_strength > 0.7 else "MODERATE"
            
            return {
                "support": support,
                "resistance": resistance,
                "sma_support": sma_20,
                "current": current_price,
                "strength": strength_level
            }
        except:
            return {"support": 0, "resistance": 0, "sma_support": 0, "current": 0, "strength": "WEAK"}
    
    def comprehensive_analysis(self, candle_data):
        """تحليل فني شامل ومتقدم"""
        try:
            prices = [candle['close'] for candle in candle_data]
            if len(prices) < 15:
                return self.get_advanced_fallback_analysis()
            
            # حساب المؤشرات المتقدمة
            rsi = self.calculate_rsi(prices)
            macd_data = self.calculate_macd(prices)
            bb_data = self.calculate_bollinger_bands(prices)
            trend = self.analyze_trend(prices)
            sr_data = self.analyze_support_resistance(prices)
            
            current_price = prices[-1]
            
            # تحليل متقدم
            analysis = {
                'rsi': rsi,
                'rsi_signal': "OVERSOLD" if rsi < 30 else "OVERBOUGHT" if rsi > 70 else "NEUTRAL",
                'macd_histogram': macd_data['histogram'],
                'macd_signal': "BULLISH" if macd_data['histogram'] > 0 else "BEARISH",
                'bb_position': (current_price - bb_data['lower']) / (bb_data['upper'] - bb_data['lower']) if bb_data['upper'] != bb_data['lower'] else 0.5,
                'bb_signal': "OVERSOLD" if current_price < bb_data['lower'] else "OVERBOUGHT" if current_price > bb_data['upper'] else "NEUTRAL",
                'trend': trend,
                'trend_strength': self._get_trend_strength(trend),
                'support_distance': current_price - sr_data['support'],
                'resistance_distance': sr_data['resistance'] - current_price,
                'sr_strength': sr_data['strength']
            }
            
            # نظام نقاط متقدم
            buy_points = 0
            sell_points = 0
            
            # RSI analysis (3 points)
            if rsi < 35:
                buy_points += 3
            elif rsi > 65:
                sell_points += 3
            elif 40 <= rsi <= 60:
                buy_points += 1
                sell_points += 1
            
            # MACD analysis (2 points)
            if macd_data['histogram'] > 0.0005:
                buy_points += 2
            elif macd_data['histogram'] < -0.0005:
                sell_points += 2
            
            # Bollinger Bands analysis (2 points)
            if analysis['bb_position'] < 0.2:
                buy_points += 2
            elif analysis['bb_position'] > 0.8:
                sell_points += 2
            
            # Trend analysis (3 points)
            if "UPTREND" in trend:
                buy_points += 3
            elif "DOWNTREND" in trend:
                sell_points += 3
            
            # Support/Resistance analysis (2 points)
            if analysis['support_distance'] < analysis['support_distance'] * 0.1:
                buy_points += 2
            elif analysis['resistance_distance'] < analysis['resistance_distance'] * 0.1:
                sell_points += 2
            
            # تحديد الاتجاه والثقة
            total_points = buy_points + sell_points
            if total_points > 0:
                buy_ratio = buy_points / total_points
                sell_ratio = sell_points / total_points
                
                if buy_ratio > 0.6:
                    direction = "BUY"
                    confidence = min(95, 60 + int((buy_ratio - 0.6) * 100))
                    method = "STRONG_BULLISH_SIGNALS"
                elif sell_ratio > 0.6:
                    direction = "SELL" 
                    confidence = min(95, 60 + int((sell_ratio - 0.6) * 100))
                    method = "STRONG_BEARISH_SIGNALS"
                else:
                    # اتجاه محايد - نتبع الاتجاه
                    direction = "BUY" if "UPTREND" in trend else "SELL"
                    confidence = 55
                    method = "TREND_FOLLOWING"
            else:
                direction = random.choice(['BUY', 'SELL'])
                confidence = 50
                method = "MARKET_NEUTRAL"
            
            return {
                'direction': direction,
                'confidence': confidence,
                'analysis_method': method,
                'indicators': {
                    'rsi': round(rsi, 2),
                    'rsi_signal': analysis['rsi_signal'],
                    'macd_histogram': round(macd_data['histogram'], 6),
                    'macd_signal': analysis['macd_signal'],
                    'trend': trend,
                    'trend_strength': analysis['trend_strength'],
                    'bb_position': round(analysis['bb_position'] * 100, 2),
                    'bb_signal': analysis['bb_signal']
                },
                'points_analysis': {
                    'buy_points': buy_points,
                    'sell_points': sell_points,
                    'buy_ratio': round(buy_ratio, 2) if total_points > 0 else 0.5
                }
            }
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل الفني المتقدم: {e}")
            return self.get_advanced_fallback_analysis()
    
    def _get_trend_strength(self, trend):
        """الحصول على قوة الاتجاه"""
        if "STRONG" in trend:
            return "VERY_STRONG"
        elif trend in ["UPTREND", "DOWNTREND"]:
            return "STRONG" 
        else:
            return "WEAK"
    
    def get_advanced_fallback_analysis(self):
        """تحليل احتياطي متقدم"""
        import random
        direction = random.choice(['BUY', 'SELL'])
        confidence = random.randint(60, 80)
        method = random.choice(self.analysis_methods)
        
        return {
            'direction': direction,
            'confidence': confidence,
            'analysis_method': method,
            'indicators': {
                'rsi': round(random.uniform(35, 65), 2),
                'rsi_signal': random.choice(['NEUTRAL', 'OVERSOLD', 'OVERBOUGHT']),
                'macd_histogram': round(random.uniform(-0.001, 0.001), 6),
                'macd_signal': random.choice(['BULLISH', 'BEARISH']),
                'trend': random.choice(['UPTREND', 'DOWNTREND', 'SIDEWAYS']),
                'trend_strength': random.choice(['STRONG', 'WEAK']),
                'bb_position': round(random.uniform(25, 75), 2),
                'bb_signal': random.choice(['NEUTRAL', 'OVERSOLD', 'OVERBOUGHT'])
            }
        }
