# HR Management Simulator by Jeffrey
# Inspired by ideas from Danila, Audrey, and Lyra

print("Starting HR Management Simulator... Please wait for the window to appear.")

import tkinter as tk
import tkinter.messagebox as messagebox
import random
import time
from tkinter import ttk

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
    
        self.active_order = None
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
    if game.active_order or game.order_cooldown > 0:
        return

    max_value = 1_000_000
    base = 2000 + (game.market_share * 500) + (game.reputation * 100)
    value = min(max_value, int(base))

    success_rate = min(95, int(
        40 +
        game.productivity * 0.3 +
        game.reputation * 0.2 +
        game.customer_satisfaction * 0.2
    ))

    penalty = random.choice(["productivity", "reputation", "money"])

    game.active_order = {
        "value": value,
        "success": success_rate,
        "penalty": penalty
    }

    show_order_ui()


def resolve_order(accepted):
    order = game.active_order
    game.active_order = None
    game.order_cooldown = 2

    if not accepted:
        add_news("Order declined.")
        hide_order_ui()
        return

    roll = random.randint(1, 100)
    if roll <= order["success"]:
        game.money += order["value"]
        game.market_share += 1
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
    hide_order_ui()


def show_order_ui():
    o = game.active_order
    order_label.config(
        text=f"NEW ORDER\n"
             f"Value: ${o['value']:,}\n"
             f"Success Chance: {o['success']}%\n"
             f"Failure Penalty: -{o['penalty'].capitalize()}"
    )
    order_frame.pack(pady=8, fill="x")


def hide_order_ui():
    order_frame.pack_forget()


def check_achievements():
    for ach, data in game.achievements.items():
        if not data["unlocked"]:
            if ach in ["Global GDP", "USA Debt", "Billionaire"]:
                if game.money >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")
            elif ach == "Market Dominator":
                if game.market_share >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")
            elif ach == "Employee Empire":
                if game.employees >= data["target"]:
                    data["unlocked"] = True
                    add_news(f"Achievement Unlocked: {ach} - {data['desc']}")

def add_news(msg):
    game.news_feed.append(f"Year {game.year}, Month {game.month}: {msg}")
    if len(game.news_feed) > 10:
        game.news_feed.pop(0)
    news_box.config(state="normal")
    news_box.delete(1.0, tk.END)
    news_box.insert(tk.END, "\n".join(reversed(game.news_feed)))
    news_box.config(state="disabled")

