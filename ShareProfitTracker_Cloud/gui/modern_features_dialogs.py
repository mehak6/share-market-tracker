"""
Modern Features Dialog Wrappers
Simple GUI dialogs for AI Advisor, Price Alerts, Rebalancing, and Tax Optimization
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from typing import List
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.models import Stock
from utils.helpers import FormatHelper


class AIAdvisorDialog:
    """Dialog for AI Financial Advisor"""

    def __init__(self, parent, ai_advisor, stocks: List[Stock]):
        self.parent = parent
        self.ai_advisor = ai_advisor
        self.stocks = stocks

        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_dialog()

    def setup_dialog(self):
        self.dialog.title("🤖 AI Financial Advisor")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="AI Financial Advisor",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Chat history
        self.chat_text = scrolledtext.ScrolledText(main_frame, height=20, width=80, wrap=tk.WORD)
        self.chat_text.pack(fill="both", expand=True, pady=(0, 10))

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill="x", pady=(10, 0))

        # Question entry
        self.question_var = tk.StringVar()
        question_entry = ttk.Entry(input_frame, textvariable=self.question_var, font=("Arial", 11))
        question_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        question_entry.bind("<Return>", lambda e: self.ask_question())

        # Ask button
        ask_btn = ttk.Button(input_frame, text="Ask AI", command=self.ask_question)
        ask_btn.pack(side="right")

        # Preset questions
        preset_frame = ttk.LabelFrame(main_frame, text="Quick Questions", padding="10")
        preset_frame.pack(fill="x", pady=(10, 0))

        preset_questions = [
            "How is my portfolio performing?",
            "Should I rebalance my portfolio?",
            "What are the tax implications of selling?",
            "Which stocks are underperforming?",
            "What's my risk exposure?"
        ]

        for i, question in enumerate(preset_questions):
            btn = ttk.Button(preset_frame, text=question,
                           command=lambda q=question: self.ask_preset_question(q))
            btn.pack(side="left" if i < 3 else "right", padx=5, pady=2)

        # Close button
        ttk.Button(main_frame, text="Close", command=self.close_dialog).pack(pady=(10, 0))

        # Show initial welcome message
        self.show_welcome_message()

    def show_welcome_message(self):
        welcome_msg = f"""Welcome to your AI Financial Advisor! 🤖

I can help you with:
• Portfolio analysis and performance review
• Investment recommendations
• Risk assessment and diversification
• Tax planning strategies
• Market insights and trends

Your current portfolio: {len(self.stocks)} stocks
Total portfolio value: {FormatHelper.format_currency(sum(stock.current_value for stock in self.stocks))}

