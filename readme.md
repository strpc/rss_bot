# RSS BOT
---


Telegram bot for delivery feed for you. Worked on [@fromRSS2bot](https://t.me/fromRSS2bot). Hosted on Raspberry Pi(yes)).

For hosted bot on your environment do next:
1. `git clone https://github.com/strpc/rss_bot.git`
2. `cp .env.example .env`
3. Edit `.env`-file. Requiered params: `TELEGRAM_TOKEN`. For receiving token go to [@BotFather](https://t.me/BotFather).
4. Set your bot webhook:
```shell
curl -F "url=https://YOUR_HOST/" https://api.telegram.org/bot${BOT_TOKEN}/setWebhook
```
5. Run: `docker-compose -f docker-compose.yml up -d`
