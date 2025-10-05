import time
import logging
from datetime import datetime, timedelta
from config import UTC3_TZ, TRADING_PAIRS, TRADE_INTERVAL
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
            'total_profit': 0,
            'accuracy_rate': 0,
            'best_pair': '',
            'worst_pair': '',
            'trades_per_hour': 0,
            'hourly_target': 60  # 60 صفقة في الساعة
        }
        
        # تتبع الأداء لكل زوج
        self.pair_performance = {pair: {'wins': 0, 'losses': 0, 'total': 0} for pair in TRADING_PAIRS}
        
        self.next_trade_time = None
        self.trade_in_progress = False
        self.current_trade_data = None
        self.market_status = "ACTIVE"
        self.trades_this_hour = 0
        self.hour_start_time = datetime.now(UTC3_TZ)
        
        # إعدادات متقدمة
        self.trade_settings = {
            'max_trades_per_hour': 60,  # 60 صفقة في الساعة
            'min_confidence': 60,       # ثقة أقل علشان كثر الصفقات
            'risk_reward_ratio': 1.2,
            'adaptive_trading': True
        }
        
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ)
    
    def calculate_next_trade_time(self):
        """حساب وقت الصفقة التالية كل دقيقة"""
        now = self.get_utc3_time()
        
        # الصفقات كل دقيقة (0, 1, 2, 3, ...)
        next_trade = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
        
        # إذا كان الوقت الحالي بعد الوقت المستهدف، نضيف دقيقة
        if next_trade <= now:
            next_trade += timedelta(minutes=1)
            
        return next_trade
    
    def check_hourly_limit(self):
        """التحقق من الحد الأقصى للصفقات في الساعة"""
        current_time = self.get_utc3_time()
        hour_diff = (current_time - self.hour_start_time).total_seconds() / 3600
        
        if hour_diff >= 1:
            # إعادة تعيين العد كل ساعة
            self.trades_this_hour = 0
            self.hour_start_time = current_time
            logging.info("🔄 إعادة تعيين عداد الصفقات للساعة الجديدة")
        
        return self.trades_this_hour < self.trade_settings['max_trades_per_hour']
    
    def get_market_session(self):
        """تحديد جلسة السوق الحالية"""
        current_hour = self.get_utc3_time().hour
        
        if 0 <= current_hour < 4:    # جلسة آسيا
            return "ASIAN_SESSION"
        elif 4 <= current_hour < 9:  # بين الجلسات
            return "TRANSITION_SESSION" 
        elif 9 <= current_hour < 13: # جلسة أوروبا
            return "EUROPEAN_SESSION"
        elif 13 <= current_hour < 17: # تداخل أوروبا وأمريكا
            return "OVERLAP_SESSION"
        elif 17 <= current_hour < 21: # جلسة أمريكا
            return "AMERICAN_SESSION"
        else:                         # جلسة مسائية
            return "EVENING_SESSION"
    
    def adjust_confidence_by_session(self, base_confidence, pair):
        """ضبط الثقة بناء على جلسة السوق والزوج"""
        session = self.get_market_session()
        session_multipliers = {
            "ASIAN_SESSION": 0.85,     # تقلبات منخفضة - ثقة أقل
            "TRANSITION_SESSION": 0.9,  # انتقالية
            "EUROPEAN_SESSION": 1.05,   # تقلبات عالية
            "OVERLAP_SESSION": 1.1,     # أعلى تقلبات
            "AMERICAN_SESSION": 1.05,   # تقلبات عالية
            "EVENING_SESSION": 0.95     # متوسطة
        }
        
        adjusted_confidence = base_confidence * session_multipliers.get(session, 1.0)
        
        # ضبط إضافي بناء على أداء الزوج
        pair_perf = self.pair_performance.get(pair, {'wins': 0, 'losses': 0, 'total': 0})
        if pair_perf['total'] > 3:
            win_rate = pair_perf['wins'] / pair_perf['total']
            if win_rate > 0.6:
                adjusted_confidence *= 1.05
            elif win_rate < 0.4:
                adjusted_confidence *= 0.95
        
        return min(95, adjusted_confidence)
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة بنظام متقدم"""
        logging.info("🚀 بدء التداول 24 ساعة بنظام الدقيقة الواحدة...")
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        session = self.get_market_session()
        
        welcome_message = f"""
🎯 <b>بدء تشغيل البوت السريع بنجاح!</b>

📊 <b>نظام التداول السريع</b>
• صفقة كل دقيقة ⚡
• تحليل فني متكامل
• نتائج فورية بالشموع
• إحصائيات لحظية

🕒 <b>الوقت الحالي:</b> {current_time} (UTC+3)
🌐 <b>جلسة التداول:</b> {session}
📈 <b>الأزواج:</b> {len(TRADING_PAIRS)} زوج
⚡ <b>الوتيرة:</b> 60 صفقة/ساعة

🎯 <b>مميزات النظام:</b>
• تحليل RSI + MACD + Bollinger Bands
• تحديد نتائج دقيقة بالشموع
• تقارير أداء فورية
• تكيف مع جلسات السوق

