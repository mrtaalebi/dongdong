from datetime import datetime
from pytz import timezone
import os


env = os.environ
conn = env.get('db_conn', './db.sqlite')
tz = env.get('tz', 'Asia/Tehran')
api_key = env.get("api_key")

time_now = lambda: datetime.now(timezone(tz))

start_message = 'سلام خوش اومدی. از منو هلپ رو انتخاب کن.'
help_message = ''
enter_item_name_message = 'می‌تونی یه چیز اضافه کنی یا قیمت یه چیزی رو آپدیت کنی. اسمش رو بگو.'
enter_item_price_message = 'چنده؟'
item_created_message = 'أیتم اضافه شد.'
item_updated_message = 'أیتم آپدیت شد.'
message_not_matched_message = 'نفهیدم، چی؟'
menu_message = 'چی میل داری؟'
order_message = '{} درسته؟'
order_confirmed_message = 'ناب'
order_canceled_message = 'ردیفه ثبت نشد.'

