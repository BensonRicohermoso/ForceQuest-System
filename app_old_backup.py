
import tkinter as tk
from tkinter import messagebox
from config import (WINDOW, COLORS, FONTS, SURFACE_FRICTION, SHAPE_FRICTION_FACTOR,
                    FORCE_ANGLE_MAP)
from physics_engine import PhysicsCalculator
from animation import AnimationController
from quiz import ForceQuestQuiz
from utils.timer import SimulationTimer
from utils.plotting import GraphGenerator
from ui_components.input_panel import InputPanel
from ui_components.simulation_canvas import SimulationCanvas
from ui_components.instructions_panel import InstructionsPanel

class ForceQuestApp:
    """Main application controller"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("⚙️ ForceQuest — Physics Adventure Mode")
        self.root.geometry(f"{WINDOW['width']}x{WINDOW['height']}")
        self.root.configure(bg=COLORS['bg_primary'])
        
        # Components
        self.input_panel = None
        self.canvas = None
        self.instructions_panel = None
        self.timer = None
        self.animator = None
        
        # State
        self.current_results = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Title
        title = tk.Label(self.root, text="FORCEQUEST", fg=COLORS['accent_cyan'],
                         bg=COLORS['bg_primary'], font=FONTS['title'])
        title.pack(pady=10)
        
        subtitle = tk.Label(self.root, text="The Fun Physics Simulator — Work, Energy & Power",
                            fg=COLORS['text_gray'], bg=COLORS['bg_primary'], font=FONTS['subtitle'])
        subtitle.pack()
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=COLORS['bg_primary'])
        main_frame.pack(pady=20, fill=tk.BOTH, expand=True)
        
        # === LEFT PANEL: Input Controls ===
        self.input_panel = InputPanel(main_frame)
        left_widget = self.input_panel.get_widget()
        left_widget.grid(row=0, column=0, padx=15, sticky="nsew")
        
        # Add buttons to left panel
        self._add_control_buttons(left_widget)
        
        # === CENTER PANEL: Canvas and Output ===
        center = tk.Frame(main_frame, bg=COLORS['bg_primary'])
        center.grid(row=0, column=1, padx=20, sticky="nsew")
        
        # Timer
        timer_frame = tk.Frame(center, bg=COLORS['bg_primary'])
        timer_frame.pack(fill='x', padx=10, pady=(0, 5))
        
        tk.Label(timer_frame, text="Sim Time:", bg=COLORS['bg_primary'],
                 fg=COLORS['accent_blue'], font=FONTS['timer']).pack(side=tk.LEFT)
        timer_label = tk.Label(timer_frame, text="00:00.00", bg=COLORS['bg_primary'],
                               fg=COLORS['accent_yellow'], font=FONTS['timer'])
        timer_label.pack(side=tk.LEFT, padx=(5, 0))
        
        self.timer = SimulationTimer(self.root, timer_label)
        
        # Canvas
        self.canvas = SimulationCanvas(center)
        self.canvas.get_widget().pack()
        self.canvas.reset()
        
        # Feedback labels
        self.feedback = tk.Label(center, text="⚡ Ready to simulate!", bg=COLORS['bg_primary'],
                                 fg="#aaffaa", font=FONTS['feedback'])
        self.feedback.pack(pady=5)
        
        self.delta_ke_label = tk.Label(center, text="", bg=COLORS['bg_primary'],
                                        fg=COLORS['accent_yellow'], font=FONTS['timer'])
        self.delta_ke_label.pack(pady=5)
        
        # Solution text box
        solution_frame = tk.Frame(center, bg=COLORS['bg_primary'])
        solution_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(solution_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.solution_box = tk.Text(solution_frame, width=85, height=20, bg="#111",
                                     fg=COLORS['accent_green'], font=FONTS['solution'],
                                     wrap="word", yscrollcommand=scrollbar.set)
        self.solution_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.solution_box.yview)
        self.solution_box.tag_configure("center", justify='center')
        
        # === RIGHT PANEL: Instructions ===
        self.instructions_panel = InstructionsPanel(main_frame)
        right_widget = self.instructions_panel.get_widget()
        right_widget.grid(row=0, column=2, padx=15, sticky="nsew")
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Initialize animator
        self.animator = AnimationController(
            self.canvas,
            self._update_feedback,
            self._toggle_run_button,
            self.timer.stop
        )
    
    def _add_control_buttons(self, parent):
        """Add control buttons to the input panel"""
        btn_frame = tk.Frame(parent, bg=COLORS['bg_secondary'])
        btn_frame.grid(row=20, column=0, columnspan=2, pady=10)
        
        self.run_btn = tk.Button(btn_frame, text="▶ Run Simulation",
                                  bg=COLORS['accent_cyan'], fg="black",
                                  font=FONTS['button'], command=self.run_simulation, width=20)
        self.run_btn.pack(pady=5)
        
        tk.Button(btn_frame, text="⏹ Stop", bg=COLORS['accent_red'], fg="white",
                  font=FONTS['button'], command=self.stop_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="📊 Show Energy Graph", bg=COLORS['accent_green'], fg="black",
                  font=FONTS['button'], command=self.show_plot, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="🔄 Reset", bg=COLORS['accent_blue'], fg="black",
                  font=FONTS['button'], command=self.reset_simulation, width=20).pack(pady=5)
        
        tk.Button(btn_frame, text="✅ Start Physics Quiz", bg=COLORS['accent_yellow'], fg="black",
                  font=FONTS['button'], command=self.start_quiz, width=20, height=5).pack(pady=5)
    
    def run_simulation(self):
        """Run the physics simulation"""
        if self.animator.is_animating:
            messagebox.showwarning("Busy", "Already running!")
            return
        
        # Get and validate parameters
        raw_params = self.input_panel.get_params()
        if raw_params is None:
            messagebox.showerror("Input Error", "Please enter valid numbers!")
            return
        
        params = self._process_params(raw_params)
        if params is None:
            return
        
        # Calculate physics
        results = PhysicsCalculator.calculate_physics(params)
        if not results:
            return
        
        self.current_results = results
        
        # Display solution
        self._display_solution(results)
        
        # Check if object moves
        if not results['moves']:
            self.feedback.config(text="⚠️ NOT MOVING - Insufficient Force!", fg=COLORS['accent_red'])
            self.delta_ke_label.config(text="")
            self.timer.reset()
            return
        
        # Start animation
        self.feedback.config(text="▶ Simulating Motion...", fg=COLORS['accent_cyan'])
        self.delta_ke_label.config(text=f"ΔKE (Net Work) = {results['ke_final']:.2f} J")
        
        self.canvas.update_background(params)
        self.canvas.draw_force_vectors(params)
        
        self.timer.start()
        self.animator.start(results, raw_params['anim_speed'])
        self.canvas.draw_ke_indicator(self.delta_ke_label.cget("text"))
    
    def stop_simulation(self):
        """Stop the running simulation"""
        self.animator.stop()
    
    def reset_simulation(self):
        """Reset the simulation to initial state"""
        self.stop_simulation()
        self.canvas.reset()
        self.solution_box.delete(1.0, tk.END)
        self.feedback.config(text="⚡ Ready!", fg="#aaffaa")
        self.delta_ke_label.config(text="")
        self.timer.reset()
        self.current_results = None
    
    def start_quiz(self):
        """Launch the physics quiz"""
        ForceQuestQuiz(self.root)
    
    def show_plot(self):
        """Show energy vs distance graph"""
        if self.current_results is None:
            params = self.input_panel.get_params()
            if params is None:
                messagebox.showerror("Input Error", "Please enter valid parameters!")
                return
            params = self._process_params(params)
            if params is None:
                return
            results = PhysicsCalculator.calculate_physics(params)
            if results:
                self.current_results = results
        
        if self.current_results:
            GraphGenerator.show_energy_plot(self.current_results['params'], self.current_results)
    
    def _process_params(self, raw_params):
        """Process and validate raw parameters"""
        d = raw_params['d']
        if d is None or d <= 0:
            messagebox.showerror("Input Error", "Distance must be positive!")
            return None
        
        # Calculate friction coefficient
        base_mu = SURFACE_FRICTION.get(raw_params['surface'], 0.5)
        shape_factor = SHAPE_FRICTION_FACTOR.get(raw_params['shape'], 1.0)
        mu = base_mu * shape_factor
        
        if raw_params['user_mu'] is not None:
            mu = raw_params['user_mu']
        
        # Get force angle
        force_angle = FORCE_ANGLE_MAP.get(raw_params['force_angle_mode'], 0)
        
        return {
            'F': raw_params['F'],
            'd': d,
            'm': raw_params['m'],
            'angle': raw_params['angle'],
            'mu': mu,
            'force_angle': force_angle,
            'scenario': raw_params['scenario'],
            'shape': raw_params['shape'],
            'surface': raw_params['surface'],
            'push_mode': raw_params['push_mode']
        }
    
    def _display_solution(self, results):
        """Display calculation results in solution box"""
        self.solution_box.delete(1.0, tk.END)
        
        full_output = (
            f"{'='*60}\n"
            f"PHYSICS CALCULATION\n"
            f"{'='*60}\n\n"
            f"{results['solution']}"
            f"{'='*60}\n"
        )
        
        self.solution_box.insert(tk.END, full_output)
        self.solution_box.tag_add("center", "1.0", tk.END)
    
    def _update_feedback(self, text, color):
        """Update feedback label"""
        self.feedback.config(text=text, fg=color)
    
    def _toggle_run_button(self, enabled):
        """Enable or disable the run button"""
        self.run_btn.config(state="normal" if enabled else "disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = ForceQuestApp(root)
    root.mainloop()
        