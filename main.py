import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import string
import json
from ttkthemes import ThemedStyle


class User:
    """User login details object"""
    def __init__(self, username, password, balance):
        self.username = username
        self.password = password
        self.balance = balance


class RestaurantMenuApp:
    def __init__(self, root):
        self.root = root

        # window title
        self.root.title("Restaurant Menu System")

        # tkinter stylesheet
        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")

        # contains all the users in the file
        self.users = self.load_users_from_file() or {'admin': User('admin', 'adminpass', 0)} #, **self.generate_random_users()}
        # saves user to json
        self.save_users_to_file()

        # variable for the logged-in user
        self.logged_in_user = None

        # restaurant items
        self.item_prices = {"Burger": 10, "Pizza": 12, "Pasta": 15, "Salad": 8, "Steak": 20, "Sushi": 18, "Soup": 6, "Sandwich": 7, "Dessert": 5}

        # create login page
        self.create_login_page()

    @staticmethod
    def generate_random_password():
        """Generates random password with help of string lib"""

        # joins list of random letters and integers with length 8
        return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    def generate_random_users(self):
        """Generates random users"""

        # dictionary containing the users
        random_users = {}
        for _ in range(20):
            # usernames are made up of 5 random characters
            username = ''.join(random.choices(string.ascii_lowercase, k=5)) + str(random.randint(1, 99))

            # password
            password = self.generate_random_password()

            # the balance is random number between 10 and 100
            balance = random.uniform(10, 100)

            # final user data added to the dictionary
            random_users[username] = User(username, password, balance)

        return random_users

    def save_users_to_file(self, filename='users.json'):
        """Saves users to json file"""
        with open(filename, 'w') as file:
            user_list = [{'username': user.username, 'password': user.password, 'balance': user.balance} for user in self.users.values()]
            json.dump(user_list, file, indent=2)

    @staticmethod
    def load_users_from_file(filename='users.json'):
        """Stores the users from the file in a dictionary"""
        try:
            # open file as read
            with open(filename, 'r') as file:
                # returns the json file as a dictionary
                user_list = json.load(file)

                # loop through the converted dictionary and return a dictionary making use of the User object
                return {user['username']: User(username=user['username'], password=user['password'], balance=user['balance']) for user in user_list}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def create_login_page(self):
        """Create the login page"""

        # main frame
        self.login_frame = ttk.Frame(self.root, padding="20")
        self.login_frame.grid(row=0, column=0, sticky="nsew")

        # username label and entry
        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, pady=10)

        # password label and entry
        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, pady=10)

        # login button
        login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        login_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Add tooltips
        Tooltip(self.username_entry, "Enter your username")
        Tooltip(self.password_entry, "Enter your password")
        Tooltip(login_button, "Click to log in")

    def create_menu_page(self):
        """Main(menu) page"""

        # the login window is destroyed after a successful login
        self.login_frame.destroy()

        # main frame
        self.menu_frame = ttk.Frame(self.root, padding="20")
        self.menu_frame.grid(row=0, column=0, sticky="nsew")

        # Balance label
        self.balance_label = ttk.Label(self.menu_frame, text=f"Balance: ${self.users[self.logged_in_user].balance}",
                                       font=('Helvetica', 12))
        self.balance_label.grid(row=0, column=3, columnspan=2, pady=10, sticky="e")

        # Welcome message
        ttk.Label(self.menu_frame, text=f"Welcome, {self.logged_in_user}!", font=('Helvetica', 14, 'bold')).grid(row=1,
                                                                                                                 column=0,
                                                                                                                 columnspan=5,
                                                                                                                 pady=10)
        # menu label
        ttk.Label(self.menu_frame, text="Menu", font=('Helvetica', 12, 'bold')).grid(row=2, column=0, columnspan=5,
                                                                                     pady=10)

        # Add more food variety with prices
        # creates a grid of buttons with all the menu items
        for i, (item, price) in enumerate(self.item_prices.items()):
            ttk.Button(self.menu_frame, text=f"{item}\n(${price})",
                       command=lambda i=item, p=price: self.add_to_order(i, p)).grid(row=i // 3 + 3, column=i % 3,
                                                                                     pady=5, padx=10, sticky="nsew")

        # Add a scrollbar to the order text
        self.order_text = tk.Text(self.menu_frame, height=5, width=40)
        self.order_text.grid(row=6, column=0, columnspan=4, pady=10, sticky="nsew")
        scrollbar = ttk.Scrollbar(self.menu_frame, command=self.order_text.yview)
        scrollbar.grid(row=6, column=4, pady=10, sticky="ns")
        self.order_text['yscrollcommand'] = scrollbar.set

        # Place order button
        ttk.Button(self.menu_frame, text="Place Order", command=self.place_order).grid(row=7, column=0, columnspan=5,
                                                                                       pady=10, sticky="nsew")

        # Total cost label
        self.total_cost_label = ttk.Label(self.menu_frame, text="Total Cost: $0", font=('Helvetica', 12))
        self.total_cost_label.grid(row=8, column=0, columnspan=5, pady=10)

        # Clear order button
        ttk.Button(self.menu_frame, text="Clear Order", command=self.clear_order).grid(row=9, column=0, columnspan=5,
                                                                                       pady=10, sticky="nsew")
        # add view users button if the user is admin
        if self.logged_in_user == 'admin':
            ttk.Button(self.menu_frame, text="View Users", command=self.view_users).grid(row=10, column=0, columnspan=5,
                                                                                         pady=10, sticky="nsew")
        # logout button
        ttk.Button(self.menu_frame, text="Logout", command=self.logout).grid(row=11, column=0, columnspan=5, pady=10,
                                                                             sticky="nsew")

        # Configure row and column weights to make the grid cells expand proportionally
        for i in range(12):
            self.menu_frame.grid_rowconfigure(i, weight=1)
            self.menu_frame.grid_columnconfigure(i, weight=1)

    def login(self):
        """User login"""

        # get username and password
        username = self.username_entry.get()
        password = self.password_entry.get()

        # compare with stored user and find a match
        if username in self.users and self.users[username].password == password:
            # set logged-in user and create menu page
            self.logged_in_user = username
            self.create_menu_page()
        else:
            # if there is no match display error message
            messagebox.showerror("Login Failed", "Invalid username or password")

    def add_to_order(self, item, price):
        """Add item to order"""
        self.order_text.insert(tk.END, f"Added to order: {item} (${price})\n")

        # updates cost label
        self.update_total_cost()

    def update_total_cost(self):
        """Updates the total cost of the order"""

        # split evry line of the text box
        # get the int val at every line and add them to get the sum
        total_cost = sum(float(line.split("($")[1].split(")")[0]) for line in self.order_text.get("1.0", tk.END).split("\n") if "Added to order:" in line)

        # update the total cost based on the sum of everything
        self.total_cost_label.config(text=f"Total Cost: ${total_cost}")

    def place_order(self):
        """Places the order"""

        # the total price of the user order
        total_price = sum(float(line.split("($")[1].split(")")[0]) for line in self.order_text.get("1.0", tk.END).split("\n") if "Added to order:" in line)

        # if the user is not admin process the order by comparing the balance vs the price
        if self.logged_in_user != 'admin':
            if total_price > self.users[self.logged_in_user].balance:
                messagebox.showerror("Insufficient Balance", "You do not have sufficient balance to place this order.")
                return

            # Update user balance in both the file and the menu page
            self.users[self.logged_in_user].balance -= total_price  # new balance in users dict

            # Update the balance label
            self.balance_label.config(text=f"Balance: ${self.users[self.logged_in_user].balance}")

            # save the new data to the file
            self.save_users_to_file()

        # Display informative feedback showing that the order was a success
        messagebox.showinfo("Order Placed", f"Total Order Price: ${total_price}")

        # clear textbox
        self.order_text.delete("1.0", tk.END)

        # Update the total cost (will be reset to 0 along the label)
        self.update_total_cost()

    def clear_order(self):
        """Clears the order"""
        self.order_text.delete("1.0", tk.END)

        # Updates the total cost along with the label)
        self.update_total_cost()

    def logout(self):
        """Returns to login window"""

        # Reset login user to none
        self.logged_in_user = None

        # Delete menu window
        self.menu_frame.destroy()

        # Create new login window
        self.create_login_page()

    def view_users(self):
        """For admin to view the user in the file in a table"""

        users_window = tk.Toplevel(self.root)
        users_window.title("User Details")

        tree = ttk.Treeview(users_window)
        tree["columns"] = ("Username", "Password", "Balance")
        tree.column("#0", width=0, stretch=tk.NO)
        tree.column("Username", anchor=tk.W, width=100)
        tree.column("Password", anchor=tk.W, width=100)
        tree.column("Balance", anchor=tk.W, width=100)

        tree.heading("#0", text="", anchor=tk.W)
        tree.heading("Username", text="Username", anchor=tk.W)
        tree.heading("Password", text="Password", anchor=tk.W)
        tree.heading("Balance", text="Balance", anchor=tk.W)

        for username, user in self.users.items():
            tree.insert("", tk.END, values=(username, user.password, f"${user.balance}"))

        tree.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.display_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def display_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = tk.Label(self.tooltip, text=self.text, justify='left',
                         background='#ffffe0', relief='solid', borderwidth=1)
        label.pack(ipadx=1)

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()


if __name__ == "__main__":
    pass
    root = tk.Tk()
    app = RestaurantMenuApp(root)
    root.mainloop()


