from datetime import datetime   # standard library, used only to stamp the date/time on receipts

# ---------------------------------------------------------------------------
# DATA STRUCTURES (in-memory only) [VARIABLES AND DATA STRUCTURES]
# ---------------------------------------------------------------------------
staff_accounts = {"staff": {"password": "staff123"}}   # [DATA STRUCTURE: dict of dicts] username -> password, the one built-in login

# menu: category name -> {"prices": size code -> peso price, "flavors": list of flavor names}.
# All flavors in a category share one price row (matches the menu board). B1T1 = Buy 1 Take 1 (2 cups).
menu = {                                                   # [DATA STRUCTURE: dict of dicts of lists]
    "Lemonade": {"prices": {"R": 35, "M": 45, "L": 55, "B1T1": 65},
                 "flavors": ["Green Apple", "Orange", "Lemon", "Lychee", "Blueberry", "Mango",
                             "Strawberry", "Passion Fruit", "4 Seasons", "Kiwi"]},
    "Yogurt": {"prices": {"R": 30, "M": 40, "L": 50, "B1T1": 55},
               "flavors": ["4 Seasons", "Lemon", "Green Apple", "Blueberry", "Kiwi",
                           "Passion Fruit", "Strawberry", "Orange"]},
    "Coffee": {"prices": {"R": 35, "M": 45, "L": 55, "B1T1": 65},
               "flavors": ["Macchiato", "Spanish Latte", "Cappuccino", "Mocha"]},
    "Fruity Milk": {"prices": {"R": 49, "M": 59, "L": 69, "B1T1": 90},
                    "flavors": ["Blueberry", "Strawberry", "4 Seasons", "Green Apple", "Mango",
                                "Lychee", "Kiwi", "Orange", "Buko Pandan"]},
    "Milktea": {"prices": {"R": 35, "M": 45, "L": 55, "B1T1": 65},
                "flavors": ["Strawberry", "Chocolate", "C&C", "Okinawa", "Wintermelon", "Mango",
                            "Avocado", "Buko Pandan", "Taro", "Red Velvet", "Matcha"]},
    "Fruit Soda": {"prices": {"R": 30, "M": 40, "L": 50, "B1T1": 55},
                   "flavors": ["Kiwi", "Blue Lemonade", "Passion Fruit", "Green Apple", "Mango",
                               "Strawberry", "Lychee", "Blueberry", "4 Seasons", "Orange"]},
}
SIZE_LABELS = {"R": "Regular", "M": "Medium", "L": "Large", "B1T1": "Buy 1 Take 1 (2 cups)"}  # [DATA STRUCTURE: dict] used on receipts
order_queue = []      # [DATA STRUCTURE: list] every completed order (each order is its own dict)
daily_earnings = 0    # [VARIABLE] running total of money earned today


# ---------------------------------------------------------------------------
# LOGIN (one built-in staff account, no registration)
# ---------------------------------------------------------------------------
def login():
    """Ask for credentials. Parameters: none. Returns: username (string) or None if it fails."""
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = input("Password: ")
    account = staff_accounts.get(username)                      # .get() gives None if not found (no crash)
    if account is not None and account["password"] == password: # [OPERATOR: and, ==]
        return username
    print("Invalid username or password.")
    return None


# ---------------------------------------------------------------------------
# MENU AND ORDER BUILDING
# ---------------------------------------------------------------------------
def price_line(prices):
    """Format a price row. Parameters: prices (dict). Returns: text like 'R 35 / M 45 / L 55 / B1T1 65'."""
    return " / ".join(f"{size} {price}" for size, price in prices.items())


def ask_number(prompt, highest, allow_zero=False):
    """Ask for a menu number until valid. Parameters: prompt (string), highest (int, biggest valid number),
    allow_zero (bool, True if 0 is also accepted). Returns: the number typed (int)."""
    lowest = 0 if allow_zero else 1
    while True:                                                 # [WHILE LOOP] repeat until a valid number
        text = input(prompt).strip()
        if text.isdigit() and lowest <= int(text) <= highest:   # [INPUT VALIDATION] digits only, inside the range
            return int(text)
        print(f"Please enter a number from {lowest} to {highest}.")