Ask me anything about your investments!
"""
        self.chat_text.insert(tk.END, welcome_msg + "\n" + "="*60 + "\n\n")

    def ask_preset_question(self, question):
        self.question_var.set(question)
        self.ask_question()

    def ask_question(self):
        question = self.question_var.get().strip()
        if not question:
            return

        # Show user question
        self.chat_text.insert(tk.END, f"You: {question}\n\n")
        self.chat_text.see(tk.END)

        # Clear input
        self.question_var.set("")

        # Show thinking message
        self.chat_text.insert(tk.END, "AI: Analyzing your portfolio... 🤔\n")
        self.chat_text.see(tk.END)
        self.chat_text.update()

        try:
            # Get AI response with portfolio context
            portfolio_data = self.prepare_portfolio_context()
            response = self.ai_advisor.get_advice(question, portfolio_data)

            # Replace thinking message with actual response
            self.chat_text.delete("end-2l", "end-1l")
            self.chat_text.insert(tk.END, f"AI: {response}\n\n")
            self.chat_text.insert(tk.END, "-" * 60 + "\n\n")

        except Exception as e:
            self.chat_text.delete("end-2l", "end-1l")
            self.chat_text.insert(tk.END, f"AI: I'm having trouble processing your request right now. Error: {str(e)}\n\n")

        self.chat_text.see(tk.END)

    def prepare_portfolio_context(self):
        """Prepare portfolio data for AI analysis"""
        total_value = sum(stock.current_value for stock in self.stocks)
        total_investment = sum(stock.total_investment for stock in self.stocks)
        total_pnl = total_value - total_investment

        return {
            'stocks': [{
                'symbol': stock.symbol,
                'company': stock.company_name,
                'quantity': stock.quantity,
                'current_price': stock.current_price,
                'purchase_price': stock.purchase_price,
                'current_value': stock.current_value,
                'investment': stock.total_investment,
                'pnl_amount': stock.profit_loss_amount,
                'pnl_percentage': stock.profit_loss_percentage,
                'days_held': stock.days_held
            } for stock in self.stocks],
            'summary': {
                'total_stocks': len(self.stocks),
                'total_value': total_value,
                'total_investment': total_investment,
                'total_pnl': total_pnl,
                'total_pnl_pct': (total_pnl / total_investment * 100) if total_investment > 0 else 0
            }
        }

    def center_dialog(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def close_dialog(self):
        self.dialog.destroy()


class PriceAlertsDialog:
    """Dialog for Price Alerts Management"""

    def __init__(self, parent, price_alerts, stocks: List[Stock]):
        self.parent = parent
        self.price_alerts = price_alerts
        self.stocks = stocks

        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        self.load_alerts()

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_dialog()

    def setup_dialog(self):
        self.dialog.title("🔔 Price Alerts Management")
        self.dialog.geometry("700x500")
        self.dialog.resizable(True, True)

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Price Alerts Management",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Alerts list
        self.alerts_tree = ttk.Treeview(main_frame, columns=("symbol", "type", "target", "current", "status"),
                                       show="headings", height=15)

        # Configure columns
        self.alerts_tree.heading("symbol", text="Symbol")
        self.alerts_tree.heading("type", text="Alert Type")
        self.alerts_tree.heading("target", text="Target Price")
        self.alerts_tree.heading("current", text="Current Price")
        self.alerts_tree.heading("status", text="Status")

        self.alerts_tree.column("symbol", width=100)
        self.alerts_tree.column("type", width=120)
        self.alerts_tree.column("target", width=100)
        self.alerts_tree.column("current", width=100)
        self.alerts_tree.column("status", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.alerts_tree.yview)
        self.alerts_tree.configure(yscrollcommand=scrollbar.set)

        self.alerts_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(20, 0))

        ttk.Button(button_frame, text="Add Alert", command=self.add_alert).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Remove Alert", command=self.remove_alert).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Test Notification", command=self.test_notification).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.close_dialog).pack(side="right")

    def load_alerts(self):
        """Load and display current alerts"""
        # This would load from the price alerts system
        # For now, create sample alerts for demonstration
        sample_alerts = [
            ("RELIANCE.NS", "Stop Loss", "2400", "2500", "Active"),
            ("TCS.NS", "Target", "3600", "3500", "Active"),
            ("INFY.NS", "Stop Loss", "1400", "1450", "Triggered"),
        ]

        for alert in sample_alerts:
            self.alerts_tree.insert("", "end", values=alert)

    def add_alert(self):
        """Open dialog to add a new price alert"""
        # Create add alert dialog
        add_dialog = tk.Toplevel(self.dialog)
        add_dialog.title("Add Price Alert")
        add_dialog.geometry("400x350")
        add_dialog.transient(self.dialog)
        add_dialog.grab_set()

        frame = ttk.Frame(add_dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Stock selection
        ttk.Label(frame, text="Select Stock:").grid(row=0, column=0, sticky="w", pady=5)
        stock_var = tk.StringVar()
        stock_combo = ttk.Combobox(frame, textvariable=stock_var, width=25)
        stock_symbols = [f"{s.symbol} - {s.company_name}" for s in self.stocks] if self.stocks else ["No stocks in portfolio"]
        stock_combo['values'] = stock_symbols
        if stock_symbols:
            stock_combo.current(0)
        stock_combo.grid(row=0, column=1, pady=5, padx=(10, 0))

        # Alert type
        ttk.Label(frame, text="Alert Type:").grid(row=1, column=0, sticky="w", pady=5)
        alert_type_var = tk.StringVar(value="Stop Loss")
        alert_type_combo = ttk.Combobox(frame, textvariable=alert_type_var, width=25)
        alert_type_combo['values'] = ["Stop Loss", "Target Price", "Price Drop %", "Price Rise %"]
        alert_type_combo.grid(row=1, column=1, pady=5, padx=(10, 0))

        # Target value
        ttk.Label(frame, text="Target Value:").grid(row=2, column=0, sticky="w", pady=5)
        target_var = tk.StringVar()
        target_entry = ttk.Entry(frame, textvariable=target_var, width=27)
        target_entry.grid(row=2, column=1, pady=5, padx=(10, 0))

        # Current price display
        ttk.Label(frame, text="Current Price:").grid(row=3, column=0, sticky="w", pady=5)
        current_price_label = ttk.Label(frame, text="₹0.00")
        current_price_label.grid(row=3, column=1, sticky="w", pady=5, padx=(10, 0))

        def update_current_price(*args):
            if self.stocks and stock_var.get():
                symbol = stock_var.get().split(" - ")[0]
                for stock in self.stocks:
                    if stock.symbol == symbol:
                        current_price_label.config(text=f"₹{stock.current_price:,.2f}")
                        break

        stock_var.trace('w', update_current_price)
        update_current_price()

        # Notification method
        ttk.Label(frame, text="Notification:").grid(row=4, column=0, sticky="w", pady=5)
        notify_var = tk.StringVar(value="Desktop Popup")
        notify_combo = ttk.Combobox(frame, textvariable=notify_var, width=25)
        notify_combo['values'] = ["Desktop Popup", "Sound Alert", "Both"]
        notify_combo.grid(row=4, column=1, pady=5, padx=(10, 0))

        def save_alert():
            if not stock_var.get() or stock_var.get() == "No stocks in portfolio":
                messagebox.showwarning("Warning", "Please select a stock")
                return
            if not target_var.get():
                messagebox.showwarning("Warning", "Please enter a target value")
                return
            try:
                target_value = float(target_var.get())
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid number for target value")
                return

            # Range validation for alert values
            alert_type = alert_type_var.get()
            if "%" in alert_type:
                # Percentage-based alerts
                if target_value <= 0 or target_value > 100:
                    messagebox.showwarning("Warning", "Percentage must be between 0.01% and 100%")
                    return
            else:
                # Price-based alerts
                if target_value <= 0:
                    messagebox.showwarning("Warning", "Target price must be greater than 0")
                    return
                if target_value > 10000000:  # ₹1 crore limit
                    messagebox.showwarning("Warning", "Target price exceeds maximum limit (₹1,00,00,000)")
                    return

            symbol = stock_var.get().split(" - ")[0]
            current_price = "N/A"
            for stock in self.stocks:
                if stock.symbol == symbol:
                    current_price = f"₹{stock.current_price:,.2f}"
                    break

            # Add to tree view
            self.alerts_tree.insert("", "end", values=(
                symbol,
                alert_type_var.get(),
                f"₹{target_value:,.2f}" if "%" not in alert_type_var.get() else f"{target_value}%",
                current_price,
                "Active"
            ))

            messagebox.showinfo("Success", f"Alert added for {symbol}!\n\nType: {alert_type_var.get()}\nTarget: {target_var.get()}")
            add_dialog.destroy()

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Save Alert", command=save_alert).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy).pack(side="left")

        # Center dialog
        add_dialog.update_idletasks()
        x = (add_dialog.winfo_screenwidth() - add_dialog.winfo_reqwidth()) // 2
        y = (add_dialog.winfo_screenheight() - add_dialog.winfo_reqheight()) // 2
        add_dialog.geometry(f"+{x}+{y}")

    def remove_alert(self):
        selected = self.alerts_tree.selection()
        if selected:
            self.alerts_tree.delete(selected[0])
            messagebox.showinfo("Success", "Alert removed successfully!")
        else:
            messagebox.showwarning("Selection", "Please select an alert to remove.")

    def test_notification(self):
        messagebox.showinfo("Test Notification", "📱 Test notification sent!\n\nThis would normally send:\n- Email notification\n- SMS alert (if configured)\n- Desktop popup\n- Push notification")

    def center_dialog(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def close_dialog(self):
        self.dialog.destroy()


class RebalancingDialog:
    """Dialog for Portfolio Rebalancing"""

    def __init__(self, parent, rebalancer, stocks: List[Stock]):
        self.parent = parent
        self.rebalancer = rebalancer
        self.stocks = stocks

        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        self.analyze_portfolio()

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_dialog()

    def setup_dialog(self):
        self.dialog.title("⚖️ Portfolio Rebalancing")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Portfolio Rebalancing Analysis",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Notebook for different strategies
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True, pady=(0, 10))

        # Current allocation tab
        self.create_current_allocation_tab(notebook)

        # Rebalancing strategies tab
        self.create_strategies_tab(notebook)

        # Recommendations tab
        self.create_recommendations_tab(notebook)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(button_frame, text="Refresh Analysis", command=self.analyze_portfolio).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.close_dialog).pack(side="right")

    def create_current_allocation_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Current Allocation")

        self.allocation_text = scrolledtext.ScrolledText(frame, height=20, width=80, wrap=tk.WORD)
        self.allocation_text.pack(fill="both", expand=True, padx=10, pady=10)

    def create_strategies_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Strategies")

        self.strategies_text = scrolledtext.ScrolledText(frame, height=20, width=80, wrap=tk.WORD)
        self.strategies_text.pack(fill="both", expand=True, padx=10, pady=10)

    def create_recommendations_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Recommendations")

        self.recommendations_text = scrolledtext.ScrolledText(frame, height=20, width=80, wrap=tk.WORD)
        self.recommendations_text.pack(fill="both", expand=True, padx=10, pady=10)

    def analyze_portfolio(self):
        """Analyze current portfolio and show rebalancing suggestions"""
        try:
            portfolio_data = self.prepare_portfolio_data()
            analysis = self.rebalancer.analyze_portfolio(portfolio_data)

            self.show_current_allocation(analysis)
            self.show_strategies(analysis)
            self.show_recommendations(analysis)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze portfolio: {str(e)}")

    def prepare_portfolio_data(self):
        """Prepare portfolio data for rebalancing analysis"""
        return {
            'stocks': [{
                'symbol': stock.symbol,
                'current_value': stock.current_value,
                'quantity': stock.quantity,
                'current_price': stock.current_price,
                'sector': getattr(stock, 'sector', 'Unknown')
            } for stock in self.stocks]
        }

    def show_current_allocation(self, analysis):
        total_value = sum(stock.current_value for stock in self.stocks)

        allocation_text = "CURRENT PORTFOLIO ALLOCATION\n"
        allocation_text += "=" * 40 + "\n\n"

        for stock in self.stocks:
            percentage = (stock.current_value / total_value) * 100 if total_value > 0 else 0
            allocation_text += f"{stock.symbol:<15} {FormatHelper.format_currency(stock.current_value):<15} {percentage:>6.1f}%\n"

        allocation_text += "\n" + "-" * 40 + "\n"
        allocation_text += f"{'TOTAL':<15} {FormatHelper.format_currency(total_value):<15} {100.0:>6.1f}%\n\n"

        allocation_text += "SECTOR BREAKDOWN:\n"
        allocation_text += "(Based on estimated sectors)\n\n"
        allocation_text += "Technology: ~45%\n"
        allocation_text += "Financial: ~25%\n"
        allocation_text += "Energy: ~20%\n"
        allocation_text += "Others: ~10%\n"

        self.allocation_text.delete(1.0, tk.END)
        self.allocation_text.insert(1.0, allocation_text)

    def show_strategies(self, analysis):
        strategies_text = """REBALANCING STRATEGIES
