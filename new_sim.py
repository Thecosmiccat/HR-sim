
# HR Management Simulator by Jeffrey
# Inspired by ideas from Danila, Audrey, and Lyra
#pr rebyata

print("Loading HR Management Simulator...")

import tkinter as tk
import tkinter.messagebox as messagebox
import tkinter.simpledialog as simpledialog
import json
import os
import random
import time
from tkinter import ttk
import tkinter.font as tkfont
import math

def clamp_stats():
    game.market_share = min(100, max(0, game.market_share))


# Keep strong references to animation callbacks to prevent garbage collection
_animation_callbacks = {}

def _hsl_to_hex(h, s, l):
    """Convert HSL to hex color. h: 0-360, s: 0-100, l: 0-100"""
    s = s / 100.0
    l = l / 100.0
    h = h / 360.0
    
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"

# ---------------- GAME STATE ----------------
class Game:
    def __init__(self):
        self.year = 1
        self.month = 1
        self.employees = 10
        self.morale = 50
        self.productivity = 50
        self.marketing = 50
        self.innovation = 50
        self.reputation = 50
        self.customer_satisfaction = 50
        self.market_share = 10
        self.leader_style = "democratic"
        self.competitor_market_share = 20
        self.money = 20000
        self.company = ""
        self.difficulty = "Normal"
        self.running = False
        self.company_type = ""
    
        self.orders = []
        self.order_cooldown = 0

        self.upgrades = {
            "Better Office": False,
            "Automation": False,
            "Coffee Machine": False
        }
        self.departments = {
            "HR": False,
            "IT": False,
            "PR": False
        }
        self.news_feed = ["Welcome to HR Management Simulator! News will appear here."]
        self.achievements = {
            "Global GDP": {"target": 117_000_000_000_000, "unlocked": False, "desc": "Reach $117 trillion (Global GDP)"},
            "USA Debt": {"target": 34_000_000_000_000, "unlocked": False, "desc": "Reach $34 trillion (USA National Debt)"},
            "Billionaire": {"target": 1_000_000_000, "unlocked": False, "desc": "Reach $1 billion"},
            "Market Dominator": {"target": 100, "unlocked": False, "desc": "Reach 100% market share"},
            "Employee Empire": {"target": 1000, "unlocked": False, "desc": "Hire 1000 employees"}
        }
        self.continue_mode = False

game = Game()

# ---------------- GAME FUNCTIONS ----------------
def update_status():
    target = win_target()
    company_label.config(text=f"Company: {game.company}")
    year_label.config(text=f"Year: {game.year}, Month: {game.month}")
    money_label.config(text=f"Money: ${game.money:,}")
    market_share_label.config(text=f"Market Share: {game.market_share}% / {target}%")
    employees_label.config(text=f"Employees: {game.employees}")
    
    # Update bars
    def update_bar(var, label, bar, value):
        var.set(f"{label}: {value}")
        bar['value'] = value
        if value > 66:
            bar['style'] = 'green.Horizontal.TProgressbar'
        elif value > 33:
            bar['style'] = 'yellow.Horizontal.TProgressbar'
        else:
            bar['style'] = 'red.Horizontal.TProgressbar'
    
    update_bar(morale_var, "Morale", morale_bar, game.morale)
    update_bar(productivity_var, "Productivity", productivity_bar, game.productivity)
    update_bar(marketing_var, "Marketing", marketing_bar, game.marketing)
    update_bar(innovation_var, "Innovation", innovation_bar, game.innovation)
    update_bar(reputation_var, "Reputation", reputation_bar, game.reputation)
    update_bar(customer_satisfaction_var, "Customer Satisfaction", customer_satisfaction_bar, game.customer_satisfaction)
    
    leadership_label.config(text=f"Leadership: {game.leader_style.capitalize()}")
    difficulty_label.config(text=f"Difficulty: {game.difficulty}")
    
    unlocked = [ach for ach, data in game.achievements.items() if data["unlocked"]]
    achievements_label.config(text=f"Achievements: {len(unlocked)}/{len(game.achievements)} unlocked")

    profit_label.config(text=f"Monthly Profit: ${calculate_profit():,}")

def leadership_effect():
    if game.leader_style == "autocratic":
        game.productivity += 5
        game.morale -= 5
    elif game.leader_style == "democratic":
        game.morale += 5
        game.innovation += 2
    elif game.leader_style == "laissez-faire":
        game.morale += 3
        game.productivity -= 2
        game.innovation += 3

def calculate_profit():
    base = (game.employees * game.productivity * 0.5) + (game.marketing * 2) + (game.innovation * 1.5)
    morale_factor = game.morale / 50
    rep_factor = game.reputation / 50
    sat_factor = game.customer_satisfaction / 50
    return int(base * morale_factor * rep_factor * sat_factor)

def win_target():
    return {"Easy": 50, "Normal": 70, "Hard": 90}[game.difficulty]

