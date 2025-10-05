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
            'total_profit': 0,
            'accuracy_rate': 0,
            'best_pair': '',
            'worst_pair': ''
        }
        
        # تتبع الأداء لكل زوج
        self.pair_performance = {pair: {'wins': 0, 'losses': 0, 'total': 0} for pair in TRADING_PAIRS}
        
        self.next_trade_time = None
        self.trade_in_progress = False
        self.current_trade_data = None
        self.market_status = "ACTIVE"
        
        # إعدادات متقدمة
        self.trade_settings = {
            'max_trades_per_hour': 20,
            'min_confidence': 65,
            'risk_reward_ratio': 1.5,
            'adaptive_trading': True
        }
        
    def get_utc3_time(self):
        """الحصول على وقت UTC+3"""
        return datetime.now(UTC3_TZ)
    
    def calculate_next_trade_time(self):
        """حساب وقت الصفقة التالية بدقة"""
        now = self.get_utc3_time()
        
        # الصفقات كل 3 دقائق (0, 3, 6, 9, ...)
        next_minute = ((now.minute // 3) + 1) * 3
        
        if next_minute >= 60:
            next_minute = 0
            next_hour = now.hour + 1
            if next_hour >= 24:
                next_hour = 0
        else:
            next_hour = now.hour
            
        next_trade = now.replace(
            hour=next_hour, 
            minute=next_minute, 
            second=0, 
            microsecond=0
        )
        
        # إذا كان الوقت الحالي بعد الوقت المستهدف، نضيف 3 دقائق
        if next_trade <= now:
            next_trade += timedelta(minutes=3)
            
        return next_trade
    
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
            "ASIAN_SESSION": 0.9,      # تقلبات منخفضة
            "TRANSITION_SESSION": 0.95, # انتقالية
            "EUROPEAN_SESSION": 1.1,    # تقلبات عالية
            "OVERLAP_SESSION": 1.2,     # أعلى تقلبات
            "AMERICAN_SESSION": 1.15,   # تقلبات عالية
            "EVENING_SESSION": 1.0      # متوسطة
        }
        
        adjusted_confidence = base_confidence * session_multipliers.get(session, 1.0)
        
        # ضبط إضافي بناء على أداء الزوج
        pair_perf = self.pair_performance.get(pair, {'wins': 0, 'losses': 0, 'total': 0})
        if pair_perf['total'] > 5:
            win_rate = pair_perf['wins'] / pair_perf['total']
            if win_rate > 0.7:
                adjusted_confidence *= 1.1
            elif win_rate < 0.3:
                adjusted_confidence *= 0.9
        
        return min(95, adjusted_confidence)
    
    def start_24h_trading(self):
        """بدء التداول 24 ساعة بنظام متقدم"""
        logging.info("🚀 بدء التداول 24 ساعة بنظام متقدم...")
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        session = self.get_market_session()
        
        welcome_message = f"""
🎯 <b>بدء تشغيل البوت المتقدم بنجاح!</b>

📊 <b>نظام التداول المتقدم</b>
• تحليل فني متكامل
• تحليل زمني
• مؤشرات متعددة
• تحليل الشموع الحقيقي
• إدارة مخاطر ذكية

🕒 <b>الوقت الحالي:</b> {current_time} (UTC+3)
🌐 <b>جلسة التداول:</b> {session}

🚀 <i>استعد لتحليلات دقيقة ونتائج واقعية!</i>
"""
        self.telegram_bot.send_message(welcome_message)
        
        self.next_trade_time = self.calculate_next_trade_time()
        time_until_next = (self.next_trade_time - self.get_utc3_time()).total_seconds()
        
        logging.info(f"⏰ أول صفقة: {self.next_trade_time.strftime('%H:%M:%S')} (بعد {time_until_next:.0f} ثانية)")
        logging.info(f"🌐 جلسة السوق: {session}")
    
    def execute_trade_cycle(self):
        """دورة الصفقة المتقدمة"""
        if self.trade_in_progress:
            return
            
        try:
            self.trade_in_progress = True
            trade_start_time = self.get_utc3_time()
            
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
                'entry_price': None  # سيتم تحديده من الشمعة
            }
            
            # 5. إرسال إشارة الصفقة مع تفاصيل التحليل
            self.send_detailed_trade_signal(trade_data, trade_start_time)
            
            logging.info(f"📤 إشارة صفقة متقدمة: {trade_data['pair']} - {trade_data['direction']}")
            logging.info(f"📊 الثقة: {trade_data['confidence']}% - الطريقة: {trade_data['analysis_method']}")
            
            # 6. انتظار إغلاق الشمعة (30 ثانية)
            time.sleep(30)
            
            # 7. الحصول على بيانات الشمعة بعد الإغلاق
            candle_data = self.candle_analyzer.get_candle_data(
                trade_data['pair'], 
                trade_start_time
            )
            
            # 8. تحديد نتيجة الصفقة بدقة
            result = self.candle_analyzer.determine_trade_result(
                candle_data, 
                trade_data['direction'],
                candle_data['open']  # سعر الدخول هو سعر افتتاح الشمعة
            )
            
            # 9. تحديث الإحصائيات
            self.update_advanced_stats(result, trade_data, candle_data)
            
            # 10. إرسال النتيجة المفصلة
            self.send_detailed_trade_result(result, trade_data, candle_data)
            
            logging.info(f"🎯 دورة الصفقة اكتملت: {trade_data['pair']} - {result}")
            
        except Exception as e:
            logging.error(f"❌ خطأ في دورة الصفقة المتقدمة: {e}")
        finally:
            self.trade_in_progress = False
            self.current_trade_data = None
            self.stats['last_trade_time'] = self.get_utc3_time()
    
    def send_detailed_trade_signal(self, trade_data, trade_time):
        """إرسال إشارة صفقة مفصلة"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        session = self.get_market_session()
        
        # تحويل المؤشرات لنص مقروء
        indicators = trade_data['indicators']
        
        signal_message = f"""
