"""Tkinter desktop interface for the Fashion Inventory Management System."""
import tkinter as tk
from tkinter import ttk, messagebox
from database import initialize_database, initialize_tables
from inventory import add_item, update_item, delete_item, get_inventory, record_sale, get_sales_summary

TYPE_OPTIONS = ["Shirt","T-Shirt","Pants","Dress","Jacket","Night Wear","Earrings",
 "Necklace","Shawl","Hair Accessory","Watch","Hats","Sun Glasses","Makeup Item"]
SIZE_OPTIONS = ["Free Size","S","M","L","XL","XXL","XXXL"]
COLOR_OPTIONS = ["Red","Blue","Green","Black","White","Brown","Purple","Pink","Violet",
 "Maroon","Yellow","Orange","Grey","Peach","Skin Color"]

class FashionInventoryApp:
    def __init__(self, root):
        self.root = root
        root.title("Fashion Inventory Management System")
        root.geometry("1050x680")
        root.minsize(850,560)
        self.show_login()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def heading(self, parent, title):
        ttk.Label(parent,text=title,font=("Arial",18,"bold")).pack(pady=12)

    def show_login(self):
        self.clear()
        f=ttk.Frame(self.root,padding=35); f.pack(expand=True)
        self.heading(f,"Welcome to Fashion Inventory")
        self.username=tk.StringVar(); self.password=tk.StringVar()
        ttk.Label(f,text="Username").pack()
        ttk.Entry(f,textvariable=self.username,width=32).pack(pady=5)
        ttk.Label(f,text="Password").pack()
        ttk.Entry(f,textvariable=self.password,show="*",width=32).pack(pady=5)
        ttk.Button(f,text="Login",command=self.do_login).pack(fill="x",pady=7)
        ttk.Button(f,text="Create account",command=self.show_signup).pack(fill="x")

    def do_login(self):
        from login import login_user
        try:
            if login_user(self.username.get(),self.password.get()): self.show_home()
            else: messagebox.showerror("Login","Invalid username or password.")
        except Exception as exc: messagebox.showerror("Database error",str(exc))

    def show_signup(self):
        self.clear(); f=ttk.Frame(self.root,padding=35); f.pack(expand=True)
        self.heading(f,"Create account")
        user,pwd,confirm=tk.StringVar(),tk.StringVar(),tk.StringVar()
        for label,var,secret in [("Username",user,False),("Password",pwd,True),("Confirm password",confirm,True)]:
            ttk.Label(f,text=label).pack()
            ttk.Entry(f,textvariable=var,show="*" if secret else "").pack(pady=4)
        def submit():
            from login import signup_user
            if pwd.get()!=confirm.get():
                messagebox.showerror("Signup","Passwords do not match."); return
            try:
                signup_user(user.get(),pwd.get())
                messagebox.showinfo("Signup","Account created. Please log in.")
                self.show_login()
            except Exception as exc: messagebox.showerror("Signup",str(exc))
        ttk.Button(f,text="Register",command=submit).pack(pady=8)
        ttk.Button(f,text="Back",command=self.show_login).pack()

    def show_home(self):
        self.clear(); f=ttk.Frame(self.root,padding=20); f.pack(fill="both",expand=True)
        self.heading(f,"Fashion Inventory Management System")
        for label,cmd in [("Add Item",self.show_add),("Manage / Search Inventory",self.show_inventory),
                          ("Barcode Sale Tracking",self.show_sale),("Stock & Sales Charts",self.show_charts),
                          ("Logout",self.show_login)]:
            ttk.Button(f,text=label,command=cmd).pack(fill="x",pady=7,ipady=7)

    def show_add(self):
        self.clear(); f=ttk.Frame(self.root,padding=20); f.pack(fill="both",expand=True)
        self.heading(f,"Add Inventory Item")
        specs=[("Barcode",None),("Name",None),("Type",TYPE_OPTIONS),("Size",SIZE_OPTIONS),
               ("Color",COLOR_OPTIONS),("Quantity",None),("Cost",None),("Supplier",None)]
        fields={}
        for label,choices in specs:
            line=ttk.Frame(f); line.pack(fill="x",pady=3); ttk.Label(line,text=label,width=14).pack(side="left")
            var=tk.StringVar(); fields[label]=var
            w=ttk.Combobox(line,textvariable=var,values=choices,state="readonly") if choices else ttk.Entry(line,textvariable=var)
            w.pack(side="left",fill="x",expand=True)
        def save():
            try:
                v=[fields[k].get().strip() for k,_ in specs]
                if any(not x for x in v): raise ValueError("Complete every field.")
                add_item(v[0],v[1],v[2],v[3],v[4],int(v[5]),float(v[6]),v[7])
                messagebox.showinfo("Saved","Item added."); self.show_home()
            except Exception as exc: messagebox.showerror("Add item",str(exc))
        ttk.Button(f,text="Save Item",command=save).pack(pady=8)
        ttk.Button(f,text="Back",command=self.show_home).pack()

    def show_inventory(self):
        self.clear(); f=ttk.Frame(self.root,padding=12); f.pack(fill="both",expand=True)
        self.heading(f,"Search and Manage Inventory")
        filters=ttk.Frame(f); filters.pack(fill="x")
        fv={k:tk.StringVar() for k in ("Type","Size","Color","Supplier")}
        for k,v in fv.items():
            ttk.Label(filters,text=k).pack(side="left",padx=3)
            ttk.Entry(filters,textvariable=v,width=13).pack(side="left",padx=2)
        cols=("sno","barcode","name","type","size","color","quantity","cost","supplier")
        tree=ttk.Treeview(f,columns=cols,show="headings",height=15)
        for c in cols: tree.heading(c,text=c.title()); tree.column(c,width=100,anchor="center")
        tree.pack(fill="both",expand=True,pady=8)
        def refresh():
            tree.delete(*tree.get_children())
            try:
                for item in get_inventory():
                    if all(not fv[k].get().strip() or fv[k].get().strip().lower() in str(item[i]).lower()
                           for k,i in [("Type",3),("Size",4),("Color",5),("Supplier",8)]):
                        tree.insert("","end",values=item)
            except Exception as exc: messagebox.showerror("Inventory",str(exc))
        def selected():
            s=tree.selection()
            if not s: messagebox.showwarning("Select item","Select a row first."); return None
            return tree.item(s[0],"values")
        def remove():
            row=selected()
            if row and messagebox.askyesno("Confirm",f"Delete {row[2]}?"):
                try: delete_item(int(row[0])); refresh()
                except Exception as exc: messagebox.showerror("Delete",str(exc))
        def edit():
            row=selected()
            if row: self.show_edit(row)
        bar=ttk.Frame(f); bar.pack(fill="x")
        ttk.Button(bar,text="Search / Refresh",command=refresh).pack(side="left",padx=3)
        ttk.Button(bar,text="Update selected",command=edit).pack(side="left",padx=3)
        ttk.Button(bar,text="Delete selected",command=remove).pack(side="left",padx=3)
        ttk.Button(bar,text="Back",command=self.show_home).pack(side="right")
        refresh()

    def show_edit(self,row):
        self.clear(); f=ttk.Frame(self.root,padding=20); f.pack(fill="both",expand=True)
        self.heading(f,"Update Inventory Item")
        labels=["Barcode","Name","Type","Size","Color","Quantity","Cost","Supplier"]
        values=[row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]]
        choices={"Type":TYPE_OPTIONS,"Size":SIZE_OPTIONS,"Color":COLOR_OPTIONS}; fields={}
        for label,value in zip(labels,values):
            line=ttk.Frame(f); line.pack(fill="x",pady=3); ttk.Label(line,text=label,width=14).pack(side="left")
            var=tk.StringVar(value=str(value)); fields[label]=var
            w=ttk.Combobox(line,textvariable=var,values=choices[label],state="readonly") if label in choices else ttk.Entry(line,textvariable=var)
            w.pack(side="left",fill="x",expand=True)
        def save():
            try:
                update_item(int(row[0]),fields["Barcode"].get(),fields["Name"].get(),fields["Type"].get(),
                    fields["Size"].get(),fields["Color"].get(),int(fields["Quantity"].get()),
                    float(fields["Cost"].get()),fields["Supplier"].get())
                messagebox.showinfo("Updated","Item updated."); self.show_inventory()
            except Exception as exc: messagebox.showerror("Update",str(exc))
        ttk.Button(f,text="Save changes",command=save).pack(pady=8)
        ttk.Button(f,text="Cancel",command=self.show_inventory).pack()

    def show_sale(self):
        self.clear(); f=ttk.Frame(self.root,padding=25); f.pack(expand=True)
        self.heading(f,"Barcode Sale Tracking")
        barcode,qty=tk.StringVar(),tk.StringVar()
        ttk.Label(f,text="Barcode").pack(); ttk.Entry(f,textvariable=barcode,width=30).pack(pady=5)
        ttk.Label(f,text="Quantity sold").pack(); ttk.Entry(f,textvariable=qty,width=30).pack(pady=5)
        def sell():
            try:
                record_sale(barcode.get().strip(),int(qty.get()))
                messagebox.showinfo("Sale","Sale recorded and stock updated.")
                barcode.set(""); qty.set("")
            except Exception as exc: messagebox.showerror("Sale",str(exc))
        ttk.Button(f,text="Process Sale",command=sell).pack(pady=8)
        ttk.Button(f,text="Back",command=self.show_home).pack()

    def show_charts(self):
        self.clear(); f=ttk.Frame(self.root,padding=15); f.pack(fill="both",expand=True)
        self.heading(f,"Stock and Sales Summary")
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            stock=get_inventory(); sold=get_sales_summary()
            fig=Figure(figsize=(9,4),dpi=100); a=fig.add_subplot(121); b=fig.add_subplot(122)
            if stock:
                a.bar([str(x[2])[:16] for x in stock],[int(x[6]) for x in stock])
                a.set_title("Stock quantity by item"); a.tick_params(axis="x",rotation=65)
            else: a.set_title("No stock data")
            if sold:
                b.bar([str(x[0]) for x in sold],[int(x[2]) for x in sold])
                b.set_title("Items sold by barcode"); b.tick_params(axis="x",rotation=65)
            else: b.set_title("No sales data")
            fig.tight_layout(); canvas=FigureCanvasTkAgg(fig,master=f); canvas.draw()
            canvas.get_tk_widget().pack(fill="both",expand=True)
        except Exception as exc: ttk.Label(f,text=str(exc)).pack()
        ttk.Button(f,text="Back",command=self.show_home).pack(pady=8)

def main():
    initialize_database(); initialize_tables()
    root=tk.Tk(); FashionInventoryApp(root); root.mainloop()

if __name__=="__main__":
    main()
