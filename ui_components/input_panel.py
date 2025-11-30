"""
Input Panel Component
Handles all user input controls in the left panel
"""
import tkinter as tk
from tkinter import ttk
from config import (COLORS, FONTS, SCENARIOS, SURFACE_MATERIALS,
                    OBJECT_SHAPES, FORCE_ANGLES, PUSH_MODES)

class InputPanel:
    """Manages input controls and parameter collection"""
    
    def __init__(self, parent):
        self.frame = tk.Frame(parent, bg=COLORS['bg_secondary'], bd=2, relief="ridge")
        self.entries = {}
        self.scenario = None
        self.surface_material = None
        self.object_shape = None
        self.force_angle_mode = None
        self.push_mode = None
        self.anim_speed = None
        
        self._setup_ui()
    
    def get_widget(self):
        """Return the panel frame"""
        return self.frame
    
    def _setup_ui(self):
        """Setup all input controls"""
        # Scenario selector
        tk.Label(self.frame, text="Scenario:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['label']).grid(
            row=0, column=0, sticky="w", pady=5, padx=5)
        self.scenario = ttk.Combobox(self.frame, values=SCENARIOS,
                                     state="readonly", width=18)
        self.scenario.grid(row=0, column=1, pady=5, padx=5)
        self.scenario.current(0)
        
        # Physics parameter inputs
        inputs = [
            ("Force (N)", "force"),
            ("Distance (m)", "distance"),
            ("Mass (kg)", "mass"),
            ("Angle (°)", "angle"),
            ("Friction μ", "mu")
        ]
        
        for i, (label, key) in enumerate(inputs, start=1):
            tk.Label(self.frame, text=label, bg=COLORS['bg_secondary'],
                     fg=COLORS['text_white'], font=FONTS['normal']).grid(
                row=i, column=0, sticky="w", pady=5, padx=5)
            e = tk.Entry(self.frame, width=15, font=FONTS['normal'])
            e.grid(row=i, column=1, pady=5, padx=5)
            self.entries[key] = e
        
        row_base = len(inputs) + 1
        
        # Surface material
        tk.Label(self.frame, text="Surface Material:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['normal']).grid(
            row=row_base, column=0, sticky="w", pady=5, padx=5)
        self.surface_material = ttk.Combobox(self.frame, width=18,
                                             values=SURFACE_MATERIALS, state="readonly")
        self.surface_material.grid(row=row_base, column=1, pady=5, padx=5)
        self.surface_material.current(2)
        
        # Object shape
        tk.Label(self.frame, text="Object Shape:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['normal']).grid(
            row=row_base + 1, column=0, sticky="w", pady=5, padx=5)
        self.object_shape = ttk.Combobox(self.frame, width=18,
                                         values=OBJECT_SHAPES, state="readonly")
        self.object_shape.grid(row=row_base + 1, column=1, pady=5, padx=5)
        self.object_shape.current(0)
        
        # Force angle
        tk.Label(self.frame, text="Force Angle:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['normal']).grid(
            row=row_base + 2, column=0, sticky="w", pady=5, padx=5)
        self.force_angle_mode = ttk.Combobox(self.frame, width=18,
                                             values=FORCE_ANGLES, state="readonly")
        self.force_angle_mode.grid(row=row_base + 2, column=1, pady=5, padx=5)
        self.force_angle_mode.current(0)
        
        # Push mode
        tk.Label(self.frame, text="Push Mode:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['normal']).grid(
            row=row_base + 3, column=0, sticky="w", pady=5, padx=5)
        self.push_mode = ttk.Combobox(self.frame, width=18,
                                      values=PUSH_MODES, state="readonly")
        self.push_mode.grid(row=row_base + 3, column=1, pady=5, padx=5)
        self.push_mode.current(0)
        
        # Animation speed
        tk.Label(self.frame, text="Animation Speed:", bg=COLORS['bg_secondary'],
                 fg=COLORS['text_white'], font=FONTS['normal']).grid(
            row=row_base + 4, column=0, sticky="w", pady=5, padx=5)
        self.anim_speed = ttk.Scale(self.frame, from_=0.5, to=3.0, orient="horizontal")
        self.anim_speed.set(1.0)
        self.anim_speed.grid(row=row_base + 4, column=1, pady=5, padx=5, sticky="ew")
    
    def get_params(self):
        """Collect and return all input parameters as a dictionary"""
        try:
            F = float(self.entries["force"].get()) if self.entries["force"].get() else None
            d = float(self.entries["distance"].get()) if self.entries["distance"].get() else None
            m = float(self.entries["mass"].get()) if self.entries["mass"].get() else None
            angle = float(self.entries["angle"].get()) if self.entries["angle"].get() else 0
            user_mu = float(self.entries["mu"].get()) if self.entries["mu"].get() else None
        except ValueError:
            return None
        
        return {
            'F': F,
            'd': d,
            'm': m,
            'angle': angle,
            'user_mu': user_mu,
            'scenario': self.scenario.get(),
            'surface': self.surface_material.get(),
            'shape': self.object_shape.get(),
            'force_angle_mode': self.force_angle_mode.get(),
            'push_mode': self.push_mode.get(),
            'anim_speed': self.anim_speed.get()
        }