📊 <b>إشارة تداول </b>

💰 <b>الزوج:</b> {trade_data['pair']}
🎯 <b>الاتجاه:</b> {trade_data['direction']}
⏱ <b>المدة:</b> 30 ثانية

• الجلسة: {session}
• الوقت: {current_time} (UTC+3)

"""
        self.telegram_bot.send_message(signal_message)
    
    def send_detailed_trade_result(self, result, trade_data, candle_data):
        """إرسال نتيجة صفقة مفصلة"""
        result_emoji = "🎉" if result == 'WIN' else "❌"
        result_text = "WIN 🎉" if result == 'WIN' else "LOSS ❌"
        
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        
        # تحليل السبب
        reason = self.analyze_trade_reason(result, trade_data, candle_data)
        
        result_message = f"""
🎯 <b>نتيجة الصفقة</b> {result_emoji}

💰 <b>الزوج:</b> {trade_data['pair']}
📊 <b>النتيجة:</b> {result_text}
🕒 <b>الوقت:</b> {current_time} (UTC+3)

📊 <b>إحصائيات الجلسة:</b>
• إجمالي الصفقات: {self.stats['total_trades']}
• الصفقات الرابحة: {self.stats['win_trades']}
• الصفقات الخاسرة: {self.stats['loss_trades']}
• صافي الربح: {self.stats['net_profit']}

🚀 <i>جاري تحضير الصفقة القادمة...</i>
"""
        self.telegram_bot.send_message(result_message)
    
    def analyze_trade_reason(self, result, trade_data, candle_data):
        """تحليل سبب نتيجة الصفقة"""
        open_price = candle_data['open']
        close_price = candle_data['close']
        direction = trade_data['direction']
        
        if direction == "BUY":
            if result == "WIN":
                return "• سعر الإغلاق ارتفع عن سعر الافتتاح\n• تحليل الاتجاه كان صحيحاً\n• المؤشرات دعمت قرار الشراء"
            else:
                return "• سعر الإغلاق انخفض عن سعر الافتتاح\n• تغير مفاجئ في الاتجاه\n• تقلبات سوقية غير متوقعة"
        else:  # SELL
            if result == "WIN":
                return "• سعر الإغلاق انخفض عن سعر الافتتاح\n• تحليل الاتجاه كان صحيحاً\n• المؤشرات دعمت قرار البيع"
            else:
                return "• سعر الإغلاق ارتفع عن سعر الافتتاح\n• تغير مفاجئ في الاتجاه\n• تقلبات سوقية غير متوقعة"
    
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
        
        # تحديث أفضل/أسوأ زوج
        self.update_best_worst_pairs()
    
    def update_best_worst_pairs(self):
        """تحديث أفضل وأسوأ أزواج"""
        best_win_rate = 0
        worst_win_rate = 100
        best_pair = ''
        worst_pair = ''
        
        for pair, perf in self.pair_performance.items():
            if perf['total'] >= 3:  # على الأقل 3 صفقات
                win_rate = (perf['wins'] / perf['total']) * 100
                if win_rate > best_win_rate:
                    best_win_rate = win_rate
                    best_pair = pair
                if win_rate < worst_win_rate:
                    worst_win_rate = win_rate
                    worst_pair = pair
        
        self.stats['best_pair'] = best_pair
        self.stats['worst_pair'] = worst_pair
    
    def send_performance_report(self):
        """إرسال تقرير أداء مفصل"""
        current_time = self.get_utc3_time().strftime("%H:%M:%S")
        session_duration = self.get_utc3_time() - self.stats['session_start']
        hours, remainder = divmod(session_duration.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # تحليل أفضل 3 أزواج
        top_pairs = []
        for pair, perf in self.pair_performance.items():
            if perf['total'] >= 3:
                win_rate = (perf['wins'] / perf['total']) * 100
                top_pairs.append((pair, win_rate, perf['wins'], perf['losses']))
        
        top_pairs.sort(key=lambda x: x[1], reverse=True)
        top_3_pairs = top_pairs[:3]
        
        pairs_analysis = "\n".join([
            f"• {pair}: {win_rate:.1f}% ({wins}/{wins+losses})" 
            for pair, win_rate, wins, losses in top_3_pairs
        ]) if top_3_pairs else "• لا توجد بيانات كافية"
        
        report_message = f"""
