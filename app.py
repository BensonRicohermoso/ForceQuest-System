import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading
import os
from PIL import Image, ImageTk
from config import COLORS, FONTS, SCENARIOS, SURFACE_MATERIALS, OBJECT_SHAPES, FORCE_ANGLES, PUSH_MODES, CANVAS
from quiz import ForceQuestQuiz


class ForceQuestApp:
    """Main application controller with real-time energy graph"""
    
    def load_images(self):
        """Load and prepare images for use on the tkinter Canvas"""
        self.images = {}
        surface_files = {
            "Ice": "ice.png",
            "Tile": "tiles.png",
            "Wood": "wood.png",
            "Concrete": "concrete.png",
            "Sand": "sand.jpg",
        }

        canvas_w, canvas_h = CANVAS['width'], CANVAS['height']

        for surface, fname in surface_files.items():
            path = os.path.join(os.path.dirname(__file__), 'images', 'background', fname)
            try:
                if os.path.exists(path):
                    img = Image.open(path).convert("RGBA")
                    img = img.resize((canvas_w, canvas_h), Image.LANCZOS)
                    self.images[surface] = ImageTk.PhotoImage(img)
                else:
                    self.images[surface] = None
            except Exception as e:
                print(f"⚠ Error loading image '{path}': {e}")
                self.images[surface] = None

    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ P6Quest — Physics Adventure Mode")
        self.root.geometry("1400x1000")
        self.root.configure(bg=COLORS['bg_primary'])
        self.is_animating = False
        self.animation_thread = None
        self.sim_data = {'distance': [], 'work': [], 'ke': []}
        
        # Timer attributes
        self.is_timer_running = False
        self.sim_start_time = 0.0
        self.timer_id = None
        
        # Real-time graph attributes
        self.graph_data = {'distance': [], 'work': [], 'ke': []}
        self.current_distance = 0.0
        self.max_distance = 1.0
        self.max_energy = 1.0

        # Load image assets
        try:
            self.load_images()
        except Exception:
            self.images = {}

        self.setup_ui()

    def setup_ui(self):
        title = tk.Label(self.root, text="P6QUEST", fg=COLORS['accent_cyan'],
                         bg=COLORS['bg_primary'], font=("Consolas", 28, "bold"))
        title.pack(pady=10)

        subtitle = tk.Label(self.root, text="The Fun Physics Simulator — Work, Energy & Power",
                            fg=COLORS['text_gray'], bg=COLORS['bg_primary'], font=FONTS['subtitle'])
        subtitle.pack()

        main_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # === LEFT PANEL: Input Controls ===
        left = tk.Frame(main_frame, bg=COLORS['bg_secondary'], bd=2, relief="ridge")
        left.grid(row=0, column=0, padx=15, sticky="nsew")

        tk.Label(left, text="Scenario:", bg=COLORS['bg_secondary'], fg="white", font=("Segoe UI", 10, "bold")).grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self.scenario = ttk.Combobox(left, values=SCENARIOS, state="readonly", width=18)
        self.scenario.grid(row=0, column=1, pady=5, padx=5)
        self.scenario.current(0)

        inputs = [("Force (N)", "force"), ("Distance (m)", "distance"),
                  ("Mass (kg)", "mass"), ("Angle (°)", "angle"), ("Friction μ", "mu")]
        self.entries = {}
        for i, (label, key) in enumerate(inputs, start=1):
            tk.Label(left, text=label, bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
                row=i, column=0, sticky="w", pady=5, padx=5)
            e = tk.Entry(left, width=15, font=FONTS['normal'])
            e.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key] = e

        row_base = len(inputs) + 1

        tk.Label(left, text="Surface Material:", bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
            row=row_base, column=0, sticky="w", pady=5, padx=5)
        self.surface_material = ttk.Combobox(left, width=18, values=SURFACE_MATERIALS, state="readonly")
        self.surface_material.grid(row=row_base, column=1, pady=5, padx=5)
        self.surface_material.current(2)

        tk.Label(left, text="Object Shape:", bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
            row=row_base + 1, column=0, sticky="w", pady=5, padx=5)
        self.object_shape = ttk.Combobox(left, width=18, values=OBJECT_SHAPES, state="readonly")
        self.object_shape.grid(row=row_base + 1, column=1, pady=5, padx=5)
        self.object_shape.current(0)

        tk.Label(left, text="Force Angle:", bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
            row=row_base + 2, column=0, sticky="w", pady=5, padx=5)
        self.force_angle_mode = ttk.Combobox(left, width=18, values=FORCE_ANGLES, state="readonly")
        self.force_angle_mode.grid(row=row_base + 2, column=1, pady=5, padx=5)
        self.force_angle_mode.current(0)

        tk.Label(left, text="Push Mode:", bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
            row=row_base + 3, column=0, sticky="w", pady=5, padx=5)
        self.push_mode = ttk.Combobox(left, width=18, values=PUSH_MODES, state="readonly")
        self.push_mode.grid(row=row_base + 3, column=1, pady=5, padx=5)
        self.push_mode.current(0)

        tk.Label(left, text="Animation Speed:", bg=COLORS['bg_secondary'], fg="white", font=FONTS['label']).grid(
            row=row_base + 4, column=0, sticky="w", pady=5, padx=5)
        self.anim_speed = ttk.Scale(left, from_=0.5, to=3.0, orient="horizontal")
        self.anim_speed.set(1.0)
        self.anim_speed.grid(row=row_base + 4, column=1, pady=5, padx=5, sticky="ew")

        btn_frame = tk.Frame(left, bg=COLORS['bg_secondary'])
        btn_frame.grid(row=row_base + 5, column=0, columnspan=2, pady=10)
    
        self.run_btn = tk.Button(btn_frame, text="▶ Run Simulation", bg=COLORS['accent_cyan'], fg="black", 
                                 font=FONTS['button'], command=self.run_simulation, width=20)
        self.run_btn.pack(pady=5)
        
        tk.Button(btn_frame, text="⏹ Stop", bg=COLORS['accent_red'], fg="white",
                  font=FONTS['button'], command=self.stop_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="🔄 Reset", bg=COLORS['accent_blue'], fg="black",
                  font=FONTS['button'], command=self.reset_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="✅ Start Physics Quiz", bg=COLORS['accent_yellow'], fg="black",
                  font=FONTS['button'], command=self.start_quiz, width=20, height=5).pack(pady=5)
        
        # === CENTER PANEL with Scrollable Canvas ===
        center_container = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        center_container.grid(row=0, column=1, padx=(20, 50), sticky="nsew")
        
        # Create canvas for scrolling
        center_canvas = tk.Canvas(center_container, bg=COLORS['bg_primary'], highlightthickness=0)
        center_scrollbar = tk.Scrollbar(center_container, orient="vertical", command=center_canvas.yview)
        
        # Scrollable frame inside canvas
        center = tk.Frame(center_canvas, bg=COLORS['bg_primary'])
        
        # Configure scrolling
        center.bind(
            "<Configure>",
            lambda e: center_canvas.configure(scrollregion=center_canvas.bbox("all"))
        )
        
        center_canvas.create_window((0, 0), window=center, anchor="nw")
        center_canvas.configure(yscrollcommand=center_scrollbar.set)
        
        # Pack scrollbar and canvas
        center_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        center_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            center_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        center_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Timer
        timer_frame = tk.Frame(center, bg=COLORS['bg_primary'])
        timer_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        tk.Label(timer_frame, text="Sim Time:", bg=COLORS['bg_primary'], fg=COLORS['accent_blue'], 
                 font=FONTS['timer']).pack(side=tk.LEFT)
        self.timer_label = tk.Label(timer_frame, text="00:00.00", bg=COLORS['bg_primary'], 
                                     fg=COLORS['accent_yellow'], font=FONTS['timer'])
        self.timer_label.pack(side=tk.LEFT, padx=(5, 0))

        # Simulation Canvas
        self.canvas = tk.Canvas(center, width=CANVAS['width'], height=CANVAS['height'], bg="white", 
                               highlightthickness=2, highlightbackground=COLORS['accent_cyan'])
        self.canvas.pack(padx=(0, 50))

        self.feedback = tk.Label(center, text="⚡ Ready to simulate!", bg=COLORS['bg_primary'], fg="#aaffaa", 
                                 font=FONTS['feedback'])
        self.feedback.pack(pady=5, padx=(0, 50))

        self.delta_ke_label = tk.Label(center, text="", bg=COLORS['bg_primary'], fg=COLORS['accent_yellow'], 
                                        font=FONTS['timer'])
        self.delta_ke_label.pack(pady=5, padx=(0, 50))

        # Solution Box
        solution_frame = tk.Frame(center, bg=COLORS['bg_primary'])
        solution_frame.pack(pady=5, fill=tk.BOTH, expand=True, padx=(0, 50))
        
        scrollbar = tk.Scrollbar(solution_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.solution_box = tk.Text(solution_frame, width=85, height=15, bg="#111", fg=COLORS['accent_green'],
                                     font=FONTS['solution'], wrap="word", yscrollcommand=scrollbar.set)
        self.solution_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.solution_box.yview)
        
        # === REAL-TIME ENERGY GRAPH ===
        graph_label = tk.Label(center, text="📊 Real-Time Energy Graph", bg=COLORS['bg_primary'], 
                               fg=COLORS['accent_cyan'], font=("Segoe UI", 11, "bold"))
        graph_label.pack(pady=(10, 5), padx=(0, 50))
        
        self.graph_canvas = tk.Canvas(center, width=CANVAS['width'], height=250, bg="white", 
                                      highlightthickness=2, highlightbackground=COLORS['accent_cyan'])
        self.graph_canvas.pack(pady=(5, 10), padx=(0, 50))
        self.init_graph()

        # === RIGHT PANEL: Instructions ===
        from ui_components.instructions_panel import InstructionsPanel
        self.instructions_panel = InstructionsPanel(main_frame)
        right_widget = self.instructions_panel.get_widget()
        right_widget.grid(row=0, column=2, padx=15, sticky="nsew")

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.object = None
        self.reset_canvas()
        
        self.solution_box.tag_configure("center", justify='center')
    
    def reset_canvas(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'], 
                                      CANVAS['ground_y'] + CANVAS['ground_height'], fill="#ddd", outline="")
        self.canvas.create_text(CANVAS['width']//2, CANVAS['ground_y'] + 25, 
                                text="Ground Level", fill="#666", font=("Consolas", 10))
        self.object = None
    
    def init_graph(self):
        """Initialize the energy graph with axes and labels"""
        self.graph_canvas.delete("all")
        
        margin_left = 60
        margin_right = 30
        margin_top = 20
        margin_bottom = 40
        
        self.graph_width = CANVAS['width'] - margin_left - margin_right
        self.graph_height = 250 - margin_top - margin_bottom
        self.graph_x0 = margin_left
        self.graph_y0 = margin_top
        
        # Draw axes
        self.graph_canvas.create_line(margin_left, margin_top, margin_left, 
                                       250 - margin_bottom, fill="black", width=2)
        self.graph_canvas.create_line(margin_left, 250 - margin_bottom, 
                                       CANVAS['width'] - margin_right, 250 - margin_bottom, fill="black", width=2)
        
        # Labels
        self.graph_canvas.create_text(CANVAS['width']//2, 240, text="Distance (m)", 
                                       fill="#333", font=("Segoe UI", 9, "bold"))
        self.graph_canvas.create_text(20, 135, text="Energy (J)", angle=90,
                                       fill="#333", font=("Segoe UI", 9, "bold"))
        
        # Legend
        self.graph_canvas.create_line(520, 15, 560, 15, fill="blue", width=2)
        self.graph_canvas.create_text(600, 15, text="Net Work", fill="blue", font=("Segoe UI", 8, "bold"))
        
        self.graph_canvas.create_line(520, 35, 560, 35, fill="red", width=2, dash=(4, 2))
        self.graph_canvas.create_text(605, 35, text="Kinetic Energy", fill="red", font=("Segoe UI", 8, "bold"))
        
        self.graph_canvas.create_text(margin_left - 5, 250 - margin_bottom, text="0", 
                                       anchor="e", fill="#666", font=("Consolas", 8))
    
    def update_graph(self, distance, work, ke):
        """Update the real-time energy graph with new data point"""
        self.graph_data['distance'].append(distance)
        self.graph_data['work'].append(work)
        self.graph_data['ke'].append(ke)
        
        if distance > self.max_distance:
            self.max_distance = distance
        if max(work, ke) > self.max_energy:
            self.max_energy = max(work, ke)
        
        self.graph_canvas.delete("plot_line")
        self.graph_canvas.delete("scale")
        
        margin_left = 60
        margin_bottom = 40
        
        # Y-axis scale
        for i in range(5):
            y_val = (self.max_energy / 4) * i
            y_pos = (250 - margin_bottom) - (self.graph_height / 4) * i
            self.graph_canvas.create_text(margin_left - 5, y_pos, text=f"{y_val:.1f}", 
                                          anchor="e", fill="#666", font=("Consolas", 8), tags="scale")
        
        # X-axis scale
        for i in range(5):
            x_val = (self.max_distance / 4) * i
            x_pos = margin_left + (self.graph_width / 4) * i
            self.graph_canvas.create_text(x_pos, 250 - margin_bottom + 15, text=f"{x_val:.1f}", 
                                          fill="#666", font=("Consolas", 8), tags="scale")
        
        # Plot data points
        if len(self.graph_data['distance']) > 1:
            # Plot Work line
            for i in range(len(self.graph_data['distance']) - 1):
                x1 = self.graph_x0 + (self.graph_data['distance'][i] / self.max_distance) * self.graph_width
                y1 = self.graph_y0 + self.graph_height - (self.graph_data['work'][i] / self.max_energy) * self.graph_height
                x2 = self.graph_x0 + (self.graph_data['distance'][i+1] / self.max_distance) * self.graph_width
                y2 = self.graph_y0 + self.graph_height - (self.graph_data['work'][i+1] / self.max_energy) * self.graph_height
                
                self.graph_canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="plot_line")
            
            # Plot KE line
            for i in range(len(self.graph_data['distance']) - 1):
                x1 = self.graph_x0 + (self.graph_data['distance'][i] / self.max_distance) * self.graph_width
                y1 = self.graph_y0 + self.graph_height - (self.graph_data['ke'][i] / self.max_energy) * self.graph_height
                x2 = self.graph_x0 + (self.graph_data['distance'][i+1] / self.max_distance) * self.graph_width
                y2 = self.graph_y0 + self.graph_height - (self.graph_data['ke'][i+1] / self.max_energy) * self.graph_height
                
                self.graph_canvas.create_line(x1, y1, x2, y2, fill="red", width=2, 
                                              dash=(4, 2), tags="plot_line")

    def get_physics_params(self):
        """Collect and validate physics parameters from UI"""
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

        from config import SURFACE_FRICTION, SHAPE_FRICTION_FACTOR, FORCE_ANGLE_MAP
        
        base_mu = SURFACE_FRICTION.get(self.surface_material.get(), 0.5)
        mu = base_mu * SHAPE_FRICTION_FACTOR.get(self.object_shape.get(), 1.0)
        
        if user_mu is not None:
            mu = user_mu

        force_angle_degrees = FORCE_ANGLE_MAP.get(self.force_angle_mode.get(), 0)

        return {
            'F': F, 'd': d, 'm': m, 'angle': angle, 'mu': mu,
            'force_angle': force_angle_degrees,
            'scenario': self.scenario.get(),
            'shape': self.object_shape.get(),
            'surface': self.surface_material.get(),
            'push_mode': self.push_mode.get()
        }

    def calculate_physics(self, params):
        """Calculate physics using the physics engine"""
        from physics_engine import PhysicsCalculator
        calc = PhysicsCalculator()
        return calc.calculate_motion(params)
        
    def start_timer(self):
        """Start the simulation timer"""
        if not self.is_timer_running:
            return
            
        elapsed_time = time.time() - self.sim_start_time
        
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        hundredths = int((elapsed_time % 1) * 100)
        
        time_str = f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
        self.timer_label.config(text=time_str)
        
        self.timer_id = self.root.after(50, self.start_timer)

    def run_simulation(self):
        """Run the physics simulation"""
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
        
        full_output = (
            f"{'='*110}\n"
            f"PHYSICS CALCULATION\n"
            f"{'='*110}\n\n"
            f"{results['solution']} \n \n \n"
            f"{'='*110}"
        )
        
        self.solution_box.insert(tk.END, full_output)
        self.solution_box.tag_add("center", "1.0", tk.END)
        
        if not results['moves']:
            self.feedback.config(text="⚠️ NOT MOVING - Insufficient Force!", fg=COLORS['accent_red'])
            self.delta_ke_label.config(text="")
            self.stop_timer()
            self.timer_label.config(text="00:00.00")
            return

        # Reset graph data for new simulation
        self.graph_data = {'distance': [], 'work': [], 'ke': []}
        self.current_distance = 0.0
        self.max_distance = params['d']
        self.max_energy = max(results['net_work'], results['ke_final']) * 1.1
        self.init_graph()
        
        self.is_animating = True
        self.run_btn.config(state="disabled")
        self.feedback.config(text="▶ Simulating Motion...", fg=COLORS['accent_cyan'])
        self.delta_ke_label.config(text=f"ΔKE (Net Work) = {results['ke_final']:.2f} J")
        
        self.update_background(params)

        self.sim_start_time = time.time()
        self.is_timer_running = True
        self.start_timer()

        self.animation_thread = threading.Thread(target=self.animate_motion, args=(results,))
        self.animation_thread.start()
        
    def stop_timer(self):
        """Stop the simulation timer"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.is_timer_running = False

    def stop_simulation(self):
        """Stop the running simulation"""
        self.is_animating = False
        self.run_btn.config(state="normal")
        self.feedback.config(text="⏹ Stopped", fg=COLORS['accent_yellow'])
        self.stop_timer()

    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.stop_simulation()
        self.reset_canvas()
        self.solution_box.delete(1.0, tk.END)
        self.feedback.config(text="⚡ Ready!", fg="#aaffaa")
        self.delta_ke_label.config(text="")
        self.sim_data = {'distance': [], 'work': [], 'ke': []}
        
        self.graph_data = {'distance': [], 'work': [], 'ke': []}
        self.current_distance = 0.0
        self.max_distance = 1.0
        self.max_energy = 1.0
        self.init_graph()
        
        self.timer_label.config(text="00:00.00")

    def update_background(self, params):
        """Update canvas background based on scenario"""
        self.canvas.delete("all")
        scenario = params['scenario']
        angle = params['angle']
        shape = params['shape']
        surface_name = params.get('surface', self.surface_material.get())
        bg_image = None
        if hasattr(self, 'images') and surface_name in self.images:
            bg_image = self.images.get(surface_name)

        if scenario == "Pushing Object":
            if bg_image:
                bg_id = self.canvas.create_image(0, 0, anchor='nw', image=bg_image)
                try:
                    self.canvas.tag_lower(bg_id)
                except Exception:
                    pass
                self._current_bg = bg_image
                
            # Surface colors and labels
            color_map = {
                "Ice": ("#b3e5fc", "❄️ ICE"),
                "Tile": ("#65aade", "🏠 TILE"),
                "Wood": ("#705b40", "🪵 WOOD"),
                "Concrete": ("#6e5d5d", "🏗️ CONCRETE"),
                "Sand": ("#e69f00", "🏖️ SAND")
            }
            color, label = color_map.get(surface_name, ("#ddd", "GROUND"))
            
            self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'], 
                                          CANVAS['ground_y'] + CANVAS['ground_height'], 
                                          fill=color, outline="black")
            self.canvas.create_text(700, 420, text=label, fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(50, 350, shape, "#73ff61")

        elif scenario == "Lifting Object":
            if bg_image:
                bg_id = self.canvas.create_image(0, 0, anchor='nw', image=bg_image)
                try:
                    self.canvas.tag_lower(bg_id)
                except Exception:
                    pass
                self._current_bg = bg_image
            else:
                self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'], 
                                              CANVAS['ground_y'] + CANVAS['ground_height'], 
                                              fill="#9ecae1", outline="")
            self.canvas.create_line(390, 50, 390, 400, fill="#666", width=4)
            self.canvas.create_text(700, 420, text="🏗️ CRANE", fill="black", font=("Consolas", 11, "bold"))
            self.draw_object(365, 350, shape, "#73ff61")

        elif scenario == "Inclined Plane":
            color_map = {
                "Ice": ("#b3e5fc", "❄️ ICE"),
                "Tile": ("#65aade", "🏠 TILE"),
                "Wood": ("#705b40", "🪵 WOOD"),
                "Concrete": ("#6e5d5d", "🏗️ CONCRETE"),
                "Sand": ("#e69f00", "🏖️ SAND")
            }
            surf_color, surf_label = color_map.get(surface_name, ("#ddd", "GROUND"))

            incline_height = min(math.tan(math.radians(angle)) * CANVAS['width'], 350)

            if bg_image:
                bg_id = self.canvas.create_image(0, 0, anchor='nw', image=bg_image)
                try:
                    self.canvas.tag_lower(bg_id)
                except Exception:
                    pass
                self._current_bg = bg_image
                
            self.canvas.create_polygon(0, 450, CANVAS['width'], 450, CANVAS['width'], 450 - incline_height,
                                       fill=surf_color, outline="black", width=2)

            self.canvas.create_text(700, 420, text=f"⛰️ θ={angle:.1f}°", fill="black", 
                                    font=("Consolas", 11, "bold"))
            obj_y = 450 - (math.tan(math.radians(angle)) * 100) - 50
            self.draw_object(50, obj_y, shape, "#73ff61")
            self.draw_force_vectors(params)

    def draw_object(self, x, y, shape, color):
        """Draw the object on canvas"""
        if shape == "Box":
            self.object = self.canvas.create_rectangle(x, y, x + 50, y + 50, fill=color, 
                                                        outline="black", width=2)
        elif shape == "Cylinder":
            rect = self.canvas.create_rectangle(x, y + 10, x + 50, y + 50, fill=color, 
                                                outline="black", width=2)
            oval_top = self.canvas.create_oval(x, y, x + 50, y + 20, fill=color, 
                                               outline="black", width=2)
            oval_bottom = self.canvas.create_oval(x, y + 40, x + 50, y + 60, fill=color, 
                                                  outline="black", width=2)
            self.object = [oval_bottom, rect, oval_top]
        elif shape == "Sphere":
            radius = 25
            cx, cy = x + radius, y + 25
            self.object = self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius,
                                                  fill=color, outline="black", width=2)

    def draw_force_vectors(self, params):
        """Draw force vectors for inclined plane"""
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
        self.canvas.create_text(x_center + 30, y_center + length, text="Fg", fill="green", 
                                font=("Consolas", 9, "bold"))

        fn_dx = -length * math.sin(angle_rad)
        fn_dy = -length * math.cos(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + fn_dx, y_center + fn_dy,
                                 arrow=tk.LAST, fill="orange", width=3)
        self.canvas.create_text(x_center + fn_dx - 15, y_center + fn_dy, text="Fn", fill="orange", 
                                font=("Consolas", 9, "bold"))

        f_dx = length * math.cos(angle_rad)
        f_dy = -length * math.sin(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + f_dx, y_center + f_dy,
                                 arrow=tk.LAST, fill=COLORS['accent_cyan'], width=3)
        self.canvas.create_text(x_center + f_dx + 20, y_center + f_dy, text="F", 
                                fill=COLORS['accent_cyan'], font=("Consolas", 9, "bold"))

    def animate_motion(self, results):
        """Animate the object motion and update graph in real-time"""
        params = results['params']
        scenario = params['scenario']
        distance = params['d']
        angle = params['angle']
        push_mode = params['push_mode']
        
        net_force = results['net_work'] / distance if distance > 0 else 0
        
        steps = int(distance * 15)
        speed_factor = 1.0 / self.anim_speed.get()
        
        accumulated_distance = 0.0
        distance_per_step = distance / steps if steps > 0 else 0
        
        for step in range(steps):
            if not self.is_animating:
                break
                
            if push_mode == "Constant Force":
                move_val = 4
            elif push_mode == "Sudden Push":
                move_val = 20 if step < 5 else 0.5
            elif push_mode == "Increasing Force":
                move_val = 2 + (step / steps) * 6
            
            accumulated_distance += distance_per_step
            
            current_work = net_force * accumulated_distance
            current_ke = current_work
            
            self.update_graph(accumulated_distance, current_work, current_ke)
            
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
        self.stop_timer()

        self.is_animating = False
        self.run_btn.config(state="normal")
        self.feedback.config(text="✅ Simulation Complete!", fg=COLORS['accent_green'])

    def _move_object(self, dx, dy):
        """Move the object on canvas"""
        if isinstance(self.object, list):
            for part in self.object:
                self.canvas.move(part, dx, dy)
        else:
            self.canvas.move(self.object, dx, dy)

    def draw_ke_indicator(self):
        """Draw kinetic energy indicator on canvas"""
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
        """Launch the physics quiz"""
        ForceQuestQuiz(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    app = ForceQuestApp(root)
    root.mainloop()
