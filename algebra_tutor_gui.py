from owlready2 import get_ontology
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import time

# ---------------- GLOBAL STATE ----------------
student_name = ""
equations = []
progress = {}
current_index = None
current_step = 0
constant = coefficient = solution = 0
hint_step1 = hint_step2 = hint_solution = ""
attempts = 0
step_attempts = 0
start_time = None

# ---------------- LOAD ONTOLOGY ----------------
onto = get_ontology(
    "/Users/thamasha/Downloads/AI/Algebra/algebra_tutor2.owl").load()

# Extract individuals of class Equation
equations = [eq for eq in onto.individuals() if onto.Equation in eq.is_a]
if not equations:
    messagebox.showerror("Error", "No equations found in ontology!")
    exit()

# Initialize progress dictionary
for i in range(len(equations)):
    progress[f"Equation{i+1}"] = {"attempts": 0, "time": 0,
                                  "status": "unlocked" if i == 0 else "locked"}

# ---------------- MAIN WINDOW ----------------
root = tk.Tk()
root.title("Algebra Tutor")
root.geometry("600x500")

# Frames
login_frame = tk.Frame(root)
dashboard_frame = tk.Frame(root)
equation_frame = tk.Frame(root)

for frame in (login_frame, dashboard_frame, equation_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# ---------------- LOGIN PAGE ----------------
tk.Label(login_frame, text="Enter your name:",
         font=("Arial", 14)).pack(pady=20)
name_entry = tk.Entry(login_frame, font=("Arial", 14), width=25)
name_entry.pack(pady=10)


def start_session():
    global student_name
    student_name = name_entry.get().strip()
    if not student_name:
        messagebox.showerror("Error", "Please enter your name.")
        return
    update_dashboard_buttons()
    show_frame(dashboard_frame)


start_button = tk.Button(login_frame, text="Start",
                         font=("Arial", 14), command=start_session)
start_button.pack(pady=20)

# ---------------- DASHBOARD PAGE ----------------
tk.Label(dashboard_frame, text="Select an Equation",
         font=("Arial", 16)).pack(pady=20)

button_frame = tk.Frame(dashboard_frame)
button_frame.pack(pady=20)

equation_buttons = []


def open_equation(index):
    global current_index
    current_index = index
    load_equation(index)
    show_frame(equation_frame)


for i in range(len(equations)):
    btn = tk.Button(button_frame, text=f"Equation {i+1}", font=("Arial", 14),
                    command=lambda i=i: open_equation(i))
    row, col = divmod(i, 3)
    btn.grid(row=row, column=col, padx=20, pady=20)
    equation_buttons.append(btn)


def update_dashboard_buttons():
    for i, btn in enumerate(equation_buttons):
        status = progress[f"Equation{i+1}"]["status"]
        btn.config(state="normal" if status != "locked" else "disabled")

# ---------------- PROGRESS CHART ----------------


def show_progress_chart():
    eq_names = [f"Eq{i+1}" for i in range(len(progress))]
    attempts_list = [progress[f"Equation{i+1}"]
                     ["attempts"] for i in range(len(progress))]
    times_list = [progress[f"Equation{i+1}"]["time"]
                  for i in range(len(progress))]

    plt.figure(figsize=(8, 5))

    # Attempts per equation
    plt.subplot(2, 1, 1)
    plt.bar(eq_names, attempts_list, color='skyblue')
    plt.title("Attempts per Equation (Completed)")
    plt.ylabel("Attempts")

    # Time per equation
    plt.subplot(2, 1, 2)
    plt.bar(eq_names, times_list, color='lightgreen')
    plt.title("Time per Equation (seconds)")
    plt.ylabel("Time")
    plt.tight_layout()
    plt.show()


progress_button = tk.Button(dashboard_frame, text="View Progress", font=(
    "Arial", 14), command=show_progress_chart)
progress_button.pack(pady=20)

# ---------------- EQUATION PAGE ----------------
equation_label = tk.Label(equation_frame, text="", font=("Arial", 16))
equation_label.pack(pady=10)

instruction_label = tk.Label(equation_frame, text="", font=("Arial", 14))
instruction_label.pack(pady=10)

progress_label = tk.Label(equation_frame, text="",
                          font=("Arial", 14), fg="#87CEFA")
progress_label.pack(pady=10)

entry = tk.Entry(equation_frame, font=("Arial", 14), width=20)
entry.pack(pady=10)


def show_frame(frame):
    frame.tkraise()

# ---------------- LOAD EQUATION ---------------


def load_equation(index):
    global current_step, constant, coefficient, solution, hint_step1, hint_step2, hint_solution
    global attempts, step_attempts, start_time

    current_step = 0
    attempts = 0
    step_attempts = 0
    eq = equations[index]

    # Extract numeric details
    constant = int(eq.hasConstant[0]) if hasattr(
        eq, "hasConstant") and eq.hasConstant else 0
    coefficient = int(eq.hasCoefficient[0]) if hasattr(
        eq, "hasCoefficient") and eq.hasCoefficient else 0
    solution = float(eq.hasSolution[0]) if hasattr(
        eq, "hasSolution") and eq.hasSolution else 0

    # Hardcoded hints
    hint_step1 = "The constant is the number added or subtracted from x in the equation."
    hint_step2 = "The coefficient is the number multiplied by x."
    hint_solution = "Divide both sides by the coefficient to isolate x."

    # Start timer
    start_time = time.time()

    equation_label.config(
        text=f"Equation: {eq.hasExpression[0] if hasattr(eq, 'hasExpression') and eq.hasExpression else 'Unknown'}")
    instruction_label.config(text="Step 1: What is the constant term?")
    progress_label.config(text="")
    entry.delete(0, tk.END)

# ---------------- CHECK ANSWER ----------------


def check_answer():
    global current_step, step_attempts
    user_input = entry.get().strip()
    step_attempts += 1

    try:
        user_value = int(user_input)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer.")
        return

    if step_attempts >= 3:
        messagebox.showinfo(
            "Extra Help", f"Here's a tip: {get_adaptive_hint()}")
        step_attempts = 0

    if current_step == 0:
        if user_value == constant:
            current_step += 1
            step_attempts = 0
            instruction_label.config(text="Step 2: What do you divide by?")
            progress_label.config(
                text=f"After subtracting constant: {coefficient}x = {solution * coefficient}")
            entry.delete(0, tk.END)
        else:
            messagebox.showerror("Incorrect", "Try again!")

    elif current_step == 1:
        if user_value == coefficient:
            current_step += 1
            step_attempts = 0
            instruction_label.config(text="Step 3: What is the value of x?")
            progress_label.config(
                text=f"After subtracting constant: {coefficient}x = {solution * coefficient}")
            entry.delete(0, tk.END)
        else:
            messagebox.showerror("Incorrect", "Try again!")

    elif current_step == 2:
        if user_value == solution:
            messagebox.showinfo("Excellent!", "Great job!")
            progress_label.config(text=f"Final solution: x = {solution}")
            time_taken = round(time.time() - start_time, 2)

            # ✅ Count ONE attempt per completed equation
            progress[f"Equation{current_index+1}"]["attempts"] += 1
            progress[f"Equation{current_index+1}"]["time"] = time_taken
            progress[f"Equation{current_index+1}"]["status"] = "completed"

            # Unlock next equation if available
            if current_index + 2 <= len(equations):
                progress[f"Equation{current_index+2}"]["status"] = "unlocked"

            update_dashboard_buttons()
            show_frame(dashboard_frame)
        else:
            messagebox.showerror("Incorrect", "Try again!")

# ---------------- HINT FUNCTIONS ----------------


def get_adaptive_hint():
    if current_step == 0:
        return f"Look at the number added or subtracted from x. Hint: {hint_step1}"
    elif current_step == 1:
        return f"Focus on the multiplier of x. Hint: {hint_step2}"
    elif current_step == 2:
        return f"Think about isolating x. Hint: {hint_solution}"


def show_hint():
    if current_step == 0:
        messagebox.showinfo("Hint", hint_step1)
    elif current_step == 1:
        messagebox.showinfo("Hint", hint_step2)
    elif current_step == 2:
        messagebox.showinfo("Hint", hint_solution)

# ---------------- GRAPH ----------------


def show_graph():
    x = np.linspace(-10, 10, 100)
    y = coefficient * x + constant
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, label=f"{equations[current_index].hasExpression[0]}")
    plt.scatter(solution, 0, color='red', label=f"Solution: x={solution}")
    plt.axhline(0, color='black', linewidth=1)
    plt.axvline(0, color='black', linewidth=1)
    plt.title("Graph of the Equation")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.grid(True)
    plt.show()


# Buttons on equation page
tk.Button(equation_frame, text="Submit", font=(
    "Arial", 14), command=check_answer).pack(pady=10)
tk.Button(equation_frame, text="Hint", font=(
    "Arial", 14), command=show_hint).pack(pady=10)
tk.Button(equation_frame, text="Show Graph", font=(
    "Arial", 14), command=show_graph).pack(pady=10)
tk.Button(equation_frame, text="Back to Dashboard", font=("Arial", 14),
          command=lambda: show_frame(dashboard_frame)).pack(pady=10)

# Start with login frame
show_frame(login_frame)
root.mainloop()