📊 <b>تقرير أداء مفصل</b>

⏰ <b>مدة الجلسة:</b> {int(hours)}h {int(minutes)}m
📈 <b>إجمالي الصفقات:</b> {self.stats['total_trades']}
✅ <b>الصفقات الرابحة:</b> {self.stats['win_trades']}
❌ <b>الصفقات الخاسرة:</b> {self.stats['loss_trades']}
💰 <b>صافي الربح:</b> {self.stats['net_profit']}

📅 <b>الإنجازات:</b>
• أقوى سلسلة ربح: {self.stats['max_win_streak']}
• أفضل زوج: {self.stats['best_pair']}

🕒 <b>آخر تحديث:</b> {current_time} (UTC+3)

"""
        self.telegram_bot.send_message(report_message)
    
    def keep_system_alive(self):
        """الحفاظ على نشاط النظام"""
        try:
            # إرسال تقرير كل ساعة
            current_time = self.get_utc3_time()
            if self.stats['last_trade_time']:
                time_since_last_report = (current_time - self.stats.get('last_report_time', current_time)).total_seconds()
                if time_since_last_report >= 3600:  # كل ساعة
                    self.send_performance_report()
                    self.stats['last_report_time'] = current_time
            
            # تحديث حالة السوق
            session = self.get_market_session()
            if hasattr(self, 'last_session'):
                if self.last_session != session:
                    logging.info(f"🌐 تغيير جلسة السوق: {self.last_session} → {session}")
                    self.last_session = session
            else:
                self.last_session = session
                
        except Exception as e:
            logging.error(f"❌ خطأ في الحفاظ على نشاط النظام: {e}")
    
    def run_advanced_scheduler(self):
        """تشغيل الجدولة المتقدمة"""
        try:
            self.start_24h_trading()
            
            logging.info("✅ بدء تشغيل الجدولة المتقدمة...")
            
            # الحلقة الرئيسية المتقدمة
            while True:
                current_time = self.get_utc3_time()
                
                # التحقق إذا حان وقت الصفقة
                if (self.next_trade_time and 
                    current_time >= self.next_trade_time and 
                    not self.trade_in_progress):
                    
                    logging.info(f"⏰ بدء صفقة جديدة: {current_time.strftime('%H:%M:%S')}")
                    self.execute_trade_cycle()
                    
                    # حساب الوقت التالي
                    self.next_trade_time = self.calculate_next_trade_time()
                    time_until_next = (self.next_trade_time - current_time).total_seconds()
                    
                    logging.info(f"⏰ الصفقة القادمة: {self.next_trade_time.strftime('%H:%M:%S')} (بعد {time_until_next:.0f} ثانية)")
                
                # الحفاظ على نشاط النظام
                self.keep_system_alive()
                
                # انتظار 5 ثواني قبل التكرار (أكثر كفاءة)
                time.sleep(5)
                    
        except Exception as e:
            logging.error(f"❌ خطأ فادح في التشغيل: {e}")
            logging.info("🔄 إعادة التشغيل بعد 30 ثانية...")
            time.sleep(30)
            self.run_advanced_scheduler()
