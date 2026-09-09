import turtle
import random
import sys

# Windows-only sound import handling
try:
    import winsound
    HAS_SOUND = True
except ImportError:
    HAS_SOUND = False

# ==========================================================
# 🇵🇭 AHAS NG BARANGAY: FUSION DYEEPSTIK EDITION
# Ultimate Filipino Snake Game with Jeepney Route & Traffic System
# ==========================================================

screen = turtle.Screen()
screen.title("🇵🇭 Ahas ng SFXC - Jeepney Odyssey Edition")
screen.bgcolor("#0B3D2E")
screen.setup(600, 600)
screen.tracer(0)

# ---------------- OBJECT MAKER ----------------
def make(shape, color):
    t = turtle.Turtle(shape)
    t.color(color)
    t.penup()
    t.speed(0)
    return t

# ---------------- GAME OBJECTS ----------------
head = make("square", "#00FF66")
head.shapesize(1.1)

# 🍎 FOOD / LOCAL DELICACIES
food = make("circle", "orange")
food.shapesize(0.8)

foods = [
    ("MANGO", "#FFA500"),
    ("PANDESAL", "#D2A679"),
    ("ADOBO", "#8B4513"),
    ("HALO-HALO", "#FF69B4"),
    ("ISDA", "#87CEEB"),
    ("BIBINGKA", "#FFD700")
]

# ⭐ SPECIAL GOLDEN SUMAN (Shield & Bonus)
suman_food = make("square", "#FFFF00")
suman_food.shapesize(0.6)
suman_food.hideturtle()
suman_active = False

# 🛺 PASAHERO (Passenger)
pasahero = make("turtle", "#00FFFF")
pasahero.shapesize(0.8)
pasahero.hideturtle()
pasahero_active = False

# 🏫 BARANGAY TERMINAL (Drop-off point)
terminal = make("square", "#FF4500")
terminal.shapesize(1.2)
terminal.hideturtle()
terminal_active = False

# 🚦 TRAFFIC LIGHT SYSTEM (Unique Obstacle Mechanic)
traffic_light = make("circle", "#00FF00")
traffic_light.shapesize(0.9)
traffic_light.goto(260, 245)
traffic_state = "GO" # GO, WARNING, RED
traffic_timer = 0

# 💣 BOMBS / OBSTACLES
bomb_colors = ["#FF3030", "#FF8C00", "#FFD700", "#FF00FF"]

backgrounds = [
    "#0B3D2E", "#123B5D", "#5C3317", "#4B1F4B",
    "#164A4A", "#333333", "#3B2415", "#082A13"
]

directions = {
    "up": (0, 20),
    "down": (0, -20),
    "left": (-20, 0),
    "right": (20, 0)
}

head.direction = "stop"
segments = []
bombs = []

score = 0
high_score = 0
delay = 100
food_name = ""
paused = False
game_running = True

# 🌟 ARCADE METRICS
combo_streak = 0
invincible_ticks = 0
has_pasahero = False

# ---------------- TEXT DISPLAY ----------------
title = make("square", "white")
title.hideturtle()
title.goto(0, 270)
title.write(
    "🇵🇭 AHAS NG SFXC: JEEPNEY ODYSSEY",
    align="center",
    font=("Arial", 18, "bold")
)

score_text = make("square", "white")
score_text.hideturtle()
score_text.goto(0, 245)

message = make("square", "#FFD700")
message.hideturtle()
message.goto(0, -285)

floating_text = make("square", "#00FFFF")
floating_text.hideturtle()
floating_alpha_timer = 0

def update_score():
    score_text.clear()
    shield_status = "🛡️" if invincible_ticks > 0 else ""
    ride_status = "🛺 PASAKAY" if has_pasahero else ""
    light_icon = "🟢" if traffic_state == "GO" else ("🟡" if traffic_state == "WARNING" else "🔴")
    score_text.write(
        f"Score: {score} | {light_icon} {shield_status}{ride_status} | High: {high_score}",
        align="center",
        font=("Courier", 10, "bold")
    )

def show_message(text):
    message.clear()
    message.write(
        text,
        align="center",
        font=("Arial", 11, "bold")
    )

def trigger_floating_text(text, x, y):
    global floating_alpha_timer
    floating_text.goto(x, y + 10)
    floating_text.clear()
    floating_text.write(text, align="center", font=("Arial", 10, "bold"))
    floating_alpha_timer = 15

# ---------------- SCREEN SHAKE EFFECT ----------------
def screen_shake():
    if not game_running:
        return
    for dx, dy in [(12, 6), (-12, -6), (6, -6), (-6, 6), (0, 0)]:
        screen.getcanvas().winfo_toplevel().geometry(f"+{100+dx}+{100+dy}")

