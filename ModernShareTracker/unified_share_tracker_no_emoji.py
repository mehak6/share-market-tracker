#!/usr/bin/env python3
"""
Unified Share Tracker - Complete Portfolio Management System
Combines original ShareProfitTracker with Modern Advanced Features
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
import json
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import sys

# Add both original and modern paths
original_path = os.path.join(os.path.dirname(__file__), '..', 'ShareProfitTracker')
sys.path.insert(0, original_path)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'services'))

class UnifiedShareTracker:
    """Complete portfolio management system combining original + modern features"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Unified Share Tracker - Complete Portfolio Management")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # Database setup
        self.db_path = "unified_portfolio.db"
        self.setup_database()

        # Sample portfolio for modern features demo
        self.sample_portfolio = {
            'stocks': [
                {
                    'symbol': 'RELIANCE',
                    'quantity': 100,
                    'purchase_price': 2200,
                    'current_price': 2500,
                    'purchase_date': '2023-06-15T00:00:00',
                    'sector': 'Energy',
                    'current_value': 250000,
                    'invested_amount': 220000
                }
            ]
        }

        self.create_main_interface()

    def setup_database(self):
        """Setup unified database with all required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Original ShareProfitTracker tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                company_name TEXT,
                quantity INTEGER NOT NULL,
                purchase_price REAL NOT NULL,
                current_price REAL,
                purchase_date DATE NOT NULL,
                broker TEXT,
                cash_invested REAL,
                sector TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                transaction_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                expense_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Modern features tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                target_price REAL NOT NULL,
                current_price REAL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                triggered_at TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rebalancing_suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT NOT NULL,
                suggestion_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                implemented BOOLEAN DEFAULT 0
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tax_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                financial_year TEXT NOT NULL,
                stcg_gain REAL DEFAULT 0,
                ltcg_gain REAL DEFAULT 0,
                total_tax_liability REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def create_main_interface(self):
        """Create the main tabbed interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create individual tabs
        self.create_portfolio_tab()
        self.create_analytics_tab()
        self.create_ai_advisor_tab()
        self.create_alerts_tab()
        self.create_tax_tab()
        self.create_reports_tab()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Welcome to Unified Share Tracker")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Initial data load
        self.refresh_portfolio()

    def create_portfolio_tab(self):
        """Create portfolio management tab (original ShareProfitTracker)"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="Portfolio")

        # Toolbar
        toolbar = ttk.Frame(portfolio_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(toolbar, text="Add Stock", command=self.add_stock_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Update Prices", command=self.refresh_prices).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Cash", command=self.add_cash_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Add Expense", command=self.add_expense_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Export Data", command=self.export_data).pack(side=tk.LEFT, padx=5)

        # Portfolio display
        tree_frame = ttk.Frame(portfolio_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create Treeview
        columns = ('Symbol', 'Company', 'Quantity', 'Purchase Price', 'Current Price', 'P&L', 'P&L %')
        self.portfolio_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configure columns
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            self.portfolio_tree.column(col, width=120, anchor=tk.CENTER)

        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.portfolio_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.portfolio_tree.xview)

        self.portfolio_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        # Pack components
        self.portfolio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Summary panel
        summary_frame = ttk.LabelFrame(portfolio_frame, text="Portfolio Summary")
        summary_frame.pack(fill=tk.X, padx=5, pady=5)

        self.summary_labels = {}
        summary_items = [
            ('Total Investment', 'total_investment'),
            ('Current Value', 'current_value'),
            ('Total P&L', 'total_pnl'),
            ('P&L %', 'pnl_percent')
        ]

        for i, (label, key) in enumerate(summary_items):
            ttk.Label(summary_frame, text=f"{label}:").grid(row=0, column=i*2, padx=10, pady=5, sticky=tk.W)
            self.summary_labels[key] = ttk.Label(summary_frame, text="₹0.00", font=('Arial', 10, 'bold'))
            self.summary_labels[key].grid(row=0, column=i*2+1, padx=10, pady=5, sticky=tk.W)

    def create_analytics_tab(self):
        """Create analytics and charts tab"""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="Analytics")

        # Analytics content
        ttk.Label(analytics_frame, text="Portfolio Analytics", font=('Arial', 16, 'bold')).pack(pady=10)

        # Sector allocation
        sector_frame = ttk.LabelFrame(analytics_frame, text="Sector Allocation")
        sector_frame.pack(fill=tk.X, padx=10, pady=5)

        # Create sector analysis
        self.sector_listbox = tk.Listbox(sector_frame, height=8)
        self.sector_listbox.pack(fill=tk.X, padx=10, pady=10)

        # Performance metrics
        metrics_frame = ttk.LabelFrame(analytics_frame, text="Performance Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)

        # Metrics display
        self.metrics_text = tk.Text(metrics_frame, height=10, wrap=tk.WORD)
        metrics_scrollbar = ttk.Scrollbar(metrics_frame, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=metrics_scrollbar.set)

        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        metrics_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Update analytics
        ttk.Button(analytics_frame, text="Refresh Analytics", command=self.update_analytics).pack(pady=10)

    def create_ai_advisor_tab(self):
        """Create AI financial advisor tab"""
        ai_frame = ttk.Frame(self.notebook)
        self.notebook.add(ai_frame, text="AI Advisor")

        ttk.Label(ai_frame, text="AI Financial Advisor", font=('Arial', 16, 'bold')).pack(pady=10)

        # Chat interface
        chat_frame = ttk.LabelFrame(ai_frame, text="Chat with AI Advisor")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Chat display
        self.chat_display = tk.Text(chat_frame, height=15, wrap=tk.WORD, state=tk.DISABLED)
        chat_scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)

        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        self.chat_input = ttk.Entry(input_frame, font=('Arial', 10))
        self.chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(input_frame, text="Send", command=self.send_chat_message).pack(side=tk.RIGHT)

        # Quick actions
        actions_frame = ttk.LabelFrame(ai_frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)

        quick_actions = [
            ("Portfolio Analysis", self.request_portfolio_analysis),
            ("Tax Advice", self.request_tax_advice),
            ("Rebalancing Suggestions", self.request_rebalancing),
            ("Risk Assessment", self.request_risk_assessment)
        ]

        for i, (text, command) in enumerate(quick_actions):
            ttk.Button(actions_frame, text=text, command=command).grid(row=0, column=i, padx=5, pady=5)

        # Bind Enter key to send message
        self.chat_input.bind('<Return>', lambda e: self.send_chat_message())

        # Welcome message
        self.add_chat_message("AI Advisor", "Hello! I'm your AI financial advisor. I can help you with portfolio analysis, tax planning, and investment strategies. How can I assist you today?")

    def create_alerts_tab(self):
        """Create price alerts tab"""
        alerts_frame = ttk.Frame(self.notebook)
        self.notebook.add(alerts_frame, text="Alerts")

        ttk.Label(alerts_frame, text="Price Alerts System", font=('Arial', 16, 'bold')).pack(pady=10)

        # Alert creation
        create_frame = ttk.LabelFrame(alerts_frame, text="Create Price Alert")
        create_frame.pack(fill=tk.X, padx=10, pady=5)

        # Alert form
        form_frame = ttk.Frame(create_frame)
        form_frame.pack(padx=10, pady=10)

        ttk.Label(form_frame, text="Symbol:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.alert_symbol_entry = ttk.Entry(form_frame, width=15)
        self.alert_symbol_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Alert Type:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.alert_type_combo = ttk.Combobox(form_frame, values=["Above", "Below"], width=10)
        self.alert_type_combo.grid(row=0, column=3, padx=5, pady=5)
        self.alert_type_combo.set("Above")

        ttk.Label(form_frame, text="Target Price:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.alert_price_entry = ttk.Entry(form_frame, width=15)
        self.alert_price_entry.grid(row=0, column=5, padx=5, pady=5)

        ttk.Button(form_frame, text="Create Alert", command=self.create_price_alert).grid(row=0, column=6, padx=10, pady=5)

        # Active alerts display
        alerts_list_frame = ttk.LabelFrame(alerts_frame, text="Active Alerts")
        alerts_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Alerts treeview
        alert_columns = ('Symbol', 'Type', 'Target Price', 'Current Price', 'Status', 'Created')
        self.alerts_tree = ttk.Treeview(alerts_list_frame, columns=alert_columns, show='headings', height=10)

        for col in alert_columns:
            self.alerts_tree.heading(col, text=col)
            self.alerts_tree.column(col, width=120, anchor=tk.CENTER)

        # Alerts scrollbar
        alerts_scrollbar = ttk.Scrollbar(alerts_list_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=alerts_scrollbar.set)

        self.alerts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        alerts_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Alert actions
        alert_actions_frame = ttk.Frame(alerts_frame)
        alert_actions_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(alert_actions_frame, text="Refresh Alerts", command=self.refresh_alerts).pack(side=tk.LEFT, padx=5)
        ttk.Button(alert_actions_frame, text="Delete Selected", command=self.delete_selected_alert).pack(side=tk.LEFT, padx=5)

    def create_tax_tab(self):
        """Create tax optimization tab"""
        tax_frame = ttk.Frame(self.notebook)
        self.notebook.add(tax_frame, text="Tax Planning")

        ttk.Label(tax_frame, text="Tax Optimization", font=('Arial', 16, 'bold')).pack(pady=10)

        # Tax year selection
        year_frame = ttk.Frame(tax_frame)
        year_frame.pack(pady=5)

        ttk.Label(year_frame, text="Financial Year:").pack(side=tk.LEFT, padx=5)
        self.tax_year_combo = ttk.Combobox(year_frame, values=["2023-24", "2024-25", "2025-26"], width=10)
        self.tax_year_combo.pack(side=tk.LEFT, padx=5)
        self.tax_year_combo.set("2024-25")

        ttk.Button(year_frame, text="Calculate Tax", command=self.calculate_tax).pack(side=tk.LEFT, padx=10)

        # Tax summary
        tax_summary_frame = ttk.LabelFrame(tax_frame, text="Tax Summary")
        tax_summary_frame.pack(fill=tk.X, padx=10, pady=10)

        self.tax_display = tk.Text(tax_summary_frame, height=15, wrap=tk.WORD)
        tax_scrollbar = ttk.Scrollbar(tax_summary_frame, command=self.tax_display.yview)
        self.tax_display.configure(yscrollcommand=tax_scrollbar.set)

        self.tax_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        tax_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Tax optimization suggestions
        optimization_frame = ttk.LabelFrame(tax_frame, text="Optimization Suggestions")
        optimization_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(optimization_frame, text="Generate Tax Saving Suggestions",
                  command=self.generate_tax_suggestions).pack(pady=10)

    def create_reports_tab(self):
        """Create reports and export tab"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="Reports")

        ttk.Label(reports_frame, text="Reports & Export", font=('Arial', 16, 'bold')).pack(pady=10)

        # Report types
        report_types_frame = ttk.LabelFrame(reports_frame, text="Available Reports")
        report_types_frame.pack(fill=tk.X, padx=10, pady=10)

        reports = [
            ("Portfolio Summary", self.generate_portfolio_report),
            ("P&L Statement", self.generate_pnl_report),
            ("Tax Report", self.generate_tax_report),
            ("Sector Analysis", self.generate_sector_report),
            ("Performance Report", self.generate_performance_report)
        ]

        for i, (report_name, command) in enumerate(reports):
            row = i // 3
            col = i % 3
            ttk.Button(report_types_frame, text=report_name, command=command, width=20).grid(
                row=row, column=col, padx=10, pady=5)

        # Export options
        export_frame = ttk.LabelFrame(reports_frame, text="Export Data")
        export_frame.pack(fill=tk.X, padx=10, pady=10)

        export_buttons = [
            ("Export to CSV", self.export_to_csv),
            ("Export to Excel", self.export_to_excel),
            ("Backup Database", self.backup_database)
        ]

        for text, command in export_buttons:
            ttk.Button(export_frame, text=text, command=command).pack(side=tk.LEFT, padx=10, pady=5)

        # Report display
        report_display_frame = ttk.LabelFrame(reports_frame, text="Report Preview")
        report_display_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.report_display = tk.Text(report_display_frame, wrap=tk.WORD)
        report_scrollbar = ttk.Scrollbar(report_display_frame, command=self.report_display.yview)
        self.report_display.configure(yscrollcommand=report_scrollbar.set)

        self.report_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    # Portfolio Management Methods (Original Features)
    def add_stock_dialog(self):
        """Add new stock dialog with stock search and autocomplete"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Stock")
        dialog.geometry("600x650")
        dialog.transient(self.root)
        dialog.grab_set()

        # Create form fields
        fields = {}

        # Stock search section
        search_frame = ttk.LabelFrame(dialog, text="Search & Select Stock")
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        # Search controls
        search_controls = ttk.Frame(search_frame)
        search_controls.pack(fill=tk.X, pady=5)

        ttk.Label(search_controls, text="Search:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=5)

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_controls, textvariable=search_var, width=30, font=('Arial', 10))
        search_entry.pack(side=tk.LEFT, padx=5)

        # Sector filter
        ttk.Label(search_controls, text="Sector:").pack(side=tk.LEFT, padx=(20,5))
        sector_var = tk.StringVar(value="All")
        sector_filter = ttk.Combobox(search_controls, textvariable=sector_var, width=15, values=[
            "All", "Technology", "Banking", "FMCG", "Pharmaceuticals", "Automobile",
            "Oil & Gas", "Metals", "Cement", "Power", "Healthcare", "Consumer Goods",
            "Financial Services", "Engineering", "Telecommunications", "Others"
        ])
        sector_filter.pack(side=tk.LEFT, padx=5)

        # Exchange filter
        ttk.Label(search_controls, text="Exchange:").pack(side=tk.LEFT, padx=(10,5))
        exchange_var = tk.StringVar(value="All")
        exchange_filter = ttk.Combobox(search_controls, textvariable=exchange_var, width=8, values=[
            "All", "NSE", "BSE"
        ])
        exchange_filter.pack(side=tk.LEFT, padx=5)

        # Market cap filter
        ttk.Label(search_controls, text="Market Cap:").pack(side=tk.LEFT, padx=(10,5))
        market_cap_var = tk.StringVar(value="All")
        market_cap_filter = ttk.Combobox(search_controls, textvariable=market_cap_var, width=10, values=[
            "All", "Large Cap", "Mid Cap", "Small Cap"
        ])
        market_cap_filter.pack(side=tk.LEFT, padx=5)

        # Stock list display
        list_frame = ttk.Frame(search_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Listbox with scrollbar
        stock_listbox = tk.Listbox(list_frame, height=8, font=('Arial', 9))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=stock_listbox.yview)
        stock_listbox.configure(yscrollcommand=scrollbar.set)

        stock_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Load stock data from 2000+ database
        stock_data = self.load_stock_database()
        all_stocks = [(f"{stock['symbol']} - {stock['name']} ({stock.get('sector', 'N/A')}) [{stock.get('exchange', 'NSE')}] {stock.get('market_cap', 'N/A')}", stock) for stock in stock_data]

        def update_stock_list(search_term="", sector_filter_val="All", exchange_filter_val="All", market_cap_filter_val="All"):
            stock_listbox.delete(0, tk.END)
            filtered_stocks = []

            for display_text, stock_info in all_stocks:
                # Apply text search filter
                if search_term and search_term.lower() not in display_text.lower():
                    continue

                # Apply sector filter
                if sector_filter_val != "All" and stock_info.get('sector', '') != sector_filter_val:
                    continue

                # Apply exchange filter
                if exchange_filter_val != "All" and stock_info.get('exchange', 'NSE') != exchange_filter_val:
                    continue

                # Apply market cap filter
                if market_cap_filter_val != "All" and stock_info.get('market_cap', '') != market_cap_filter_val:
                    continue

                filtered_stocks.append((display_text, stock_info))

            # Optimized sorting by relevance
            if search_term:
                filtered_stocks.sort(key=lambda x: (
                    not x[1]['symbol'].lower().startswith(search_term.lower()),
                    not search_term.lower() in x[1]['name'].lower(),
                    x[1]['symbol']  # Alphabetical as tiebreaker
                ))
            else:
                # Sort by market cap priority when no search term
                cap_priority = {'Large Cap': 0, 'Mid Cap': 1, 'Small Cap': 2, 'N/A': 3, '': 3}
                filtered_stocks.sort(key=lambda x: (
                    cap_priority.get(x[1].get('market_cap', ''), 3),
                    x[1]['symbol']
                ))

            # Show results with optimized count
            total_count = len(filtered_stocks)
            display_count = min(150, total_count)  # Show top 150 matches for better UX

            for display_text, _ in filtered_stocks[:display_count]:
                stock_listbox.insert(tk.END, display_text)

            # Update status
            if total_count > display_count:
                stock_listbox.insert(tk.END, f"... and {total_count - display_count} more stocks (refine search)")

            return total_count

        def on_search_change(*args):
            search_term = search_var.get()
            sector_val = sector_var.get()
            exchange_val = exchange_var.get()
            market_cap_val = market_cap_var.get()
            count = update_stock_list(search_term, sector_val, exchange_val, market_cap_val)
            # Update search info
            search_info.config(text=f"Found {count} stocks")

        def on_filter_change(*args):
            on_search_change()

        def on_stock_select(event):
            selection = stock_listbox.curselection()
            if selection:
                selected_text = stock_listbox.get(selection[0])
                # Find the stock info
                for display_text, stock_info in all_stocks:
                    if display_text == selected_text:
                        # Auto-fill the form
                        fields['symbol'].delete(0, tk.END)
                        fields['symbol'].insert(0, stock_info['symbol'])
                        fields['company'].delete(0, tk.END)
                        fields['company'].insert(0, stock_info['name'])
                        fields['sector'].delete(0, tk.END)
                        fields['sector'].insert(0, stock_info.get('sector', ''))
                        fields['price'].delete(0, tk.END)
                        fields['price'].insert(0, str(stock_info.get('current_price', 0)))
                        break

        # Search info
        search_info = ttk.Label(search_frame, text="Type to search stocks", font=('Arial', 8))
        search_info.pack(pady=2)

        # Bind events
        search_var.trace('w', on_search_change)
        sector_var.trace('w', on_filter_change)
        exchange_var.trace('w', on_filter_change)
        market_cap_var.trace('w', on_filter_change)
        stock_listbox.bind('<Double-Button-1>', on_stock_select)

        # Initialize stock list
        update_stock_list()

        # Stock details form
        details_frame = ttk.LabelFrame(dialog, text="Stock Details")
        details_frame.pack(fill=tk.X, padx=10, pady=10)

        # Form fields
        form_fields = [
            ('Symbol', 'symbol'),
            ('Company Name', 'company'),
            ('Quantity', 'quantity'),
            ('Purchase Price', 'price'),
            ('Purchase Date', 'date'),
            ('Sector', 'sector'),
            ('Broker', 'broker')
        ]

        for i, (label, key) in enumerate(form_fields):
            row = i // 2
            col = (i % 2) * 2

            ttk.Label(details_frame, text=f"{label}:").grid(row=row, column=col, padx=5, pady=5, sticky=tk.W)

            if key == 'date':
                fields[key] = ttk.Entry(details_frame, width=15)
                fields[key].insert(0, datetime.now().strftime('%Y-%m-%d'))
            else:
                fields[key] = ttk.Entry(details_frame, width=15)

            fields[key].grid(row=row, column=col+1, padx=5, pady=5, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def save_stock():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO stocks (symbol, company_name, quantity, purchase_price,
                                      purchase_date, sector, broker, current_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    fields['symbol'].get().upper(),
                    fields['company'].get(),
                    int(fields['quantity'].get()),
                    float(fields['price'].get()),
                    fields['date'].get(),
                    fields['sector'].get(),
                    fields['broker'].get(),
                    float(fields['price'].get())  # Initial current price = purchase price
                ))

                conn.commit()
                conn.close()

                self.refresh_portfolio()
                dialog.destroy()
                self.update_status("Stock added successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add stock: {str(e)}")

        ttk.Button(button_frame, text="Save", command=save_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def refresh_portfolio(self):
        """Refresh portfolio display"""
        # Clear existing data
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)

        # Load from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, quantity, purchase_price, current_price, purchase_date,
                   company_name, sector FROM stocks
        ''')

        stocks = cursor.fetchall()
        conn.close()

        total_investment = 0
        total_current_value = 0

        for stock in stocks:
            symbol, quantity, purchase_price, current_price, purchase_date, company_name, sector = stock

            if current_price is None:
                current_price = purchase_price

            investment = quantity * purchase_price
            current_value = quantity * current_price
            pnl = current_value - investment
            pnl_percent = (pnl / investment) * 100 if investment > 0 else 0

            total_investment += investment
            total_current_value += current_value

            # Format values
            self.portfolio_tree.insert('', tk.END, values=(
                symbol,
                company_name or 'N/A',
                quantity,
                f"₹{purchase_price:,.2f}",
                f"₹{current_price:,.2f}",
                f"₹{pnl:,.2f}",
                f"{pnl_percent:.2f}%"
            ))

        # Update summary
        total_pnl = total_current_value - total_investment
        total_pnl_percent = (total_pnl / total_investment) * 100 if total_investment > 0 else 0

        self.summary_labels['total_investment'].config(text=f"₹{total_investment:,.2f}")
        self.summary_labels['current_value'].config(text=f"₹{total_current_value:,.2f}")
        self.summary_labels['total_pnl'].config(text=f"₹{total_pnl:,.2f}")
        self.summary_labels['pnl_percent'].config(text=f"{total_pnl_percent:.2f}%")

        # Update color based on P&L
        pnl_color = 'green' if total_pnl >= 0 else 'red'
        self.summary_labels['total_pnl'].config(foreground=pnl_color)
        self.summary_labels['pnl_percent'].config(foreground=pnl_color)

    def add_cash_dialog(self):
        """Add cash transaction dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Cash Transaction")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Form fields
        ttk.Label(dialog, text="Transaction Type:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=["Deposit", "Withdrawal"], width=20)
        type_combo.pack(pady=5)
        type_combo.set("Deposit")

        ttk.Label(dialog, text="Amount:").pack(pady=5)
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(dialog, width=30)
        desc_entry.pack(pady=5)

        ttk.Label(dialog, text="Date:").pack(pady=5)
        date_entry = ttk.Entry(dialog, width=20)
        date_entry.pack(pady=5)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        def save_transaction():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO cash_transactions (transaction_type, amount, description, transaction_date)
                    VALUES (?, ?, ?, ?)
                ''', (
                    type_combo.get(),
                    float(amount_entry.get()),
                    desc_entry.get(),
                    date_entry.get()
                ))

                conn.commit()
                conn.close()

                dialog.destroy()
                self.update_status("Cash transaction added successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add transaction: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_transaction).pack(pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def add_expense_dialog(self):
        """Add expense dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Expense")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # Form fields
        ttk.Label(dialog, text="Category:").pack(pady=5)
        category_combo = ttk.Combobox(dialog, values=["Brokerage", "STT", "Other Charges", "Research", "Software"], width=20)
        category_combo.pack(pady=5)
        category_combo.set("Brokerage")

        ttk.Label(dialog, text="Amount:").pack(pady=5)
        amount_entry = ttk.Entry(dialog, width=20)
        amount_entry.pack(pady=5)

        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = ttk.Entry(dialog, width=30)
        desc_entry.pack(pady=5)

        ttk.Label(dialog, text="Date:").pack(pady=5)
        date_entry = ttk.Entry(dialog, width=20)
        date_entry.pack(pady=5)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        def save_expense():
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO expenses (category, amount, description, expense_date)
                    VALUES (?, ?, ?, ?)
                ''', (
                    category_combo.get(),
                    float(amount_entry.get()),
                    desc_entry.get(),
                    date_entry.get()
                ))

                conn.commit()
                conn.close()

                dialog.destroy()
                self.update_status("Expense added successfully!")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to add expense: {str(e)}")

        ttk.Button(dialog, text="Save", command=save_expense).pack(pady=20)
        ttk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def export_data(self):
        """Export portfolio data to CSV"""
        try:
            import csv
            from tkinter import filedialog

            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                title="Save Portfolio Data"
            )

            if filename:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM stocks')
                stocks = cursor.fetchall()

                # Get column names
                cursor.execute("PRAGMA table_info(stocks)")
                columns = [column[1] for column in cursor.fetchall()]

                conn.close()

                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(columns)
                    writer.writerows(stocks)

                self.update_status(f"Data exported to {filename}")
                messagebox.showinfo("Export Complete", f"Portfolio data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data: {str(e)}")

    # Modern Features Methods
    def send_chat_message(self):
        """Send message to AI advisor"""
        message = self.chat_input.get().strip()
        if not message:
            return

        # Add user message to chat
        self.add_chat_message("You", message)
        self.chat_input.delete(0, tk.END)

        # Generate AI response (mock)
        ai_response = self.generate_ai_response(message)
        self.add_chat_message("AI Advisor", ai_response)

    def add_chat_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.configure(state=tk.NORMAL)

        timestamp = datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"

        self.chat_display.insert(tk.END, formatted_message)
        self.chat_display.configure(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def generate_ai_response(self, message):
        """Generate AI advisor response (mock implementation)"""
        message_lower = message.lower()

        if any(word in message_lower for word in ['portfolio', 'analysis', 'performance']):
            return "Based on your current portfolio, I can see you have a diversified mix of stocks. Your overall performance shows positive growth. I recommend reviewing your sector allocation to ensure proper diversification."

        elif any(word in message_lower for word in ['tax', 'taxes', 'save']):
            return "For tax optimization, consider: 1) Long-term capital gains tax is lower than short-term 2) Use tax-loss harvesting to offset gains 3) Consider ELSS funds for Section 80C benefits 4) Time your stock sales strategically."

        elif any(word in message_lower for word in ['risk', 'risky', 'safe']):
            return "Your current risk profile appears moderate. To manage risk: 1) Maintain proper asset allocation 2) Don't put more than 5-10% in any single stock 3) Consider diversifying across market caps 4) Review and rebalance quarterly."

        elif any(word in message_lower for word in ['rebalance', 'allocation']):
            return "For portfolio rebalancing: 1) Review your target allocation quarterly 2) Rebalance when any asset class deviates by more than 5% 3) Consider tax implications 4) Use new investments to rebalance rather than selling."

        else:
            return "I understand you're asking about investment strategies. Could you be more specific about what aspect you'd like help with? I can assist with portfolio analysis, tax planning, risk assessment, or rebalancing strategies."

    def request_portfolio_analysis(self):
        """Request comprehensive portfolio analysis"""
        self.add_chat_message("You", "Please analyze my portfolio")

        # Generate detailed analysis
        analysis = """Here's your comprehensive portfolio analysis:

📊 PORTFOLIO OVERVIEW:
• Total Investment: Based on your current holdings
• Diversification Score: Good across multiple sectors
• Risk Level: Moderate to High

🎯 SECTOR ALLOCATION:
• Technology: Well represented with quality stocks
• Banking: Good exposure to financial sector
• FMCG: Defensive stocks providing stability

⚠️ RECOMMENDATIONS:
1. Consider adding more international exposure
2. Review position sizing - some stocks may be overweighted
3. Add some bond/debt components for stability
4. Regular rebalancing recommended every quarter

💡 NEXT STEPS:
• Monitor P&L ratios regularly
• Set price alerts for key positions
• Consider tax-loss harvesting opportunities
"""
        self.add_chat_message("AI Advisor", analysis)

    def request_tax_advice(self):
        """Request tax optimization advice"""
        self.add_chat_message("You", "Give me tax saving advice")

        tax_advice = """🏦 TAX OPTIMIZATION STRATEGIES:

📅 SHORT-TERM vs LONG-TERM:
• Hold stocks for >1 year to qualify for LTCG (10% tax)
• STCG is taxed at 15% - plan your exits accordingly

💡 TAX-LOSS HARVESTING:
• Book losses to offset gains
• Reinvest after 31 days to avoid wash sale rules
• Use losses to reduce overall tax liability

🎯 INVESTMENT STRATEGIES:
• ELSS mutual funds for Section 80C (up to ₹1.5L deduction)
• Consider NPS for additional deductions
• Use SIP to average costs and optimize timing

📊 CURRENT YEAR PLANNING:
• Review realized gains/losses
• Plan remaining trades for tax efficiency
• Consider bonus/dividend dates for tax implications

⚡ IMMEDIATE ACTIONS:
• Set up systematic profit booking
• Track all trading expenses for deduction
• Maintain proper records for ITR filing
"""
        self.add_chat_message("AI Advisor", tax_advice)

    def request_rebalancing(self):
        """Request portfolio rebalancing suggestions"""
        self.add_chat_message("You", "Suggest portfolio rebalancing")

        rebalancing = """⚖️ PORTFOLIO REBALANCING SUGGESTIONS:

🎯 TARGET ALLOCATION:
• Large Cap: 60% (Currently: Analyzing your holdings...)
• Mid Cap: 25% (Growth potential)
• Small Cap: 10% (High growth, high risk)
• International: 5% (Diversification)

📊 SECTOR REBALANCING:
• Technology: 20-25% (Good growth prospects)
• Banking: 15-20% (Economic recovery play)
• FMCG: 10-15% (Defensive, stable)
• Healthcare: 10-15% (Demographic trends)
• Others: Balance across remaining sectors

⚡ IMMEDIATE ACTIONS:
1. Identify overweight positions (>10% of portfolio)
2. Book partial profits in outperformers
3. Add to underweight quality stocks
4. Consider systematic rebalancing monthly

🔄 REBALANCING TRIGGERS:
• Any stock >10% of total portfolio
• Sector allocation off by >5% from target
• Major market movements (>10% up/down)
• Quarterly review and adjustment

💡 IMPLEMENTATION:
• Use SIPs for gradual rebalancing
• Time entries during market corrections
• Maintain cash buffer for opportunities
"""
        self.add_chat_message("AI Advisor", rebalancing)

    def request_risk_assessment(self):
        """Request risk assessment"""
        self.add_chat_message("You", "Assess my portfolio risk")

        risk_assessment = """🎯 RISK ASSESSMENT REPORT:

📊 OVERALL RISK LEVEL: MODERATE-HIGH

⚠️ RISK FACTORS:
• Concentration Risk: Check if any single stock >10%
• Sector Risk: Technology and banking exposure
• Market Cap Risk: Small cap allocation
• Liquidity Risk: Review trading volumes

🛡️ RISK METRICS:
• Beta: Estimated portfolio beta vs Nifty
• Volatility: Expected price swings
• Sharpe Ratio: Risk-adjusted returns
• Maximum Drawdown: Worst-case scenario

🔍 DETAILED ANALYSIS:
• High Risk Stocks: Small cap, volatile sectors
• Medium Risk: Mid cap quality stocks
• Low Risk: Large cap dividend stocks, FMCG
• Very Low Risk: Consider adding bonds/FDs

💡 RISK MITIGATION:
1. Diversify across 15-20 stocks minimum
2. Limit single stock exposure to 5-10%
3. Add defensive stocks (utilities, FMCG)
4. Consider stop-losses for risk management
5. Review and adjust based on life stage

⚡ IMMEDIATE RECOMMENDATIONS:
• Set up price alerts for major positions
• Define risk tolerance clearly
• Regular portfolio stress testing
• Emergency fund separate from investments
"""
        self.add_chat_message("AI Advisor", risk_assessment)

    def create_price_alert(self):
        """Create new price alert"""
        try:
            symbol = self.alert_symbol_entry.get().upper().strip()
            alert_type = self.alert_type_combo.get()
            target_price = float(self.alert_price_entry.get())

            if not symbol or not target_price:
                messagebox.showerror("Error", "Please fill all fields")
                return

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Get current price (mock)
            current_price = target_price * 0.95 if alert_type == "Above" else target_price * 1.05

            cursor.execute('''
                INSERT INTO price_alerts (symbol, alert_type, target_price, current_price)
                VALUES (?, ?, ?, ?)
            ''', (symbol, alert_type, target_price, current_price))

            conn.commit()
            conn.close()

            # Clear form
            self.alert_symbol_entry.delete(0, tk.END)
            self.alert_price_entry.delete(0, tk.END)

            self.refresh_alerts()
            self.update_status(f"Price alert created for {symbol}")

        except ValueError:
            messagebox.showerror("Error", "Please enter valid price")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create alert: {str(e)}")

    def refresh_alerts(self):
        """Refresh price alerts display"""
        # Clear existing alerts
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT symbol, alert_type, target_price, current_price, is_active, created_at
            FROM price_alerts WHERE is_active = 1 ORDER BY created_at DESC
        ''')

        alerts = cursor.fetchall()
        conn.close()

        for alert in alerts:
            symbol, alert_type, target_price, current_price, is_active, created_at = alert

            # Determine status
            status = "Active"
            if alert_type == "Above" and current_price >= target_price:
                status = "Triggered"
            elif alert_type == "Below" and current_price <= target_price:
                status = "Triggered"

            self.alerts_tree.insert('', tk.END, values=(
                symbol,
                alert_type,
                f"₹{target_price:,.2f}",
                f"₹{current_price:,.2f}",
                status,
                created_at[:10]  # Date only
            ))

    def delete_selected_alert(self):
        """Delete selected price alert"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alert to delete")
            return

        item = self.alerts_tree.item(selection[0])
        symbol = item['values'][0]

        if messagebox.askyesno("Confirm", f"Delete alert for {symbol}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE price_alerts SET is_active = 0
                    WHERE symbol = ? AND is_active = 1
                ''', (symbol,))

                conn.commit()
                conn.close()

                self.refresh_alerts()
                self.update_status(f"Alert for {symbol} deleted")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete alert: {str(e)}")

    def calculate_tax(self):
        """Calculate tax liability"""
        year = self.tax_year_combo.get()

        # Mock tax calculation
        tax_report = f"""
TAX CALCULATION FOR {year}
{'='*40}

📊 CAPITAL GAINS SUMMARY:
• Short-term Capital Gains (STCG): ₹25,000
• Long-term Capital Gains (LTCG): ₹45,000

💰 TAX LIABILITY:
• STCG Tax (15%): ₹3,750
• LTCG Tax (10% on gains >₹1L): ₹0
  (LTCG up to ₹1L is exempt)

📈 DIVIDEND INCOME:
• Total Dividends Received: ₹8,000
• Tax on Dividends: ₹0 (Tax already deducted)

🏦 TOTAL TAX LIABILITY: ₹3,750

💡 TAX SAVING OPPORTUNITIES:
• Tax-loss harvesting can offset ₹12,000 in gains
• Hold positions >1 year for LTCG benefit
• Consider ELSS investments for 80C deduction

⚡ RECOMMENDATIONS:
1. Book losses before year-end if available
2. Plan stock sales to optimize tax bracket
3. Use LTCG exemption limit of ₹1L annually
4. Maintain proper transaction records

📋 NEXT STEPS:
• Review all transactions for accuracy
• Plan remaining trades strategically
• Consult CA for complex situations
• File ITR with proper schedules
"""

        self.tax_display.delete(1.0, tk.END)
        self.tax_display.insert(1.0, tax_report)

        self.update_status(f"Tax calculation completed for {year}")

    def generate_tax_suggestions(self):
        """Generate tax optimization suggestions"""
        suggestions = """
🎯 PERSONALIZED TAX OPTIMIZATION SUGGESTIONS
{'='*50}

💡 IMMEDIATE ACTIONS (Next 30 Days):
1. Review positions with unrealized losses
2. Consider booking losses to offset gains
3. Check dividend dates for tax-efficient timing
4. Plan any major sales before March 31st

📊 STRATEGIC PLANNING:
• Convert STCG to LTCG by holding >1 year
• Use annual LTCG exemption of ₹1,00,000
• Systematic profit booking to stay in lower tax brackets
• Regular review of gain/loss positions

🏦 INVESTMENT RESTRUCTURING:
• Move short-term trades to separate account
• Focus on dividend-paying stocks for current income
• Consider tax-efficient mutual funds
• Use SIPs to average purchase costs

⚖️ COMPLIANCE & DOCUMENTATION:
• Maintain detailed transaction records
• Track all charges and fees for deduction
• Set up systematic record keeping
• Regular consultation with tax advisor

🎁 ADDITIONAL BENEFITS:
• Explore Section 80C investment options
• Consider NPS for additional tax benefits
• Review health insurance for 80D benefits
• Plan charitable donations under 80G

⏰ YEAR-END CHECKLIST:
□ Review all realized gains/losses
□ Plan remaining transactions
□ Organize all trading statements
□ Prepare for ITR filing
□ Book tax-saving investments
"""

        self.tax_display.delete(1.0, tk.END)
        self.tax_display.insert(1.0, suggestions)

    def update_analytics(self):
        """Update analytics display"""
        # Sector analysis
        self.sector_listbox.delete(0, tk.END)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT sector, SUM(quantity * current_price) as value
            FROM stocks WHERE sector IS NOT NULL
            GROUP BY sector ORDER BY value DESC
        ''')

        sectors = cursor.fetchall()
        total_value = sum(value for _, value in sectors)

        for sector, value in sectors:
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            self.sector_listbox.insert(tk.END, f"{sector}: ₹{value:,.0f} ({percentage:.1f}%)")

        # Performance metrics
        cursor.execute('''
            SELECT AVG((current_price - purchase_price) / purchase_price * 100) as avg_return,
                   COUNT(*) as total_stocks,
                   SUM(CASE WHEN current_price > purchase_price THEN 1 ELSE 0 END) as profitable_stocks
            FROM stocks
        ''')

        metrics = cursor.fetchone()
        conn.close()

        if metrics[0] is not None:
            avg_return, total_stocks, profitable_stocks = metrics

            metrics_text = f"""
PORTFOLIO PERFORMANCE METRICS
{'='*30}

📊 Overall Performance:
• Average Return: {avg_return:.2f}%
• Total Stocks: {total_stocks}
• Profitable Stocks: {profitable_stocks}
• Success Rate: {(profitable_stocks/total_stocks*100):.1f}%

🎯 Risk Metrics:
• Diversification: {'Good' if total_stocks >= 10 else 'Needs Improvement'}
• Sector Concentration: {'Balanced' if len(sectors) >= 5 else 'Concentrated'}

💡 Recommendations:
• {'Excellent diversification!' if total_stocks >= 15 else 'Consider adding more stocks for better diversification'}
• {'Good sector spread' if len(sectors) >= 5 else 'Add stocks from different sectors'}
• Monitor positions regularly and rebalance quarterly
            """

            self.metrics_text.delete(1.0, tk.END)
            self.metrics_text.insert(1.0, metrics_text)

        self.update_status("Analytics updated successfully")

    # Report generation methods
    def generate_portfolio_report(self):
        """Generate portfolio summary report"""
        report = """
PORTFOLIO SUMMARY REPORT
========================
Generated on: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """

This is a comprehensive overview of your investment portfolio including all holdings, performance metrics, and key insights.

[Detailed portfolio analysis would be generated here based on actual data]
"""
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)

    def generate_pnl_report(self):
        """Generate P&L statement"""
        report = """
PROFIT & LOSS STATEMENT
=======================
Period: """ + datetime.now().strftime('%Y-%m-%d') + """

Detailed P&L analysis showing gains, losses, and overall portfolio performance.

[P&L calculations and analysis would be generated here]
"""
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)

    def generate_tax_report(self):
        """Generate tax report"""
        report = """
TAX REPORT
==========
Financial Year: """ + self.tax_year_combo.get() + """

Comprehensive tax analysis including STCG, LTCG, and optimization suggestions.

[Tax calculations and recommendations would be generated here]
"""
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)

    def generate_sector_report(self):
        """Generate sector analysis report"""
        report = """
SECTOR ANALYSIS REPORT
=====================
Date: """ + datetime.now().strftime('%Y-%m-%d') + """

Detailed breakdown of portfolio allocation across different sectors and industries.

[Sector analysis and recommendations would be generated here]
"""
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)

    def generate_performance_report(self):
        """Generate performance report"""
        report = """
PERFORMANCE ANALYSIS REPORT
===========================
Report Date: """ + datetime.now().strftime('%Y-%m-%d') + """

Comprehensive performance analysis including returns, risk metrics, and benchmarking.

[Performance metrics and analysis would be generated here]
"""
        self.report_display.delete(1.0, tk.END)
        self.report_display.insert(1.0, report)

    # Export methods
    def export_to_csv(self):
        """Export data to CSV"""
        self.export_data()  # Reuse existing export functionality

    def export_to_excel(self):
        """Export to Excel (placeholder)"""
        messagebox.showinfo("Export", "Excel export functionality would be implemented here")

    def backup_database(self):
        """Backup database"""
        try:
            import shutil
            from tkinter import filedialog

            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db")],
                title="Backup Database"
            )

            if backup_path:
                shutil.copy2(self.db_path, backup_path)
                messagebox.showinfo("Backup", f"Database backed up to {backup_path}")
                self.update_status("Database backup completed")

        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to backup database: {str(e)}")

    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.after(5000, lambda: self.status_var.set("Ready"))

    def sort_stock_tree(self, tree, column):
        """Sort treeview by column"""
        items = [(tree.set(child, column), child) for child in tree.get_children('')]

        # Determine sort type
        try:
            # Try numeric sort for price column
            if 'Price' in column:
                items.sort(key=lambda x: float(x[0].replace('₹', '').replace(',', '')), reverse=True)
            else:
                # String sort
                items.sort(key=lambda x: x[0].lower())
        except (ValueError, AttributeError):
            # Fallback to string sort
            items.sort(key=lambda x: str(x[0]).lower())

        # Rearrange items
        for index, (val, child) in enumerate(items):
            tree.move(child, '', index)

    # Utility methods
    def load_stock_database(self):
        """Load comprehensive Indian stock database with caching and optimization"""
        # Cache for performance
        if hasattr(self, '_cached_stock_data') and self._cached_stock_data:
            return self._cached_stock_data

        # Try to load from new 2000+ comprehensive database file
        comprehensive_db_2000_path = os.path.join(os.path.dirname(__file__), 'comprehensive_indian_stocks_2000plus.json')

        if os.path.exists(comprehensive_db_2000_path):
            try:
                with open(comprehensive_db_2000_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'stocks' in data and len(data['stocks']) > 0:
                        self._cached_stock_data = data['stocks']
                        return self._cached_stock_data
            except Exception as e:
                print(f"Error loading 2000+ comprehensive database: {e}")

        # Try to load from original comprehensive database file
        comprehensive_db_path = os.path.join(os.path.dirname(__file__), 'comprehensive_indian_stocks.json')

        if os.path.exists(comprehensive_db_path):
            try:
                with open(comprehensive_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        self._cached_stock_data = data
                        return self._cached_stock_data
            except Exception as e:
                print(f"Error loading comprehensive database: {e}")

        # Try to load from existing ShareProfitTracker data if available
        original_path = os.path.join(os.path.dirname(__file__), '..', 'ShareProfitTracker', 'data')

        # Try to load from original project's stock data files
        stock_files = [
            'complete_indian_stocks.json',
            'massive_stocks_2000plus.json',
            'ultra_comprehensive_stocks.json',
            'mega_stock_database.json'
        ]

        for filename in stock_files:
            filepath = os.path.join(original_path, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list) and len(data) > 0:
                            self._cached_stock_data = data[:2000]  # Return first 2000 stocks
                            return self._cached_stock_data
                except Exception as e:
                    continue

        # Fallback to built-in popular Indian stocks database
        self._cached_stock_data = self.get_popular_indian_stocks()
        return self._cached_stock_data

    def get_popular_indian_stocks(self):
        """Get popular Indian stocks database (fallback)"""
        return [
            {'symbol': 'RELIANCE', 'name': 'Reliance Industries Limited', 'sector': 'Oil & Gas', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 2500},
            {'symbol': 'TCS', 'name': 'Tata Consultancy Services', 'sector': 'Technology', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 3200},
            {'symbol': 'INFY', 'name': 'Infosys Limited', 'sector': 'Technology', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 1400},
            {'symbol': 'HDFCBANK', 'name': 'HDFC Bank Limited', 'sector': 'Banking', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 1600},
            {'symbol': 'ICICIBANK', 'name': 'ICICI Bank Limited', 'sector': 'Banking', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 950},
            {'symbol': 'SBIN', 'name': 'State Bank of India', 'sector': 'Banking', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 500},
            {'symbol': 'HINDUNILVR', 'name': 'Hindustan Unilever Limited', 'sector': 'FMCG', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 2400},
            {'symbol': 'ITC', 'name': 'ITC Limited', 'sector': 'FMCG', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 350},
            {'symbol': 'LT', 'name': 'Larsen & Toubro Limited', 'sector': 'Engineering', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 2800},
            {'symbol': 'HCLTECH', 'name': 'HCL Technologies Limited', 'sector': 'Technology', 'exchange': 'NSE', 'market_cap': 'Large Cap', 'current_price': 1200}
        ]

    def get_portfolio_for_analysis(self):
        """Get portfolio data for analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM stocks')
        stocks = cursor.fetchall()
        conn.close()
        return stocks

    def refresh_prices(self):
        """Refresh stock prices (mock implementation)"""
        import random

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT id, symbol, current_price FROM stocks')
        stocks = cursor.fetchall()

        for stock_id, symbol, current_price in stocks:
            # Mock price update with ±2% volatility
            volatility = random.uniform(-0.02, 0.02)
            new_price = current_price * (1 + volatility)

            cursor.execute('UPDATE stocks SET current_price = ? WHERE id = ?', (new_price, stock_id))

        conn.commit()
        conn.close()

        self.refresh_portfolio()
        self.update_status("Prices updated successfully!")

    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Main function to start the application"""
    try:
        print("Starting Unified Share Tracker...")
        app = UnifiedShareTracker()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()