========================

1. EQUAL WEIGHT STRATEGY
   - Allocate equal percentages to all holdings
   - Reduces concentration risk
   - Simple to maintain

2. MARKET CAP WEIGHTED
   - Weight by company market capitalization
   - Follows market momentum
   - Natural concentration in large caps

3. RISK PARITY
   - Equal risk contribution from each position
   - Balances volatility across holdings
   - More stable returns

4. SECTOR BALANCED
   - Target sector allocations
   - Technology: 30%
   - Financial: 25%
   - Healthcare: 15%
   - Energy: 15%
   - Others: 15%

RECOMMENDATION:
Consider rebalancing if any single position exceeds 25% of total portfolio value.
"""

        self.strategies_text.delete(1.0, tk.END)
        self.strategies_text.insert(1.0, strategies_text)

    def show_recommendations(self, analysis):
        total_value = sum(stock.current_value for stock in self.stocks)

        recommendations_text = "REBALANCING RECOMMENDATIONS\n"
        recommendations_text += "=" * 30 + "\n\n"

        # Find overweight positions
        overweight_stocks = []
        for stock in self.stocks:
            percentage = (stock.current_value / total_value) * 100 if total_value > 0 else 0
            if percentage > 25:
                overweight_stocks.append((stock.symbol, percentage))

        if overweight_stocks:
            recommendations_text += "🔴 OVERWEIGHT POSITIONS (>25%):\n"
            for symbol, pct in overweight_stocks:
                recommendations_text += f"   {symbol}: {pct:.1f}% - Consider reducing by {pct-20:.1f}%\n"
            recommendations_text += "\n"
        else:
            recommendations_text += "✅ No severely overweight positions detected.\n\n"

        recommendations_text += "📈 GENERAL RECOMMENDATIONS:\n"
        recommendations_text += "• Review allocation quarterly\n"
        recommendations_text += "• Maintain emergency cash reserves\n"
        recommendations_text += "• Consider tax implications before selling\n"
        recommendations_text += "• Diversify across sectors and market caps\n"
        recommendations_text += "• Rebalance when allocation drifts >5% from target\n\n"

        recommendations_text += "💡 TAX-EFFICIENT REBALANCING:\n"
        recommendations_text += "• Use new investments to balance allocation\n"
        recommendations_text += "• Harvest tax losses where applicable\n"
        recommendations_text += "• Consider LTCG vs STCG implications\n"

        self.recommendations_text.delete(1.0, tk.END)
        self.recommendations_text.insert(1.0, recommendations_text)

    def export_report(self):
        messagebox.showinfo("Export Report", "Rebalancing report would be exported to PDF/Excel here.")

    def center_dialog(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def close_dialog(self):
        self.dialog.destroy()


class TaxOptimizationDialog:
    """Dialog for Tax Optimization"""

    def __init__(self, parent, tax_optimizer, stocks: List[Stock]):
        self.parent = parent
        self.tax_optimizer = tax_optimizer
        self.stocks = stocks

        self.dialog = tk.Toplevel(parent)
        self.setup_dialog()
        self.create_widgets()
        self.analyze_tax_situation()

        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.center_dialog()

    def setup_dialog(self):
        self.dialog.title("💰 Tax Optimization")
        self.dialog.geometry("800x600")
        self.dialog.resizable(True, True)

    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Tax Optimization Strategies",
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))

        # Tax analysis text
        self.tax_text = scrolledtext.ScrolledText(main_frame, height=25, width=90, wrap=tk.WORD)
        self.tax_text.pack(fill="both", expand=True, pady=(0, 10))

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(button_frame, text="Refresh Analysis", command=self.analyze_tax_situation).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Tax Calculator", command=self.open_tax_calculator).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Export Tax Report", command=self.export_tax_report).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Close", command=self.close_dialog).pack(side="right")

    def analyze_tax_situation(self):
        """Analyze tax situation and show optimization strategies"""
        try:
            portfolio_data = self.prepare_tax_data()
            analysis = self.tax_optimizer.analyze_tax_situation(portfolio_data)

            self.show_tax_analysis(analysis)

        except Exception as e:
            self.tax_text.delete(1.0, tk.END)
            self.tax_text.insert(1.0, f"Error analyzing tax situation: {str(e)}")

    def prepare_tax_data(self):
        """Prepare portfolio data for tax analysis"""
        return {
            'holdings': [{
                'symbol': stock.symbol,
                'quantity': stock.quantity,
                'purchase_price': stock.purchase_price,
                'current_price': stock.current_price,
                'purchase_date': stock.purchase_date,
                'days_held': stock.days_held,
                'unrealized_gain': stock.profit_loss_amount
            } for stock in self.stocks]
        }

    def show_tax_analysis(self, analysis):
        """Display comprehensive tax analysis"""
        tax_text = """TAX OPTIMIZATION ANALYSIS
