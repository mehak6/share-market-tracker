"""
Cloud Login Dialog for ShareProfitTracker
Handles cloud account login/registration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.modern_ui import ModernUI
    from services.cloud_sync import CloudSyncService
except ImportError:
    from .modern_ui import ModernUI
    from services.cloud_sync import CloudSyncService


class CloudLoginDialog:
    """Dialog for cloud account login and registration"""

    def __init__(self, parent, cloud_service: CloudSyncService, on_login_success=None):
        self.parent = parent
        self.cloud_service = cloud_service
        self.on_login_success = on_login_success

        self.dialog = None
        self.create_dialog()

    def create_dialog(self):
        """Create the login dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Cloud Account")
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        # Center
        self.dialog.transient(self.parent)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"400x450+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Cloud Sync",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(pady=(0, 5))

        # Subtitle
        subtitle = ttk.Label(
            main_frame,
            text="Access your portfolio from anywhere",
            font=("Segoe UI", 9)
        )
        subtitle.pack(pady=(0, 20))

        # Notebook for Login/Register tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill="both", expand=True)

        # Login tab
        self.create_login_tab(notebook)

        # Register tab
        self.create_register_tab(notebook)

        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side="right", pady=(15, 0))

    def create_login_tab(self, notebook):
        """Create login tab"""
        login_frame = ttk.Frame(notebook, padding="15")
        notebook.add(login_frame, text="Login")

        # Email
        ttk.Label(login_frame, text="Email:").grid(row=0, column=0, sticky="w", pady=5)
        self.login_email = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.login_email, width=35).grid(
            row=0, column=1, pady=5, padx=(10, 0))

        # Password
        ttk.Label(login_frame, text="Password:").grid(row=1, column=0, sticky="w", pady=5)
        self.login_password = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.login_password, show="*", width=35).grid(
            row=1, column=1, pady=5, padx=(10, 0))

        # Login button
        ttk.Button(
            login_frame,
            text="Login",
            command=self.do_login
        ).grid(row=2, column=0, columnspan=2, pady=(20, 10))

        # Status
        self.login_status = ttk.Label(login_frame, text="", foreground="gray")
        self.login_status.grid(row=3, column=0, columnspan=2, pady=5)

    def create_register_tab(self, notebook):
        """Create registration tab"""
        register_frame = ttk.Frame(notebook, padding="15")
        notebook.add(register_frame, text="Register")

        # Display name
        ttk.Label(register_frame, text="Display Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.reg_name = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_name, width=35).grid(
            row=0, column=1, pady=5, padx=(10, 0))

        # Email
        ttk.Label(register_frame, text="Email:").grid(row=1, column=0, sticky="w", pady=5)
        self.reg_email = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_email, width=35).grid(
            row=1, column=1, pady=5, padx=(10, 0))

        # Password
        ttk.Label(register_frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        self.reg_password = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_password, show="*", width=35).grid(
            row=2, column=1, pady=5, padx=(10, 0))

        # Confirm password
        ttk.Label(register_frame, text="Confirm:").grid(row=3, column=0, sticky="w", pady=5)
        self.reg_confirm = tk.StringVar()
        ttk.Entry(register_frame, textvariable=self.reg_confirm, show="*", width=35).grid(
            row=3, column=1, pady=5, padx=(10, 0))

        # Register button
        ttk.Button(
            register_frame,
            text="Create Account",
            command=self.do_register
        ).grid(row=4, column=0, columnspan=2, pady=(20, 10))

        # Status
        self.register_status = ttk.Label(register_frame, text="", foreground="gray")
        self.register_status.grid(row=5, column=0, columnspan=2, pady=5)

    def do_login(self):
        """Perform login"""
        email = self.login_email.get().strip()
        password = self.login_password.get()

        if not email or not password:
            messagebox.showwarning("Warning", "Please enter email and password")
            return

        self.login_status.config(text="Logging in...", foreground="blue")
        self.dialog.update()

        result = self.cloud_service.login(email, password)

        if result['success']:
            self.login_status.config(text="Login successful!", foreground="green")
            messagebox.showinfo("Success", f"Welcome, {result.get('display_name', email)}!")

            if self.on_login_success:
                self.on_login_success()

            self.dialog.destroy()
        else:
            self.login_status.config(text=result['message'], foreground="red")

    def do_register(self):
        """Perform registration"""
        name = self.reg_name.get().strip()
        email = self.reg_email.get().strip()
        password = self.reg_password.get()
        confirm = self.reg_confirm.get()

        if not name:
            messagebox.showwarning("Warning", "Please enter your display name")
            return
        if not email:
            messagebox.showwarning("Warning", "Please enter your email")
            return
        if not password:
            messagebox.showwarning("Warning", "Please enter a password")
            return
        if len(password) < 6:
            messagebox.showwarning("Warning", "Password must be at least 6 characters")
            return
        if password != confirm:
            messagebox.showwarning("Warning", "Passwords do not match")
            return

        self.register_status.config(text="Creating account...", foreground="blue")
        self.dialog.update()

        result = self.cloud_service.register(email, password, name)

        if result['success']:
            self.register_status.config(text="Account created!", foreground="green")
            messagebox.showinfo("Success", "Account created successfully!\nYou are now logged in.")

            if self.on_login_success:
                self.on_login_success()

            self.dialog.destroy()
        else:
            self.register_status.config(text=result['message'], foreground="red")


