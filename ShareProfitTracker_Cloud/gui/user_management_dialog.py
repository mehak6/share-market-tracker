"""
User Management Dialog for ShareProfitTracker

Allows creating, editing, deleting, and switching between users.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from gui.modern_ui import ModernUI
except ImportError:
    class ModernUI:
        FONTS = {'heading': ('Segoe UI', 14, 'bold'), 'normal': ('Segoe UI', 10)}


class UserManagementDialog:
    """Dialog for managing application users"""

    def __init__(self, parent, db_manager, on_user_changed=None):
        self.parent = parent
        self.db_manager = db_manager
        self.on_user_changed = on_user_changed  # Callback when user switches

        self.dialog = None
        self.users_tree = None

        self.create_dialog()
        self.load_users()

    def create_dialog(self):
        """Create the user management dialog window"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("User Management")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.grab_set()  # Make it modal

        # Center the dialog
        self.dialog.transient(self.parent)
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"500x450+{x}+{y}")

        # Create main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill="both", expand=True)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="User Management",
            font=ModernUI.FONTS['heading']
        )
        title_label.pack(anchor="w", pady=(0, 10))

        # Description
        desc_label = ttk.Label(
            main_frame,
            text="Manage user accounts. Each user has separate portfolio data.",
            wraplength=450
        )
        desc_label.pack(anchor="w", pady=(0, 15))

        # Users list frame
        list_frame = ttk.LabelFrame(main_frame, text="Users", padding="10")
        list_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Treeview for users
        columns = ("ID", "Username", "Display Name", "Status")
        self.users_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)

        # Configure columns
        self.users_tree.heading("ID", text="ID")
        self.users_tree.heading("Username", text="Username")
        self.users_tree.heading("Display Name", text="Display Name")
        self.users_tree.heading("Status", text="Status")

        self.users_tree.column("ID", width=40, anchor="center")
        self.users_tree.column("Username", width=120)
        self.users_tree.column("Display Name", width=150)
        self.users_tree.column("Status", width=80, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)

        self.users_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Configure tag for active user
        self.users_tree.tag_configure("active", background="#d4edda")

        # Action buttons frame
        actions_frame = ttk.Frame(main_frame)
        actions_frame.pack(fill="x", pady=(0, 15))

        ttk.Button(
            actions_frame,
            text="Add User",
            command=self.add_user
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Edit User",
            command=self.edit_user
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Delete User",
            command=self.delete_user
        ).pack(side="left", padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="Switch to Selected",
            command=self.switch_user
        ).pack(side="left")

        # Close button
        ttk.Button(
            main_frame,
            text="Close",
            command=self.dialog.destroy
        ).pack(side="right")

    def load_users(self):
        """Load users from database into treeview"""
        # Clear existing items
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)

        # Get all users
        users = self.db_manager.get_all_users()

        for user in users:
            status = "Active" if user.get('is_active') else ""
            tags = ("active",) if user.get('is_active') else ()

            self.users_tree.insert("", "end", values=(
                user['id'],
                user['username'],
                user['display_name'],
                status
            ), tags=tags)

    def add_user(self):
        """Add a new user"""
        # Create add user dialog
        add_dialog = tk.Toplevel(self.dialog)
        add_dialog.title("Add New User")
        add_dialog.geometry("350x200")
        add_dialog.resizable(False, False)
        add_dialog.grab_set()
        add_dialog.transient(self.dialog)

        # Center
        add_dialog.update_idletasks()
        x = (add_dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (add_dialog.winfo_screenheight() // 2) - (200 // 2)
        add_dialog.geometry(f"350x200+{x}+{y}")

        frame = ttk.Frame(add_dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Username
        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        username_var = tk.StringVar()
        username_entry = ttk.Entry(frame, textvariable=username_var, width=30)
        username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        # Display name
        ttk.Label(frame, text="Display Name:").grid(row=1, column=0, sticky="w", pady=5)
        display_var = tk.StringVar()
        display_entry = ttk.Entry(frame, textvariable=display_var, width=30)
        display_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        def save_user():
            username = username_var.get().strip()
            display_name = display_var.get().strip()

            if not username:
                messagebox.showwarning("Warning", "Username is required")
                return
            if not display_name:
                display_name = username

            # Check for duplicate username
            existing_users = self.db_manager.get_all_users()
            for user in existing_users:
                if user['username'].lower() == username.lower():
                    messagebox.showwarning("Warning", f"Username '{username}' already exists")
                    return

            try:
                user_id = self.db_manager.add_user(username, display_name)
                messagebox.showinfo("Success", f"User '{display_name}' created successfully!")
                add_dialog.destroy()
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create user: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Save", command=save_user).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=add_dialog.destroy).pack(side="left")

        username_entry.focus()

    def edit_user(self):
        """Edit selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to edit")
            return

        item = self.users_tree.item(selected[0])
        user_id = item['values'][0]
        current_username = item['values'][1]
        current_display = item['values'][2]

        # Create edit dialog
        edit_dialog = tk.Toplevel(self.dialog)
        edit_dialog.title("Edit User")
        edit_dialog.geometry("350x200")
        edit_dialog.resizable(False, False)
        edit_dialog.grab_set()
        edit_dialog.transient(self.dialog)

        # Center
        edit_dialog.update_idletasks()
        x = (edit_dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (edit_dialog.winfo_screenheight() // 2) - (200 // 2)
        edit_dialog.geometry(f"350x200+{x}+{y}")

        frame = ttk.Frame(edit_dialog, padding="20")
        frame.pack(fill="both", expand=True)

        # Username
        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="w", pady=5)
        username_var = tk.StringVar(value=current_username)
        username_entry = ttk.Entry(frame, textvariable=username_var, width=30)
        username_entry.grid(row=0, column=1, pady=5, padx=(10, 0))

        # Display name
        ttk.Label(frame, text="Display Name:").grid(row=1, column=0, sticky="w", pady=5)
        display_var = tk.StringVar(value=current_display)
        display_entry = ttk.Entry(frame, textvariable=display_var, width=30)
        display_entry.grid(row=1, column=1, pady=5, padx=(10, 0))

        def update_user():
            username = username_var.get().strip()
            display_name = display_var.get().strip()

            if not username:
                messagebox.showwarning("Warning", "Username is required")
                return
            if not display_name:
                display_name = username

            # Check for duplicate username (excluding current user)
            existing_users = self.db_manager.get_all_users()
            for user in existing_users:
                if user['username'].lower() == username.lower() and user['id'] != user_id:
                    messagebox.showwarning("Warning", f"Username '{username}' already exists")
                    return

            try:
                self.db_manager.update_user(user_id, username, display_name)
                messagebox.showinfo("Success", f"User updated successfully!")
                edit_dialog.destroy()
                self.load_users()

                # Notify parent if active user was edited
                active_user = self.db_manager.get_active_user()
                if active_user and active_user['id'] == user_id and self.on_user_changed:
                    self.on_user_changed()

            except Exception as e:
                messagebox.showerror("Error", f"Failed to update user: {str(e)}")

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))

        ttk.Button(button_frame, text="Update", command=update_user).pack(side="left", padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=edit_dialog.destroy).pack(side="left")

    def delete_user(self):
        """Delete selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to delete")
            return

        item = self.users_tree.item(selected[0])
        user_id = item['values'][0]
        username = item['values'][1]
        is_active = item['values'][3] == "Active"

        # Check if trying to delete active user
        if is_active:
            messagebox.showwarning("Warning", "Cannot delete the active user. Please switch to another user first.")
            return

        # Count users
        users = self.db_manager.get_all_users()
        if len(users) <= 1:
            messagebox.showwarning("Warning", "Cannot delete the last user. At least one user must exist.")
            return

        # Confirm deletion
        if messagebox.askyesno("Confirm Delete",
                               f"Are you sure you want to delete user '{username}'?\n\n"
                               f"This will permanently delete all their portfolio data, "
                               f"including stocks, cash transactions, expenses, and dividends."):
            try:
                self.db_manager.delete_user(user_id)
                messagebox.showinfo("Success", f"User '{username}' deleted successfully!")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete user: {str(e)}")

    def switch_user(self):
        """Switch to selected user"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a user to switch to")
            return

        item = self.users_tree.item(selected[0])
        user_id = item['values'][0]
        display_name = item['values'][2]
        is_active = item['values'][3] == "Active"

        if is_active:
            messagebox.showinfo("Info", f"'{display_name}' is already the active user")
            return

        try:
            self.db_manager.set_active_user(user_id)
            messagebox.showinfo("Success", f"Switched to user '{display_name}'")
            self.load_users()

            # Notify parent to reload data
            if self.on_user_changed:
                self.on_user_changed()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to switch user: {str(e)}")
