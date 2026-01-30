
#  Management Simulator by Jeffrey(AND ONLY ME)
# thx danila for help with logic and ideas



import tkinter as tk
import tkinter.messagebox as messagebox
import random

# ---------------- GAME STATE ----------------
class Game:
    def __init__(self):
        self.quarter = 1
        self.employees = 10
        self.morale = 50
        self.productivity = 50
        self.marketing = 50
        self.leader_style = "democratic"
        self.competitor_money = 12000
        self.money = 12000
        self.company = ""
        self.difficulty = "Normal"
        self.running = False

game = Game()

# ---------------- GAME FUNCTIONS ----------------
def update_status():
    target = win_target()
    status.set(
        f"Company: {game.company}\nMoney: ${game.money:,} / ${target:,}\n"
        f"Employees: {game.employees}\nMorale: {game.morale}\nProductivity: {game.productivity}\n"
        f"Marketing: {game.marketing}\nLeadership: {game.leader_style.capitalize()}\n"
        f"Difficulty: {game.difficulty}"
    )
    money_per_sec_label.config(text=f"Money/sec: ${money_per_second():,}")

def leadership_effect():
    if game.leader_style == "autocratic":
        game.productivity += 5
        game.morale -= 5
    elif game.leader_style == "democratic":
        game.morale += 5
    elif game.leader_style == "laissez-faire":
        game.morale += 3
        game.productivity -= 2

def calculate_profit():
    return (game.employees * game.productivity) + (game.marketing * 2)

def win_target():
    return {"Easy": 10_000_000, "Normal": 50_000_000, "Hard": 100_000_000}[game.difficulty]

def money_per_second():
    base = (game.employees * game.productivity * 0.5) + (game.marketing * 2)
    morale_factor = game.morale / 50
    difficulty_factor = {"Easy":1.2, "Normal":1, "Hard":0.8}[game.difficulty]
    return int(base * morale_factor * difficulty_factor)

def random_event():
    event = random.choice(["none","strike","lawsuit","big_order"])
    difficulty_factor = {"Easy": 0.5, "Normal": 1, "Hard": 1.5}[game.difficulty]

    if event == "strike" and game.morale < 40:
        game.productivity -= int(10 * difficulty_factor)
        message.set(f"Strike! Productivity fell by {int(10 * difficulty_factor)}.")
        return None
    elif event == "lawsuit":
        game.lawsuit_loss = int(3000 * difficulty_factor)
        message.set(f"Lawsuit! lost ${game.lawsuit_loss}.")
        return "lawsuit"
    elif event == "big_order":
        gain = int(3000 * difficulty_factor)
        game.money += gain
        message.set(f"Big order! Earned ${gain}.")
        return None
    else:
        message.set("Quarter completed.")
        return None
    
def money_tick():
    if not game.running:
        return

    leadership_effect()

    profit = money_per_second() * 3  # since tick is every 3 seconds
    game.money += profit

    # Slow morale decay
    morale_loss = 10  # you can adjust this number for faster/slower loss
    game.morale = game.morale - morale_loss if game.morale > 0 else 0

    if game.morale < 20 and game.employees > 0:
        game.employees -= 1
        message.set(message.get() + " Low morale! An employee quit.")

    if game.productivity > 80:
        game.morale -= 2

    random_event()
    update_status()
    check_game_end()

    game_window.after(2000, money_tick)

def next_quarter():
    leadership_effect()

    event_result = random_event()
    profit = calculate_profit()



    game.morale -= int(5 * {"Easy": 0.7, "Normal":1, "Hard":1.3}[game.difficulty])

    difficulty_factor = {"Easy": 0.8, "Normal":1, "Hard":1.3}[game.difficulty]
    if game.company == "Factory":
        competitor_growth = int(random.randint(400, 800) * difficulty_factor)
    elif game.company == "Hospital":
        competitor_growth = int(random.randint(300, 700) * difficulty_factor)
    else:
        competitor_growth = int(random.randint(350, 750) * difficulty_factor)
    game.competitor_money += competitor_growth



    game.quarter += 1
    check_game_end()
    update_status()

def check_game_end():
    target = win_target()
    if game.money >= target:
        message.set(f"YOU WIN! ${target:,} reached!")
        end_game()
    elif game.money <= 0:
        message.set("Bankrupt! Game Over.")
        end_game()
    elif game.employees <= 0:
        message.set("All workers left! Game Over.")
        end_game()

def end_game():
    game.running = False
    disable_buttons()
    restart_btn.pack(pady=10)

