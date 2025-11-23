"""
Supabase database connection and utilities
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Supabase credentials not configured. "
            "Set SUPABASE_URL and SUPABASE_KEY environment variables."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Database table names
TABLES = {
    'users': 'users',
    'stocks': 'stocks',
    'cash_transactions': 'cash_transactions',
    'expenses': 'expenses',
    'dividends': 'dividends',
    'price_cache': 'price_cache'
}

def init_database():
    """
    Initialize database tables in Supabase.
    Run this once to set up the database schema.

    Note: In Supabase, you typically create tables via the dashboard SQL editor.
    This function is for reference/documentation.
    """
    sql_schema = """
    -- Users table (handled by Supabase Auth, but we add custom fields)
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

    -- Cash transactions table
    CREATE TABLE IF NOT EXISTS public.cash_transactions (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users NOT NULL,
        transaction_type TEXT NOT NULL,
        amount NUMERIC NOT NULL,
        description TEXT DEFAULT '',
        transaction_date DATE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Expenses table
    CREATE TABLE IF NOT EXISTS public.expenses (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id UUID REFERENCES auth.users NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        amount NUMERIC NOT NULL,
        expense_date DATE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Dividends table
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

    -- Price cache table
    CREATE TABLE IF NOT EXISTS public.price_cache (
        symbol TEXT PRIMARY KEY,
        current_price NUMERIC,
        last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

    -- Row Level Security (RLS) policies
    ALTER TABLE public.stocks ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.cash_transactions ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.expenses ENABLE ROW LEVEL SECURITY;
    ALTER TABLE public.dividends ENABLE ROW LEVEL SECURITY;

    -- Users can only access their own data
    CREATE POLICY "Users can access own stocks" ON public.stocks
        FOR ALL USING (auth.uid() = user_id);

    CREATE POLICY "Users can access own cash_transactions" ON public.cash_transactions
        FOR ALL USING (auth.uid() = user_id);

    CREATE POLICY "Users can access own expenses" ON public.expenses
        FOR ALL USING (auth.uid() = user_id);

    CREATE POLICY "Users can access own dividends" ON public.dividends
        FOR ALL USING (auth.uid() = user_id);

    -- Indexes for performance
    CREATE INDEX IF NOT EXISTS idx_stocks_user ON public.stocks(user_id);
    CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON public.stocks(symbol);
    CREATE INDEX IF NOT EXISTS idx_cash_user ON public.cash_transactions(user_id);
    CREATE INDEX IF NOT EXISTS idx_expenses_user ON public.expenses(user_id);
    CREATE INDEX IF NOT EXISTS idx_dividends_user ON public.dividends(user_id);
    """

    return sql_schema
