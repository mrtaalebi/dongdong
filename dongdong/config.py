from datetime import datetime
from pytz import timezone
import os


env = os.environ
conn = env.get('db_conn', './db.sqlite')
tz = env.get('tz', 'Asia/Tehran')
api_key = env.get("api_key")

time_now = lambda: datetime.now(timezone(tz))

start_message = 'سلام خوش اومدی. شماره کارتتو بدون فاصله و به انگلیسی بزن عشق کنیم.'
welcome_message = 'به به، یه دونه /help بزن که بهت بگم چجوری کار می‌کنم.'
help_message = '''
/start
که برای شروعه.

/help
که همینه.

/menu
منوی کافه رو برات میاره.

/pay
برا وقتیه که می‌خوای هزینه اون روز رو تو حساب کنی. حتما هر روز یه نفر این رو بزنه.

/settle
حداقل تعداد کارت به کارت مورد نیاز رو پیدا می‌کنه و بهت می‌گه. هرچندوقت یه بار که خواستی اینو بزن و بدهی‌هات رو صاف کن.

/item
که باهاش آیتم‌های منوی کافه رو اضافه می‌کنی یا تغییر می‌دی

جاییشم سوراخ بود بهم بگید.
'''
enter_item_name_message = 'می‌تونی یه چیز اضافه کنی یا قیمت یه چیزی رو آپدیت کنی. اسمش رو بگو.'
enter_item_price_message = 'چنده؟'
item_created_message = 'أیتم اضافه شد.'
item_updated_message = 'أیتم آپدیت شد.'
message_not_matched_message = 'نفهیدم، چی؟'
menu_message = 'چی میل داری؟'
order_message = '{} درسته؟'
order_is_correct_message = 'آره'
order_is_incorrect_message = 'نه'
order_confirmed_message = 'ناب'
order_canceled_message = 'ردیفه ثبت نشد.'
pay_message = 'درود {} تومن از جیبت رفت.'
settle_message = 'اینجوریاس:'