def random_event():
    events = [
        ("none", "A quiet month."),
        ("strike", "Employees are striking due to low morale!"),
        ("lawsuit", "A lawsuit has been filed against the company!"),
        ("big_order", "A massive order came in!"),
        ("competitor_attack", "Competitor launched a smear campaign!"),
        ("innovation_breakthrough", "Your team had an innovation breakthrough!"),
        ("customer_complaint", "Customers are complaining about service!"),
        ("talent_poached", "A competitor poached one of your top employees!"),
        ("market_boom", "The market is booming!"),
        ("economic_downturn", "Economic downturn affecting sales.")
    ]
    event, desc = random.choice(events)
    difficulty_factor = {"Easy": 0.5, "Normal": 1, "Hard": 1.5}[game.difficulty]

    if event == "strike" and game.morale < 40:
        game.productivity -= int(15 * difficulty_factor)
        add_news(f"Strike! Productivity fell by {int(15 * difficulty_factor)}.")
        return "strike"
    elif event == "lawsuit":
        loss = int(5000 * difficulty_factor)
        game.money -= loss
        game.reputation -= 5
        add_news(f"Lawsuit! Lost ${loss} and reputation.")
        return "lawsuit"
    elif event == "big_order":
        gain = int(8000 * difficulty_factor)
        game.money += gain
        game.market_share += 2
        add_news(f"Big order! Earned ${gain} and gained market share.")
        return None
    elif event == "competitor_attack":
        if game.competitor_market_share > game.market_share:
            game.marketing -= 10
            game.reputation -= 5
            add_news("Competitor smear campaign! Marketing and reputation down.")
        else:
            add_news("Competitor tried to attack, but we held strong!")
        return None
    elif event == "innovation_breakthrough":
        game.innovation += 10
        game.reputation += 3
        add_news("Innovation breakthrough! Innovation and reputation up.")
        return None
    elif event == "customer_complaint":
        game.customer_satisfaction -= 10
        game.reputation -= 2
        add_news("Customer complaints! Satisfaction and reputation down.")
        return None
    elif event == "talent_poached":
        if game.employees > 1:
            game.employees -= 1
            game.productivity -= 5
            add_news("Employee poached! Lost a worker and productivity.")
        return None
    elif event == "market_boom":
        game.market_share += 3
        game.money += 3000
        add_news("Market boom! Gained market share and money.")
        game.market_share = min(100, game.market_share + 2)
        return None
    elif event == "economic_downturn":
        game.money -= 2000
        game.market_share -= 1
        add_news("Economic downturn! Lost money and market share.")
        return None
    else:
        add_news(desc)
        return None
    
def generate_order():
    if game.order_cooldown > 0 or len(game.orders) >= 3:
        return

    max_value = 1_000_000
    base = 2000 + (game.market_share * 500) + (game.reputation * 100)
    value = min(max_value, int(base))

    # New, slower scaling success rate
    base_success = 30  # base chance for any order
    prod_factor = game.productivity * 0.2  # smaller effect than before
    rep_factor = game.reputation * 0.15
    sat_factor = game.customer_satisfaction * 0.15

    success_rate = min(90, int(base_success + prod_factor + rep_factor + sat_factor))

    penalty = random.choice(["productivity", "reputation", "money"])

    game.orders.append({
        "value": value,
        "success": success_rate,
        "penalty": penalty
    })

    game.order_cooldown = 2
    update_orders_ui()




def resolve_order(index, accepted):
    order = game.orders.pop(index)
    game.order_cooldown = 2

    if not accepted:
        add_news("Order declined.")
        update_orders_ui()
        return

    roll = random.randint(1, 100)
    if roll <= order["success"]:
        game.money += order["value"]
        game.market_share = min(100, game.market_share + 1)
        add_news(f"Order success! Earned ${order['value']:,}")
    else:
        if order["penalty"] == "productivity":
            game.productivity -= 10
        elif order["penalty"] == "reputation":
            game.reputation -= 10
        else:
            game.money -= order["value"] // 2
        add_news("Order failed! Penalty applied.")

    update_status()
    update_orders_ui()


def update_orders_ui():
    # Clear current children
    for w in orders_frame.winfo_children():
        w.destroy()

    # Measure a single order widget to determine required height
    # We'll size the orders_frame to fit up to 3 orders so none get clipped
    sample_count = 3
    per_height = 0
    if True:
        sample = tk.Frame(orders_frame, bg="#FFFDF6", bd=2, relief="ridge")
        lbl = tk.Label(sample,
            text=f"Value: $0\nSuccess: 0%\nPenalty: -None",
            bg="#FFFDF6",
            fg="#1F2937",
            justify="center",
            font=("Arial", 12),
            anchor="center"
        )
        btn_frame_s = tk.Frame(sample, bg="#FFFDF6")
        btn_frame_s.pack(fill="x")
        tk.Button(btn_frame_s, text="Accept", bg="#A7C7A5", fg="#1F2937", font=("Arial", 10, "bold")).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(btn_frame_s, text="Decline", bg="#D8A1A1", fg="#1F2937", font=("Arial", 10, "bold")).pack(side="right", expand=True, fill="x", padx=2)
        # Temporarily pack to allow geometry calculation then remove
        lbl.pack(pady=2, fill="x", padx=3)
        sample.pack(pady=2, fill="x", padx=3)
        # Ensure the whole window processes geometry so we get a reliable height
        try:
            game_window.update_idletasks()
        except Exception:
            orders_frame.update_idletasks()
        per_height = sample.winfo_height()
        # Enforce a sensible minimum per-order height so three items never get squashed
        per_height = max(per_height, 130)
        sample.destroy()

    # Reserve space for exactly three orders so the panel fits tightly
    total_height = per_height * sample_count
    orders_frame.config(height=total_height)
    # Keep the right-side container slightly larger than the orders area
    try:
        right_frame.config(height=total_height + 2)
    except Exception:
        pass
    # Ensure geometry is recalculated so the change takes effect immediately
    try:
        game_window.update_idletasks()
    except Exception:
        orders_frame.update_idletasks()

    # Now create real order widgets
    for i, o in enumerate(game.orders):
        frame = tk.Frame(orders_frame, bg="#FFFDF6", bd=2, relief="ridge")
        frame.pack(pady=5, fill="x", padx=5)

        tk.Label(frame,
            text=f"Value: ${o['value']:,}\nSuccess: {o['success']}%\nPenalty: -{o['penalty'].capitalize()}",
            bg="#FFFDF6",
            fg="#1F2937",
            justify="center",
            font=("Arial", 12),
            anchor="center"
        ).pack(pady=6, fill="x", padx=4)

        btn_frame = tk.Frame(frame, bg="#FFFDF6")
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Accept",
                  command=lambda idx=i: resolve_order(idx, True),
                  bg="#A7C7A5", fg="#1F2937", font=("Arial", 10, "bold")).pack(side="left", expand=True, fill="x", padx=2)

        tk.Button(btn_frame, text="Decline",
                  command=lambda idx=i: resolve_order(idx, False),
                  bg="#D8A1A1", fg="#1F2937", font=("Arial", 10, "bold")).pack(side="right", expand=True, fill="x", padx=2)




