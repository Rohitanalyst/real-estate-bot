# 🚀 Deploy Your Bot Forever (Free) — Step by Step Guide

## What You'll Have After This

Your Telegram bot (@myrenshapropbot) running 24/7, automatically qualifying leads even while you sleep. Total cost: ₹0.

## Total Time Needed: 15-20 minutes

---

## STEP 1: Get a Free Google Gemini API Key (3 minutes)

The AI brain of your bot needs a key. Google gives this for FREE.

1. Open this link: https://aistudio.google.com/apikey
2. Sign in with your Google account (Gmail)
3. Click "Create API Key"
4. Click "Create API key in new project"
5. You'll see a long key like: `AIzaSyB1234567890abcdefghijk`
6. **COPY THIS KEY** — save it in your notes

✅ Done! This key is 100% free with generous limits (1,500 requests/day).

---

## STEP 2: Create a GitHub Account (3 minutes)

GitHub is where your bot's code will live. Railway reads it from here.

1. Go to https://github.com/signup
2. Enter your email, create a password, pick a username
3. Verify your email
4. Done!

If you already have GitHub, skip this step.

---

## STEP 3: Upload Your Bot Code to GitHub (5 minutes)

1. Log in to GitHub
2. Click the "+" icon (top right) → "New repository"
3. Name it: `real-estate-bot`
4. Keep it "Public" (or Private, both work)
5. Click "Create repository"
6. On the next page, click "uploading an existing file" link
7. **Drag and drop ALL these files** from the zip I gave you:
   - `main.py`
   - `config.py`
   - `ai_engine.py`
   - `telegram_bot.py`
   - `whatsapp_bot.py`
   - `admin_api.py`
   - `database.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `nixpacks.toml`
   - `.gitignore`
8. Click "Commit changes"

✅ Your code is now on GitHub!

---

## STEP 4: Deploy on Railway (5 minutes)

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway to access your GitHub
4. Click "New Project"
5. Click "Deploy from GitHub Repo"
6. Select your `real-estate-bot` repository
7. Railway will start building automatically

**Now add your secret keys:**

8. Click on your deployed service (the purple box)
9. Go to "Variables" tab
10. Click "New Variable" and add these ONE BY ONE:

```
Variable Name:  TELEGRAM_BOT_TOKEN
Value:          8700863365:AAFYWHqABR1zXqHP6H7pUyoOp35dThw5GO0

Variable Name:  GOOGLE_API_KEY
Value:          (paste your key from Step 1)

Variable Name:  AI_PROVIDER
Value:          google

Variable Name:  AI_MODEL
Value:          gemini-2.0-flash

Variable Name:  AGENT_NAME
Value:          Alex

Variable Name:  COMPANY_NAME
Value:          Premium Properties
```

11. After adding all variables, Railway will automatically redeploy
12. Wait 1-2 minutes for it to finish

✅ Your bot is now running 24/7!

---

## STEP 5: Test Your Bot

1. Open Telegram
2. Go to @myrenshapropbot
3. Send /start
4. Chat with it!

---

## How to Check if It's Working

- Go to Railway dashboard → your project
- Click on your service → "Logs" tab
- You should see: "🚀 Starting Premium Properties Lead Bot (Telegram)..."
- Every time someone messages your bot, you'll see logs here

---

## Troubleshooting

### Bot not responding?
- Check Railway logs for errors
- Make sure all 6 variables are added correctly
- Make sure there are no extra spaces in the values

### "Invalid API key" error?
- Go to https://aistudio.google.com/apikey
- Create a new key and update it in Railway variables

### Railway says "Build failed"?
- Make sure you uploaded ALL files listed in Step 3
- Check that `requirements.txt` is included

---

## Railway Free Tier Limits

- 500 hours/month of runtime (enough for 24/7 for ~20 days)
- After that, it's $5/month (very cheap)
- To stay free forever: Railway gives $5 free credit monthly with a linked credit card (you won't be charged)

**Alternative free option:** If Railway free tier runs out, you can use:
- **Render.com** — Similar setup, free tier available
- **Fly.io** — Free tier with 3 shared VMs

---

## What's Next?

Your bot is live! Now:
1. Share the bot link (t.me/myrenshapropbot) with real estate agents
2. Offer them a free trial
3. Check the BUSINESS_GUIDE.md for selling strategies

---

## Quick Reference

| Item | Value |
|------|-------|
| Bot Link | https://t.me/myrenshapropbot |
| Railway Dashboard | https://railway.app/dashboard |
| Google AI Studio | https://aistudio.google.com/apikey |
| Bot Token | 8700863365:AAFY...GO0 |
