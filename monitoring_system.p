import logging
import time
import psutil
import os
from datetime import datetime
from config import UTC3_TZ

class MonitoringSystem:
    """نظام مراقبة متقدم لأداء البوت"""
    
    def __init__(self, trading_engine=None, telegram_bot=None):
        self.trading_engine = trading_engine
        self.telegram_bot = telegram_bot
        self.performance_metrics = {
            'start_time': datetime.now(UTC3_TZ),
            'total_errors': 0,
            'consecutive_errors': 0,
            'last_successful_trade': None,
            'system_uptime': 0,
            'performance_alerts': [],
            'resource_usage': {},
            'trade_accuracy': 0
        }
        
        self.alert_thresholds = {
            'max_consecutive_errors': 5,
            'max_memory_usage': 85,  # %
            'max_cpu_usage': 80,     # %
            'min_trade_accuracy': 40  # %
        }
        
    def log_error(self, error_type, error_message):
        """تسجيل الأخطاء"""
        self.performance_metrics['total_errors'] += 1
        self.performance_metrics['consecutive_errors'] += 1
        
        error_data = {
            'type': error_type,
            'message': error_message,
            'timestamp': datetime.now(UTC3_TZ).strftime("%H:%M:%S"),
            'severity': 'HIGH' if self.performance_metrics['consecutive_errors'] >= 3 else 'MEDIUM'
        }
        
        self.performance_metrics['performance_alerts'].append(error_data)
        
        # الحفاظ على آخر 50 تنبيه فقط
        if len(self.performance_metrics['performance_alerts']) > 50:
            self.performance_metrics['performance_alerts'] = self.performance_metrics['performance_alerts'][-50:]
        
        logging.warning(f"⚠️ خطأ مسجل: {error_type} - {error_message}")
        
        # إرسال تنبيه للأخطاء المتتالية
        if self.performance_metrics['consecutive_errors'] >= self.alert_thresholds['max_consecutive_errors']:
            self.send_alert(f"🔴 حالة حرجة! {self.performance_metrics['consecutive_errors']} أخطاء متتالية")
    
    def log_success(self, trade_data=None):
        """تسجيل نجاح الصفقة"""
        self.performance_metrics['consecutive_errors'] = 0
        self.performance_metrics['last_successful_trade'] = datetime.now(UTC3_TZ)
        
        if trade_data:
            # تحديث دقة التداول
            self.update_trade_accuracy(trade_data)
        
        logging.info("✅ تم تسجيل نجاح الصفقة")
    
    def update_trade_accuracy(self, trade_data):
        """تحديث دقة التداول"""
        try:
            # يمكن إضافة منطق أكثر تعقيداً هنا
            # حالياً نستخدم ثقة التحليل كمؤشر للدقة
            if 'confidence' in trade_data and trade_data['confidence'] > 70:
                self.performance_metrics['trade_accuracy'] = min(
                    100, 
                    self.performance_metrics.get('trade_accuracy', 50) + 2
                )
        except Exception as e:
            logging.error(f"❌ خطأ في تحديث دقة التداول: {e}")
    
    def monitor_resources(self):
        """مراقبة استخدام الموارد"""
        try:
            memory_usage = psutil.virtual_memory().percent
            cpu_usage = psutil.cpu_percent(interval=1)
            
            self.performance_metrics['resource_usage'] = {
                'memory': memory_usage,
                'cpu': cpu_usage,
                'timestamp': datetime.now(UTC3_TZ).strftime("%H:%M:%S")
            }
            
            # التحقق من العتبات
            if memory_usage > self.alert_thresholds['max_memory_usage']:
                self.send_alert(f"⚠️ استخدام ذاكرة مرتفع: {memory_usage}%")
            
            if cpu_usage > self.alert_thresholds['max_cpu_usage']:
                self.send_alert(f"⚠️ استخدام معالج مرتفع: {cpu_usage}%")
                
        except Exception as e:
            logging.error(f"❌ خطأ في مراقبة الموارد: {e}")
    
    def send_alert(self, message):
        """إرسال تنبيه عبر التليجرام"""
        try:
            if self.telegram_bot:
                current_time = datetime.now(UTC3_TZ).strftime("%H:%M:%S")
                alert_message = f"🚨 <b>تنبيه نظام المراقبة</b>\n\n{message}\n\n⏰ الوقت: {current_time}"
                self.telegram_bot.send_message(alert_message)
            else:
                logging.warning(f"🚨 تنبيه: {message}")
        except Exception as e:
            logging.error(f"❌ خطأ في إرسال التنبيه: {e}")
    
    def get_system_health(self):
        """الحصول على تقرير صحة النظام"""
        try:
            current_time = datetime.now(UTC3_TZ)
            uptime = current_time - self.performance_metrics['start_time']
            uptime_hours = uptime.total_seconds() / 3600
            
            # مراقبة الموارد
            self.monitor_resources()
            
            resource_usage = self.performance_metrics['resource_usage']
            
            health_report = f"""
🩺 <b>تقرير صحة النظام المتقدم</b>

⏰ <b>وقت التشغيل:</b> {uptime_hours:.1f} ساعة
📊 <b>إجمالي الأخطاء:</b> {self.performance_metrics['total_errors']}
🔴 <b>أخطاء متتالية:</b> {self.performance_metrics['consecutive_errors']}
🎯 <b>دقة التداول:</b> {self.performance_metrics['trade_accuracy']}%

💻 <b>استخدام الموارد:</b>
• الذاكرة: {resource_usage.get('memory', 0):.1f}%
• المعالج: {resource_usage.get('cpu', 0):.1f}%

✅ <b>آخر صفقة ناجحة:</b> {self.performance_metrics['last_successful_trade'].strftime('%H:%M:%S') if self.performance_metrics['last_successful_trade'] else 'N/A'}

📈 <b>حالة النظام:</b> {'🟢 ممتازة' if self.performance_metrics['consecutive_errors'] == 0 else '🟡 متوسطة' if self.performance_metrics['consecutive_errors'] < 3 else '🔴 حرجة'}
"""
            return health_report
        except Exception as e:
            logging.error(f"❌ خطأ في إنشاء تقرير الصحة: {e}")
            return "🩺 <b>تقرير صحة النظام</b>\n\n⚠️ غير متوفر حاليًا"
    
    def run_health_check(self):
        """تشغيل فحص صحة دوري"""
        try:
            # مراقبة الموارد
            self.monitor_resources()
            
            # فحص الأخطاء المتتالية
            if self.performance_metrics['consecutive_errors'] >= 5:
                self.send_alert("🔴 حالة حرجة! البوت يواجه صعوبات متتالية في التنفيذ")
            
            # فحص دقة التداول
            if self.performance_metrics['trade_accuracy'] < self.alert_thresholds['min_trade_accuracy']:
                self.send_alert(f"⚠️ دقة تداول منخفضة: {self.performance_metrics['trade_accuracy']}%")
                
        except Exception as e:
            logging.error(f"❌ خطأ في فحص الصحة: {e}")
