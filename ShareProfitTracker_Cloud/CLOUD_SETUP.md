# ShareProfitTracker Cloud Setup Guide

## Overview

This guide helps you set up the cloud sync feature for ShareProfitTracker, enabling you to access your portfolio from anywhere - completely FREE.

---

## Step 1: Create Supabase Account (Free)

1. Go to [https://supabase.com](https://supabase.com)
2. Click "Start your project" and sign up with GitHub
3. Create a new project:
   - **Name:** `sharetracker`
   - **Database Password:** (save this!)
   - **Region:** Choose closest to you

**Free Tier Includes:**
- 500 MB database storage
- 50,000 monthly active users
- Unlimited API requests
- Built-in authentication

---

## Step 2: Set Up Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Run the following SQL to create tables:

```sql
-- User profiles (extends Supabase auth)
CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID REFERENCES auth.users PRIMARY KEY,
    display_name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stocks table
CREATE TABLE IF NOT EXISTS public.stocks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL,
    symbol TEXT NOT NULL,
    company_name TEXT,
    quantity NUMERIC NOT NULL,
    purchase_price NUMERIC NOT NULL,
    purchase_date DATE NOT NULL,
    broker TEXT DEFAULT '',
    cash_invested NUMERIC DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cash transactions
CREATE TABLE IF NOT EXISTS public.cash_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL,
    transaction_type TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    description TEXT DEFAULT '',
    transaction_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Expenses
CREATE TABLE IF NOT EXISTS public.expenses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount NUMERIC NOT NULL,
    expense_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Dividends
CREATE TABLE IF NOT EXISTS public.dividends (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users NOT NULL,
    symbol TEXT NOT NULL,
    company_name TEXT,
    dividend_per_share NUMERIC NOT NULL,
    total_dividend NUMERIC NOT NULL,
    shares_held NUMERIC NOT NULL,
    ex_dividend_date DATE NOT NULL,
    payment_date DATE,
    dividend_type TEXT DEFAULT 'regular',
    tax_deducted NUMERIC DEFAULT 0,
    net_dividend NUMERIC,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE public.stocks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.cash_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.dividends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Create policies (users can only access their own data)
CREATE POLICY "Users access own stocks" ON public.stocks
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users access own transactions" ON public.cash_transactions
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users access own expenses" ON public.expenses
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users access own dividends" ON public.dividends
    FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users access own profile" ON public.user_profiles
    FOR ALL USING (auth.uid() = id);

-- Create indexes for performance
CREATE INDEX idx_stocks_user ON public.stocks(user_id);
CREATE INDEX idx_cash_user ON public.cash_transactions(user_id);
CREATE INDEX idx_expenses_user ON public.expenses(user_id);
CREATE INDEX idx_dividends_user ON public.dividends(user_id);
```

---

## Step 3: Get API Keys

1. In Supabase dashboard, go to **Settings > API**
2. Copy these values:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon public key:** `eyJhbGci...` (long string)

---

## Step 4: Deploy Backend API (Free)

### Option A: Railway (Recommended)

1. Go to [https://railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" > "Deploy from GitHub repo"
4. Select the `backend` folder
5. Add environment variables:
   - `SUPABASE_URL` = your project URL
   - `SUPABASE_KEY` = your anon key
6. Railway will auto-deploy

**Railway gives $5 free credit/month** - enough for personal use.

### Option B: Render

1. Go to [https://render.com](https://render.com)
2. Sign up and create new "Web Service"
3. Connect GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables
7. Deploy

**Render free tier:** 750 hours/month (sleeps after 15min inactivity)

### Option C: Vercel (Serverless)

1. Install Vercel CLI: `npm i -g vercel`
2. In backend folder, create `vercel.json`:
```json
{
  "builds": [{"src": "main.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "main.py"}]
}
```
3. Run `vercel` and follow prompts
4. Set environment variables in Vercel dashboard

---

## Step 5: Configure Desktop App

1. Open the cloud-enabled exe
2. Click "Cloud" button in toolbar
3. Click "Login" or "Register"
4. Enter your cloud server URL when prompted

Or set environment variable:
```
CLOUD_API_URL=https://your-app.railway.app
```

---

## Using Cloud Sync

### First Time Setup

1. **Register** a cloud account in the app
2. **Upload** your local data to cloud
3. You can now access from any device!

### Daily Use

- **Work offline:** App works normally with local data
- **Sync when needed:** Click "Upload" to save to cloud
- **Access anywhere:** Login on another device and "Download"

### From Another Device

1. Install ShareProfitTracker_Cloud.exe
2. Login with your cloud account
3. Click "Download from Cloud"
4. Your portfolio is now available!

---

## Cost Summary: $0/month

| Service | Free Tier |
|---------|-----------|
| Supabase | 500MB database, 50K users |
| Railway | $5/month credit |
| OR Render | 750 hours/month |
| OR Vercel | Serverless, generous limits |

**Total: FREE** for personal use!

---

## Troubleshooting

### "Cannot connect to cloud server"
- Check your internet connection
- Verify API URL is correct
- Check if backend is running (visit URL in browser)

### "Invalid token"
- Token may have expired
- Try logging out and back in

### "Sync failed"
- Check Supabase dashboard for errors
- Verify tables were created correctly
- Check Row Level Security policies

---

## Security Notes

- All data is encrypted in transit (HTTPS)
- Row Level Security ensures users only see their own data
- Passwords are hashed by Supabase Auth
- Never share your Supabase service key (only use anon key)

---

## Support

- Supabase Docs: https://supabase.com/docs
- FastAPI Docs: https://fastapi.tiangolo.com
- Railway Docs: https://docs.railway.app

---

**Enjoy your cloud-enabled portfolio tracker!**
