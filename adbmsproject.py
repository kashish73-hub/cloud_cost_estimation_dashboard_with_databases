import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Use seaborn theme
sns.set(style="whitegrid")

class CloudCostDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("☁️Cloud Cost Estimation Dashboard")
        self.root.state("zoomed")  # Full screen
        self.root.configure(bg="#dff6ff")

        # Initialize database
        self.setup_database()

        # --- Header ---
        header = tk.Label(self.root, text="☁️Cloud Cost Estimation Dashboard☁️",
                          bg="#007acc", fg="white",
                          font=("Segoe UI", 26, "bold"), pady=18)
        header.pack(fill="x")

        # --- Input Frame ---
        form_frame = tk.Frame(self.root, bg="#c7e2ec")
        form_frame.pack(pady=20)

        style = ttk.Style()
        style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8)
        style.map("TButton",
                  background=[("active", "#005f99"), ("!disabled", "#0088cc")],
                  foreground=[("active", "white")])

        tk.Label(form_frame, text="Enter VM Count:", bg="#dff6ff", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=15, pady=10, sticky="e")
        self.vm_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=12, relief="solid", borderwidth=1)
        self.vm_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Hours Used:", bg="#dff6ff", font=("Segoe UI", 14, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="e")
        self.hours_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=12, relief="solid", borderwidth=1)
        self.hours_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(form_frame, text="Rate per Hour (₹):", bg="#dff6ff", font=("Segoe UI", 14, "bold")).grid(row=2, column=0, padx=15, pady=10, sticky="e")
        self.rate_entry = tk.Entry(form_frame, font=("Segoe UI", 14), width=12, relief="solid", borderwidth=1)
        self.rate_entry.grid(row=2, column=1, padx=10, pady=10)

        # Buttons
        ttk.Button(form_frame, text="💰 Calculate", command=self.calculate_cost).grid(row=3, column=0, padx=15, pady=15)
        ttk.Button(form_frame, text="📊 Show Graph", command=self.show_graph).grid(row=3, column=1, padx=15, pady=15)
        ttk.Button(form_frame, text="🧹 Clear", command=self.clear_all).grid(row=3, column=2, padx=15, pady=15)

        # --- Output Frame ---
        output_frame = tk.LabelFrame(self.root, text="Cost Summary", font=("Segoe UI", 14, "bold"),
                                     bg="#f2f9ff", fg="#005f99", padx=10, pady=10)
        output_frame.pack(padx=20, pady=15, fill="x")

        self.output_text = tk.Text(output_frame, height=7, font=("Consolas", 12), wrap="word",
                                   bg="#ffffff", relief="solid", borderwidth=1)
        self.output_text.pack(fill="x", padx=10, pady=10)

        # --- Table Frame ---
        table_frame = tk.LabelFrame(self.root, text="Recent Cost Records", font=("Segoe UI", 14, "bold"),
                                    bg="#f2f9ff", fg="#005f99")
        table_frame.pack(padx=20, pady=10, fill="both", expand=True)

        columns = ("vm", "hours", "rate", "cost")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col.upper(), anchor="center")
            self.tree.column(col, width=200, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # --- Stats Frame ---
        self.stats_label = tk.Label(self.root, text="", bg="#b8c5ca", font=("Segoe UI", 14, "bold"), fg="#004466")
        self.stats_label.pack(pady=10)

        self.records = []

    def setup_database(self):
        """Initialize MySQL database connection with auto-creation"""
        try:
            # First connect without database to create it
            temp_conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234"  # Add your MySQL password here if needed
            )
            temp_cursor = temp_conn.cursor()
            
            # Create database if not exists
            temp_cursor.execute("CREATE DATABASE IF NOT EXISTS cloud_cost_db")
            temp_cursor.close()
            temp_conn.close()
            
            # Now connect to the database
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="1234",  # Add your MySQL password here if needed
                database="cloud_cost_db"
            )
            self.cursor = self.conn.cursor()
            
            # Create table if not exists
            create_table_query = """
            CREATE TABLE IF NOT EXISTS cost_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vm_count INT NOT NULL,
                hours_used DECIMAL(10,2) NOT NULL,
                rate_per_hour DECIMAL(10,2) NOT NULL,
                total_cost DECIMAL(10,2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_table_query)
            self.conn.commit()
            
            print("✅ MySQL Database connected successfully!")
            
        except mysql.connector.Error as e:
            print(f"❌ Database Error: {e}")
            messagebox.showerror(
                "Database Connection Failed", 
                f"Cannot connect to MySQL database!\n\n"
                f"Error: {e}\n\n"
                f"Please ensure:\n"
                f"1. MySQL Server is running\n"
                f"2. MySQL is installed on your system\n"
                f"3. Correct password is set in the code\n"
                f"4. You have necessary permissions"
            )
            self.conn = None
            self.cursor = None

    def calculate_cost(self):
        try:
            vms = int(self.vm_entry.get())
            hours = float(self.hours_entry.get())
            rate = float(self.rate_entry.get())

            cost = np.round(vms * hours * rate, 2)
            monthly = np.round(cost * 30, 2)

            self.output_text.insert(tk.END, f"\n➡️ {vms} VMs × {hours} hrs × ₹{rate}/hr = ₹{cost}\n")
            self.output_text.insert(tk.END, f"📅 Estimated Monthly Cost: ₹{monthly}\n{'-'*70}\n")

            record = {"VMs": vms, "Hours": hours, "Rate": rate, "Cost": cost}
            self.records.append(record)
            self.tree.insert("", "end", values=(vms, hours, rate, cost))

            # Save to database
            if self.conn and self.conn.is_connected():
                self.save_to_database(vms, hours, rate, cost)
            else:
                messagebox.showwarning("Database Warning", "Not connected to database. Data not saved!")

            self.update_stats()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values!")

    def save_to_database(self, vms, hours, rate, cost):
        """Save calculation to MySQL database"""
        try:
            insert_query = """
            INSERT INTO cost_records (vm_count, hours_used, rate_per_hour, total_cost)
            VALUES (%s, %s, %s, %s)
            """
            self.cursor.execute(insert_query, (vms, hours, rate, cost))
            self.conn.commit()
            print(f"✅ Data saved to MySQL: {vms} VMs, {hours} hrs, ₹{rate}/hr = ₹{cost}")
        except mysql.connector.Error as e:
            print(f"❌ Failed to save to database: {e}")
            messagebox.showerror("Database Error", f"Failed to save record to database:\n{e}")

    def update_stats(self):
        if not self.records:
            self.stats_label.config(text="")
            return

        costs = np.array([r["Cost"] for r in self.records])
        avg_cost = np.mean(costs)
        max_cost = np.max(costs)
        min_cost = np.min(costs)

        self.stats_label.config(text=f"📊 Avg: ₹{avg_cost:.2f}   |   🔼 Max: ₹{max_cost:.2f}   |   🔽 Min: ₹{min_cost:.2f}")

    def show_graph(self):
        if not self.records:
            messagebox.showwarning("No Data", "No records to display!")
            return

        vms = np.array([r["VMs"] for r in self.records])
        cost = np.array([r["Cost"] for r in self.records])

        plt.figure(figsize=(10, 6))
        plt.title("Cloud Cost Analysis Trend", fontsize=16, fontweight="bold", color="#004466")
        sns.barplot(x=vms, y=cost, palette="coolwarm", alpha=0.8)
        sns.lineplot(x=vms, y=cost, marker="o", color="black", label="Cost Line")
        plt.xlabel("Number of VMs", fontsize=12)
        plt.ylabel("Total Cost (₹)", fontsize=12)
        plt.legend()
        plt.tight_layout()
        plt.show()

    def clear_all(self):
        self.vm_entry.delete(0, tk.END)
        self.hours_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)
        self.output_text.delete("1.0", tk.END)
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.stats_label.config(text="")
        self.records.clear()

    def __del__(self):
        """Close database connection when app closes"""
        if hasattr(self, 'conn') and self.conn and self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            print("✅ Database connection closed")


# --- Run the App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CloudCostDashboard(root)
    root.mainloop()