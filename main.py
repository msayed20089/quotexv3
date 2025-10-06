from telegram_bot import TelegramBot
from advanced_scheduler import AdvancedScheduler
import logging
import threading
import time
import sys

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

def keep_alive_output():
    """إرسال output مستمر"""
    while True:
        logger.info("🔄 النظام الدقيق يعمل بشكل طبيعي...")
        time.sleep(30)

def main():
    """الدالة الرئيسية"""
    try:
        logger.info("⏳ جاري تهيئة النظام الدقيق...")
        
        # بدء thread للإخراج المستمر
        output_thread = threading.Thread(target=keep_alive_output)
        output_thread.daemon = True
        output_thread.start()
        
        time.sleep(5)
        
        logger.info("🚀 بدء تشغيل بوت التداول الدقيق...")
        
        # اختبار بوت التليجرام
        telegram_bot = TelegramBot()
        
        if telegram_bot.send_message("🟢 **بدء تشغيل البوت الدقيق**\n\nجاري تهيئة النظام بالتوقيت المحدد..."):
            logger.info("✅ تم الاتصال بنجاح ببوت التليجرام")
        
        # تشغيل الجدولة الدقيقة
        logger.info("⏰ جاري تشغيل جدولة المهام الدقيقة...")
        scheduler = AdvancedScheduler()
        scheduler.run_precision_scheduler()
        
    except Exception as e:
        logger.error(f"❌ خطأ في التشغيل: {e}")
        logger.info("🔄 إعادة التشغيل بعد 30 ثانية...")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
