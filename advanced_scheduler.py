import time
import logging
from datetime import datetime, timedelta
from config import UTC3_TZ, TRADING_PAIRS
import random

class AdvancedScheduler:
    def __init__(self):
        from qx_broker import QXBrokerManager
        from telegram_bot import TelegramBot
        from candle_analyzer import CandleAnalyzer
        from technical_analyzer import TechnicalAnalyzer
        from trading_engine import TradingEngine
        
        self.qx_manager = QXBrokerManager()
        self.telegram_bot = TelegramBot()
        self.candle_analyzer = CandleAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        self.trading_engine = TradingEngine(self.candle_analyzer, self.technical_analyzer)
        
        # إحصائيات متقدمة
        self.stats = {
            'total_trades': 0,
            'win_trades': 0,
            'loss_trades': 0,
            'net_profit': 0,
            'win_rate': 0,
            'current_streak': 0,
            'max_win_streak': 0,
            'max_loss_streak': 0,
            'session_start': datetime.now(UTC3_TZ),
            'last_trade_time': None,
            'skipped_trades': 0,
            'total_analyzed': 0
        }
        
        self.next_signal_time = None
        self.next_trade_time = None
        self.trade_in_progress = False
        self.current_trade_data = None
        self.pending_trade = None
        
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ)
    
    def calculate_next_signal_time(self):
        """حساب وقت الإشارة التالية (كل دقيقة في الثانية 00)"""
        now = self.get_utc3_time()
        next_signal = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        return next_signal
    
    def calculate_trade_execution_time(self, signal_time):
        """حساب وقت تنفيذ الصفقة (بعد الإشارة بدقيقة)"""
        return signal_time + timedelta(minutes=1)
    
    def calculate_result_time(self, trade_time):
        """حساب وقت نشر النتيجة (بعد التنفيذ بـ 35 ثانية)"""
        return trade_time + timedelta(seconds=35)
    
    def start_trading_system(self):
        """بدء نظام التداول بالتوقيت المحدد"""
        logging.info("🚀 بدء نظام التداول بالتوقيت المحدد...")
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        welcome_message = f"""
🎯 <b>بدء تشغيل النظام بالتوقيت المحدد</b>

⏰ <b>نظام التوقيت:</b>
• 6:00:00 → نشر إشارة الصفقة
• 6:01:00 → دخول الصفقة
• 6:01:35 → نشر النتيجة
• 6:02:00 → الإشارة التالية

📊 <b>مميزات النظام:</b>
• توقيت دقيق بالثانية
• تحليل فني متقدم
• نتائج دقيقة بالشموع
• نشر رسائل التخطي

🕒 <b>الوقت الحالي:</b> {current_time} (UTC+3)

⚡ <b>جاري التحضير للإشارة الأولى...</b>
"""
        self.telegram_bot.send_message(welcome_message)
        
        # بدء أول إشارة
        self.next_signal_time = self.calculate_next_signal_time()
        time_until_signal = (self.next_signal_time - self.get_utc3_time()).total_seconds()
        
        logging.info(f"⏰ أول إشارة: {self.next_signal_time.strftime('%H:%M:%S')} (بعد {time_until_signal:.0f} ثانية)")
    
    def execute_signal_cycle(self):
        """دورة الإشارة (نشر إشارة الصفقة)"""
        try:
            # 1. التحليل الفني واتخاذ القرار
            trade_data = self.trading_engine.analyze_and_decide()
            self.stats['total_analyzed'] += 1
            
            # 2. التحقق من الثقة
            if trade_data['confidence'] < 65:  # إذا الثقة أقل من 65%
                self.send_skip_message(trade_data)
                self.stats['skipped_trades'] += 1
                logging.info(f"⏭️ تم تخطي صفقة {trade_data['pair']} - ثقة منخفضة: {trade_data['confidence']}%")
                return None
            
            # 3. تخزين بيانات الصفقة المعلقة
            self.pending_trade = {
                'data': trade_data,
                'signal_time': self.get_utc3_time(),
                'trade_time': self.calculate_trade_execution_time(self.get_utc3_time()),
                'result_time': self.calculate_result_time(self.calculate_trade_execution_time(self.get_utc3_time()))
            }
            
           def send_trade_signal(self, trade_data):
    """إرسال إشارة الصفقة مع معلومات التحليل المتقدم"""
    current_time = self.get_utc3_time().strftime("%H:%M:%S")
    trade_time = (self.get_utc3_time() + timedelta(minutes=1)).strftime("%H:%M:%S")
    
    # معلومات البنوشرات
    news_info = ""
    if trade_data['news_impact']['events_count'] > 0:
        news_info = f"• البنوشرات: {trade_data['news_impact']['direction']} ({trade_data['news_impact']['events_count']} حدث)"
    else:
        news_info = "• البنوشرات: لا توجد أحداث هامة"
    
    # معلومات الزخم
    sentiment_info = f"• زخم السوق: {trade_data['market_sentiment']['overall_direction']} ({trade_data['market_sentiment']['confidence']}%)"
    
    signal_message = f"""
📊 <b>إشارة تداول متقدمة</b>

💰 <b>الزوج:</b> {trade_data['pair']}
🎯 <b>الاتجاه:</b> {trade_data['direction']}
⏱ <b>المدة:</b> 30 ثانية

📈 <b>التحليل المتقدم:</b>
• الثقة: {trade_data['confidence']}%
• الطريقة: {trade_data['analysis_method']}
{news_info}
{sentiment_info}
• RSI: {trade_data['indicators']['rsi']} ({trade_data['indicators']['rsi_signal']})
• MACD: {trade_data['indicators']['macd_signal']}

🕒 <b>مواعيد الصفقة:</b>
• وقت الإشارة: {current_time}
• وقت الدخول: {trade_time} 🎯
• وقت النتيجة: {(self.get_utc3_time() + timedelta(minutes=1, seconds=35)).strftime('%H:%M:%S')}

⚡ <b>جاري التحضير لدخول الصفقة...</b>
"""
    self.telegram_bot.send_message(signal_message)
    
    def send_skip_message(self, trade_data):
        """إرسال رسالة تخطي الصفقة"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        skip_message = f"""