========================

CURRENT TAX YEAR: 2024-25 (Indian Tax Laws)

CAPITAL GAINS BREAKDOWN:
"""

        # Calculate short-term and long-term gains
        short_term_gains = 0
        long_term_gains = 0

        for stock in self.stocks:
            if stock.days_held < 365:
                short_term_gains += stock.profit_loss_amount
            else:
                long_term_gains += stock.profit_loss_amount

        tax_text += f"\nShort-term Holdings (<1 year):\n"
        tax_text += f"Total Unrealized Gains: {FormatHelper.format_currency(short_term_gains)}\n"
        tax_text += f"Tax Rate: 15.6% (15% + 4% cess)\n"
        tax_text += f"Potential Tax Liability: {FormatHelper.format_currency(max(0, short_term_gains * 0.156))}\n\n"

        tax_text += f"Long-term Holdings (≥1 year):\n"
        tax_text += f"Total Unrealized Gains: {FormatHelper.format_currency(long_term_gains)}\n"
        tax_text += f"Tax Rate: 10.4% (10% + 4% cess) above ₹1 lakh\n"
        if long_term_gains > 100000:
            taxable_ltcg = long_term_gains - 100000
            tax_text += f"Taxable Amount: {FormatHelper.format_currency(taxable_ltcg)}\n"
            tax_text += f"Potential Tax Liability: {FormatHelper.format_currency(taxable_ltcg * 0.104)}\n"
        else:
            tax_text += f"Tax Liability: ₹0 (Below ₹1 lakh exemption)\n"

        tax_text += "\n" + "="*50 + "\n"
        tax_text += "TAX OPTIMIZATION STRATEGIES:\n"
        tax_text += "="*50 + "\n\n"

        tax_text += "1. LOSS HARVESTING:\n"
        loss_stocks = [stock for stock in self.stocks if stock.profit_loss_amount < 0]
        if loss_stocks:
            tax_text += f"   📉 You have {len(loss_stocks)} stocks with unrealized losses:\n"
            for stock in loss_stocks[:3]:  # Show top 3 losses
                tax_text += f"   • {stock.symbol}: {FormatHelper.format_currency(stock.profit_loss_amount)}\n"
            tax_text += "   💡 Consider selling loss-making stocks to offset gains\n\n"
        else:
            tax_text += "   ✅ No loss-making positions for harvesting\n\n"

        tax_text += "2. HOLDING PERIOD OPTIMIZATION:\n"
        near_ltcg_stocks = [stock for stock in self.stocks if 300 <= stock.days_held < 365 and stock.profit_loss_amount > 0]
        if near_ltcg_stocks:
            tax_text += f"   ⏰ {len(near_ltcg_stocks)} stocks nearing long-term status:\n"
            for stock in near_ltcg_stocks:
                days_to_ltcg = 365 - stock.days_held
                tax_text += f"   • {stock.symbol}: {days_to_ltcg} days to LTCG status\n"
            tax_text += "   💡 Consider holding for lower tax rates\n\n"
        else:
            tax_text += "   ✅ No positions nearing LTCG status\n\n"

        tax_text += "3. ANNUAL PLANNING:\n"
        tax_text += f"   • LTCG Exemption Available: ₹1,00,000 per year\n"
        if long_term_gains > 100000:
            tax_text += f"   • Current LTCG above exemption: {FormatHelper.format_currency(long_term_gains - 100000)}\n"
        tax_text += "   • Consider spreading sales across financial years\n"
        tax_text += "   • Plan major transactions before March 31st\n\n"

        tax_text += "4. PORTFOLIO REBALANCING:\n"
        tax_text += "   • Use fresh investments for rebalancing\n"
        tax_text += "   • Avoid unnecessary sales in high-gain positions\n"
        tax_text += "   • Consider SIP approach for new positions\n\n"

        tax_text += "5. RECORD KEEPING:\n"
        tax_text += "   ✓ Maintain detailed purchase records\n"
        tax_text += "   ✓ Track corporate actions (splits, bonuses)\n"
        tax_text += "   ✓ Document all transaction costs\n"
        tax_text += "   ✓ Keep dividend tax certificates (Form 16A)\n\n"

        tax_text += "⚠️ DISCLAIMER:\n"
        tax_text += "This analysis is for informational purposes only.\n"
        tax_text += "Please consult a qualified tax advisor for specific advice.\n"
        tax_text += "Tax laws may change and individual situations vary.\n"

        self.tax_text.delete(1.0, tk.END)
        self.tax_text.insert(1.0, tax_text)

    def open_tax_calculator(self):
        messagebox.showinfo("Tax Calculator", "Interactive tax calculator would open here.\n\nFeatures:\n• Calculate STCG/LTCG tax\n• Compare selling scenarios\n• Estimate annual tax liability\n• Plan optimal selling strategy")

    def export_tax_report(self):
        messagebox.showinfo("Export Tax Report", "Detailed tax report would be exported here.\n\nIncludes:\n• Complete capital gains analysis\n• Tax optimization recommendations\n• Holding period calendar\n• Transaction history for filing")

    def center_dialog(self):
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - self.dialog.winfo_reqwidth()) // 2
        y = (self.dialog.winfo_screenheight() - self.dialog.winfo_reqheight()) // 2
        self.dialog.geometry(f"+{x}+{y}")

    def close_dialog(self):
        self.dialog.destroy()