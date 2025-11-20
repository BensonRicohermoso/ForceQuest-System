import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading
import numpy as np
import matplotlib.pyplot as plt


class ForceQuestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ ForceQuest 5.0 — Physics Adventure Mode")
        self.root.geometry("1400x900")
        self.root.configure(bg="#1e1e2f")
        self.is_animating = False
        self.animation_thread = None
        self.sim_data = {'distance': [], 'work': [], 'ke': []}
        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="FORCEQUEST 5.0", fg="#00e6e6",
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

        # Center Canvas
        center = tk.Frame(main_frame, bg="#1e1e2f")
        center.grid(row=0, column=1, padx=20, sticky="nsew")

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
        solution_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(solution_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.solution_box = tk.Text(solution_frame, width=85, height=12, bg="#111", fg="#98c379",
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
        instructions.insert("1.0", """1️⃣ Choose scenario
2️⃣ Enter values (leave ONE blank)
3️⃣ Customize parameters
4️⃣ Click ▶ Run Simulation

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
        
        solution = ""
        
        if m is None:
            if scenario == "Lifting Object" and F is not None:
                m = F / g
                solution += f"✓ Mass: m = F/g = {m:.2f} kg\n\n"
            elif scenario == "Inclined Plane" and F is not None:
                sin_theta = math.sin(math.radians(angle))
                if sin_theta == 0:
                    messagebox.showerror("Error", "Angle cannot be 0°!")
                    return None
                m = F / (g * sin_theta)
                solution += f"✓ Mass: m = {m:.2f} kg\n\n"
            elif scenario == "Pushing Object" and F is not None and mu != 0:
                m = F / (mu * g)
                solution += f"✓ Mass: m = {m:.2f} kg\n\n"
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
            solution += f"✓ Force: F = {F:.2f} N\n\n"

        params['F'] = F

        if F < F_req:
            solution += f"❌ INSUFFICIENT FORCE!\n\n"
            solution += f"Applied: {F:.2f} N\nRequired: {F_req:.2f} N\n"
            return {'moves': False, 'solution': solution, 'params': params}

        net_force = F - F_req
        net_work = net_force * d
        ke_final = max(net_work, 0)
        v_final = math.sqrt(2 * ke_final / m) if m > 0 and ke_final > 0 else 0
        
        time_interval = 3.0 / self.anim_speed.get()
        power = net_work / time_interval if time_interval > 0 else 0

        solution += f"{'='*60}\n"
        solution += f"PHYSICS CALCULATION\n{'='*60}\n\n"
        solution += f"📋 Given:\n"
        solution += f"   m = {m:.2f} kg | F = {F:.2f} N | d = {d:.2f} m\n"
        solution += f"   μ = {mu:.3f}\n\n"
        solution += f"⚖️ Forces:\n"
        solution += f"   Weight = {weight:.2f} N\n"
        solution += f"   Normal = {Fn:.2f} N\n"
        solution += f"   {formula} = {F_req:.2f} N\n"
        solution += f"   Net = {net_force:.2f} N ✓\n\n"
        solution += f"⚡ Energy:\n"
        solution += f"   Net Work = {net_work:.2f} J\n"
        solution += f"   ΔKE = {ke_final:.2f} J\n"
        solution += f"   v = {v_final:.2f} m/s\n"
        solution += f"   Power = {power:.2f} W\n"
        solution += f"{'='*60}\n"

        return {
            'moves': True, 'solution': solution, 'params': params,
            'F_req': F_req, 'net_work': net_work, 'ke_final': ke_final,
            'v_final': v_final, 'power': power, 'Fn': Fn
        }

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
        self.solution_box.insert(tk.END, results['solution'])

        if not results['moves']:
            self.feedback.config(text="⚠️ NOT MOVING - Insufficient Force!", fg="#ff6b6b")
            self.delta_ke_label.config(text="")
            return

        self.feedback.config(
            text=f"✅ Work={results['net_work']:.2f}J | v={results['v_final']:.2f}m/s | P={results['power']:.2f}W",
            fg="#00ff00"
        )
        self.delta_ke_label.config(text=f"🔥 ΔKE = {results['ke_final']:.2f} J", fg="#ffaa00")

        self.is_animating = True
        self.run_btn.config(state="disabled")
        self.update_background(params)
        
        self.animation_thread = threading.Thread(target=self.animate_motion, args=(results,), daemon=True)
        self.animation_thread.start()

    def stop_simulation(self):
        self.is_animating = False
        self.run_btn.config(state="normal")
        self.feedback.config(text="⏹ Stopped", fg="#ffaa00")

    def reset_simulation(self):
        self.stop_simulation()
        self.reset_canvas()
        self.solution_box.delete(1.0, tk.END)
        self.feedback.config(text="⚡ Ready!", fg="#aaffaa")
        self.delta_ke_label.config(text="")
        self.sim_data = {'distance': [], 'work': [], 'ke': []}

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

            self.canvas.create_rectangle(0, 400, 700, 450, fill=color, outline="")
            self.canvas.create_text(600, 420, text=f"{label}", fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(50, 350, shape, "#ff6f61")

        elif scenario == "Lifting Object":
            self.canvas.create_rectangle(0, 400, 700, 450, fill="#9ecae1", outline="")
            self.canvas.create_line(340, 50, 340, 400, fill="#666", width=4)
            self.canvas.create_text(600, 420, text="🏗️ CRANE", fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(315, 350, shape, "#f4a261")

        elif scenario == "Inclined Plane":
            incline_height = min(math.tan(math.radians(angle)) * 700, 350)
            self.canvas.create_polygon(0, 450, 700, 450, 700, 450 - incline_height,
                                      fill="#c7e9b4", outline="black", width=2)
            self.canvas.create_text(600, 420, text=f"⛰️ θ={angle:.1f}°", fill="black", font=("Consolas", 11, "bold"))
            
            obj_y = 450 - (math.tan(math.radians(angle)) * 100) - 50
            self.draw_object(50, obj_y, shape, "#d95f02")
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
        self.is_animating = False
        self.run_btn.config(state="normal")

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
        self.canvas.create_line(x1, y, x2, y, fill="#ffaa00", width=3, tags="ke_line")
        
        ke_text = self.delta_ke_label.cget("text")
        if "=" in ke_text:
            ke_val = ke_text.split("=")[1].strip().split()[0]
            self.canvas.create_text((x1 + x2) / 2, y + 15, text=f"ΔKE={ke_val}J",
                                   fill="#ffaa00", font=("Consolas", 11, "bold"), tags="ke_text")

    def show_plot(self):
        try:
            params = self.get_physics_params()
            if not params:
                return
                
            results = self.calculate_physics(params)
            if not results or not results['moves']:
                messagebox.showerror("Error", "Run a successful simulation first!")
                return
            
            d = params['d']
            net_force = results['F_req']
            F = params['F']
            
            x = np.linspace(0, d, 50)
            work = (F - net_force) * x
            ke = work
            
            plt.figure(figsize=(10, 6))
            plt.plot(x, work, 'b-', linewidth=2, label='Net Work')
            plt.plot(x, ke, 'r--', linewidth=2, label='Kinetic Energy')
            plt.title('Energy vs Distance', fontsize=14, fontweight='bold')
            plt.xlabel('Distance (m)', fontsize=12)
            plt.ylabel('Energy (J)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate graph: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ForceQuestApp(root)
    root.mainloop()