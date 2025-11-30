"""
Simulation Canvas Component
Handles all canvas drawing operations for the simulation
"""
import tkinter as tk
import math
from config import CANVAS, SURFACE_COLORS, OBJECT_COLORS

class SimulationCanvas:
    """Manages the simulation canvas and drawing operations"""
    
    def __init__(self, parent):
        self.canvas = tk.Canvas(parent, width=CANVAS['width'], height=CANVAS['height'],
                                bg="white", highlightthickness=2, highlightbackground="#00e6e6")
        self.object = None
    
    def get_widget(self):
        """Return the canvas widget"""
        return self.canvas
    
    def reset(self):
        """Clear canvas and draw ground"""
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'],
                                      CANVAS['ground_y'] + CANVAS['ground_height'],
                                      fill="#ddd", outline="")
        self.canvas.create_text(350, 425, text="Ground Level", fill="#666", font=("Consolas", 10))
        self.object = None
    
    def update_background(self, params):
        """Update canvas background based on scenario"""
        self.canvas.delete("all")
        scenario = params['scenario']
        angle = params['angle']
        mu = params['mu']
        shape = params['shape']
        
        if scenario == "Pushing Object":
            self._draw_pushing_background(mu, shape)
        elif scenario == "Lifting Object":
            self._draw_lifting_background(shape)
        elif scenario == "Inclined Plane":
            self._draw_incline_background(angle, shape)
    
    def _draw_pushing_background(self, mu, shape):
        """Draw background for pushing scenario"""
        # Determine surface type based on friction
        if mu <= 0.15:
            color, label = SURFACE_COLORS['Ice']
        elif mu <= 0.35:
            color, label = SURFACE_COLORS['Tile']
        elif mu <= 0.6:
            color, label = SURFACE_COLORS['Wood']
        elif mu <= 0.8:
            color, label = SURFACE_COLORS['Concrete']
        else:
            color, label = SURFACE_COLORS['Sand']
        
        self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'],
                                      CANVAS['ground_y'] + CANVAS['ground_height'],
                                      fill=color, outline="")
        self.canvas.create_text(600, 420, text=f"{label}", fill="black", font=("Consolas", 11, "bold"))
        self.draw_object(50, 350, shape, OBJECT_COLORS['Pushing Object'])
    
    def _draw_lifting_background(self, shape):
        """Draw background for lifting scenario"""
        self.canvas.create_rectangle(0, CANVAS['ground_y'], CANVAS['width'],
                                      CANVAS['ground_y'] + CANVAS['ground_height'],
                                      fill="#9ecae1", outline="")
        self.canvas.create_line(340, 50, 340, CANVAS['ground_y'], fill="#666", width=4)
        self.canvas.create_text(600, 420, text="🏗️ CRANE", fill="black", font=("Consolas", 11, "bold"))
        self.draw_object(315, 350, shape, OBJECT_COLORS['Lifting Object'])
    
    def _draw_incline_background(self, angle, shape):
        """Draw background for inclined plane scenario"""
        incline_height = min(math.tan(math.radians(angle)) * CANVAS['width'], 350)
        self.canvas.create_polygon(0, CANVAS['ground_y'] + CANVAS['ground_height'],
                                     CANVAS['width'], CANVAS['ground_y'] + CANVAS['ground_height'],
                                     CANVAS['width'], CANVAS['ground_y'] + CANVAS['ground_height'] - incline_height,
                                     fill="#c7e9b4", outline="black", width=2)
        self.canvas.create_text(600, 420, text=f"⛰️ θ={angle:.1f}°", fill="black", font=("Consolas", 11, "bold"))
        
        obj_y = (CANVAS['ground_y'] + CANVAS['ground_height']) - (math.tan(math.radians(angle)) * 100) - 50
        self.draw_object(50, obj_y, shape, OBJECT_COLORS['Inclined Plane'])
    
    def draw_object(self, x, y, shape, color):
        """Draw the object based on shape"""
        if shape == "Box":
            self.object = self.canvas.create_rectangle(x, y, x + 50, y + 50,
                                                        fill=color, outline="black", width=2)
        elif shape == "Cylinder":
            rect = self.canvas.create_rectangle(x, y + 10, x + 50, y + 50,
                                                 fill=color, outline="black", width=2)
            oval_top = self.canvas.create_oval(x, y, x + 50, y + 20,
                                                fill=color, outline="black", width=2)
            oval_bottom = self.canvas.create_oval(x, y + 40, x + 50, y + 60,
                                                   fill=color, outline="black", width=2)
            self.object = [oval_bottom, rect, oval_top]
        elif shape == "Sphere":
            radius = 25
            cx, cy = x + radius, y + 25
            self.object = self.canvas.create_oval(cx - radius, cy - radius,
                                                   cx + radius, cy + radius,
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
        
        # Gravity force (down)
        self.canvas.create_line(x_center, y_center, x_center, y_center + length,
                                 arrow=tk.LAST, fill="green", width=3)
        self.canvas.create_text(x_center + 30, y_center + length, text="Fg",
                                 fill="green", font=("Consolas", 9, "bold"))
        
        # Normal force (perpendicular to surface)
        fn_dx = -length * math.sin(angle_rad)
        fn_dy = -length * math.cos(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + fn_dx, y_center + fn_dy,
                                 arrow=tk.LAST, fill="orange", width=3)
        self.canvas.create_text(x_center + fn_dx - 15, y_center + fn_dy, text="Fn",
                                 fill="orange", font=("Consolas", 9, "bold"))
        
        # Applied force (parallel to surface)
        f_dx = length * math.cos(angle_rad)
        f_dy = -length * math.sin(angle_rad)
        self.canvas.create_line(x_center, y_center, x_center + f_dx, y_center + f_dy,
                                 arrow=tk.LAST, fill="#00e6e6", width=3)
        self.canvas.create_text(x_center + f_dx + 20, y_center + f_dy, text="F",
                                 fill="#00e6e6", font=("Consolas", 9, "bold"))
    
    def move_object(self, dx, dy):
        """Move the drawn object by dx, dy"""
        if isinstance(self.object, list):
            for part in self.object:
                self.canvas.move(part, dx, dy)
        else:
            self.canvas.move(self.object, dx, dy)
    
    def draw_ke_indicator(self, ke_text):
        """Draw kinetic energy indicator below object"""
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
        
        if "=" in ke_text:
            ke_val = ke_text.split("=")[1].strip().split()[0]
            self.canvas.create_text((x1 + x2) / 2, y + 15, text=f"ΔKE={ke_val}J",
                                     fill="#ffaa00", font=("Consolas", 11, "bold"), tags="ke_text")
    
    def update(self):
        """Update the canvas display"""
        self.canvas.update()