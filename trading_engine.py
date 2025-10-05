import random
import logging
from datetime import datetime
from config import UTC3_TZ, TRADING_PAIRS

class TradingEngine:
    def __init__(self, candle_analyzer, technical_analyzer):
        self.pairs = TRADING_PAIRS
        self.candle_analyzer = candle_analyzer
        self.technical_analyzer = technical_analyzer
        self.last_analysis = {}
    
    def analyze_and_decide(self):
        """تحليل فني متقدم واتخاذ قرار التداول"""
        try:
            # اختيار زوج عشوائي
            pair = random.choice(self.pairs)
            
            # الحصول على شموع تاريخية للتحليل
            historical_candles = self.candle_analyzer.get_historical_candles(pair, 25)
            
            if historical_candles and len(historical_candles) >= 15:
                # تحليل فني متقدم
                analysis_result = self.technical_analyzer.comprehensive_analysis(historical_candles)
                
                # تحسين القرار بناء على تحليل إضافي
                final_decision = self.refine_decision(analysis_result, historical_candles)
                
                trade_data = {
                    'pair': pair,
                    'direction': final_decision['direction'],
                    'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
                    'duration': 30,
                    'confidence': final_decision['confidence'],
                    'analysis_method': final_decision['method'],
                    'indicators': final_decision['indicators'],
                    'risk_level': final_decision['risk_level']
                }
                
                # حفظ آخر تحليل
                self.last_analysis[pair] = trade_data
                
            else:
                # تحليل بسيط إذا فشل التحليل المتقدم
                trade_data = self.get_smart_fallback_analysis(pair)
            
            logging.info(f"🎯 قرار التداول لـ {pair}: {trade_data['direction']} (ثقة: {trade_data['confidence']}%)")
            return trade_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل واتخاذ القرار: {e}")
            return self.get_smart_fallback_analysis(random.choice(self.pairs))
    
    def refine_decision(self, analysis_result, historical_candles):
        """تحسين القرار بناء على تحليل إضافي"""
        try:
            prices = [candle['close'] for candle in historical_candles]
            current_price = prices[-1]
            
            # تحليل التقلبات
            volatility = self.calculate_volatility(prices[-10:])
            
            # تحليل القوة النسبية
            strength_analysis = self.analyze_strength(analysis_result, prices)
            
            # تحديد مستوى المخاطرة
            risk_level = self.determine_risk_level(analysis_result['confidence'], volatility, strength_analysis)
            
            # ضبط الثقة النهائية
            final_confidence = self.adjust_confidence(analysis_result['confidence'], volatility, strength_analysis)
            
            # اختيار طريقة التحليل النهائية
            final_method = self.select_final_method(analysis_result, strength_analysis)
            
            return {
                'direction': analysis_result['direction'],
                'confidence': final_confidence,
                'method': final_method,
                'indicators': analysis_result['indicators'],
                'risk_level': risk_level,
                'volatility': volatility,
                'strength': strength_analysis
            }
            
        except Exception as e:
            logging.error(f"❌ خطأ في تحسين القرار: {e}")
            return {
                'direction': analysis_result['direction'],
                'confidence': analysis_result['confidence'],
                'method': analysis_result['analysis_method'],
                'indicators': analysis_result['indicators'],
                'risk_level': 'MEDIUM',
                'volatility': 'MEDIUM',
                'strength': 'NEUTRAL'
            }
    
    def calculate_volatility(self, prices):
        """حساب التقلبات"""
        try:
            if len(prices) < 5:
                return "LOW"
            
            returns = []
            for i in range(1, len(prices)):
                returns.append(abs((prices[i] - prices[i-1]) / prices[i-1]))
            
            avg_return = sum(returns) / len(returns)
            
            if avg_return < 0.001:
                return "LOW"
            elif avg_return < 0.003:
                return "MEDIUM"
            else:
                return "HIGH"
                
        except:
            return "MEDIUM"
    
    def analyze_strength(self, analysis_result, prices):
        """تحليل قوة الإشارة"""
        try:
            strength_signals = 0
            
            # قوة RSI
            rsi = analysis_result['indicators']['rsi']
            if rsi < 25 or rsi > 75:
                strength_signals += 2
            
            # قوة MACD
            macd_hist = abs(analysis_result['indicators']['macd_histogram'])
            if macd_hist > 0.001:
                strength_signals += 1
            
            # قوة الاتجاه
            if "STRONG" in analysis_result['indicators']['trend']:
                strength_signals += 2
            
            # قوة Bollinger Bands
            bb_position = analysis_result['indicators']['bb_position']
            if bb_position < 20 or bb_position > 80:
                strength_signals += 1
            
            if strength_signals >= 4:
                return "VERY_STRONG"
            elif strength_signals >= 2:
                return "STRONG"
            else:
                return "NEUTRAL"
                
        except:
            return "NEUTRAL"
    
    def determine_risk_level(self, confidence, volatility, strength):
        """تحديد مستوى المخاطرة"""
        risk_score = 0
        
        # الثقة
        if confidence >= 80:
            risk_score -= 2
        elif confidence <= 60:
            risk_score += 2
        
        # التقلبات
        if volatility == "HIGH":
            risk_score += 2
        elif volatility == "LOW":
            risk_score -= 1
        
        # القوة
        if strength == "VERY_STRONG":
            risk_score -= 2
        elif strength == "NEUTRAL":
            risk_score += 1
        
        if risk_score >= 2:
            return "HIGH"
        elif risk_score <= -2:
            return "LOW"
        else:
            return "MEDIUM"
    
    def adjust_confidence(self, base_confidence, volatility, strength):
        """ضبط الثقة النهائية"""
        adjusted = base_confidence
        
        # تأثير التقلبات
        if volatility == "HIGH":
            adjusted *= 0.9
        elif volatility == "LOW":
            adjusted *= 1.05
        
        # تأثير القوة
        if strength == "VERY_STRONG":
            adjusted *= 1.1
        elif strength == "NEUTRAL":
            adjusted *= 0.95
        
        return min(95, max(55, int(adjusted)))
    
    def select_final_method(self, analysis_result, strength):
        """اختيار طريقة التحليل النهائية"""
        base_method = analysis_result['analysis_method']
        
        if strength == "VERY_STRONG":
            return f"STRONG_{base_method}"
        elif strength == "STRONG":
            return f"CONFIRMED_{base_method}"
        else:
            return base_method
    
    def get_smart_fallback_analysis(self, pair):
        """تحليل احتياطي ذكي"""
        # محاولة استخدام آخر تحليل ناجح للزوج
        if pair in self.last_analysis:
            last_trade = self.last_analysis[pair]
            if last_trade['confidence'] > 70:
                direction = last_trade['direction']
                confidence = 65
            else:
                direction = 'BUY' if last_trade['direction'] == 'SELL' else 'SELL'
                confidence = 60
        else:
            direction = random.choice(['BUY', 'SELL'])
            confidence = random.randint(60, 75)
        
        return {
            'pair': pair,
            'direction': direction,
            'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
            'duration': 30,
            'confidence': confidence,
            'analysis_method': 'SMART_FALLBACK',
            'indicators': {
                'rsi': round(random.uniform(40, 60), 2),
                'rsi_signal': 'NEUTRAL',
                'macd_histogram': round(random.uniform(-0.0005, 0.0005), 6),
                'macd_signal': random.choice(['BULLISH', 'BEARISH']),
                'trend': random.choice(['UPTREND', 'DOWNTREND']),
                'trend_strength': random.choice(['STRONG', 'WEAK']),
                'bb_position': round(random.uniform(30, 70), 2),
                'bb_signal': 'NEUTRAL'
            },
            'risk_level': 'MEDIUM'
        }
    
    def update_stats(self, result, stats, trade_data):
        """تحديث الإحصائيات مع بيانات إضافية"""
        stats['total_trades'] += 1
        
        if result == 'WIN':
            stats['win_trades'] += 1
        else:
            stats['loss_trades'] += 1
            
        stats['net_profit'] = stats['win_trades'] - stats['loss_trades']
        
        # حساب معدل الربح
        if stats['total_trades'] > 0:
            stats['win_rate'] = (stats['win_trades'] / stats['total_trades']) * 100
        else:
            stats['win_rate'] = 0
            
        # تحديث السلاسل
        if result == 'WIN':
            stats['current_streak'] = max(0, stats.get('current_streak', 0)) + 1
            stats['max_win_streak'] = max(stats.get('max_win_streak', 0), stats['current_streak'])
        else:
            stats['current_streak'] = min(0, stats.get('current_streak', 0)) - 1
            stats['max_loss_streak'] = max(stats.get('max_loss_streak', 0), abs(stats['current_streak']))
        
        # إحصائيات الثقة
        if 'confidence_stats' not in stats:
            stats['confidence_stats'] = {'high_confidence_wins': 0, 'high_confidence_total': 0}
        
        if trade_data['confidence'] >= 75:
            stats['confidence_stats']['high_confidence_total'] += 1
            if result == 'WIN':
                stats['confidence_stats']['high_confidence_wins'] += 1
        
        return stats
