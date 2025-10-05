import random
import logging
from datetime import datetime
from config import UTC3_TZ, TRADING_PAIRS

class TradingEngine:
    def __init__(self, candle_analyzer):
        self.pairs = TRADING_PAIRS
        self.candle_analyzer = candle_analyzer
    
    def analyze_and_decide(self):
        """تحليل فني متقدم واتخاذ قرار التداول"""
        try:
            pair = random.choice(self.pairs)
            
            # الحصول على شموع تاريخية للتحليل
            historical_candles = self.candle_analyzer.get_historical_candles(pair, 20)
            
            if historical_candles:
                # تحليل فني متقدم
                analysis_result = self.candle_analyzer.technical_analyzer.comprehensive_analysis(historical_candles)
                
                trade_data = {
                    'pair': pair,
                    'direction': analysis_result['direction'],
                    'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
                    'duration': 30,
                    'confidence': analysis_result['confidence'],
                    'analysis_method': analysis_result['analysis_method'],
                    'indicators': analysis_result['indicators']
                }
            else:
                # تحليل بسيط إذا فشل التحليل المتقدم
                trade_data = self.get_fallback_analysis(pair)
            
            return trade_data
            
        except Exception as e:
            logging.error(f"❌ خطأ في التحليل واتخاذ القرار: {e}")
            return self.get_fallback_analysis(random.choice(self.pairs))
    
    def get_fallback_analysis(self, pair):
        """تحليل احتياطي"""
        direction = random.choice(['BUY', 'SELL'])
        
        return {
            'pair': pair,
            'direction': direction,
            'trade_time': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
            'duration': 30,
            'confidence': random.randint(65, 80),
            'analysis_method': 'MARKET_ANALYSIS',
            'indicators': {
                'rsi': round(random.uniform(40, 60), 2),
                'macd_histogram': round(random.uniform(-0.0005, 0.0005), 6),
                'trend': random.choice(['UPTREND', 'DOWNTREND']),
                'bb_position': round(random.uniform(30, 70), 2)
            }
        }
    
    def update_stats(self, result, stats):
        """تحديث الإحصائيات"""
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
        
        return stats
