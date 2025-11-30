import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import random 

class ForceQuestQuiz:
    def __init__(self, master):
        self.master = master
        self.score = 0
        self.current_question = 0
        self.question_pool = QUIZ_QUESTIONS.copy()
        
        # Shuffle questions for randomization
        random.shuffle(self.question_pool) 
        
        # Create the new window (Toplevel)
        self.quiz_window = tk.Toplevel(master)
        self.quiz_window.title("💡 ForceQuest Quiz Time!")
        self.quiz_window.geometry("800x600")
        self.quiz_window.configure(bg="#1e1e2f")
        self.quiz_window.grab_set() # Forces user to interact with the quiz window
        
        self.style = ttk.Style()
        self.style.configure("Quiz.TButton", font=("Segoe UI", 12, "bold"), padding=10, 
                             background="#3e82e5", foreground="black")

        self.setup_quiz_ui()
        self.load_question()

    def setup_quiz_ui(self):
        # --- Header ---
        header_frame = tk.Frame(self.quiz_window, bg="#1e1e2f", pady=10)
        header_frame.pack(fill='x')
        
        tk.Label(header_frame, text="FORCEQUEST QUIZ", font=("Consolas", 20, "bold"), 
                 bg="#1e1e2f", fg="#00e6e6").pack()
        
        self.score_label = tk.Label(header_frame, text="Score: 0", font=("Segoe UI", 12, "bold"), 
                                     bg="#1e1e2f", fg="#98c379")
        self.score_label.pack()

        # --- Question Area ---
        question_frame = tk.Frame(self.quiz_window, bg="#252540", pady=30, padx=20)
        question_frame.pack(pady=20, padx=20, fill='both', expand=True)

        self.question_label = tk.Label(question_frame, text="Question text goes here...", 
                                        font=("Segoe UI", 16), bg="#252540", fg="white", 
                                        wraplength=700)
        self.question_label.pack(pady=10)

        # --- Choices Area ---
        self.choice_frame = tk.Frame(question_frame, bg="#252540")
        self.choice_frame.pack(pady=20)
        
        self.selected_choice = tk.StringVar()
        self.choice_buttons = []

        # Create 4 choice buttons
        for i in range(4):
            btn = ttk.Button(self.choice_frame, text=f"Choice {i+1}", style="Quiz.TButton",
                             command=lambda i=i: self.check_answer(self.choice_buttons[i].cget("text")))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, ipadx=50, ipady=10, sticky="ew")
            self.choice_buttons.append(btn)
            
        # Ensure grid columns can expand
        self.choice_frame.grid_columnconfigure(0, weight=1)
        self.choice_frame.grid_columnconfigure(1, weight=1)

    def load_question(self):
        if self.current_question >= len(self.question_pool):
            self.show_results()
            return

        q_data = self.question_pool[self.current_question]
        self.question_label.config(text=f"Q{self.current_question + 1}: {q_data['q']}")
        
        choices = q_data['choices']
        random.shuffle(choices) # Shuffle choices for each question
        
        for i, choice in enumerate(choices):
            self.choice_buttons[i].config(text=choice, state='normal')

    def check_answer(self, user_answer):
        q_data = self.question_pool[self.current_question]
        correct_answer = q_data['ans']
        
        is_correct = (user_answer == correct_answer)

        # Configure styles for immediate feedback (must be done here)
        self.style.configure("Correct.TButton", background="#98c379", foreground="black")
        self.style.configure("Incorrect.TButton", background="#ff6b6b", foreground="white")

        # Visually indicate correct/incorrect answer
        for btn in self.choice_buttons:
            if btn.cget("text") == correct_answer:
                btn.config(style="Correct.TButton")
            else:
                btn.config(style="Incorrect.TButton")
            btn.config(state='disabled') # Disable buttons after selection

        # Scoring Logic
        if is_correct:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score} - Correct!")
        else:
            self.score_label.config(text=f"Score: {self.score} - Incorrect.")

        # Move to next question after a brief delay
        self.quiz_window.after(1000, self.next_question)

    def next_question(self):
        # Reset button styles to default quiz style
        for btn in self.choice_buttons:
            btn.config(style="Quiz.TButton")

        self.current_question += 1
        self.load_question()

    def show_results(self):
        total = len(self.question_pool)
        messagebox.showinfo(
            "Quiz Complete! 🎉", 
            f"You finished the quiz!\n\nFinal Score: {self.score} out of {total}.", 
            parent=self.quiz_window
        )
        self.quiz_window.destroy()