def monthly_tick():
    if not game.running:
        return

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
    game.market_share = max(0, game.market_share - 0.5 + min(2, game.money // 100000))  # slight decay, but money helps

    if game.order_cooldown > 0:
        game.order_cooldown -= 1
    else:
        generate_order()

    random_event()
    check_achievements()
    update_status()
    check_game_end()

    game_window.after(3000, monthly_tick)  # every 3 seconds for demo

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
    disable_buttons()
    restart_btn.pack(pady=10)

def restart_game():
    global start_window
    game.__init__()
    message.set("")
    # status.set("")  # removed
    news_box.config(state="normal")
    news_box.delete(1.0, tk.END)
    news_box.insert(tk.END, "Welcome to HR Management Simulator! News will appear here.")
    news_box.config(state="disabled")
    for b in buttons:
        b.config(state="normal")
    restart_btn.pack_forget()
    update_upgrade_buttons()
    update_dept_buttons()
    game_window.withdraw()
    create_start_screen()

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
        game.reputation = min(100, game.reputation + 15)
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
game_window.configure(bg="#0F172A")
game_window.title("HR Management Simulator")
game_window.geometry("800x900")
game_window.withdraw()

status = tk.StringVar()
message = tk.StringVar()

# Status frame with bars
status_frame = tk.Frame(game_window, bg="#1E293B")
status_frame.pack(pady=5, fill="x")  # back to original position

# Style for progress bars
style = ttk.Style()
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", background='green')
style.configure("yellow.Horizontal.TProgressbar", background='yellow')
style.configure("red.Horizontal.TProgressbar", background='red')

# Status labels and bars
company_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
company_label.pack(fill="x")

year_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
year_label.pack(fill="x")

money_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
money_label.pack(fill="x")

market_share_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
market_share_label.pack(fill="x")

employees_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
employees_label.pack(fill="x")

# Function to create stat frame with label and bar
def create_stat_frame(parent, text_var):
    frame = tk.Frame(parent, bg="#1E293B")
    label = tk.Label(frame, textvariable=text_var, font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
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

leadership_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
leadership_label.pack(fill="x")

difficulty_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
difficulty_label.pack(fill="x")

achievements_label = tk.Label(status_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", anchor="w")
achievements_label.pack(fill="x")

profit_label = tk.Label(
    game_window,
    text="Monthly Profit: $0",
    font=("Arial", 16, "bold"),
    bg="#0F172A",
    fg="#22C55E"
)
profit_label.pack(pady=2)

message_label = tk.Label(
    game_window,
    textvariable=message,
    font=("Comic Sans MS", 14),
    fg="#F1F5F9",
    bg="#334155",
    width=80,
    height=1,
    relief="solid",
    bd=2
)
message_label.pack(pady=2)

news_label = tk.Label(
    game_window,
    text="News Feed:",
    font=("Arial", 14, "bold"),
    bg="#0F172A",
    fg="#F59E0B"
)
news_label.pack(pady=5)

# News feed with scrollbar
news_frame = tk.Frame(game_window, bg="#0F172A")
news_frame.pack(pady=5)
news_scrollbar = tk.Scrollbar(news_frame)
news_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
news_box = tk.Text(
    news_frame,
    font=("Arial", 10),
    bg="#1E293B",
    fg="#F1F5F9",
    width=80,
    height=5,
    relief="solid",
    bd=2,
    yscrollcommand=news_scrollbar.set
)
news_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
news_scrollbar.config(command=news_box.yview)
news_box.insert(tk.END, "Welcome to HR Management Simulator! News will appear here.")
news_box.config(state="disabled")  # Make it read-only

# Buttons
buttons = [
    tk.Button(game_window, text="Training ($5000) - Productivity +15", command=training),
    tk.Button(game_window, text="PR Campaign ($5000) - Reputation +15", command=pr_campaign),
    tk.Button(game_window, text="Bonuses ($4000) - Morale +20", command=bonus),
    tk.Button(game_window, text="Recruit ($3000) - +1 Employee", command=recruit),
    tk.Button(game_window, text="Marketing ($4000) - Marketing +15, Reputation +5", command=marketing_campaign),
    tk.Button(game_window, text="R&D ($6000) - Innovation +20", command=r_and_d),
    tk.Button(game_window, text="Customer Service ($2000) - Satisfaction +15, Reputation +3", command=customer_service),
    tk.Button(game_window, text="Change Leadership (Cycle Styles)", command=change_leadership),
    tk.Button(game_window, text="Special Ability (Style-Dependent)", command=special_ability)
]

for b in buttons:
    b.pack(fill="x", pady=2)
    b.configure(bg="#334155", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)

# status_frame.pack(pady=5, fill="x")  # back after buttons

# Upgrade buttons
upgrade_frame = tk.Frame(game_window, bg="#0F172A")
upgrade_frame.pack(pady=10)
tk.Label(upgrade_frame, text="Upgrades:", font=("Arial", 14, "bold"), bg="#0F172A", fg="#22C55E").pack()
upgrade_buttons = {}
upgrade_effects = {
    "Better Office": "Morale +10",
    "Automation": "Productivity +15",
    "Coffee Machine": "Slower Morale Decay"
}
for up in ["Better Office", "Automation", "Coffee Machine"]:
    cost = {"Better Office": 10000, "Automation": 15000, "Coffee Machine": 5000}[up]
    btn = tk.Button(upgrade_frame, text=f"{up} (${cost}) - {upgrade_effects[up]}", command=lambda u=up: buy_upgrade(u))
    btn.pack(fill="x", pady=1)
    btn.configure(bg="#475569", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)
    upgrade_buttons[up] = btn

# Department buttons
dept_frame = tk.Frame(game_window, bg="#0F172A")
dept_frame.pack(pady=10)
tk.Label(dept_frame, text="Departments:", font=("Arial", 14, "bold"), bg="#0F172A", fg="#22C55E").pack()
dept_buttons = {}
dept_effects = {
    "HR": "Ongoing Morale Boost",
    "IT": "Ongoing Productivity Boost",
    "PR": "Ongoing Reputation Boost"
}
for dept in ["HR", "IT", "PR"]:
    cost = {"HR": 8000, "IT": 10000, "PR": 7000}[dept]
    btn = tk.Button(dept_frame, text=f"{dept} (${cost}) - {dept_effects[dept]}", command=lambda d=dept: buy_department(d))
    btn.pack(fill="x", pady=1)
    btn.configure(bg="#475569", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)
    dept_buttons[dept] = btn

# Order frame
order_frame = tk.Frame(game_window, bg="#1E293B", bd=3, relief="ridge")
order_label = tk.Label(order_frame, text="", font=("Arial", 12), bg="#1E293B", fg="#F1F5F9", justify="left")
order_label.pack(pady=5)

accept_btn = tk.Button(order_frame, text="Accept", command=lambda: resolve_order(True))
decline_btn = tk.Button(order_frame, text="Decline", command=lambda: resolve_order(False))

accept_btn.pack(side="left", expand=True, fill="x", padx=5, pady=5)
decline_btn.pack(side="right", expand=True, fill="x", padx=5, pady=5)

order_frame.pack_forget()


# Restart button
restart_btn = tk.Button(
    game_window,
    text="Restart Game",
    font=("Arial", 16),
    bg="#22C55E",
    fg="#0F172A",
    command=restart_game
)

# ---------------- START SCREEN ----------------
def create_start_screen():
    global start_window, company_var, leadership_var, difficulty_var
    start_window = tk.Tk()
    start_window.configure(bg="#0F172A")
    start_window.title("Start Your Empire")
    start_window.geometry("600x700")

    tk.Label(start_window, text="HR Management Simulator", font=("Arial", 24, "bold"), bg="#0F172A", fg="#1E3A8A").pack(pady=20)

    company_var = tk.StringVar(value="")
    leadership_var = tk.StringVar(value="democratic")
    difficulty_var = tk.StringVar(value="Normal")

    company_label = tk.Label(start_window, text="Selected Company: None", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    company_label.pack(pady=5)
    leader_label = tk.Label(start_window, text="Selected Leadership: Democratic", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    leader_label.pack(pady=5)
    diff_label = tk.Label(start_window, text="Selected Difficulty: Normal", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    diff_label.pack(pady=5)

    tk.Label(start_window, text="Choose Your Company", font=("Arial", 18, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=10)
    def set_company(c):
        company_var.set(c)
        company_label.config(text=f"Selected Company: {c}", fg="green")
    tk.Button(start_window, text="Tech Startup", command=lambda: set_company("Tech Startup")).pack(pady=2)
    tk.Button(start_window, text="Restaurant Chain", command=lambda: set_company("Restaurant Chain")).pack(pady=2)
    tk.Button(start_window, text="Manufacturing", command=lambda: set_company("Manufacturing")).pack(pady=2)
    tk.Button(start_window, text="Entertainment", command=lambda: set_company("Entertainment")).pack(pady=2)

    tk.Label(start_window, text="Choose Leadership Style", font=("Arial", 18, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=10)
    def set_leadership(l):
        leadership_var.set(l)
        leader_label.config(text=f"Selected Leadership: {l.capitalize()}", fg="green")
    tk.Button(start_window, text="Autocratic", command=lambda: set_leadership("autocratic")).pack(pady=2)
    tk.Button(start_window, text="Democratic", command=lambda: set_leadership("democratic")).pack(pady=2)
    tk.Button(start_window, text="Laissez-faire", command=lambda: set_leadership("laissez-faire")).pack(pady=2)

    tk.Label(start_window, text="Choose Difficulty", font=("Arial", 18, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=10)
    def set_difficulty(d):
        difficulty_var.set(d)
        diff_label.config(text=f"Selected Difficulty: {d}", fg="green")
    tk.Button(start_window, text="Easy", command=lambda: set_difficulty("Easy")).pack(pady=2)
    tk.Button(start_window, text="Normal", command=lambda: set_difficulty("Normal")).pack(pady=2)
    tk.Button(start_window, text="Hard", command=lambda: set_difficulty("Hard")).pack(pady=2)

    def start_game():
        if company_var.get() == "":
            company_label.config(text="Please select a company!", fg="red")
            return
        game.company = company_var.get()
        game.leader_style = leadership_var.get()
        game.difficulty = difficulty_var.get()

        # Starting adjustments
        if game.difficulty == "Easy":
            game.money = 10000000000
            game.market_share = 15
        elif game.difficulty == "Hard":
            game.money = 15000
            game.market_share = 5
        else:
            game.money = 20000
            game.market_share = 10

        if game.company == "Tech Startup":
            game.innovation += 10
            game.productivity -= 5
        elif game.company == "Restaurant Chain":
            game.customer_satisfaction += 10
            game.reputation += 5
        elif game.company == "Manufacturing":
            game.productivity += 10
            game.morale -= 5
        elif game.company == "Entertainment":
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
        update_status()
        update_upgrade_buttons()
        update_dept_buttons()
        game.running = True
        monthly_tick()

    tk.Button(start_window, text="Start Empire", font=("Arial", 18, "bold"), command=start_game, bg="#22C55E", fg="#0F172A").pack(pady=20)

    start_window.mainloop()

# ---------------- START ----------------
create_start_screen()