def display_categories():
    """Show every category with its prices. Parameters: none. Returns: nothing."""
    print("\n--- Categories ---")
    for number, category in enumerate(menu, start=1):           # enumerate() gives (number, name) pairs, counting from 1
        print(f"{number}. {category}  ({price_line(menu[category]['prices'])})")
    print("\nSize guide: R = Regular | M = Medium | L = Large | B1T1 = Buy 1 Take 1 (2 cups)")


def display_flavors(category):
    """Show one category's flavors. Parameters: category (string). Returns: nothing."""
    print(f"\n--- {category} Flavors ---")
    for number, flavor in enumerate(menu[category]["flavors"], start=1):
        print(f"{number}. {flavor}")


def display_menu():
    """Show the full menu (used by the customer menu). Parameters: none. Returns: nothing."""
    print("\n--- Full Menu ---")
    for category, details in menu.items():                      # .items() gives (key, value) pairs together
        print(f"\n{category} ({price_line(details['prices'])})")
        print(", ".join(details["flavors"]))                    # .join() makes one comma-separated string


def get_category():
    """Ask for a category number. Parameters: none. Returns: category name, or None if the staff typed 0 (done)."""
    categories = list(menu)                                     # category names in menu order, so number 1 = first
    display_categories()
    number = ask_number("\nEnter category number (or 0 to finish): ", len(categories), allow_zero=True)
    if number == 0:                                             # [IF] staff is finished adding items
        return None
    return categories[number - 1]                               # numbers start at 1, list positions start at 0


def get_flavor(category):
    """Ask for a flavor number. Parameters: category (string). Returns: flavor name (string)."""
    flavors = menu[category]["flavors"]
    display_flavors(category)
    number = ask_number("Enter flavor number: ", len(flavors))
    return flavors[number - 1]


def get_size(category):
    """Ask for a size until valid. Parameters: category (string). Returns: size code (R, M, L or B1T1)."""
    prices = menu[category]["prices"]
    while True:
        print("\n--- Sizes ---")
        for code, price in prices.items():                      # e.g. R = Regular - PHP 35
            print(f"{code} = {SIZE_LABELS[code]} - PHP {price}")
        size = input("Choose size (R/M/L/B1T1): ").strip().upper()
        if size in prices:                                      # [OPERATOR: in] [INPUT VALIDATION]
            return size
        print("Invalid size, try again.")


def get_quantity():
    """Ask for a quantity until valid. Parameters: none. Returns: quantity (int, 1 or more)."""
    while True:
        text = input("Quantity: ")
        if text.isdigit() and int(text) > 0:                    # [OPERATOR: and, >] [INPUT VALIDATION]
            return int(text)                                    # convert typed text into a real number
        print("Quantity must be a positive whole number.")


def remove_item(order):
    """Optionally remove one line item, changing the list directly. Parameters: order (list of dicts). Returns: nothing."""
    while True:                                                 # [WHILE LOOP] keep asking until the answer is y or n
        answer = input("Remove an item instead? (y/n): ").strip().lower()
        if answer in ("y", "n"):                                # [INPUT VALIDATION] only y or n is accepted
            break
        print("Please type y or n.")
    if answer == "y" and order:                                 # [IF] only offer if the order isn't empty
        for i, line in enumerate(order):                        # enumerate() gives (index, item) pairs
            print(f"{i}: {line['quantity']} x {line['size']} {line['flavor']} ({line['category']})")
        index = input("Enter the number to remove: ")
        if index.isdigit() and 0 <= int(index) < len(order):    # [INPUT VALIDATION]
            removed = order.pop(int(index))                     # .pop() removes the item AND gives it back
            print(f"Removed {removed['quantity']} x {removed['flavor']}.")


def take_order():
    """Build one order: category -> flavor -> size -> quantity. Parameters: none. Returns: order (list of dicts)."""
    order = []                                                  # [DATA STRUCTURE: list] collects each item added
    print("\n--- New Order ---")
    while True:                                                 # [WHILE LOOP] until staff types 'done'
        category = get_category()
        if category is None:
            break
        flavor = get_flavor(category)
        size = get_size(category)
        note = input("Any customization? (e.g. 'less sugar', or leave blank): ")
        quantity = get_quantity()
        order.append({"category": category, "flavor": flavor, "size": size,
                      "price": menu[category]["prices"][size],  # [EXPRESSION: dict lookup] price for the chosen size
                      "quantity": quantity, "customization": note})
        print(f"Added {quantity} x {size} {flavor} ({category}) to the order.")
        remove_item(order)
    return order