class CloudSyncDialog:
    """Dialog for syncing data with cloud"""

    def __init__(self, parent, cloud_service: CloudSyncService, db_manager):
        self.parent = parent
        self.cloud_service = cloud_service
        self.db_manager = db_manager

        self.dialog = None
        self.create_dialog()

    def create_dialog(self):
        """Create sync dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Cloud Sync")
        self.dialog.geometry("450x400")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()

        # Center
        self.dialog.transient(self.parent)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"450x400+{x}+{y}")

        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            main_frame,
            text="Cloud Sync",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 5))

        # User info
        if self.cloud_service.is_logged_in():
            ttk.Label(
                main_frame,
                text=f"Logged in as: {self.cloud_service.display_name}",
                font=("Segoe UI", 9)
            ).pack(pady=(0, 15))
        else:
            ttk.Label(
                main_frame,
                text="Not logged in",
                foreground="red"
            ).pack(pady=(0, 15))

        # Sync options frame
        options_frame = ttk.LabelFrame(main_frame, text="Sync Options", padding="15")
        options_frame.pack(fill="x", pady=(0, 15))

        # Upload button
        ttk.Button(
            options_frame,
            text="Upload to Cloud",
            command=self.upload_to_cloud,
            width=25
        ).pack(pady=5)
        ttk.Label(
            options_frame,
            text="Send your local data to cloud",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(pady=(0, 10))

        # Download button
        ttk.Button(
            options_frame,
            text="Download from Cloud",
            command=self.download_from_cloud,
            width=25
        ).pack(pady=5)
        ttk.Label(
            options_frame,
            text="Replace local data with cloud data",
            font=("Segoe UI", 8),
            foreground="gray"
        ).pack(pady=(0, 10))

        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.pack(fill="both", expand=True, pady=(0, 15))

        self.status_text = tk.Text(status_frame, height=6, width=50, state="disabled")
        self.status_text.pack(fill="both", expand=True)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")

        ttk.Button(
            button_frame,
            text="Check Status",
            command=self.check_status
        ).pack(side="left")

        ttk.Button(
            button_frame,
            text="Logout",
            command=self.logout
        ).pack(side="left", padx=(10, 0))

        ttk.Button(
            button_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side="right")

    def log_status(self, message: str, clear: bool = False):
        """Log message to status area"""
        self.status_text.config(state="normal")
        if clear:
            self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.dialog.update()

    def upload_to_cloud(self):
        """Upload local data to cloud"""
        if not self.cloud_service.is_logged_in():
            messagebox.showwarning("Warning", "Please login first")
            return

        if not messagebox.askyesno("Confirm Upload",
                                   "This will replace your cloud data with local data.\n\nContinue?"):
            return

        self.log_status("Starting upload...", clear=True)

        try:
            # Get local data
            stocks = self.db_manager.get_all_stocks()
            cash = self.db_manager.get_all_cash_transactions()
            expenses = self.db_manager.get_all_expenses()
            dividends = self.db_manager.get_all_dividends()

            self.log_status(f"Local data: {len(stocks)} stocks, {len(cash)} transactions")

            # Upload
            result = self.cloud_service.upload_data(stocks, cash, expenses, dividends)

            if result['success']:
                self.log_status(f"SUCCESS: {result['message']}")
                messagebox.showinfo("Success", "Data uploaded to cloud successfully!")
            else:
                self.log_status(f"ERROR: {result['message']}")
                messagebox.showerror("Error", result['message'])

        except Exception as e:
            self.log_status(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

    def download_from_cloud(self):
        """Download cloud data to local"""
        if not self.cloud_service.is_logged_in():
            messagebox.showwarning("Warning", "Please login first")
            return

        if not messagebox.askyesno("Confirm Download",
                                   "This will replace your LOCAL data with cloud data.\n\n"
                                   "Your current local data will be lost!\n\nContinue?"):
            return

        self.log_status("Starting download...", clear=True)

        try:
            result = self.cloud_service.download_data()

            if result['success']:
                data = result.get('data', {})
                self.log_status(f"Downloaded: {len(data.get('stocks', []))} stocks")

                # TODO: Import data to local database
                # This requires implementing import methods in db_manager

                self.log_status(f"SUCCESS: {result['message']}")
                messagebox.showinfo("Success",
                                   "Data downloaded from cloud!\n\n"
                                   "Note: Local import not yet implemented.\n"
                                   "Data is available in the result.")
            else:
                self.log_status(f"ERROR: {result['message']}")
                messagebox.showerror("Error", result['message'])

        except Exception as e:
            self.log_status(f"ERROR: {str(e)}")
            messagebox.showerror("Error", str(e))

    def check_status(self):
        """Check cloud sync status"""
        if not self.cloud_service.is_logged_in():
            self.log_status("Not logged in", clear=True)
            return

        self.log_status("Checking cloud status...", clear=True)

        result = self.cloud_service.get_sync_status()

        if result['success']:
            data = result['data']
            self.log_status(f"Cloud data:")
            self.log_status(f"  Stocks: {data.get('stocks_count', 0)}")
            self.log_status(f"  Transactions: {data.get('cash_transactions_count', 0)}")
            self.log_status(f"  Expenses: {data.get('expenses_count', 0)}")
            self.log_status(f"  Dividends: {data.get('dividends_count', 0)}")
        else:
            self.log_status(f"ERROR: {result['message']}")

    def logout(self):
        """Logout from cloud"""
        self.cloud_service.logout()
        messagebox.showinfo("Logged Out", "You have been logged out from cloud.")
        self.dialog.destroy()