# --- Question Data ---
QUIZ_QUESTIONS = [
    {
        "q": "What is the unit of Work?",
        "ans": "Joule (J)",
        "choices": ["Watt (W)", "Newton (N)", "Joule (J)", "Pascal (Pa)"]
    },
    {
        "q": "Which theorem relates Net Work done to the change in Kinetic Energy?",
        "ans": "Work-Energy Theorem",
        "choices": ["Newton's Second Law", "Work-Energy Theorem", "Conservation of Momentum", "Ohm's Law"]
    },
    {
        "q": "If you push an object horizontally over a distance (d) with a constant force (F), what is the Work done?",
        "ans": "W = F × d",
        "choices": ["W = F + d", "W = F / d", "W = F × d", "W = F × d × cos(θ)"]
    },
    {
        "q": "What is the formula for Kinetic Energy?",
        "ans": "$KE = 1/2 mv^2$",
        "choices": ["$PE = mgh$", "$KE = mv$", "$KE = 1/2 mv^2$", "$P = W/t$"]
    },
    {
        "q": "If you double the velocity of an object, its Kinetic Energy increases by a factor of:",
        "ans": "Four",
        "choices": ["Two", "Four", "Eight", "Half"]
    },
]


class ForceQuestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ ForceQuest — Physics Adventure Mode")
        self.root.geometry("1400x1000")
        self.root.configure(bg="#1e1e2f")
        self.is_animating = False
        self.animation_thread = None
        self.sim_data = {'distance': [], 'work': [], 'ke': []}
        
        # Timer attributes
        self.is_timer_running = False
        self.sim_start_time = 0.0
        self.timer_id = None
        
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="FORCEQUEST", fg="#00e6e6",
                         bg="#1e1e2f", font=("Consolas", 28, "bold"))
        title.pack(pady=10)

        subtitle = tk.Label(self.root, text="The Fun Physics Simulator — Work, Energy & Power",
                            fg="#bbb", bg="#1e1e2f", font=("Segoe UI", 12, "italic"))
        subtitle.pack()

        main_frame = tk.Frame(self.root, bg="#1e1e2f")
        main_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Left Panel
        left = tk.Frame(main_frame, bg="#252540", bd=2, relief="ridge")
        left.grid(row=0, column=0, padx=15, sticky="nsew")

        tk.Label(left, text="Scenario:", bg="#252540", fg="white", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self.scenario = ttk.Combobox(left, values=["Pushing Object", "Lifting Object", "Inclined Plane"], 
                                     state="readonly", width=18)
        self.scenario.grid(row=0, column=1, pady=5, padx=5)
        self.scenario.current(0)

        inputs = [("Force (N)", "force"), ("Distance (m)", "distance"),
                  ("Mass (kg)", "mass"), ("Angle (°)", "angle"), ("Friction μ", "mu")]
        self.entries = {}
        for i, (label, key) in enumerate(inputs, start=1):
            tk.Label(left, text=label, bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
                row=i, column=0, sticky="w", pady=5, padx=5)
            e = tk.Entry(left, width=15, font=("Segoe UI", 10))
            e.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key] = e

        row_base = len(inputs) + 1

        tk.Label(left, text="Surface Material:", bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
            row=row_base, column=0, sticky="w", pady=5, padx=5)
        self.surface_material = ttk.Combobox(left, width=18,
            values=["Ice", "Tile", "Wood", "Concrete", "Sand"], state="readonly")
        self.surface_material.grid(row=row_base, column=1, pady=5, padx=5)
        self.surface_material.current(2)

        tk.Label(left, text="Object Shape:", bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
            row=row_base + 1, column=0, sticky="w", pady=5, padx=5)
        self.object_shape = ttk.Combobox(left, width=18, values=["Box", "Cylinder", "Sphere"], state="readonly")
        self.object_shape.grid(row=row_base + 1, column=1, pady=5, padx=5)
        self.object_shape.current(0)

        tk.Label(left, text="Force Angle:", bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
            row=row_base + 2, column=0, sticky="w", pady=5, padx=5)
        self.force_angle_mode = ttk.Combobox(left, width=18, values=["Horizontal", "Upward", "Downward"], 
                                             state="readonly")
        self.force_angle_mode.grid(row=row_base + 2, column=1, pady=5, padx=5)
        self.force_angle_mode.current(0)

        tk.Label(left, text="Push Mode:", bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
            row=row_base + 3, column=0, sticky="w", pady=5, padx=5)
        self.push_mode = ttk.Combobox(left, width=18, 
            values=["Constant Force", "Sudden Push", "Increasing Force"], state="readonly")
        self.push_mode.grid(row=row_base + 3, column=1, pady=5, padx=5)
        self.push_mode.current(0)

        tk.Label(left, text="Animation Speed:", bg="#252540", fg="white", font=("Segoe UI", 10)).grid(
            row=row_base + 4, column=0, sticky="w", pady=5, padx=5)
        self.anim_speed = ttk.Scale(left, from_=0.5, to=3.0, orient="horizontal")
        self.anim_speed.set(1.0)
        self.anim_speed.grid(row=row_base + 4, column=1, pady=5, padx=5, sticky="ew")

        btn_frame = tk.Frame(left, bg="#252540")
        btn_frame.grid(row=row_base + 5, column=0, columnspan=2, pady=10)
    
        self.run_btn = tk.Button(btn_frame, text="▶ Run Simulation", bg="#00e6e6", fg="black", 
                                 font=("Segoe UI", 10, "bold"), command=self.run_simulation, width=20)
        self.run_btn.pack(pady=5)
        
        tk.Button(btn_frame, text="⏹ Stop", bg="#ff6b6b", fg="white",
                  font=("Segoe UI", 10, "bold"), command=self.stop_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="📊 Show Energy Graph", bg="#98c379", fg="black",
                  font=("Segoe UI", 10, "bold"), command=self.show_plot, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="🔄 Reset", bg="#61afef", fg="black",
                  font=("Segoe UI", 10, "bold"), command=self.reset_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="✅ Start Physics Quiz", bg="#ffaa00", fg="black",
                  font=("Segoe UI", 10, "bold"), command=self.start_quiz, width=20, height = 5).pack(pady=5)
        
        # Center Canvas
        center = tk.Frame(main_frame, bg="#1e1e2f")
        center.grid(row=0, column=1, padx=20, sticky="nsew")

        # --- UPDATED: Single Timer Label (Top Right) ---
        timer_frame = tk.Frame(center, bg="#1e1e2f")
        timer_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        tk.Label(timer_frame, text="Sim Time:", bg="#1e1e2f", fg="#61afef", font=("Consolas", 11, "bold")).pack(side=tk.LEFT)
        self.timer_label = tk.Label(timer_frame, text="00:00.00", bg="#1e1e2f", fg="#ffaa00", font=("Consolas", 11, "bold"))
        self.timer_label.pack(side=tk.LEFT, padx=(5, 0)) 
        # --------------------------------------------------

        self.canvas = tk.Canvas(center, width=700, height=450, bg="white", highlightthickness=2,
                               highlightbackground="#00e6e6")
        self.canvas.pack()

        self.feedback = tk.Label(center, text="⚡ Ready to simulate!", bg="#1e1e2f", fg="#aaffaa", 
                                 font=("Consolas", 12, "bold"))
        self.feedback.pack(pady=5)

        self.delta_ke_label = tk.Label(center, text="", bg="#1e1e2f", fg="#ffaa00", 
                                        font=("Consolas", 11, "bold"))
        self.delta_ke_label.pack(pady=5)

        solution_frame = tk.Frame(center, bg="#1e1e2f")
        solution_frame.pack(pady=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(solution_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.solution_box = tk.Text(solution_frame, width=85, height=20, bg="#111", fg="#98c379",
                                     font=("Consolas", 10), wrap="word", yscrollcommand=scrollbar.set)
        self.solution_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.solution_box.yview)

        # Right Panel
        right = tk.Frame(main_frame, bg="#252540", bd=2, relief="ridge")
        right.grid(row=0, column=2, padx=15, sticky="nsew")
        
        tk.Label(right, text="🧭 HOW TO PLAY", bg="#252540", fg="#00e6e6", 
                 font=("Segoe UI", 13, "bold")).pack(pady=10)
        
        instructions = tk.Text(right, width=35, height=35, bg="#252540", fg="white", 
                               font=("Segoe UI", 9), wrap="word", bd=0)
        instructions.pack(padx=10, pady=5)
        instructions.insert("1.0", """1️ Choose scenario
2️ Enter values (leave ONE blank)
3️ Customize parameters
4️Click ▶ Run Simulation

Surface Friction (μ):
• Ice: 0.1 (slippery)
• Tile: 0.3 (smooth)
• Wood: 0.5 (moderate)
• Concrete: 0.7 (rough)
• Sand: 0.9 (very rough)

Object Shapes:
• Box: Full friction
• Cylinder: 15% (rolling)
• Sphere: 5% (minimal)

Force Angles:
• Horizontal: Standard
• Upward: Reduces normal
• Downward: Increases normal

Push Modes:
• Constant: Steady
• Sudden: Quick impulse
• Increasing: Gradual ramp
""")
        instructions.config(state="disabled")

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.object = None
        self.reset_canvas()
        
        self.solution_box.tag_configure("center", justify='center') 
    
    def reset_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 400, 700, 450, fill="#ddd", outline="")
        self.canvas.create_text(350, 425, text="Ground Level", fill="#666", font=("Consolas", 10))
        self.object = None

    def get_physics_params(self):
        try:
            F = float(self.entries["force"].get()) if self.entries["force"].get() else None
            d = float(self.entries["distance"].get()) if self.entries["distance"].get() else None
            m = float(self.entries["mass"].get()) if self.entries["mass"].get() else None
            angle = float(self.entries["angle"].get()) if self.entries["angle"].get() else 0
            user_mu = float(self.entries["mu"].get()) if self.entries["mu"].get() else None
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numbers!")
            return None

        if d is None or d <= 0:
            messagebox.showerror("Input Error", "Distance must be positive!")
            return None

        surface_mu_map = {"Ice": 0.1, "Tile": 0.3, "Wood": 0.5, "Concrete": 0.7, "Sand": 0.9}
        shape_friction_factor = {"Box": 1.0, "Cylinder": 0.15, "Sphere": 0.05}
        
        base_mu = surface_mu_map.get(self.surface_material.get(), 0.5)
        mu = base_mu * shape_friction_factor.get(self.object_shape.get(), 1.0)
        
        if user_mu is not None:
            mu = user_mu

        force_angle_map = {"Horizontal": 0, "Upward": 30, "Downward": -30}
        force_angle_degrees = force_angle_map.get(self.force_angle_mode.get(), 0)

        return {
            'F': F, 'd': d, 'm': m, 'angle': angle, 'mu': mu,
            'force_angle': force_angle_degrees,
            'scenario': self.scenario.get(),
            'shape': self.object_shape.get(),
            'surface': self.surface_material.get(),
            'push_mode': self.push_mode.get()
        }

    def calculate_physics(self, params):
        g = 9.81
        scenario = params['scenario']
        F, d, m, angle, mu = params['F'], params['d'], params['m'], params['angle'], params['mu']
        force_angle = params['force_angle']
        
        solution_data = "" # Renamed to avoid confusion with final output
        
        if m is None:
            if scenario == "Lifting Object" and F is not None:
                m = F / g
                solution_data += f"✓ Mass: m = F/g = {m:.2f} kg\n\n"
            elif scenario == "Inclined Plane" and F is not None:
                sin_theta = math.sin(math.radians(angle))
                if sin_theta == 0:
                    messagebox.showerror("Error", "Angle cannot be 0°!")
                    return None
                m = F / (g * sin_theta)
                solution_data += f"✓ Mass: m = {m:.2f} kg\n\n"
            elif scenario == "Pushing Object" and F is not None and mu != 0:
                m = F / (mu * g)
                solution_data += f"✓ Mass: m = {m:.2f} kg\n\n"
            else:
                messagebox.showerror("Error", "Cannot calculate mass!")
                return None

        params['m'] = m
    
        weight = m * g
        F_vertical = (F if F else 0) * math.sin(math.radians(force_angle))
        
        if scenario == "Inclined Plane":
            Fn = weight * math.cos(math.radians(angle))
        else:
            Fn = weight - F_vertical
        Fn = max(Fn, 0)

        if scenario == "Lifting Object":
            F_req = weight
            formula = "F_req = m × g"
        elif scenario == "Inclined Plane":
            F_req = weight * math.sin(math.radians(angle)) + mu * Fn
            formula = f"F_req = m×g×sin({angle}°) + μ×Fn"
        else:
            F_req = mu * Fn
            formula = "F_req = μ × Fn"

        if F is None:
            F = F_req * 1.2
            solution_data += f"✓ Force: F = {F:.2f} N\n\n"

        params['F'] = F

        if F < F_req:
            solution_data += f"❌ INSUFFICIENT FORCE!\n\n"
            solution_data += f"Applied: {F:.2f} N\nRequired: {F_req:.2f} N\n"
            return {'moves': False, 'solution': solution_data, 'params': params}

        # Calculate Net Force in the direction of motion
        F_parallel_applied = F * math.cos(math.radians(force_angle)) if scenario == "Pushing Object" else F
        F_parallel_gravity = weight * math.sin(math.radians(angle)) if scenario == "Inclined Plane" else 0
        F_friction = mu * Fn if scenario != "Lifting Object" else 0
        
        # Net Force calculation adjusted for different scenarios
        if scenario == "Lifting Object":
            net_force = F - weight
        elif scenario == "Inclined Plane":
            # Assuming force F is applied parallel to the incline
            net_force = F - F_parallel_gravity - F_friction
        else: # Pushing Object
            net_force = F_parallel_applied - F_friction
            
        # Ensure positive net force for motion/work calculation (or zero if insufficient)
        if net_force < 0:
             net_force = 0
             # If net force is zero but F > F_req, we assume motion just started
             # For a simple simulation, we'll ensure we move if F > F_req
             if F > F_req and scenario != "Lifting Object" and scenario != "Inclined Plane":
                 net_force = F - F_req

        net_work = net_force * d
        ke_final = max(net_work, 0) # Work-Energy Theorem: W_net = ΔKE
        v_final = math.sqrt(2 * ke_final / m) if m > 0 and ke_final > 0 else 0
        
        time_interval = 3.0 / self.anim_speed.get()
        power = net_work / time_interval if time_interval > 0 else 0

        solution_data += f"📋 Given:\n \n"
        solution_data += f"   m = {m:.2f} kg | F = {F:.2f} N | d = {d:.2f} m\n"
        solution_data += f"   μ = {mu:.3f}\n\n\n"
        solution_data += f"⚖️ Forces:\n \n"
        solution_data += f"   Weight = {weight:.2f} N |\t"
        solution_data += f"   Normal = {Fn:.2f} N |\t"
        solution_data += f"   {formula} = {F_req:.2f} N |\t"
        solution_data += f"   Net = {net_force:.2f} N ✓\n\n\n"
        solution_data += f"⚡ Energy:\n \n"
        solution_data += f"   Net Work = {net_work:.2f} J |\t"
        solution_data += f"   ΔKE = {ke_final:.2f} J |\t"
        solution_data += f"   v = {v_final:.2f} m/s |\t"
        solution_data += f"   Power = {power:.2f} W\t"

        return {
        'moves': True, 'solution': solution_data, 'params': params,
        'F_req': F_req, 'net_work': net_work, 'ke_final': ke_final,
        'v_final': v_final, 'power': power, 'Fn': Fn
        }
        
    def start_timer(self):
        if not self.is_timer_running:
            return
            
        elapsed_time = time.time() - self.sim_start_time
        
        # Format time as MM:SS.cc (minutes:seconds.hundredths)
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        hundredths = int((elapsed_time % 1) * 100)
        
        time_str = f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
        self.timer_label.config(text=time_str)
        
        # Schedule the next update after 50 milliseconds (20 times per second)
        self.timer_id = self.root.after(50, self.start_timer)


    def run_simulation(self):
        if self.is_animating:
            messagebox.showwarning("Busy", "Already running!")
            return

        params = self.get_physics_params()
        if not params:
            return

        results = self.calculate_physics(params)
        if not results:
            return

        self.solution_box.delete(1.0, tk.END)
        
        # Combine the header/footer with the solution data
        full_output = (
            f"{'='*125}\n"
            f"PHYSICS CALCULATION\n"
            f"{'='*125}\n\n"
            f"{results['solution']} \n \n \n"
            f"{'='*125}\n"
        )
        
        # Insert the full output block
        self.solution_box.insert(tk.END, full_output)
        
        # Apply the 'center' tag to the entire inserted text block
        self.solution_box.tag_add("center", "1.0", tk.END)
        
        if not results['moves']:
            self.feedback.config(text="⚠️ NOT MOVING - Insufficient Force!", fg="#ff6b6b")
            self.delta_ke_label.config(text="")
            self.stop_timer() # Ensure timer is stopped if force is insufficient
            self.timer_label.config(text="00:00.00")
            return

        # Start animation if moves=True
        self.is_animating = True
        self.run_btn.config(state="disabled")
        self.feedback.config(text="▶ Simulating Motion...", fg="#00e6e6")
        self.delta_ke_label.config(text=f"ΔKE (Net Work) = {results['ke_final']:.2f} J")
        
        self.update_background(params)

        # --- Timer Start Logic ---
        self.sim_start_time = time.time()
        self.is_timer_running = True
        self.start_timer()
        # -------------------------

        # Start animation in a separate thread
        self.animation_thread = threading.Thread(target=self.animate_motion, args=(results,))
        self.animation_thread.start()
        
    def stop_timer(self):
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.is_timer_running = False

    def stop_simulation(self):
        self.is_animating = False
        self.run_btn.config(state="normal")
        self.feedback.config(text="⏹ Stopped", fg="#ffaa00")
        
        # Timer stops and freezes on the current time
        self.stop_timer()

    def reset_simulation(self):
        self.stop_simulation()
        self.reset_canvas()
        self.solution_box.delete(1.0, tk.END)
        self.feedback.config(text="⚡ Ready!", fg="#aaffaa")
        self.delta_ke_label.config(text="")
        self.sim_data = {'distance': [], 'work': [], 'ke': []}
        
        # Reset timer label
        self.timer_label.config(text="00:00.00")

    def update_background(self, params):
        self.canvas.delete("all")
        scenario = params['scenario']
        angle = params['angle']
        mu = params['mu']
        shape = params['shape']

        if scenario == "Pushing Object":
            if mu <= 0.15:
                color, label = "#b3e5fc", "❄️ ICE"
            elif mu <= 0.35:
                color, label = "#f0f0f0", "🏠 TILE"
            elif mu <= 0.6:
                color, label = "#deb887", "🪵 WOOD"
            elif mu <= 0.8:
                color, label = "#a9a9a9", "🏗️ CONCRETE"
            else:
                color, label = "#e69f00", "🏖️ SAND"

            self.canvas.create_rectangle(0, 400, 700, 450, fill=color, outline="black")
            self.canvas.create_text(600, 420, text=f"{label}", fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(50, 350, shape, "#73ff61")

        elif scenario == "Lifting Object":
            self.canvas.create_rectangle(0, 400, 700, 450, fill="#9ecae1", outline="")
            self.canvas.create_line(340, 50, 340, 400, fill="#666", width=4)
            self.canvas.create_text(600, 420, text="🏗️ CRANE", fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(315, 350, shape, "#73ff61")

        elif scenario == "Inclined Plane":
            incline_height = min(math.tan(math.radians(angle)) * 700, 350)
            self.canvas.create_polygon(0, 450, 700, 450, 700, 450 - incline_height,
                                     fill="#c7e9b4", outline="black", width=2)
            self.canvas.create_text(600, 420, text=f"⛰️ θ={angle:.1f}°", fill="black", font=("Consolas", 11, "bold"))
            
            obj_y = 450 - (math.tan(math.radians(angle)) * 100) - 50
            self.draw_object(50, obj_y, shape, "#73ff61")
            self.draw_force_vectors(params)

    def draw_object(self, x, y, shape, color):
        if shape == "Box":
            self.object = self.canvas.create_rectangle(x, y, x + 50, y + 50, fill=color, outline="black", width=2)
        elif shape == "Cylinder":
            rect = self.canvas.create_rectangle(x, y + 10, x + 50, y + 50, fill=color, outline="black", width=2)
            oval_top = self.canvas.create_oval(x, y, x + 50, y + 20, fill=color, outline="black", width=2)
            oval_bottom = self.canvas.create_oval(x, y + 40, x + 50, y + 60, fill=color, outline="black", width=2)
            self.object = [oval_bottom, rect, oval_top]
        elif shape == "Sphere":
            radius = 25
            cx, cy = x + radius, y + 25
            self.object = self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                                  fill=color, outline="black", width=2)

    def draw_force_vectors(self, params):
        if params['scenario'] != "Inclined Plane":
            return

        if isinstance(self.object, list):
            coords = self.canvas.coords(self.object[1])
        else:
            coords = self.canvas.coords(self.object)
        
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2

        angle = params['angle']
        length = 60
        angle_rad = math.radians(angle)

        self.canvas.create_line(x_center, y_center, x_center, y_center + length,
                                 arrow=tk.LAST, fill="green", width=3)
        self.canvas.create_text(x_center + 30, y_center + length, text="Fg", fill="green", font=("Consolas", 9, "bold"))

        fn_dx = -length * math.sin(angle_rad)
        fn_dy = -length * math.cos(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + fn_dx, y_center + fn_dy,
                                 arrow=tk.LAST, fill="orange", width=3)
        self.canvas.create_text(x_center + fn_dx - 15, y_center + fn_dy, text="Fn", fill="orange", font=("Consolas", 9, "bold"))

        f_dx = length * math.cos(angle_rad)
        f_dy = -length * math.sin(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + f_dx, y_center + f_dy,
                                 arrow=tk.LAST, fill="#00e6e6", width=3)
        self.canvas.create_text(x_center + f_dx + 20, y_center + f_dy, text="F", fill="#00e6e6", font=("Consolas", 9, "bold"))

    def animate_motion(self, results):
        params = results['params']
        scenario = params['scenario']
        distance = params['d']
        angle = params['angle']
        push_mode = params['push_mode']
        
        steps = int(distance * 15)
        speed_factor = 1.0 / self.anim_speed.get()
        
        for step in range(steps):
            if not self.is_animating:
                break
                
            if push_mode == "Constant Force":
                move_val = 4
            elif push_mode == "Sudden Push":
                move_val = 20 if step < 5 else 0.5
            elif push_mode == "Increasing Force":
                move_val = 2 + (step / steps) * 6
            
            if scenario == "Lifting Object":
                self._move_object(0, -move_val)
            elif scenario == "Inclined Plane":
                dx = move_val * math.cos(math.radians(angle))
                dy = -move_val * math.sin(math.radians(angle))
                self._move_object(dx, dy)
            else:
                force_angle = params['force_angle']
                dx = move_val * math.cos(math.radians(force_angle))
                dy = -move_val * math.sin(math.radians(force_angle))
                self._move_object(dx, dy)
            
            self.canvas.update()
            time.sleep(0.02 * speed_factor)
        
        self.draw_ke_indicator()
        
        # Stop the timer when animation thread completes normally
        self.stop_timer()

        self.is_animating = False
        self.run_btn.config(state="normal")
        self.feedback.config(text="✅ Simulation Complete!", fg="#98c379")

    def _move_object(self, dx, dy):
        if isinstance(self.object, list):
            for part in self.object:
                self.canvas.move(part, dx, dy)
        else:
            self.canvas.move(self.object, dx, dy)

    def draw_ke_indicator(self):
        if isinstance(self.object, list):
            all_coords = []
            for part in self.object:
                all_coords.extend(self.canvas.coords(part))
            x1, x2 = min(all_coords[::2]), max(all_coords[::2])
            y2 = max(all_coords[1::2])
        else:
            coords = self.canvas.coords(self.object)
            x1, x2, y2 = coords[0], coords[2], coords[3]
        
        y = y2 + 20
        self.canvas.create_line(x1, y, x2, y, fill="#73ff61", width=3, tags="ke_line")
        
        ke_text = self.delta_ke_label.cget("text")
        if "=" in ke_text:
            ke_val = ke_text.split("=")[1].strip().split()[0]
            self.canvas.create_text((x1 + x2) / 2, y + 15, text=f"ΔKE={ke_val}J",
                                     fill="#73ff61", font=("Consolas", 11, "bold"), tags="ke_text")
    def start_quiz(self):
        ForceQuestQuiz(self.root)

    def show_plot(self):
        try:
            params = self.get_physics_params()
            if not params:
                return
                
            results = self.calculate_physics(params)
            # Use the more reliable key 'net_work' from the calculated results
            if not results or not results['moves'] or 'net_work' not in results:
                messagebox.showerror("Error", "Run a successful simulation first!")
                return
            
            d = params['d']
            F_req = results['F_req']
            F = params['F']
            
            # The net force is F - F_req (when force is applied horizontally)
            net_force = F - F_req
            
            x = np.linspace(0, d, 50)
            work = net_force * x
            ke = work # W_net = ΔKE
            
            plt.figure(figsize=(10, 6))
            plt.plot(x, work, 'b-', linewidth=2, label='Net Work (W_net)')
            plt.plot(x, ke, 'r--', linewidth=2, label='Kinetic Energy (ΔKE)')
            plt.title('Energy vs Distance (Work-Energy Theorem)', fontsize=14, fontweight='bold')
            plt.xlabel('Distance (m)', fontsize=12)
            plt.ylabel('Energy (J)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            # Catching generic errors in plotting (like missing numpy/matplotlib data)
            messagebox.showerror("Error", f"Could not generate graph: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ForceQuestApp(root)
    root.mainloop()