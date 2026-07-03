# Greenwich Visa Bot Pro

Stable professional MVP Telegram bot for Greenwich Visa Center.

## What this version includes

- Python + aiogram 3
- Armenian, Russian, English
- Focus countries: USA, Germany, France, Schengen / Europe, UK, Canada
- Country-specific questions
- Preliminary visa scoring from 5% to 95%
- Strengths, risks, recommendations
- Lead collection
- SQLite database
- CSV export
- Manager notification
- Simple admin commands
- Windows-friendly startup

## Install on Windows

Open PowerShell in this folder.

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
copy .env.example .env
```

Open `.env` and add your BOT_TOKEN.

Then run:

```powershell
py bot.py
```

## BotFather

1. Open Telegram
2. Search @BotFather
3. Send `/newbot`
4. Copy the token
5. Paste it into `.env`

## Admin

Add your Telegram user ID to `.env`:

```env
ADMIN_IDS=123456789
```

Commands:

- `/admin` - statistics
- `/export` - export leads CSV
- `/start` - start bot

## Important legal note

This bot only provides preliminary assessment.
It never guarantees visa approval.
The final decision is made only by the embassy or consulate.
