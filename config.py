import os
from pytz import timezone

# إعدادات البوت
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', "7920984703:AAHkRNpgzDxBzS61hAe7r7cO_fATlAB8oqM")
CHANNEL_ID = os.getenv('CHANNEL_ID', "@Kingelg0ld")
QX_SIGNUP_URL = "https://broker-qx.pro/sign-up/?lid=1376472"

# بيانات الدخول لـ QX Broker (للتحليل فقط)
QX_EMAIL = os.getenv('QX_EMAIL', 'mohamedels928@gmail.com')
QX_PASSWORD = os.getenv('QX_PASSWORD', 'Mrvip@219')
QX_LOGIN_URL = 'https://qxbroker.com/ar/sign-in/'

# الأزواج المطلوبة
TRADING_PAIRS = [
    'USD/BRL', 'USD/EGP', 'USD/TRY', 'USD/ARS', 'USD/COP',
    'USD/DZD', 'USD/IDR', 'USD/BDT', 'USD/CAD', 'USD/NGN',
    'USD/PKR', 'USD/INR', 'USD/MXN', 'USD/PHP'
]

# إعدادات التداول
TRADE_DURATION = 30
TRADE_INTERVAL = 1  # كل دقيقة بدل 3 دقائق

# توقيت UTC+3 (توقيت مصر)
UTC3_TZ = timezone('Africa/Cairo')

# إعدادات التحليل الفني
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