🚀 <i>استعد لتحليلات سريعة ودقيقة!</i>
"""
        self.telegram_bot.send_message(welcome_message)
        
        self.next_trade_time = self.calculate_next_trade_time()
        time_until_next = (self.next_trade_time - self.get_utc3_time()).total_seconds()
        
        logging.info(f"⏰ أول صفقة: {self.next_trade_time.strftime('%H:%M:%S')} (بعد {time_until_next:.0f} ثانية)")
        logging.info(f"🌐 جلسة السوق: {session}")
        logging.info(f"🎯 الوتيرة: صفقة كل دقيقة")
    
    def execute_trade_cycle(self):
        """دورة الصفقة السريعة"""
        if self.trade_in_progress:
            return
            
        try:
            self.trade_in_progress = True
            trade_start_time = self.get_utc3_time()
            
            # التحقق من الحد الأقصى للصفقات في الساعة
            if not self.check_hourly_limit():
                logging.info("⏸️ تم الوصول للحد الأقصى للصفقات هذه الساعة")
                self.trade_in_progress = False
                return
            
            # 1. التحليل الفني واتخاذ القرار
            trade_data = self.trading_engine.analyze_and_decide()
            
            # 2. ضبط الثقة بناء على جلسة السوق
            adjusted_confidence = self.adjust_confidence_by_session(
                trade_data['confidence'], 
                trade_data['pair']
            )
            trade_data['confidence'] = adjusted_confidence
            
            # 3. التحقق من الحد الأدنى للثقة
            if trade_data['confidence'] < self.trade_settings['min_confidence']:
                logging.info(f"⚠️ تخطي صفقة {trade_data['pair']} - ثقة منخفضة: {trade_data['confidence']}%")
                self.trade_in_progress = False
                return
            
            # 4. تخزين بيانات الصفقة الحالية
            self.current_trade_data = {
                'data': trade_data,
                'start_time': trade_start_time,
                'entry_price': None
            }
            
            # 5. زيادة عداد الصفقات هذه الساعة
            self.trades_this_hour += 1
            self.stats['trades_per_hour'] = self.trades_this_hour
            
            # 6. إرسال إشارة الصفقة السريعة
            self.send_quick_trade_signal(trade_data, trade_start_time)
            
            logging.info(f"📤 إشارة صفقة سريعة: {trade_data['pair']} - {trade_data['direction']}")
            logging.info(f"📊 الثقة: {trade_data['confidence']}% - الصفقات هذه الساعة: {self.trades_this_hour}")
            
            # 7. انتظار إغلاق الشمعة (30 ثانية)
            time.sleep(30)
            
            # 8. الحصول على بيانات الشمعة بعد الإغلاق
            candle_data = self.candle_analyzer.get_candle_data(
                trade_data['pair'], 
                trade_start_time
            )
            
            # 9. تحديد نتيجة الصفقة بدقة
            result = self.candle_analyzer.determine_trade_result(
                candle_data, 
                trade_data['direction'],
                candle_data['open']
            )
            
            # 10. تحديث الإحصائيات
            self.update_advanced_stats(result, trade_data, candle_data)
            
            # 11. إرسال النتيجة السريعة
            self.send_quick_trade_result(result, trade_data, candle_data)
            
            logging.info(f"🎯 دورة الصفقة اكتملت: {trade_data['pair']} - {result}")
            
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة السريعة: {e}")
        finally:
            self.trade_in_progress = False
            self.current_trade_data = None
            self.stats['last_trade_time'] = self.get_utc3_time()
    
    def send_quick_trade_signal(self, trade_data, trade_time):
        """إرسال إشارة صفقة سريعة"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        signal_message = f"""
⚡ <b>إشارة تداول سريعة</b>

💰 <b>الزوج:</b> {trade_data['pair']}
🎯 <b>الاتجاه:</b> {trade_data['direction']}
⏱ <b>المدة:</b> 30 ثانية

📈 <b>التحليل المختصر:</b>
• الثقة: {trade_data['confidence']}%
• RSI: {trade_data['indicators']['rsi']}
• MACD: {trade_data['indicators']['macd_signal']}
• الاتجاه: {trade_data['indicators']['trend']}

🕒 <b>الوقت:</b> {current_time} (UTC+3)
🔢 <b>الصفقات هذه الساعة:</b> {self.trades_this_hour}/60

⚡ <b>نتيجة الصفقة بعد 30 ثانية...</b>
"""
        self.telegram_bot.send_message(signal_message)
    
    def send_quick_trade_result(self, result, trade_data, candle_data):
        """إرسال نتيجة صفقة سريعة"""
        result_emoji = "🎉" if result == 'WIN' else "❌"
        result_text = "WIN 🎉" if result == 'WIN' else "LOSS ❌"
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        result_message = f"""
🎯 <b>نتيجة الصفقة</b> {result_emoji}

💰 <b>الزوج:</b> {trade_data['pair']}
📊 <b>النتيجة:</b> {result_text}
📈 <b>السعر:</b> {candle_data['open']} → {candle_data['close']}
🕒 <b>الوقت:</b> {current_time}

