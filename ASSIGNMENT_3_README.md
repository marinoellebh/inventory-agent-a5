# EECE 430 Assignment 3: price and VAT

## What was changed

- `chat/models.py`: added a two-decimal, nonnegative `price` to each item.
- `chat/migrations/0002_item_price.py`: adds the column to an existing database. Existing items get a price of 0.00 until updated.
- `chat/admin.py`: shows the price in the item list and edit form.
- `chat/tools.py`: stock tools also return unit prices; `set_item_price` updates a price; `calculate_total` computes subtotal, VAT, and total from the database price without changing stock.
- `chat/agent.py`: tells the agent to call the calculator for cost/VAT questions.
- `chat/migrations/0003_sample_chocolate_bar.py`: adds a Chocolate bar at 2.50 with quantity 10 on a fresh installation if one is not already present.

## Result

The live chat screenshot is in `screenshots/chat_result.png`. Asked *"What is the cost of 3 items of chocolate bar after adding 10% VAT?"*, the agent answered **8.25** (subtotal 7.50 + VAT 0.75).

## Quick start on Windows

Double-click `run_windows.bat` in the `inventory` folder. It sets up dependencies, applies migrations and starts the server. Your computer needs Python, an internet connection for the first package install, and your own Gemini key for the live AI chat. Add `GEMINI_API_KEY=your_key_here` to `inventory/.env` before starting, or add it and restart the server. The server can open the admin page without a key, but the AI chat needs one.

## Run on Windows (PowerShell)

In the folder containing `manage.py`:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

On macOS/Linux, activate with `source .venv/bin/activate` and use `python3` if `python` is unavailable. If you already have a project and an admin account, keep your existing database and skip `createsuperuser`.

Before starting the server, create a file named `.env` beside `manage.py` containing `GEMINI_API_KEY=your_key_here`. If your existing `.env` works, keep it; the submitted ZIP intentionally excludes it. Never submit or share the key.

On a fresh install, the sample Chocolate bar already has quantity 10 and price 2.50. If you are using an existing database with a Chocolate bar, check its price at `http://127.0.0.1:8000/admin/` and set it to 2.50 if you want to reproduce the example. Then go to `http://127.0.0.1:8000/` and ask:

> What is the cost of 3 items of chocolate bar after adding 10% VAT?

For a price of 2.50, the expected result is **subtotal 7.50 + VAT 0.75 = total 8.25** (in whichever currency you use). A different price gives a different total. The quote does not reduce stock.

## What to submit

Follow your instructor's submission page if it specifies a format. The PDF only says to modify the agent and run that chat. Show a screenshot of the chat answer and a screenshot of the admin item/price if screenshots are requested. Do not include `.env` or a database containing personal data in a shared submission.
