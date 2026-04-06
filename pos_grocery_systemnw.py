import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import os

# =======================
# Item Class
# =======================
class Item:
    def __init__(self, name, price, unit, stock):
        if not name.strip():
            raise ValueError("Item name cannot be empty")
        if price <= 0:
            raise ValueError("Price must be greater than 0")
        if stock < 0:
            raise ValueError("Stock cannot be negative")
        if not unit.strip():
            raise ValueError("Unit cannot be empty")

        self.name = name.strip()
        self.price = float(price)
        self.unit = unit.strip()
        self.stock = float(stock)

    def update_stock(self, qty):
        if qty <= 0:
            raise ValueError("Quantity must be > 0")
        if qty > self.stock:
            raise ValueError("Insufficient stock")
        self.stock -= qty


# =======================
# Inventory Class
# =======================
class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        for i in self.items:
            if i.name.lower() == item.name.lower():
                raise ValueError("Item already exists")
        self.items.append(item)

    def search_item(self, name):
        for i in self.items:
            if i.name.lower() == name.strip().lower():
                return i
        return None


# =======================
# Sale Class
# =======================
class Sale:
    def __init__(self, bill_no, item, qty, price, total):
        self.bill_no = bill_no
        self.item_name = item
        self.quantity = qty
        self.unit_price = price
        self.total = total
        self.date_time = datetime.now().strftime("%Y-%m-%d %H:%M")