def calculate_total(order):
    """Add up the order. Parameters: order (list). Returns: total (number)."""
    total = 0
    for line in order:                                          # [FOR LOOP]
        total += line["price"] * line["quantity"]               # [OPERATOR: *, +=]
    return total


def process_payment(total):
    """Ask for payment until it covers the total. Parameters: total (number). Returns: payment and change (a pair of numbers)."""
    while True:                                                 # [WHILE LOOP]
        text = input(f"\nTotal is PHP {total}. Enter customer payment: ")
        if not text.replace(".", "", 1).isdigit():              # [INPUT VALIDATION] allow one decimal point
            print("Please enter a valid amount.")
        elif float(text) < total:                               # [OPERATOR: <] not enough money
            print("Payment is less than the total, ask for more.")
        else:
            return float(text), float(text) - total             # [RETURN VALUE] two values at once (a tuple)


# ---------------------------------------------------------------------------
# RECEIPT AND ORDER QUEUE
# ---------------------------------------------------------------------------
def print_receipt(entry):
    """Print one receipt. Parameters: entry (dict, a saved order from order_queue). Returns: nothing (just prints)."""
    w, aw = 46, 12                                              # [VARIABLE] receipt width, width of the amount column
    print("\n" + "=" * w)
    print("SWEET SIP".center(w))                                # .center() puts the text in the middle
    print("Coffee Shop Receipt".center(w))
    print("=" * w)
    print(f"Order #: {entry['priority_number']}")
    print(f"Date:    {entry['time']}")
    print(f"Cashier: {entry['cashier']}")
    print("-" * w)
    for line in entry["items"]:                                 # [FOR LOOP] one block per item ordered
        left = f"    {SIZE_LABELS[line['size']]} @ {line['price']:.2f}"
        right = f"PHP {line['price'] * line['quantity']:.2f}"
        print(f"{line['quantity']} x {line['flavor']} ({line['category']})")
        print(f"{left:<{w - aw}}{right:>{aw}}")                 # left-align text, right-align the amount
        if line["customization"].strip() != "":                 # only show a note if one was given
            print(f"    Note: {line['customization'].strip()}")
    print("-" * w)
    for label, value in (("TOTAL", entry["total"]), ("PAYMENT", entry["payment"]), ("CHANGE", entry["change"])):
        print(f"{label:<{w - aw}}{'PHP ' + format(value, '.2f'):>{aw}}")
    print("=" * w)
    print("Thank you! Please wait for your order number.".center(w))
    print("=" * w)


def add_to_queue(order, total, payment, change, cashier):
    """Save a completed order with everything needed to reprint its receipt. New orders start as 'Preparing'.
    Parameters: order, total, payment, change, cashier. Returns: priority_number."""
    priority_number = len(order_queue) + 1                      # [OPERATOR: +] unique, because orders are never deleted
    order_queue.append({"priority_number": priority_number, "items": order, "status": "Preparing",
                        "total": total, "payment": payment, "change": change, "cashier": cashier,
                        "time": datetime.now().strftime("%Y-%m-%d %I:%M %p")})
    return priority_number


def summarize_items(items):
    """One short text line for an order, e.g. '2x M Okinawa, 1x L Mango'. Parameters: items (list). Returns: text."""
    return ", ".join(f"{l['quantity']}x {l['size']} {l['flavor']}" for l in items)


def view_queue():
    """Show every saved order with its status. Parameters: none. Returns: nothing (just prints)."""
    print("\n--- Order Queue ---")
    if not order_queue:                                         # [IF] an empty list means no orders yet
        print("No orders yet.")
    for entry in order_queue:
        print(f"#{entry['priority_number']} [{entry['status']}] {summarize_items(entry['items'])} — PHP {entry['total']}")


def mark_order_done():
    """Staff marks one order as finished. Parameters: none. Returns: nothing."""
    pending = [e for e in order_queue if e["status"] == "Preparing"]   # only orders that are not done yet
    if not pending:
        print("\nNo orders waiting. Everything is done!")
        return
    print("\n--- Orders Being Prepared ---")
    for entry in pending:
        print(f"#{entry['priority_number']} {summarize_items(entry['items'])}")
    while True:
        text = input("Enter the order number that is done (or 0 to cancel): ").strip()
        if text == "0":
            return
        for entry in pending:                                   # [FOR LOOP] find the order with that number
            if text.isdigit() and entry["priority_number"] == int(text):
                entry["status"] = "Done"                        # change the saved order directly
                print(f"Order #{entry['priority_number']} is now marked as DONE.")
                return
        print("That number is not in the waiting list, try again.")


