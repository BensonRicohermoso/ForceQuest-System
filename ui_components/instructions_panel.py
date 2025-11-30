"""
Instructions Panel Component
Displays help and usage instructions
"""
import tkinter as tk
from config import COLORS, FONTS

class InstructionsPanel:
    """Manages the instructions/help panel"""
    
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=COLORS['bg_secondary'], bd=2, relief="ridge")
        self._setup_ui()
    
    def get_widget(self):
        """Return the panel frame"""
        return self.frame
    
    def _setup_ui(self):
        """Setup instructions display"""
        # Header
        tk.Label(self.frame, text="🧭 HOW TO PLAY", bg=COLORS['bg_secondary'],
                 fg=COLORS['accent_cyan'], font=('Segoe UI', 13, 'bold')).pack(pady=10)
        
        # Instructions text area
        instructions = tk.Text(self.frame, width=35, height=35,
                               bg=COLORS['bg_secondary'], fg=COLORS['text_white'],
                               font=FONTS['instruction'], wrap="word", bd=0)
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