# =======================
# POS Application
# =======================
class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KDU Grocery POS System")
        self.root.geometry("600x650")

        self.inventory = Inventory()
        self.sales = []

        self.bg = "#ecf0f1"
        self.header = "#2c3e50"
        self.btn = "#27ae60"

        self.root.configure(bg=self.bg)

        self.create_header()
        self.create_main_menu()

    # ---------- Header ----------
    def create_header(self):
        header = tk.Frame(self.root, bg=self.header, height=90)
        header.pack(fill="x")

        tk.Label(header, text="Kothalawala Mini Mart",
                 bg=self.header, fg="white",
                 font=("Arial", 26, "bold")).pack(side="left", padx=20)

        if os.path.exists("kdu_logo.png"):
            img = Image.open("kdu_logo.png")
            img.thumbnail((70, 70))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.logo, bg=self.header).pack(side="right", padx=20)

    # ---------- Main Menu ----------
    def create_main_menu(self):
        body = tk.Frame(self.root, bg=self.bg)
        body.pack(expand=True)

        style = {"bg": self.btn, "fg": "white",
                 "font": ("Arial", 16, "bold"),
                 "width": 28, "height": 2}

        tk.Button(body, text="Add Item", command=self.add_item_window, **style).pack(pady=8)
        tk.Button(body, text="Search Item Price", command=self.search_item_window, **style).pack(pady=8)
        tk.Button(body, text="Create Bill", command=self.billing_window, **style).pack(pady=8)
        tk.Button(body, text="Stock Report", command=self.stock_report, **style).pack(pady=8)
        tk.Button(body, text="Sales Report", command=self.sales_report, **style).pack(pady=8)

        tk.Button(body, text="Exit",
                  bg="#c0392b", fg="white",
                  font=("Arial", 16, "bold"),
                  width=28, height=2,
                  command=self.root.destroy).pack(pady=10)

    # ---------- Add Item ----------
    def add_item_window(self):
        win = tk.Toplevel(self.root)
        win.title("Add Item")

        labels = ["Item Name", "Price", "Unit", "Stock"]
        entries = []

        for i, l in enumerate(labels):
            tk.Label(win, text=l, font=("Arial", 13, "bold")).grid(row=i, column=0, padx=10, pady=6)
            e = tk.Entry(win, font=("Arial", 13))
            e.grid(row=i, column=1)
            entries.append(e)

        def save():
            try:
                item = Item(entries[0].get(),
                            float(entries[1].get()),
                            entries[2].get(),
                            float(entries[3].get()))
                self.inventory.add_item(item)
                messagebox.showinfo("Success", "Item added")
                win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Save Item",
                  bg=self.btn, fg="white",
                  font=("Arial", 13, "bold"),
                  command=save).grid(row=4, columnspan=2, pady=10)

    # ---------- Search ----------
    def search_item_window(self):
        win = tk.Toplevel(self.root)

        tk.Label(win, text="Enter Item Name", font=("Arial", 13)).pack(pady=10)
        entry = tk.Entry(win, font=("Arial", 13))
        entry.pack()

        result = tk.Label(win, font=("Arial", 13, "bold"))
        result.pack(pady=10)

        def search():
            item = self.inventory.search_item(entry.get())
            if item:
                result.config(text=f"{item.name}: Rs.{item.price}/{item.unit}")
            else:
                result.config(text="Item not found")

        tk.Button(win, text="Search", bg=self.btn, fg="white",
                  font=("Arial", 13, "bold"),
                  command=search).pack(pady=5)

    # ---------- BILLING (MULTI ITEM) ----------
    def billing_window(self):
        win = tk.Toplevel(self.root)
        win.title("Billing")

        cart = []

        tk.Label(win, text="Item Name", font=("Arial", 13)).grid(row=0, column=0)
        tk.Label(win, text="Quantity", font=("Arial", 13)).grid(row=1, column=0)

        name = tk.Entry(win, font=("Arial", 13))
        qty = tk.Entry(win, font=("Arial", 13))
        name.grid(row=0, column=1)
        qty.grid(row=1, column=1)

        cart_box = tk.Text(win, width=60, height=12, font=("Arial", 12))
        cart_box.grid(row=3, columnspan=3, pady=10)

        total_label = tk.Label(win, text="Total: Rs.0.00",
                               font=("Arial", 14, "bold"))
        total_label.grid(row=4, columnspan=3)

        def add_to_cart():
            try:
                item = self.inventory.search_item(name.get())
                if not item:
                    raise ValueError("Item not found")

                q = float(qty.get())
                item.update_stock(q)

                total = q * item.price

                cart.append({
                    "name": item.name,
                    "qty": q,
                    "price": item.price,
                    "total": total,
                    "unit": item.unit
                })

                update_cart()

                name.delete(0, tk.END)
                qty.delete(0, tk.END)

            except Exception as e:
                messagebox.showerror("Error", str(e))

        def update_cart():
            cart_box.delete(1.0, tk.END)
            grand = 0

            for i, c in enumerate(cart, 1):
                cart_box.insert(tk.END,
                    f"{i}. {c['name']} - {c['qty']} {c['unit']} x {c['price']} = Rs.{c['total']:.2f}\n")
                grand += c['total']

            total_label.config(text=f"Total: Rs.{grand:.2f}")

        def generate_bill():
            try:
                if not cart:
                    raise ValueError("Cart is empty")

                bill_no = f"BILL-{len(self.sales)+1:04d}"
                grand_total = sum(c["total"] for c in cart)

                for c in cart:
                    self.sales.append(Sale(bill_no, c["name"], c["qty"], c["price"], c["total"]))

                path = filedialog.asksaveasfilename(defaultextension=".pdf")

                if path:
                    self.save_bill_pdf(cart, bill_no, grand_total, path)

                messagebox.showinfo("Success", "Bill Generated")
                win.destroy()

            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(win, text="Add to Cart", bg=self.btn, fg="white",
                  font=("Arial", 13, "bold"),
                  command=add_to_cart).grid(row=2, columnspan=2)

        tk.Button(win, text="Generate Bill", bg="#2c3e50", fg="white",
                  font=("Arial", 13, "bold"),
                  command=generate_bill).grid(row=5, columnspan=3, pady=10)

    # ---------- PDF ----------
    def save_bill_pdf(self, cart, bill_no, grand_total, path):
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4

        # Header
        c.setFillColorRGB(0.04, 0.24, 0.36)
        c.rect(0, height - 110, width, 110, fill=1)

        if os.path.exists("kdu_logo.png"):
            c.drawImage("kdu_logo.png", width - 100, height - 95,
                        width=60, height=60)

        c.setFillColorRGB(1, 1, 1)
        c.setFont("Helvetica-Bold", 22)
        c.drawString(40, height - 60, "Kothalawala Mini Mart")

        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 140, f"Bill No: {bill_no}")
        c.drawString(50, height - 160, f"Date: {datetime.now()}")

        y = height - 200

        for item in cart:
            c.drawString(50, y,
                f"{item['name']} {item['qty']} {item['unit']} = Rs.{item['total']:.2f}")
            y -= 20

        c.drawString(50, y - 20, f"Total: Rs.{grand_total:.2f}")
        c.save()

    # ---------- Reports ----------
    def stock_report(self):
        win = tk.Toplevel(self.root)
        text = tk.Text(win)
        text.pack()

        for i in self.inventory.items:
            text.insert(tk.END, f"{i.name} {i.stock}{i.unit}\n")

    def sales_report(self):
        win = tk.Toplevel(self.root)
        text = tk.Text(win)
        text.pack()

        total = 0
        for s in self.sales:
            text.insert(tk.END, f"{s.bill_no} {s.item_name} Rs.{s.total}\n")
            total += s.total

        text.insert(tk.END, f"\nTotal: Rs.{total:.2f}")


# =======================
# RUN
# =======================
if __name__ == "__main__":
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()