# ---------------------------------------------------------------------------
# CUSTOMER FEATURES: look up an order by its order number (printed on the receipt)
# ---------------------------------------------------------------------------
def find_my_order():
    """Ask for the order number on the receipt. Parameters: none. Returns: that order (dict), or None if not found."""
    text = input("\nEnter your order number (shown on your receipt): ").strip()
    if text.isdigit():
        for entry in order_queue:
            if entry["priority_number"] == int(text):
                return entry
    print("No order found with that number. Please check your receipt or ask the cashier.")
    return None


def view_my_order_status():
    """Show the customer's order number, items, total and whether it is ready. Parameters: none. Returns: nothing."""
    entry = find_my_order()
    if entry is not None:
        print(f"\nOrder #{entry['priority_number']}")
        print(f"Items: {summarize_items(entry['items'])}")
        print(f"Total: PHP {entry['total']:.2f}")
        if entry["status"] == "Done":
            print("Status: DONE - your order is ready, please pick it up!")
        else:
            print("Status: Preparing - please wait.")


def view_my_receipt():
    """Print the customer's receipt again. Parameters: none. Returns: nothing."""
    entry = find_my_order()
    if entry is not None:
        print_receipt(entry)


# ---------------------------------------------------------------------------
# MENUS: customer, staff, main [CONSOLE MENU AND SYSTEM FLOW]
# ---------------------------------------------------------------------------
def customer_menu():
    """No login needed, customers can only look things up. Parameters: none. Returns: nothing."""
    while True:                                                 # [WHILE LOOP] until the customer goes back
        print("\n=== Customer Menu ===\n1. View menu\n2. Check my order status\n3. View my receipt\n4. Back to main menu")
        choice = input("Choose an option: ")
        if choice == "1":                                       # [IF]
            display_menu()
        elif choice == "2":                                     # [ELIF]
            view_my_order_status()
        elif choice == "3":
            view_my_receipt()
        elif choice == "4":
            print("Returning to main menu.")
            break                                               # control returns to main()
        else:                                                   # [ELSE]
            print("Invalid choice, try again.")


def staff_menu(username):
    """Staff options after login. Parameters: username (string). Returns: nothing."""
    global daily_earnings                                       # update the outer variable, not a new local one
    while True:                                                 # [WHILE LOOP] until staff logs out
        print(f"\n=== Staff Menu ({username}) ===\n1. Take a new order\n2. View order queue\n3. Mark an order as done\n4. View total earned today\n5. Log out")
        choice = input("Choose an option: ")
        if choice == "1":
            order = take_order()
            if not order:                                       # [IF] empty list means nothing was added
                print("Order cancelled, no items added.")
                continue                                        # skip payment, show the staff menu again
            total = calculate_total(order)
            payment, change = process_payment(total)            # get back what was paid AND the change owed
            priority_number = add_to_queue(order, total, payment, change, username)
            daily_earnings += total                             # [OPERATOR: +=] add this sale to today's total
            print(f"\nOrder #{priority_number} complete. Tell the customer to remember this number. Change due: PHP {change:.2f}")
            print_receipt(order_queue[-1])                      # the order we just saved is the last one in the list
        elif choice == "2":
            view_queue()
        elif choice == "3":
            mark_order_done()
        elif choice == "4":
            print(f"Total earned today: PHP {daily_earnings}")
        elif choice == "5":
            print("Logging out.")
            break
        else:
            print("Invalid choice, try again.")


def main():
    """Where the program starts. Parameters: none. Returns: nothing."""
    print("=== Sweet Sip Coffee Shop Ordering System ===")
    while True:                                                 # [WHILE LOOP] the outermost loop
        print("\n1. Staff Login\n2. Customer\n3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            username = login()                                  # comes back as None if login failed
            if username is not None:                            # [OPERATOR: is not]
                staff_menu(username)
        elif choice == "2":
            customer_menu()
        elif choice == "3":
            print("Closing the system. Goodbye!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":       # True only when you run this file directly (not when imported)
    main()