# ---------------- RANDOM POSITION ----------------
def random_position():
    while True:
        x = random.randrange(-260, 261, 20)
        y = random.randrange(-210, 221, 20)

        if abs(x) < 40 and abs(y) < 40:
            continue

        if any(s.distance(x, y) < 20 for s in segments):
            continue

        if any(b.distance(x, y) < 20 for b in bombs):
            continue

        return x, y

# ---------------- FOOD & UNIQUE SPAWNS ----------------
def new_food():
    global food_name, suman_active, pasahero_active

    food_name, color = random.choice(foods)
    food.shape("circle")
    food.shapesize(0.8)
    food.color(color)
    food.goto(*random_position())

    # Random Golden Suman Spawn (15% chance)
    if not suman_active and random.random() < 0.15:
        suman_active = True
        suman_food.goto(*random_position())
        suman_food.showturtle()

    # Random Pasahero Spawn (12% chance)
    if not has_pasahero and not pasahero_active and random.random() < 0.12:
        pasahero_active = True
        pasahero.goto(*random_position())
        pasahero.showturtle()

# ---------------- BOMBS ----------------
def add_bomb():
    b = make("triangle", random.choice(bomb_colors))
    b.shapesize(1.0)
    b.goto(*random_position())
    bombs.append(b)

add_bomb()
new_food()

# ---------------- CONTROLS ----------------
def change_direction(new_direction):
    global game_running, traffic_state
    if not game_running:
        return

    # UNIQUE MECHANIC: If Traffic Light is Red and player moves, penalty/stall check!
    if traffic_state == "RED":
        trigger_floating_text("🛑 RED LIGHT! PAALALA SA TRAPIKO!", head.xcor(), head.ycor())

    opposite = {
        "up": "down",
        "down": "up",
        "left": "right",
        "right": "left"
    }

    if head.direction != opposite.get(new_direction):
        head.direction = new_direction

def bind_keys():
    screen.onkeypress(lambda: change_direction("up"), "w")
    screen.onkeypress(lambda: change_direction("up"), "Up")
    screen.onkeypress(lambda: change_direction("down"), "s")
    screen.onkeypress(lambda: change_direction("down"), "Down")
    screen.onkeypress(lambda: change_direction("left"), "a")
    screen.onkeypress(lambda: change_direction("left"), "Left")
    screen.onkeypress(lambda: change_direction("right"), "d")
    screen.onkeypress(lambda: change_direction("right"), "Right")

bind_keys()

# ---------------- PAUSE ----------------
def pause_game():
    global paused
    if not game_running:
        return
    paused = not paused
    if paused:
        show_message("⏸ PAUSED - Press P to continue")
    else:
        show_message(f"Kainin ang {food_name}!")

screen.onkeypress(pause_game, "p")
screen.onkeypress(pause_game, "P")

