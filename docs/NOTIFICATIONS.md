```markdown
# سیستم نوتیفیکیشن (Phase 9)

## معماری
سیستم نوتیفیکیشن از معماری Provider-based استفاده می‌کند تا ارسال اعلان‌ها را از منطق بیزینسی جدا کند.

### جریان ایجاد اعلان:
1. Business Service (مثلاً RegistrationService) متد `NotificationService.create_notification` را فراخوانی می‌کند.
2. `NotificationService` درخواست را به `NotificationDispatcher` می‌فرستد.
3. Dispatcher تنظیمات کاربر (`NotificationPreferenceModel`) را بررسی می‌کند.
4. برای هر کانال فعال (Web, Telegram, Bale)، Provider مربوطه فراخوانی می‌شود.
5. خطای هر Provider به صورت مستقل Catch شده و Log می‌شود تا خرابی یک کانال روی بقیه تاثیر نگذارد.

## کانال‌های پشتیبانی شده
1. **Web:** ذخیره در دیتابیس (جدول `notifications`).
2. **Telegram:** ارسال از طریق ربات تلگرام (نیازمند `TELEGRAM_BOT_TOKEN`).
3. **Bale:** ارسال از طریق ربات بله (نیازمند `BALE_BOT_TOKEN`).

## اتصال حساب کاربری (Account Linking)
برای اتصال تلگرام/بله، سیستم از یک توکن امن ۳۲ بایتی (`secrets.token_urlsafe`) با زمان انقضای ۱۰ دقیقه استفاده می‌کند.
- کاربر روی "اتصال" کلیک می‌کند -> توکن ساخته می‌شود.
- کاربر به ربات هدایت می‌شود (`/start TOKEN`).
- ربات از طریق Webhook، توکن را به سایت برمی‌گرداند.
- سایت توکن را اعتبارسنجی کرده و `chat_id` را ذخیره می‌کند. توکن بلافاصله باطل می‌شود.

## متغیرهای محیطی مورد نیاز
- `TELEGRAM_BOT_TOKEN`: توکن ربات تلگرام از BotFather
- `BALE_BOT_TOKEN`: توکن ربات بله

## راه‌اندازی Webhook (برای Production)
رویه رسمی و یکتای ثبت Webhook — شامل `secret_token` برای هر دو ربات،
اعتبارسنجی پاسخ و بررسی `getWebhookInfo` — در سند استقرار آمده است:

**`docs/DEPLOYMENT.md` → بخش ۱۱**

نکته حیاتی: اگر متغیرهای `TELEGRAM_WEBHOOK_SECRET` / `BALE_WEBHOOK_SECRET`
در `.env` تنظیم شده باشند، ثبت Webhook **بدون** همان مقدار در پارامتر
`secret_token` باعث می‌شود همه پیام‌های ورودی با خطای ۴۰۳ رد شوند
(علت اصلی «اتصال نشدن» ربات).