def check_achievements():
    for ach, data in game.achievements.items():
        if not data["unlocked"]:
            if ach in ["Global GDP", "USA Debt", "Billionaire"]:
                if game.money >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")
                    messagebox.showinfo("Achievement Unlocked!", f"{ach}\n\n{data['desc']}")
            elif ach == "Market Dominator":
                if game.market_share >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")
                    messagebox.showinfo("Achievement Unlocked!", f"{ach}\n\n{data['desc']}")
            elif ach == "Employee Empire":
                if game.employees >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")
                    messagebox.showinfo("Achievement Unlocked!", f"{ach}\n\n{data['desc']}")

def add_news(msg):
    timestamp = f"Year {game.year}, Month {game.month}: "
    stackable_prefixes = (
        "Training session!",
        "PR campaign successful!",
        "Bonuses paid!",
        "New hire!",
        "Marketing campaign!",
        "R&D investment!",
        "Customer service focus!",
        "Upgraded ",
        "Hired "
    )

    def _is_stackable(m):
        return m.startswith(stackable_prefixes)

    if game.news_feed and _is_stackable(msg):
        last = game.news_feed[-1]
        last_body = last
        last_count = 1
        if ": " in last_body:
            last_body = last_body.split(": ", 1)[1]
        if " (x" in last_body and last_body.endswith(")"):
            try:
                count_str = last_body.rsplit(" (x", 1)[1][:-1]
                last_count = int(count_str)
                last_body = last_body.rsplit(" (x", 1)[0]
            except ValueError:
                last_count = 1
        if last_body == msg:
            game.news_feed[-1] = f"{timestamp}{msg} (x{last_count + 1})"
        else:
            game.news_feed.append(f"{timestamp}{msg} (x1)")
    else:
        if _is_stackable(msg):
            game.news_feed.append(f"{timestamp}{msg} (x1)")
        else:
            game.news_feed.append(f"{timestamp}{msg}")
    if len(game.news_feed) > 10:
        game.news_feed.pop(0)
    news_box.config(state="normal")
    news_box.delete(1.0, tk.END)
    news_box.insert(tk.END, "\n".join(reversed(game.news_feed)))
    news_box.config(state="disabled")