def restart_game():
    global start_window

    game.quarter = 1
    game.employees = 10
    game.morale = 50
    game.productivity = 50
    game.marketing = 50
    game.money = 12000
    game.competitor_money = 12000
    game.company = ""
    game.leader_style = "democratic"
    game.difficulty = "Normal"

    message.set("")
    status.set("")

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
    if game.money >= 4000:
        game.money -= 4000
        game.productivity += 20
        message.set("Training completed! Productivity +20")
    else:
        message.set("Not enough money for training!")

def bonus():
    if game.money >= 3000:
        game.money -= 3000
        game.morale += 30
        message.set("Bonuses paid! Morale +30")
    else:
        message.set("Not enough money for bonuses!")

def recruit():
    if game.money >= 2000:
        game.money -= 2000
        game.employees += 1
        message.set("New employee hired! +1 worker")
    else:
        message.set("Not enough money to recruit!")

def communication():
    if game.money >= 2000:
        game.money -= 2000
        game.morale += 10
        game.productivity += 10
        message.set("Team meeting held! Morale +10, Productivity +10")
    else:
        message.set("Not enough money for team meeting!")

def marketing_spend():
    if game.money >= 3000:
        game.money -= 3000
        game.marketing += 20
        message.set("Marketing campaign launched! +20 marketing")
    else:
        message.set("Not enough money for marketing!")

def change_leader():
    styles = ["autocratic", "democratic", "laissez-faire"]
    current = styles.index(game.leader_style)
    game.leader_style = styles[(current + 1) % 3]
    message.set(f"Leadership changed to {game.leader_style.capitalize()}!")
    update_status()


# ---------------- GAME WINDOW ----------------
game_window = tk.Tk()
game_window.configure(bg="#0F172A")
game_window.title("HR Management Simulator")
game_window.geometry("500x650")
game_window.withdraw()

status = tk.StringVar()
message = tk.StringVar()

tk.Label(
    game_window,
    textvariable=status,
    font=("Arial", 16),
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
    width=60,
    height=3,
    relief="solid",
    bd=2
)
message_label.pack(pady=8)

money_per_sec_label = tk.Label(
    game_window,
    text="Money/sec: $0",
    font=("Arial", 20, "bold"),
    bg="#0F172A",
    fg="#22C55E"
)

money_per_sec_label.pack(pady=10, side="bottom")

buttons = [
    tk.Button(game_window, text="Training (+20 productivity)(4000)", font=("Arial", 14), command=training),
    tk.Button(game_window, text="Bonuses (+30 morale)(3000)", font=("Arial", 14), command=bonus),
    tk.Button(game_window, text="Recruit (+1 employee)(2000)", font=("Arial", 14), command=recruit),
    tk.Button(game_window, text="Communication (+10 morale +10 productivity)(2000)", font=("Arial", 14), command=communication),
    tk.Button(game_window, text="Marketing (+20 marketing)(3000)", font=("Arial", 14), command=marketing_spend),
    tk.Button(game_window, text="Change Leadership", font=("Arial", 14), command=change_leader)
]

for b in buttons:
    b.pack(fill="x", pady=4)

for b in buttons:
    b.configure(
        bg="#334155",
        fg="#D3DDF9",         # <-- navy text
        activebackground="#1E293B",
        activeforeground="#22C55E",
        relief="flat",
        bd=0
    )