# ---------------- SOUND ----------------
def play_sound():
    if HAS_SOUND and sys.platform == "win32":
        try:
            winsound.PlaySound(
                "ahhh.wav",
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except Exception:
            pass

# ---------------- RESTART GAME ----------------
def reset_game():
    global score, delay, paused, game_running, combo_streak, invincible_ticks, suman_active, pasahero_active, terminal_active, has_pasahero, traffic_state, traffic_timer

    for segment in segments:
        segment.hideturtle()
        segment.goto(1000, 1000)
    segments.clear()

    for bomb in bombs:
        bomb.hideturtle()
        bomb.goto(1000, 1000)
    bombs.clear()

    suman_food.hideturtle()
    pasahero.hideturtle()
    terminal.hideturtle()

    suman_active = False
    pasahero_active = False
    terminal_active = False
    has_pasahero = False
    traffic_state = "GO"
    traffic_timer = 0
    traffic_light.color("#00FF00")

    head.goto(0, 0)
    head.direction = "stop"
    head.color("#00FF66")
    head.shapesize(1.1)

    score = 0
    combo_streak = 0
    invincible_ticks = 0
    delay = 100
    paused = False
    
    screen.bgcolor(backgrounds[0])
    add_bomb()
    new_food()
    update_score()

    game_running = True
    show_message("🔄 JEEPNEY ODYSSEY RESTARTED!")

screen.onkeypress(reset_game, "space")
screen.listen()

# ---------------- GAME OVER ----------------
def game_over(reason):
    global high_score, game_running

    if not game_running:
        return

    screen_shake()
    game_running = False
    high_score = max(high_score, score)

    show_message(f"GAME OVER! {reason} | Press SPACE to Restart")
    screen.update()

# ---------------- GAME LOOP ----------------
def game():
    global score, high_score, delay, combo_streak, invincible_ticks, floating_alpha_timer, suman_active, pasahero_active, terminal_active, has_pasahero, traffic_state, traffic_timer

    if game_running and not paused:
        # Dynamic Traffic Light Cycle Mechanic (Changes state every ~5 seconds)
        traffic_timer += 1
        if traffic_timer > 50:
            traffic_timer = 0
            if traffic_state == "GO":
                traffic_state = "WARNING"
                traffic_light.color("#FFA500")
            elif traffic_state == "WARNING":
                traffic_state = "RED"
                traffic_light.color("#FF0000")
            else:
                traffic_state = "GO"
                traffic_light.color("#00FF00")
            update_score()

        if invincible_ticks > 0:
            invincible_ticks -= 1
            head.color("#FFFF00" if invincible_ticks % 2 == 0 else "#00FF66")

        for i in range(len(segments) - 1, 0, -1):
            segments[i].goto(segments[i - 1].pos())

        if segments:
            segments[0].goto(head.pos())

        if head.direction != "stop":
            dx, dy = directions[head.direction]
            head.goto(
                head.xcor() + dx,
                head.ycor() + dy
            )

            # Unique Red Light Penalty Check (Moving during Red Light speeds up or drains combo)
            if traffic_state == "RED" and head.direction != "stop":
                if random.random() < 0.05: # 5% chance per tick to get caught by traffic enforcer
                    combo_streak = max(0, combo_streak - 1)
                    trigger_floating_text("👮 ENFORCER TICKET! -1 Combo!", head.xcor(), head.ycor())

        if floating_alpha_timer > 0:
            floating_alpha_timer -= 1
            if floating_alpha_timer == 0:
                floating_text.clear()

        # Wall Collision
        if abs(head.xcor()) > 280 or abs(head.ycor()) > 280:
            game_over("Nabangga sa pader ng kalsada!")

        # Self Collision
        elif any(segment.distance(head) < 18 for segment in segments):
            game_over("Nabangga sa sariling katawan!")

        # Bomb Collision
        elif any(bomb.distance(head) < 18 for bomb in bombs):
            play_sound()
            if invincible_ticks > 0:
                trigger_floating_text("🛡️ SHIELD BLOCKED!", head.xcor(), head.ycor())
            else:
                screen_shake()
                game_over("💣 Trapiko Na-aksidente!")

        # Golden Suman Collision
        elif suman_active and head.distance(suman_food) < 20:
            play_sound()
            score += 25
            combo_streak += 2
            invincible_ticks = 50
            suman_active = False
            suman_food.hideturtle()
            trigger_floating_text("✨ SPECIAL SUMAN! +25 & SHIELD!", head.xcor(), head.ycor())
            update_score()

        # Pasahero Collision (Pick up passenger)
        elif pasahero_active and head.distance(pasahero) < 20:
            play_sound()
            pasahero_active = False
            pasahero.hideturtle()
            has_pasahero = True
            
            terminal_active = True
            terminal.goto(*random_position())
            terminal.showturtle()
            trigger_floating_text("🛺 PASAHERO SAKAY! Hanapin ang Terminal!", head.xcor(), head.ycor())
            update_score()

        # Barangay Terminal Drop-off Collision
        elif terminal_active and head.distance(terminal) < 20:
            play_sound()
            terminal_active = False
            terminal.hideturtle()
            has_pasahero = False
            
            drop_bonus = 60
            score += drop_bonus
            high_score = max(high_score, score)
            trigger_floating_text(f"🏫 BARANGAY DROP-OFF! +{drop_bonus} Pts!", head.xcor(), head.ycor())
            update_score()

        # Regular Food Collision
        elif head.distance(food) < 20:
            play_sound()
            combo_streak += 1

            color = food.color()[0]
            if invincible_ticks == 0:
                head.color(color)
            
            head.shapesize(min(1.8, 1.1 + (len(segments) * 0.01)))

            new_segment = make("square", color)
            segments.append(new_segment)

            earned = 10 + (combo_streak * 2)
            score += earned
            high_score = max(high_score, score)

            delay = max(35, 100 - score // 10 * 3)

            trigger_floating_text(f"+{earned} ({combo_streak}x Streak!)", head.xcor(), head.ycor())
            new_food()

            for bomb in bombs:
                bomb.goto(*random_position())
                bomb.color(random.choice(bomb_colors))

            if score % 30 == 0:
                add_bomb()
                screen.bgcolor(
                    backgrounds[(score // 30) % len(backgrounds)]
                )
                show_message(f"⚠️ ROTA UPDATE! Bagong sagabal sa kalsada: {score}")

            update_score()

    screen.update()
    screen.ontimer(game, delay)

# ---------------- INSTRUCTIONS ----------------
update_score()
show_message("WASD / Arrow Keys = Galaw | P = Pause | Igalaw ang Jeep nang Ayos sa Trapiko!")

game()
screen.mainloop()