⏭️ <b>تم تخطي الصفقة</b>

💰 <b>الزوج:</b> {trade_data['pair']}
🎯 <b>الاتجاه المحتمل:</b> {trade_data['direction']}
📉 <b>نسبة الثقة:</b> {trade_data['confidence']}%

❌ <b>سبب التخطي:</b>
نسبة نجاح الصفقة منخفضة وغير مضمونة

🕒 <b>الوقت:</b> {current_time} (UTC+3)

⚡ <b>جاري البحث عن صفقة أفضل...</b>
"""
        self.telegram_bot.send_message(skip_message)
    
    def execute_trade_cycle(self):
        """دورة تنفيذ الصفقة"""
        if not self.pending_trade or self.trade_in_progress:
            return
            
        try:
            self.trade_in_progress = True
            trade_data = self.pending_trade['data']
            
            logging.info(f"🎯 بدء تنفيذ الصفقة: {trade_data['pair']} - {trade_data['direction']}")
            
            # تنفيذ الصفقة (وهمي)
            success = self.qx_manager.execute_trade(
                trade_data['pair'],
                trade_data['direction'],
                30
            )
            
            if success:
                logging.info(f"✅ تم تنفيذ الصفقة: {trade_data['pair']}")
                
                # انتظار 30 ثانية للشمعة
                time.sleep(30)
                
                # الحصول على بيانات الشمعة
                candle_data = self.candle_analyzer.get_candle_data(
                    trade_data['pair'], 
                    self.get_utc3_time()
                )
                
                # تحديد النتيجة
                result = self.candle_analyzer.determine_trade_result(
                    candle_data, 
                    trade_data['direction'],
                    candle_data['open']
                )
                
                # تحديث الإحصائيات
                self.update_stats(result, trade_data)
                
                # إرسال النتيجة
                self.send_trade_result(result, trade_data, candle_data)
                
                logging.info(f"🎯 اكتملت الصفقة: {trade_data['pair']} - {result}")
                
            else:
                logging.error(f"❌ فشل تنفيذ الصفقة: {trade_data['pair']}")
                
        except Exception as e:
            logging.error(f"❌ خطأ في دورة التنفيذ: {e}")
        finally:
            self.trade_in_progress = False
            self.pending_trade = None
            self.stats['last_trade_time'] = self.get_utc3_time()
    
    def send_trade_result(self, result, trade_data, candle_data):
        """إرسال نتيجة الصفقة"""
        result_emoji = "🎉" if result == 'WIN' else "❌"
        result_text = "WIN 🎉" if result == 'WIN' else "LOSS ❌"
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        price_change = candle_data['close'] - candle_data['open']
        change_percent = (price_change / candle_data['open']) * 100
        
        result_message = f"""