def monthly_tick():
    if not game.running:
        return

    # Decrease order cooldown
    if game.order_cooldown > 0:
        game.order_cooldown -= 1

    leadership_effect()
    profit = calculate_profit()
    game.money += profit

    # Increment time
    game.month += 1
    if game.month > 12:
        game.month = 1
        game.year += 1

    # Stat decays
    game.morale = max(0, game.morale - 5)
    game.customer_satisfaction = max(0, game.customer_satisfaction - 3)
    game.reputation = max(0, game.reputation - 2)

    # Employee effects
    if game.morale < 20 and game.employees > 0:
        game.employees -= 1
        add_news("Low morale! An employee quit.")

    # Competitor growth
    comp_growth = random.randint(1, 3)
    game.competitor_market_share += comp_growth
    game.market_share = min(100, max(0, game.market_share - 0.5 + min(2, game.money // 100000)))


    # Generate new orders
    generate_order()

    random_event()
    check_achievements()
    clamp_stats()
    update_status()
    check_game_end()

    game_window.after(3000, monthly_tick)


def next_year():
    leadership_effect()
    random_event()

    # Year end calculations
    game.year += 1
    check_game_end()
    update_status()

def check_game_end():
    target = win_target()
    if game.market_share >= target and not game.continue_mode:
        result = messagebox.askyesno("Victory!", f"YOU WIN! {target}% market share achieved!\n\nContinue for achievements?")
        if result:
            game.continue_mode = True
            message.set("Continuing for achievements... No win condition now!")
            add_news("Continuing in achievement mode!")
        else:
            message.set(f"YOU WIN! {target}% market share achieved!")
            end_game()
    elif game.money <= 0:
        message.set("Bankrupt! Game Over.")
        end_game()
    elif game.employees <= 0:
        message.set("All employees left! Game Over.")
        end_game()
    elif game.reputation <= 0:
        message.set("Reputation ruined! Game Over.")
        end_game()

def end_game():
    game.running = False
    # Remove any active orders immediately from the UI
    game.orders.clear()
    update_orders_ui()
    disable_buttons()
    save_exit_btn.grid_remove()
    restart_btn.grid()

def restart_game():
    global start_window, main_menu_window
    game.__init__()
    message.set("")
    # status.set("")  # removed
    news_box.config(state="normal")
    news_box.delete(1.0, tk.END)
    news_box.insert(tk.END, "Welcome to HR Management Simulator! News will appear here.")
    news_box.config(state="disabled")
    for b in buttons:
        b.config(state="normal")
    restart_btn.grid_remove()
    save_exit_btn.grid_remove()
    update_upgrade_buttons()
    update_dept_buttons()
    # Ensure orders UI reflects the reset state
    update_orders_ui()
    game_window.withdraw()
    create_main_menu()

def disable_buttons():
    for b in buttons:
        b.config(state="disabled")

# ---------------- ACTIONS ----------------
def training():
    cost = 5000
    if game.money >= cost:
        game.money -= cost
        game.productivity += 15
        add_news("Training session! Productivity +15")
    else:
        message.set("Not enough money!")

def pr_campaign():
    cost = 5000
    if game.money >= cost:
        game.money -= cost
        game.reputation = game.reputation + 15
        add_news("PR campaign successful! Reputation +15")
        update_status()
    else:
        message.set("Not enough money!")


def bonus():
    cost = 4000
    if game.money >= cost:
        game.money -= cost
        game.morale += 20
        add_news("Bonuses paid! Morale +20")
    else:
        message.set("Not enough money!")

def recruit():
    cost = 3000
    if game.money >= cost:
        game.money -= cost
        game.employees += 1
        add_news("New hire! +1 employee")
    else:
        message.set("Not enough money!")

def marketing_campaign():
    cost = 4000
    if game.money >= cost:
        game.money -= cost
        game.marketing += 15
        game.reputation += 5
        add_news("Marketing campaign! Marketing +15, Reputation +5")
    else:
        message.set("Not enough money!")

def r_and_d():
    cost = 6000
    if game.money >= cost:
        game.money -= cost
        game.innovation += 20
        add_news("R&D investment! Innovation +20")
    else:
        message.set("Not enough money!")

def customer_service():
    cost = 2000
    if game.money >= cost:
        game.money -= cost
        game.customer_satisfaction += 15
        game.reputation += 3
        add_news("Customer service focus! Satisfaction +15, Reputation +3")
    else:
        message.set("Not enough money!")

def change_leadership():
    styles = ["autocratic", "democratic", "laissez-faire"]
    current = styles.index(game.leader_style)
    game.leader_style = styles[(current + 1) % 3]
    add_news(f"Leadership changed to {game.leader_style.capitalize()}!")
    update_status()

def special_ability():
    if game.leader_style == "autocratic":
        if game.money >= 2000:
            game.money -= 2000
            game.productivity += 10
            game.morale -= 5
            add_news("Forced overtime! Productivity +10, Morale -5")
        else:
            message.set("Not enough money!")
    elif game.leader_style == "democratic":
        if game.money >= 3000:
            game.money -= 3000
            game.morale += 15
            game.innovation += 10
            add_news("Team building! Morale +15, Innovation +10")
        else:
            message.set("Not enough money!")
    elif game.leader_style == "laissez-faire":
        game.innovation += 5
        add_news("Creative freedom! Innovation +5")

def buy_upgrade(upgrade):
    costs = {"Better Office": 10000, "Automation": 15000, "Coffee Machine": 5000}
    effects = {
        "Better Office": lambda: setattr(game, 'morale', min(100, game.morale + 10)),
        "Automation": lambda: setattr(game, 'productivity', min(100, game.productivity + 15)),
        "Coffee Machine": None  # slower morale decay, handled elsewhere
    }
    cost = costs[upgrade]
    if game.money >= cost and not game.upgrades[upgrade]:
        game.money -= cost
        game.upgrades[upgrade] = True
        if effects[upgrade]:
            effects[upgrade]()
        add_news(f"Upgraded {upgrade}!")
        update_upgrade_buttons()
    else:
        message.set("Cannot buy upgrade!")

def buy_department(dept):
    costs = {"HR": 8000, "IT": 10000, "PR": 7000}
    cost = costs[dept]
    if game.money >= cost and not game.departments[dept]:
        game.money -= cost
        game.departments[dept] = True
        add_news(f"Hired {dept} department!")
        update_dept_buttons()
    else:
        message.set("Cannot hire department!")

def update_upgrade_buttons():
    for up, btn in upgrade_buttons.items():
        cost = {"Better Office": 10000, "Automation": 15000, "Coffee Machine": 5000}[up]
        effect = upgrade_effects[up]
        if game.upgrades[up]:
            btn.config(state="disabled", text=f"{up} (Owned)")
        else:
            btn.config(state="normal", text=f"{up} (${cost}) - {effect}")

def update_dept_buttons():
    for dept, btn in dept_buttons.items():
        cost = {"HR": 8000, "IT": 10000, "PR": 7000}[dept]
        effect = dept_effects[dept]
        if game.departments[dept]:
            btn.config(state="disabled", text=f"{dept} (Hired)")
        else:
            btn.config(state="normal", text=f"{dept} (${cost}) - {effect}")

# ---------------- GAME WINDOW ----------------
game_window = tk.Tk()
game_window.configure(bg="#F6F1E8")
game_window.title("HR Management Simulator")
game_window.geometry("1200x900")
game_window.withdraw()

# Root layout
game_root = tk.Frame(game_window, bg="#F6F1E8")
game_root.pack(fill="both", expand=True, padx=20, pady=20)
game_root.columnconfigure(0, weight=1, minsize=260)
game_root.columnconfigure(1, weight=2, minsize=440)
game_root.columnconfigure(2, weight=0, minsize=320)
game_root.rowconfigure(0, weight=0)
game_root.rowconfigure(1, weight=1)
game_root.rowconfigure(2, weight=0)

# Left column
left_top = tk.Frame(game_root, bg="#F6F1E8")
left_top.grid(row=0, column=0, sticky="nsew", padx=(0, 16), pady=(0, 16))
left_bottom = tk.Frame(game_root, bg="#F6F1E8")
left_bottom.grid(row=1, column=0, sticky="nsew", padx=(0, 16))

# Center column
center_header = tk.Frame(game_root, bg="#F6F1E8")
center_header.grid(row=0, column=1, sticky="new", pady=(0, 10))
center_content = tk.Frame(game_root, bg="#F6F1E8")
center_content.grid(row=1, column=1, sticky="nsew")
center_content.columnconfigure(0, weight=1)

# Right column (orders remain in the same place)
right_frame = tk.Frame(game_root, bg="#EFE7D8", width=320, bd=2, relief="solid")
right_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=(16, 0))
right_frame.grid_propagate(False)

# Footer
footer_frame = tk.Frame(game_root, bg="#F6F1E8")
footer_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(12, 0))
footer_frame.columnconfigure(0, weight=1)
footer_frame.columnconfigure(1, weight=0)

status = tk.StringVar()
message = tk.StringVar()

# Center header
tk.Label(
    center_header,
    text="PLAYER STATS",
    font=("Arial", 20, "bold"),
    bg="#F6F1E8",
    fg="#1F2937"
).pack()
tk.Frame(center_header, bg="#1F2937", height=2).pack(fill="x", pady=(6, 0))

# Orders panel
tk.Label(
    right_frame,
    text="ORDERS",
    font=("Arial", 14, "bold"),
    bg="#EFE7D8",
    fg="#1F2937"
).pack(pady=10)

orders_frame = tk.Frame(
    right_frame,
    bg="#EFE7D8",
    height=640,
    bd=0,
    highlightbackground="#1F2937",
    highlightthickness=1
)
orders_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
orders_frame.pack_propagate(False)

# Status panel
status_panel = tk.Frame(center_content, bg="#FFFDF6", bd=2, relief="solid")
status_panel.pack(fill="x", pady=(0, 10))
status_frame = tk.Frame(status_panel, bg="#FFFDF6")
status_frame.pack(fill="x", padx=10, pady=10)

# Style for progress bars
style = ttk.Style()
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", background='green')
style.configure("yellow.Horizontal.TProgressbar", background='yellow')
style.configure("red.Horizontal.TProgressbar", background='red')

# Status labels and bars
company_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
company_label.pack(fill="x")

year_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
year_label.pack(fill="x")

money_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
money_label.pack(fill="x")

market_share_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
market_share_label.pack(fill="x")

employees_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
employees_label.pack(fill="x")

# Function to create stat frame with label and bar
def create_stat_frame(parent, text_var):
    frame = tk.Frame(parent, bg="#FFFDF6")
    label = tk.Label(frame, textvariable=text_var, font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
    label.pack(side="left")
    bar = ttk.Progressbar(frame, orient="horizontal", length=150, mode="determinate", maximum=100)
    bar.pack(side="left", padx=(5,0))
    frame.pack(fill="x")
    return label, bar

morale_var = tk.StringVar()
morale_label, morale_bar = create_stat_frame(status_frame, morale_var)

productivity_var = tk.StringVar()
productivity_label, productivity_bar = create_stat_frame(status_frame, productivity_var)

marketing_var = tk.StringVar()
marketing_label, marketing_bar = create_stat_frame(status_frame, marketing_var)

innovation_var = tk.StringVar()
innovation_label, innovation_bar = create_stat_frame(status_frame, innovation_var)

reputation_var = tk.StringVar()
reputation_label, reputation_bar = create_stat_frame(status_frame, reputation_var)

customer_satisfaction_var = tk.StringVar()
customer_satisfaction_label, customer_satisfaction_bar = create_stat_frame(status_frame, customer_satisfaction_var)

leadership_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
leadership_label.pack(fill="x")

difficulty_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
difficulty_label.pack(fill="x")

achievements_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#FFFDF6", fg="#111827", anchor="w")
achievements_label.pack(fill="x")

profit_label = tk.Label(
    center_content,
    text="Monthly Profit: $0",
    font=("Arial", 16, "bold"),
    bg="#F6F1E8",
    fg="#0F766E"
)
profit_label.pack(pady=(0, 8))

message_label = tk.Label(
    center_content,
    textvariable=message,
    font=("Times New Roman", 12, "italic"),
    fg="#111827",
    bg="#EFE7D8",
    width=60,
    height=2,
    relief="solid",
    bd=2
)
message_label.pack(pady=(0, 12))

# News feed (newspaper style)
news_panel = tk.Frame(left_top, bg="#FFFDF6", bd=2, relief="solid")
news_panel.pack(fill="both", expand=True)
news_header = tk.Label(
    news_panel,
    text="NEWS FEED",
    font=("Times New Roman", 14, "bold"),
    bg="#FFFDF6",
    fg="#111827"
)
news_header.pack(pady=(8, 2))
tk.Frame(news_panel, bg="#111827", height=1).pack(fill="x", padx=8, pady=(0, 6))

# News feed with scrollbar
news_frame = tk.Frame(news_panel, bg="#FFFDF6")
news_frame.pack(padx=8, pady=(0, 8), fill="both", expand=True)
news_scrollbar = tk.Scrollbar(news_frame)
news_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
news_box = tk.Text(
    news_frame,
    font=("Times New Roman", 11),
    bg="#FCF5E5",
    fg="#111827",
    width=32,
    height=14,
    relief="solid",
    bd=2,
    wrap="word",
    yscrollcommand=news_scrollbar.set
)
news_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
news_scrollbar.config(command=news_box.yview)
news_box.insert(tk.END, "Welcome to HR Management Simulator! News will appear here.")
news_box.config(state="disabled")  # Make it read-only

# Non-permanent upgrades (actions)
actions_panel = tk.Frame(left_bottom, bg="#FFFDF6", bd=2, relief="solid")
actions_panel.pack(fill="both", expand=True)
tk.Label(
    actions_panel,
    text="NON-PERMANENT UPGRADES",
    font=("Arial", 12, "bold"),
    bg="#FFFDF6",
    fg="#111827"
).pack(pady=(10, 6))
actions_frame = tk.Frame(actions_panel, bg="#FFFDF6")
actions_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

# Buttons
buttons = [
    tk.Button(actions_frame, text="Training ($5000) - Productivity +15", command=training),
    tk.Button(actions_frame, text="PR Campaign ($5000) - Reputation +15", command=pr_campaign),
    tk.Button(actions_frame, text="Bonuses ($4000) - Morale +20", command=bonus),
    tk.Button(actions_frame, text="Recruit ($3000) - +1 Employee", command=recruit),
    tk.Button(actions_frame, text="Marketing ($4000) - Marketing +15, Reputation +5", command=marketing_campaign),
    tk.Button(actions_frame, text="R&D ($6000) - Innovation +20", command=r_and_d),
    tk.Button(actions_frame, text="Customer Service ($2000) - Satisfaction +15, Reputation +3", command=customer_service),
    tk.Button(actions_frame, text="Change Leadership (Cycle Styles)", command=change_leadership),
    tk.Button(actions_frame, text="Special Ability (Style-Dependent)", command=special_ability),
    tk.Button(actions_frame, text="Save Game", command=lambda: save_game())
]

for b in buttons:
    b.pack(fill="x", pady=2)
    b.configure(bg="#E7DED0", fg="#111827", activebackground="#D7CDBD", activeforeground="#111827", relief="solid", bd=1, font=("Arial", 9, "bold"))

# Permanent upgrades panel
permanent_panel = tk.Frame(center_content, bg="#F6F1E8")
permanent_panel.pack(fill="both", expand=True)
tk.Label(
    permanent_panel,
    text="PERMANENT UPGRADES (3 PER COLUMN)",
    font=("Arial", 12, "bold"),
    bg="#F6F1E8",
    fg="#1F2937"
).pack(pady=(2, 8))

perm_columns = tk.Frame(permanent_panel, bg="#F6F1E8")
perm_columns.pack(fill="both", expand=True)
perm_columns.columnconfigure(0, weight=1)
perm_columns.columnconfigure(1, weight=1)
perm_columns.rowconfigure(0, weight=1)

perm_left = tk.Frame(perm_columns, bg="#FFFDF6", bd=2, relief="solid")
perm_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
perm_right = tk.Frame(perm_columns, bg="#FFFDF6", bd=2, relief="solid")
perm_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

# Upgrade buttons
upgrade_frame = tk.Frame(perm_left, bg="#FFFDF6")
upgrade_frame.pack(fill="both", expand=True, padx=10, pady=10)
tk.Label(upgrade_frame, text="Upgrades", font=("Arial", 12, "bold"), bg="#FFFDF6", fg="#111827").pack(pady=(0, 6))
upgrade_buttons = {}
upgrade_effects = {
    "Better Office": "Morale +10",
    "Automation": "Productivity +15",
    "Coffee Machine": "Slower Morale Decay"
}
for up in ["Better Office", "Automation", "Coffee Machine"]:
    cost = {"Better Office": 10000, "Automation": 15000, "Coffee Machine": 5000}[up]
    btn = tk.Button(upgrade_frame, text=f"{up} (${cost}) - {upgrade_effects[up]}", command=lambda u=up: buy_upgrade(u))
    btn.pack(fill="x", pady=3)
    btn.configure(bg="#E7DED0", fg="#111827", activebackground="#D7CDBD", activeforeground="#111827", relief="solid", bd=1)
    upgrade_buttons[up] = btn

# Department buttons
dept_frame = tk.Frame(perm_right, bg="#FFFDF6")
dept_frame.pack(fill="both", expand=True, padx=10, pady=10)
tk.Label(dept_frame, text="Departments", font=("Arial", 12, "bold"), bg="#FFFDF6", fg="#111827").pack(pady=(0, 6))
dept_buttons = {}
dept_effects = {
    "HR": "Ongoing Morale Boost",
    "IT": "Ongoing Productivity Boost",
    "PR": "Ongoing Reputation Boost"
}
for dept in ["HR", "IT", "PR"]:
    cost = {"HR": 8000, "IT": 10000, "PR": 7000}[dept]
    btn = tk.Button(dept_frame, text=f"{dept} (${cost}) - {dept_effects[dept]}", command=lambda d=dept: buy_department(d))
    btn.pack(fill="x", pady=3)
    btn.configure(bg="#E7DED0", fg="#111827", activebackground="#D7CDBD", activeforeground="#111827", relief="solid", bd=1)
    dept_buttons[dept] = btn




# Restart button
restart_btn = tk.Button(
    footer_frame,
    text="Restart Game",
    font=("Arial", 14, "bold"),
    bg="#E7DED0",
    fg="#111827",
    command=restart_game
)

# Save & Exit button
def save_and_exit():
    """Save the game and return to main menu."""
    try:
        save_game()
        message.set("Saving and exiting...")
        game_window.update()  # Process the message update
        game_window.after(500, restart_game)  # Delay slightly to let save complete
    except Exception as e:
        message.set(f"Error: {str(e)}")

save_exit_btn = tk.Button(
    footer_frame,
    text="Save & Exit",
    font=("Arial", 12, "bold"),
    bg="#F59E0B",
    fg="#111827",
    command=save_and_exit
)
restart_btn.grid(row=0, column=0, sticky="w", padx=10)
save_exit_btn.grid(row=0, column=1, sticky="e", padx=10)
restart_btn.grid_remove()
save_exit_btn.grid_remove()

# ---------------- MAIN MENU ----------------
def create_main_menu():
    global main_menu_window
    main_menu_window = tk.Tk()
    main_menu_window.configure(bg="#0F172A")
    main_menu_window.title("HR Management Simulator")
    try:
        main_menu_window.attributes("-fullscreen", True)
    except Exception:
        try:
            main_menu_window.state('zoomed')
        except Exception:
            main_menu_window.geometry("800x600")

    # Animated title with rainbow effect and smooth scaling
    main_menu_window.update_idletasks()
    menu_width = max(800, main_menu_window.winfo_screenwidth())
    title_container = tk.Frame(main_menu_window, bg="#0F172A", height=140, width=menu_width)
    title_container.pack(pady=(60, 30), fill="x")
    title_container.pack_propagate(False)

    title_label = tk.Label(title_container, text="HR MANAGEMENT SIMULATOR", font=("Arial", 40, "bold"), bg="#0F172A", fg="#FF0000")
    title_label.place(relx=0.5, rely=0.5, anchor="center")

    # Smooth rainbow animation with size and tilt for the title
    def _start_title_rainbow():
        global _animation_callbacks
        hue_state = {'value': 0}
        time_state = {'t': 0}
        
        def _animate():
            try:
                if not main_menu_window.winfo_exists():
                    _animation_callbacks.pop('main_menu', None)
                    return
            except Exception:
                _animation_callbacks.pop('main_menu', None)
                return
            
            # Create rainbow color with full saturation and 60% lightness for visibility
            color = _hsl_to_hex(hue_state['value'], 100, 60)
            
            # Smooth size variation using sine wave (40 to 56 range, centered at 48)
            size_variation = math.sin(time_state['t'] * 0.08) * 8
            current_size = int(48 + size_variation)
            
            # Create tilt effect by adjusting overstrike or using slight kerning simulation
            # We'll use the angle in the animation for visual feedback
            tilt_angle = math.sin(time_state['t'] * 0.06) * 10  # -10 to +10 degrees
            
            title_label.config(fg=color, font=("Arial", current_size, "bold"))
            
            # Smooth hue rotation (full circle every 4 seconds at 50ms updates)
            hue_state['value'] = (hue_state['value'] + 1.5) % 360
            time_state['t'] += 1
            
            _animation_callbacks['main_menu'] = lambda: main_menu_window.after(50, _animate)
            _animation_callbacks['main_menu']()
        
        _animate()
    _start_title_rainbow()

    buttons_frame = tk.Frame(main_menu_window, bg="#0F172A")
    buttons_frame.pack(pady=(25, 0))

    button_font = ("Comic Sans MS", 46, "bold")
    tk.Button(buttons_frame, text="New Game", font=button_font, command=create_game_selection, bg="white", fg="#0F172A", width=20, height=1, activebackground="#D0D0D0", activeforeground="#0F172A").pack(pady=12, padx=10)
    tk.Button(buttons_frame, text="Load Game", font=button_font, command=load_game_dialog, bg="white", fg="#0F172A", width=20, height=1, activebackground="#D0D0D0", activeforeground="#0F172A").pack(pady=12, padx=10)
    tk.Button(buttons_frame, text="Achievements", font=button_font, command=view_achievements, bg="white", fg="#0F172A", width=20, height=1, activebackground="#D0D0D0", activeforeground="#0F172A").pack(pady=12, padx=10)

    main_menu_window.mainloop()

def view_achievements():
    messagebox.showinfo("Achievements", "Achievements coming soon!")

# ---------------- GAME SELECTION SCREEN ----------------
def create_game_selection():
    global start_window, company_var, leadership_var, difficulty_var
    try:
        main_menu_window.destroy()
    except:
        pass
    
    start_window = tk.Tk()
    start_window.configure(bg="#0F172A")
    start_window.title("Start Your Empire")
    # Enter fullscreen immediately when the menu opens
    try:
        start_window.attributes("-fullscreen", True)
    except Exception:
        try:
            start_window.state('zoomed')
        except Exception:
            start_window.geometry("800x900")

    company_var = tk.StringVar(value="")
    leadership_var = tk.StringVar(value="democratic")
    difficulty_var = tk.StringVar(value="Normal")
    business_name_var = tk.StringVar(value="")

    company_label = tk.Label(start_window, text="Selected Company: None", font=("Arial", 13, "bold"), bg="#1E293B", fg="#FFD700")
    company_label.pack(pady=5)
    leader_label = tk.Label(start_window, text="Selected Leadership: Democratic", font=("Arial", 13, "bold"), bg="#1E293B", fg="#FFD700")
    leader_label.pack(pady=5)
    diff_label = tk.Label(start_window, text="Selected Difficulty: Normal", font=("Arial", 13, "bold"), bg="#1E293B", fg="#FFD700")
    diff_label.pack(pady=5)

    tk.Label(start_window, text="Business Name:", font=("Arial", 16, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=6)
    name_entry = tk.Entry(start_window, textvariable=business_name_var, font=("Arial", 14), width=30)
    name_entry.pack(pady=2)

    tk.Label(start_window, text="Choose Your Company", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=8)
    def set_company(c):
        company_var.set(c)
        company_label.config(text=f"Selected Company: {c}", fg="green")
    tk.Button(start_window, text="Tech Startup", command=lambda: set_company("Tech Startup"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Restaurant Chain", command=lambda: set_company("Restaurant Chain"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Manufacturing", command=lambda: set_company("Manufacturing"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Entertainment", command=lambda: set_company("Entertainment"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)

    tk.Label(start_window, text="Choose Leadership Style", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=8)
    def set_leadership(l):
        leadership_var.set(l)
        leader_label.config(text=f"Selected Leadership: {l.capitalize()}", fg="green")
    tk.Button(start_window, text="Autocratic", command=lambda: set_leadership("autocratic"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Democratic", command=lambda: set_leadership("democratic"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Laissez-faire", command=lambda: set_leadership("laissez-faire"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)

    tk.Label(start_window, text="Choose Difficulty", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=8)
    def set_difficulty(d):
        difficulty_var.set(d)
        diff_label.config(text=f"Selected Difficulty: {d}", fg="green")
    tk.Button(start_window, text="Easy", command=lambda: set_difficulty("Easy"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Normal", command=lambda: set_difficulty("Normal"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)
    tk.Button(start_window, text="Hard", command=lambda: set_difficulty("Hard"), font=("Arial", 14), width=22).pack(pady=6, ipady=6)

    def start_game():
        # Business name required (read directly from entry to avoid StringVar sync issues)
        name_text = name_entry.get().strip()
        if name_text == "":
            messagebox.showerror("Name Required", "Please enter a business name.")
            return
        # If player didn't pick a company type, default to 'Custom'
        selected_type = company_var.get().strip() if company_var.get().strip() != "" else "Custom"
        # Business name is the player-chosen company name; store type separately
        game.company = name_text
        game.company_type = selected_type
        game.leader_style = leadership_var.get()
        game.difficulty = difficulty_var.get()

        # Starting adjustments
        if game.difficulty == "Easy":
            game.money = 30000
            game.market_share = 15
        elif game.difficulty == "Hard":
            game.money = 15000
            game.market_share = 5
        else:
            game.money = 20000
            game.market_share = 10

        if getattr(game, 'company_type', None) == "Tech Startup":
            game.innovation += 10
            game.productivity -= 5
        elif getattr(game, 'company_type', None) == "Restaurant Chain":
            game.customer_satisfaction += 10
            game.reputation += 5
        elif getattr(game, 'company_type', None) == "Manufacturing":
            game.productivity += 10
            game.morale -= 5
        elif getattr(game, 'company_type', None) == "Entertainment":
            game.marketing += 10
            game.reputation += 5

        rules = (
            "Welcome to HR Management Simulator!\n\n"
            "Made by Jeffrey, Ideas from Danila, Audrey and Lyra.\n\n"
            "Rules:\n"
            "- Manage your employees, morale, productivity, marketing, innovation, reputation, and customer satisfaction.\n"
            "- Gain market share to reach your win target based on difficulty.\n"
            "- Stats decay over time, keep them up with actions!\n"
            "- Higher morale keeps employees from quitting.\n"
            "- Watch out for strikes, lawsuits, competitor attacks, and random events!\n"
            "- Game ends if market share reaches target, or money to zero, all employees quit, or reputation to zero.\n"
            "- Use buttons wisely to train, give bonuses, recruit, market, invest in R&D, and more.\n"
            "- Buy upgrades and departments for permanent bonuses.\n\n"
            "Good luck!"
        )
        messagebox.showinfo("Rules", rules)

        start_window.destroy()
        game_window.deiconify()
        # Enter fullscreen immediately when the game window appears
        try:
            game_window.attributes("-fullscreen", True)
        except Exception:
            # Fallback to maximized window on platforms that don't support fullscreen attribute
            try:
                game_window.state('zoomed')
            except Exception:
                pass
        update_status()
        update_upgrade_buttons()
        update_dept_buttons()
        save_exit_btn.grid()
        save_exit_btn.lift()
        game.running = True
        monthly_tick()

        # Auto-save initial state so it appears in load list
        save_game()

    tk.Button(start_window, text="Start", font=("Arial", 20, "bold"), command=start_game, bg="#22C55E", fg="#0F172A", width=24).pack(pady=20, ipady=8)

    start_window.mainloop()

# ---------------- SAVE / LOAD ----------------
def ensure_saves_dir():
    saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'saves')
    if not os.path.exists(saves_dir):
        try:
            os.makedirs(saves_dir, exist_ok=True)
        except PermissionError:
            # Fallback to temp directory if permission denied
            saves_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Temp', 'HR_Sim_Saves')
            os.makedirs(saves_dir, exist_ok=True)
    return saves_dir

def get_saves_dir():
    """Get the saves directory path."""
    return ensure_saves_dir()

def _sanitize_filename(name):
    cleaned = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
    return cleaned.strip().replace(' ', '_')

def save_game():
    saves_dir = get_saves_dir()
    if not getattr(game, 'company', None) or str(game.company).strip() == "":
        # ask for a name
        name = simpledialog.askstring("Save Game", "Enter business name for save:")
        if not name:
            message.set("Save cancelled.")
            return
        game.company = name.strip()
    filename = _sanitize_filename(game.company) + ".json"
    path = os.path.join(saves_dir, filename)
    try:
        # We only save plain data; Game contains simple types
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(game.__dict__, f, indent=2)
        message.set(f"Game saved as {filename}")
        add_news(f"Game saved: {filename}")
    except Exception as e:
        message.set(f"Save failed: {e}")

def load_game_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        messagebox.showerror("Load Error", f"Failed to load: {e}")
        return
    # Reset and apply loaded values
    game.__init__()
    for k, v in data.items():
        try:
            setattr(game, k, v)
        except Exception:
            pass

    # Update UI after loading
    try:
        update_upgrade_buttons()
        update_dept_buttons()
        update_orders_ui()
        update_status()
        # Refresh news feed UI from loaded data
        try:
            news_box.config(state="normal")
            news_box.delete(1.0, tk.END)
            news_box.insert(tk.END, "\n".join(reversed(game.news_feed)))
            news_box.config(state="disabled")
        except Exception:
            pass
    except Exception:
        pass
    game.running = True
    try:
        game_window.deiconify()
        game_window.attributes("-fullscreen", True)
    except Exception:
        try:
            game_window.state('zoomed')
        except Exception:
            pass
    monthly_tick()

def load_game_dialog():
    saves_dir = get_saves_dir()
    files = [f for f in os.listdir(saves_dir) if f.endswith('.json')]
    if not files:
        messagebox.showinfo("Load Game", "No save files found.")
        return
    win = tk.Toplevel()
    win.title("Load Game")
    win.configure(bg="#0F172A")
    lb = tk.Listbox(win, width=60, height=12)
    for f in files:
        lb.insert(tk.END, f)
    lb.pack(padx=10, pady=10)
    def do_load():
        sel = lb.curselection()
        if not sel:
            return
        fname = lb.get(sel[0])
        path = os.path.join(saves_dir, fname)
        load_game_file(path)
        try:
            win.destroy()
        except:
            pass
        try:
            main_menu_window.destroy()
        except:
            pass
    tk.Button(win, text="Load", command=do_load, bg="#22C55E", fg="#0F172A").pack(pady=6)

# ---------------- START ----------------
create_main_menu()
