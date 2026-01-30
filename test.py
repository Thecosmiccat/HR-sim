# Business Empire Builder by Jeffrey
# A fun management simulator with strategy and choices

import tkinter as tk
import tkinter.messagebox as messagebox
import random
import time

# ---------------- GAME STATE ----------------
class Game:
    def __init__(self):
        self.year = 1
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
        self.news_feed = []
        self.achievements = []

game = Game()

# ---------------- GAME FUNCTIONS ----------------
def update_status():
    target = win_target()
    status.set(
        f"Company: {game.company}\nYear: {game.year}\nMoney: ${game.money:,}\n"
        f"Market Share: {game.market_share}% / {target}%\n"
        f"Employees: {game.employees}\nMorale: {game.morale}\nProductivity: {game.productivity}\n"
        f"Marketing: {game.marketing}\nInnovation: {game.innovation}\nReputation: {game.reputation}\n"
        f"Customer Satisfaction: {game.customer_satisfaction}\nLeadership: {game.leader_style.capitalize()}\n"
        f"Difficulty: {game.difficulty}"
    )
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

def add_news(msg):
    game.news_feed.append(f"Year {game.year}: {msg}")
    if len(game.news_feed) > 10:
        game.news_feed.pop(0)
    news_text.set("\n".join(reversed(game.news_feed)))

def monthly_tick():
    if not game.running:
        return

    leadership_effect()

    profit = calculate_profit()
    game.money += profit

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
    game.market_share = max(0, game.market_share - 0.5)  # slight decay

    random_event()
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
    if game.market_share >= target:
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
    status.set("")
    news_text.set("")
    for b in buttons:
        b.config(state="normal")
    restart_btn.pack_forget()
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
        if game.upgrades[up]:
            btn.config(state="disabled", text=f"{up} (Owned)")
        else:
            btn.config(state="normal")

def update_dept_buttons():
    for dept, btn in dept_buttons.items():
        if game.departments[dept]:
            btn.config(state="disabled", text=f"{dept} (Hired)")
        else:
            btn.config(state="normal")

# ---------------- GAME WINDOW ----------------
game_window = tk.Tk()
game_window.configure(bg="#0F172A")
game_window.title("Business Empire Builder")
game_window.geometry("800x900")
game_window.withdraw()

status = tk.StringVar()
message = tk.StringVar()
news_text = tk.StringVar()

tk.Label(
    game_window,
    textvariable=status,
    font=("Arial", 12),
    justify="left",
    bg="#1E293B",
    fg="#F1F5F9"
).pack(pady=10, fill="x")

message_label = tk.Label(
    game_window,
    textvariable=message,
    font=("Comic Sans MS", 14),
    fg="#F1F5F9",
    bg="#334155",
    width=80,
    height=2,
    relief="solid",
    bd=2
)
message_label.pack(pady=8)

profit_label = tk.Label(
    game_window,
    text="Monthly Profit: $0",
    font=("Arial", 16, "bold"),
    bg="#0F172A",
    fg="#22C55E"
)
profit_label.pack(pady=5)

news_label = tk.Label(
    game_window,
    text="News Feed:",
    font=("Arial", 14, "bold"),
    bg="#0F172A",
    fg="#F59E0B"
)
news_label.pack(pady=5)

news_box = tk.Label(
    game_window,
    textvariable=news_text,
    font=("Arial", 10),
    justify="left",
    bg="#1E293B",
    fg="#F1F5F9",
    width=80,
    height=10,
    relief="solid",
    bd=2
)
news_box.pack(pady=5)

# Buttons
buttons = [
    tk.Button(game_window, text="Training ($5000)", command=training),
    tk.Button(game_window, text="Bonuses ($4000)", command=bonus),
    tk.Button(game_window, text="Recruit ($3000)", command=recruit),
    tk.Button(game_window, text="Marketing ($4000)", command=marketing_campaign),
    tk.Button(game_window, text="R&D ($6000)", command=r_and_d),
    tk.Button(game_window, text="Customer Service ($2000)", command=customer_service),
    tk.Button(game_window, text="Change Leadership", command=change_leadership),
    tk.Button(game_window, text="Special Ability", command=special_ability)
]

for b in buttons:
    b.pack(fill="x", pady=2)
    b.configure(bg="#334155", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)

# Upgrade buttons
upgrade_frame = tk.Frame(game_window, bg="#0F172A")
upgrade_frame.pack(pady=10)
tk.Label(upgrade_frame, text="Upgrades:", font=("Arial", 14, "bold"), bg="#0F172A", fg="#22C55E").pack()
upgrade_buttons = {}
for up in ["Better Office", "Automation", "Coffee Machine"]:
    btn = tk.Button(upgrade_frame, text=f"{up} (${['Better Office: 10000', 'Automation: 15000', 'Coffee Machine: 5000'][['Better Office', 'Automation', 'Coffee Machine'].index(up)]})", command=lambda u=up: buy_upgrade(u))
    btn.pack(fill="x", pady=1)
    btn.configure(bg="#475569", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)
    upgrade_buttons[up] = btn

# Department buttons
dept_frame = tk.Frame(game_window, bg="#0F172A")
dept_frame.pack(pady=10)
tk.Label(dept_frame, text="Departments:", font=("Arial", 14, "bold"), bg="#0F172A", fg="#22C55E").pack()
dept_buttons = {}
for dept in ["HR", "IT", "PR"]:
    btn = tk.Button(dept_frame, text=f"{dept} (${['HR: 8000', 'IT: 10000', 'PR: 7000'][['HR', 'IT', 'PR'].index(dept)]})", command=lambda d=dept: buy_department(d))
    btn.pack(fill="x", pady=1)
    btn.configure(bg="#475569", fg="#D3DDF9", activebackground="#1E293B", activeforeground="#22C55E", relief="flat", bd=0)
    dept_buttons[dept] = btn

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

    tk.Label(start_window, text="Business Empire Builder", font=("Arial", 24, "bold"), bg="#0F172A", fg="#1E3A8A").pack(pady=20)

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
            game.money = 30000
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
            "Welcome to Business Empire Builder!\n\n"
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