# Restart button (hidden until game over)
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

    main_frame = tk.Frame(start_window, bg="#0F172A")
    main_frame.pack(fill="both", expand=True)

    start_window.configure(bg="#0F172A")
    start_window.title("Start Game :)")
    start_window.geometry("500x900")
    start_window.resizable(True, True)


    # --- Pulsing Title ---
    title_label = tk.Label(
        main_frame,
        text="HR MANAGEMENT SIMULATOR",
        font=("Arial", 28, "bold"),
        fg="#1E3A8A",  # navy
        bg="#0F172A"
    )
    title_label.pack(pady=20)

    pulse_state = {"size":28, "direction":1}
    def pulse_title():
        if pulse_state["size"] >= 36:
            pulse_state["direction"] = -1
        elif pulse_state["size"] <= 28:
            pulse_state["direction"] = 1
        pulse_state["size"] += pulse_state["direction"]
        title_label.config(font=("Arial", pulse_state["size"], "bold"))
        main_frame.after(80, pulse_title)
    pulse_title()
    # --- End Pulsing Title ---

    # --- Variables ---
    company_var = tk.StringVar(value="")
    leadership_var = tk.StringVar(value="democratic")
    difficulty_var = tk.StringVar(value="Normal")

    # --- Labels ---
    company_label = tk.Label(main_frame, text="Selected Company: None", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    company_label.pack(pady=5)
    leader_label = tk.Label(main_frame, text="Selected Leadership: Democratic", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    leader_label.pack(pady=5)
    diff_label = tk.Label(main_frame, text="Selected Difficulty: Normal", font=("Arial", 14), bg="#1E293B", fg="#1E3A8A")
    diff_label.pack(pady=5)

    # --- Buttons & Options ---
    # Company
    tk.Label(main_frame, text="Choose Your Company", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=10)
    def set_company(c):
        company_var.set(c)
        company_label.config(text=f"Selected Company: {c}", fg="green")
    tk.Button(main_frame, text="Factory", font=("Arial",16), command=lambda: set_company("Factory")).pack(pady=5)
    tk.Button(main_frame, text="Hospital", font=("Arial",16), command=lambda: set_company("Hospital")).pack(pady=5)
    tk.Button(main_frame, text="Game Studio", font=("Arial",16), command=lambda: set_company("Game Studio")).pack(pady=5)

    # Leadership
    tk.Label(main_frame, text="Choose Leadership Style", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=15)
    def set_leadership(l):
        leadership_var.set(l)
        leader_label.config(text=f"Selected Leadership: {l.capitalize()}", fg="green")
    tk.Button(main_frame, text="Autocratic", font=("Arial",16), command=lambda: set_leadership("autocratic")).pack(pady=3)
    tk.Button(main_frame, text="Democratic", font=("Arial",16), command=lambda: set_leadership("democratic")).pack(pady=3)
    tk.Button(main_frame, text="Laissez-faire", font=("Arial",16), command=lambda: set_leadership("laissez-faire")).pack(pady=3)

    # Difficulty
    tk.Label(main_frame, text="Choose Difficulty", font=("Arial", 20, "bold"), bg="#0F172A", fg="#22C55E").pack(pady=15)
    def set_difficulty(d):
        difficulty_var.set(d)
        diff_label.config(text=f"Selected Difficulty: {d}", fg="green")
    tk.Button(main_frame, text="Easy", font=("Arial",16), command=lambda: set_difficulty("Easy")).pack(pady=3)
    tk.Button(main_frame, text="Normal", font=("Arial",16), command=lambda: set_difficulty("Normal")).pack(pady=3)
    tk.Button(main_frame, text="Hard :)", font=("Arial",16), command=lambda: set_difficulty("Hard")).pack(pady=3)
    # --- Start Game Function ---
    def start_game():
        if company_var.get() == "":
            company_label.config(text="Please select a company!", fg="red")
            return

        game.company = company_var.get()
        game.leader_style = leadership_var.get()
        game.difficulty = difficulty_var.get()

        # Set starting stats based on difficulty
        if game.difficulty == "Easy":
            game.money = 15000
            game.competitor_money = 10000
            game.morale = 60
            game.productivity = 60
        elif game.difficulty == "Hard":
            game.money = 8000
            game.competitor_money = 14000
            game.morale = 45
            game.productivity = 45
        else:
            game.money = 12000
            game.competitor_money = 12000
            game.morale = 50
            game.productivity = 50

        # Company adjustments
        if game.company == "Factory":
            game.productivity += 10
            game.morale -= 10
        elif game.company == "Hospital":
            game.morale += 10
        elif game.company == "Game Studio":
            game.morale += 5
            game.productivity -= 5

        game.quarter = 1
        game.employees = 10
        game.marketing = 50

        # --- Show rules popup ---
        rules_text = (
            "Welcome to HR Management Simulator!\n\n"
            "Made by Jeffrey, Ideas from Danila.\n\n"
            "Rules:\n"
            "- Manage your employees, morale, productivity, and marketing.\n"
            "- Make money to reach your win target based on difficulty.\n"
            "- You lose morale over time, keep it up with actions!\n"
            "- Higher morale keeps employees from quitting.\n"
            "- Watch out for strikes, lawsuits, and random events!\n"
            "- Game ends if money gets to zero 0 or all employees quit.\n"
            "- Use buttons wisely to train, give bonuses, recruit, communicate, and market.\n\n"
            "Good luck!"
        )
        messagebox.showinfo("Game Rules", rules_text)

        start_window.destroy()
        game_window.deiconify()
        update_status()
        game.running = True
        money_tick()

    # --- Start Button ---
    start_btn = tk.Button(start_window, text="Start Game", font=("Arial",18,"bold"), command=start_game)
    start_btn.pack(pady=20)
    start_btn.config(bg="#22C55E", fg="#0F172A", activebackground="#16A34A")

    start_window.mainloop()


   

# ---------------- START ----------------
create_start_screen()