🎯 <b>نتيجة الصفقة</b> {result_emoji}

💰 <b>الزوج:</b> {trade_data['pair']}
📊 <b>النتيجة:</b> {result_text}
📈 <b>الاتجاه:</b> {trade_data['direction']}

💹 <b>حركة السعر:</b>
• السعر الافتتاح: {candle_data['open']}
• السعر الإغلاق: {candle_data['close']}
• التغير: {price_change:+.6f} ({change_percent:+.3f}%)

🕒 <b>الوقت:</b> {current_time} (UTC+3)

📊 <b>إحصائيات الجلسة:</b>
• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• الصفقات المتخطاة: {self.stats['skipped_trades']}

⚡ <b>جاري التحضير للإشارة القادمة...</b>
"""
        self.telegram_bot.send_message(result_message)
    
    def update_stats(self, result, trade_data):
        """تحديث الإحصائيات"""
        self.stats['total_trades'] += 1
        
        if result == 'WIN':
            self.stats['win_trades'] += 1
            self.stats['current_streak'] = max(0, self.stats.get('current_streak', 0)) + 1
            self.stats['max_win_streak'] = max(self.stats.get('max_win_streak', 0), self.stats['current_streak'])
        else:
            self.stats['loss_trades'] += 1
            self.stats['current_streak'] = min(0, self.stats.get('current_streak', 0)) - 1
            self.stats['max_loss_streak'] = max(self.stats.get('max_loss_streak', 0), abs(self.stats['current_streak']))
        
        self.stats['net_profit'] = self.stats['win_trades'] - self.stats['loss_trades']
        
        if self.stats['total_trades'] > 0:
            self.stats['win_rate'] = (self.stats['win_trades'] / self.stats['total_trades']) * 100
        else:
            self.stats['win_rate'] = 0
    
    def run_precision_scheduler(self):
        """تشغيل الجدولة الدقيقة"""
        try:
            self.start_trading_system()
            
            logging.info("✅ بدء تشغيل الجدولة الدقيقة...")
            
            # الحلقة الرئيسية
            while True:
                current_time = self.get_utc3_time()
                
                # التحقق إذا حان وقت الإشارة
                if (self.next_signal_time and 
                    current_time >= self.next_signal_time and 
                    not self.trade_in_progress and 
                    not self.pending_trade):
                    
                    logging.info(f"⏰ بدء دورة الإشارة: {current_time.strftime('%H:%M:%S')}")
                    pending_trade = self.execute_signal_cycle()
                    
                    if pending_trade:
                        # جدولة التنفيذ بعد دقيقة
                        self.next_trade_time = pending_trade['trade_time']
                        logging.info(f"⏰ تم جدولة التنفيذ: {self.next_trade_time.strftime('%H:%M:%S')}")
                    
                    # حساب وقت الإشارة التالية
                    self.next_signal_time = self.calculate_next_signal_time()
                    logging.info(f"⏰ الإشارة القادمة: {self.next_signal_time.strftime('%H:%M:%S')}")
                
                # التحقق إذا حان وقت التنفيذ
                if (self.pending_trade and 
                    self.next_trade_time and 
                    current_time >= self.next_trade_time and 
                    not self.trade_in_progress):
                    
                    logging.info(f"🎯 بدء دورة التنفيذ: {current_time.strftime('%H:%M:%S')}")
                    self.execute_trade_cycle()
                    self.next_trade_time = None
                
                # انتظار 1 ثانية قبل التكرار
                time.sleep(1)
                    
        except Exception as e:
            logging.error(f"❌ خطأ فادح في التشغيل: {e}")
            logging.info("🔄 إعادة التشغيل بعد 10 ثواني...")
            time.sleep(10)
            self.run_precision_scheduler()