📊 <b>الإحصائيات السريعة:</b>
• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• معدل الربح: {self.stats['win_rate']:.1f}%

⚡ <b>الصفقة القادمة خلال 30 ثانية...</b>
"""
        self.telegram_bot.send_message(result_message)
    
    def update_advanced_stats(self, result, trade_data, candle_data):
        """تحديث الإحصائيات المتقدمة"""
        pair = trade_data['pair']
        
        # تحديث الإحصائيات الأساسية
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
        
        # حساب معدل الربح
        if self.stats['total_trades'] > 0:
            self.stats['win_rate'] = (self.stats['win_trades'] / self.stats['total_trades']) * 100
        
        # تحديث أداء الزوج
        if pair in self.pair_performance:
            if result == 'WIN':
                self.pair_performance[pair]['wins'] += 1
            else:
                self.pair_performance[pair]['losses'] += 1
            self.pair_performance[pair]['total'] += 1
        
        # تحديث أفضل/أسوأ زوج كل 10 صفقات
        if self.stats['total_trades'] % 10 == 0:
            self.update_best_worst_pairs()
    
    def update_best_worst_pairs(self):
        """تحديث أفضل وأسوأ أزواج"""
        best_win_rate = 0
        worst_win_rate = 100
        best_pair = ''
        worst_pair = ''
        
        for pair, perf in self.pair_performance.items():
            if perf['total'] >= 3:
                win_rate = (perf['wins'] / perf['total']) * 100
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_pair = pair
                if win_rate < worst_win_rate:
                    worst_win_rate = win_rate
                    worst_pair = pair
        
        self.stats['best_pair'] = best_pair
        self.stats['worst_pair'] = worst_pair
    
    def send_hourly_report(self):
        """إرسال تقرير ساعي"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        report_message = f"""
📊 <b>تقرير أداء ساعي</b> ⏰

🔥 <b>الأداء هذه الساعة:</b>
• الصفقات المنفذة: {self.trades_this_hour}/60
• معدل التنفيذ: {(self.trades_this_hour/60)*100:.1f}%
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• معدل الربح: {self.stats['win_rate']:.1f}%

🎯 <b>الإحصائيات الكلية:</b>
• إجمالي الصفقات: {self.stats['total_trades']}
• صافي الربح: {self.stats['net_profit']}
• أقوى سلسلة: {self.stats['max_win_streak']} ربح

🕒 <b>الوقت:</b> {current_time} (UTC+3)

⚡ <b>جاري الاستعداد للساعة القادمة...</b>
"""
        self.telegram_bot.send_message(report_message)
    
    def keep_system_alive(self):
        """الحفاظ على نشاط النظام"""
        try:
            current_time = self.get_utc3_time()
            
            # إرسال تقرير ساعي
            hour_diff = (current_time - self.hour_start_time).total_seconds() / 3600
            if hour_diff >= 1 and self.trades_this_hour > 0:
                self.send_hourly_report()
                self.trades_this_hour = 0
                self.hour_start_time = current_time
            
            # تحديث حالة السوق
            session = self.get_market_session()
            if hasattr(self, 'last_session'):
                if self.last_session != session:
                    logging.info(f"🌐 تغيير جلسة السوق: {self.last_session} → {session}")
                    self.telegram_bot.send_message(f"🌐 <b>تغيير جلسة التداول</b>\n\n{self.last_session} → {session}")
                    self.last_session = session
            else:
                self.last_session = session
                
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على نشاط النظام: {e}")
    
    def run_advanced_scheduler(self):
        """تشغيل الجدولة المتقدمة"""
        try:
            self.start_24h_trading()
            
            logging.info("✅ بدء تشغيل الجدولة السريعة...")
            
            # الحلقة الرئيسية السريعة
            while True:
                current_time = self.get_utc3_time()
                
                # التحقق إذا حان وقت الصفقة
                if (self.next_trade_time and 
                    current_time >= self.next_trade_time and 
                    not self.trade_in_progress):
                    
                    logging.info(f"⏰ بدء صفقة جديدة: {current_time.strftime('%H:%M:%S')}")
                    self.execute_trade_cycle()
                    
                    # حساب الوقت التالي (دقيقة واحدة)
                    self.next_trade_time = self.calculate_next_trade_time()
                    time_until_next = (self.next_trade_time - current_time).total_seconds()
                    
                    logging.info(f"⏰ الصفقة القادمة: {self.next_trade_time.strftime('%H:%M:%S')} (بعد {time_until_next:.0f} ثانية)")
                
                # الحفاظ على نشاط النظام
                self.keep_system_alive()
                
                # انتظار 1 ثانية فقط علشان السرعه
                time.sleep(1)
                    
        except Exception as e:
            logging.error(f"❌ خطأ فادح في التشغيل: {e}")
            logging.info("🔄 إعادة التشغيل بعد 10 ثواني...")
            time.sleep(10)
            self.run_advanced_scheduler()
