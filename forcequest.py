import tkinter as tk
from tkinter import ttk, messagebox
import math
import time
import threading

# Optional scientific plotting libs — check at runtime and show helpful error
try:
	import numpy as np
except Exception:
	np = None

try:
	import matplotlib.pyplot as plt
except Exception:
	plt = None


class ForceQuestApp:
	def __init__(self, root):
		self.root = root
		self.root.title("⚙️ ForceQuest — Physics Adventure Mode")
		self.root.geometry("1300x850")  # Adjusted height for more widgets
		self.root.configure(bg="#1e1e2f")
		self.setup_ui()

	def setup_ui(self):
		title = tk.Label(self.root, text="FORCEQUEST", fg="#00e6e6",
						 bg="#1e1e2f", font=("Consolas", 28, "bold"))
		title.pack(pady=10)

		subtitle = tk.Label(self.root, text="The Fun Physics Simulator — Work, Energy & Power",
							fg="#bbb", bg="#1e1e2f", font=("Segoe UI", 12, "italic"))
		subtitle.pack()

		frame = tk.Frame(self.root, bg="#1e1e2f")
		frame.pack(pady=20)

		# Left input panel
		left = tk.Frame(frame, bg="#252540", bd=2, relief="ridge")
		left.grid(row=0, column=0, padx=15, sticky="n")

		# Existing Inputs
		tk.Label(left, text="Scenario:", bg="#252540", fg="white").grid(row=0, column=0, sticky="w", pady=5)
		self.scenario = ttk.Combobox(left, values=["Pushing Object", "Lifting Object", "Inclined Plane"], state="readonly")
		self.scenario.grid(row=0, column=1, pady=5)
		self.scenario.current(0)

		inputs = [("Force (N)", "force"), ("Distance (m)", "distance"),
				  ("Mass (kg)", "mass"), ("Angle (°)", "angle"),
				  ("Friction μ", "mu")]
		self.entries = {}
		for i, (label, key) in enumerate(inputs, start=1):
			tk.Label(left, text=label, bg="#252540", fg="white").grid(row=i, column=0, sticky="w", pady=5)
			e = tk.Entry(left, width=10)
			e.grid(row=i, column=1, pady=5)
			self.entries[key] = e

		# New Inputs for added features
		row_base = len(inputs) + 1

		# Surface Material Selector
		tk.Label(left, text="Surface Material:", bg="#252540", fg="white").grid(row=row_base, column=0, sticky="w", pady=5)
		self.surface_material = ttk.Combobox(left,
											 values=["Ice", "Tile", "Wood", "Concrete", "Sand"], state="readonly")
		self.surface_material.grid(row=row_base, column=1, pady=5)
		self.surface_material.current(2)  # Default Wood

		# Object Shape Options
		tk.Label(left, text="Object Shape:", bg="#252540", fg="white").grid(row=row_base + 1, column=0, sticky="w", pady=5)
		self.object_shape = ttk.Combobox(left, values=["Box", "Cylinder", "Sphere"], state="readonly")
		self.object_shape.grid(row=row_base + 1, column=1, pady=5)
		self.object_shape.current(0)  # Default Box

		# Force Application Angle
		tk.Label(left, text="Force Angle:", bg="#252540", fg="white").grid(row=row_base + 2, column=0, sticky="w", pady=5)
		self.force_angle_mode = ttk.Combobox(left, values=["Horizontal", "Upward", "Downward"], state="readonly")
		self.force_angle_mode.grid(row=row_base + 2, column=1, pady=5)
		self.force_angle_mode.current(0)  # Default Horizontal

		# Push Mode
		tk.Label(left, text="Push Mode:", bg="#252540", fg="white").grid(row=row_base + 3, column=0, sticky="w", pady=5)
		self.push_mode = ttk.Combobox(left, values=["Constant Force", "Sudden Push", "Increasing Force"], state="readonly")
		self.push_mode.grid(row=row_base + 3, column=1, pady=5)
		self.push_mode.current(0)  # Default Constant Force

		# Buttons
		tk.Button(left, text="▶ Run Simulation", bg="#00e6e6", fg="black", font=("Segoe UI", 10, "bold"),
				  command=self.run_simulation).grid(row=row_base + 4, column=0, columnspan=2, pady=10)
		tk.Button(left, text="📊 Show Energy Graph", bg="#98c379", fg="black",
				  font=("Segoe UI", 10, "bold"), command=self.show_plot).grid(row=row_base + 5, column=0, columnspan=2, pady=5)

		# Center canvas for animation
		center = tk.Frame(frame, bg="#1e1e2f")
		center.grid(row=0, column=1, padx=20)

		self.canvas = tk.Canvas(center, width=600, height=400, bg="white", highlightthickness=2)
		self.canvas.pack()

		self.object = self.canvas.create_rectangle(50, 330, 100, 380, fill="#ff6f61")

		self.feedback = tk.Label(center, text="", bg="#1e1e2f", fg="#aaffaa", font=("Consolas", 12, "bold"))
		self.feedback.pack(pady=10)

		# Label for Change in Kinetic Energy
		self.delta_ke_label = tk.Label(center, text="", bg="#1e1e2f", fg="#ffaa00", font=("Consolas", 12, "bold"))
		self.delta_ke_label.pack(pady=5)

		self.solution_box = tk.Text(center, width=80, height=11, bg="#111", fg="#98c379",
								   font=("Consolas", 11), wrap="word")
		self.solution_box.pack(pady=10)

		# Instruction side
		right = tk.Frame(frame, bg="#252540", bd=2, relief="ridge")
		right.grid(row=0, column=2, padx=15, sticky="n")
		tk.Label(right, text="🧭 HOW TO PLAY", bg="#252540", fg="#00e6e6", font=("Segoe UI", 12, "bold")).pack(pady=5)
		tk.Label(right, text=(
			"1️ Choose scenario.\n"
			"2️ Enter known values.\n"
			"3️ Leave one blank to auto-calc.\n"
			"4️ Select Surface Material, Object Shape, Force Angle, and Push Mode.\n"
			"5️ Click ▶ to simulate.\n"
			"💡 Watch the object move or stay still depending on your force!\n"
			"\nThemes & Effects:\n"
			"• Surface influences friction (μ).\n"
			"• Object shape affects sliding vs rolling resistance.\n"
			"• Force angle changes normal force → friction.\n"
			"• Push mode affects animation force application.\n"
			"\nExamples surface μ:\n"
			"Ice=0.1, Tile=0.3, Wood=0.5, Concrete=0.7, Sand=0.9\n"
			"\nObject shapes:\n"
			"Box=sliding, Cylinder=rolling, Sphere=very low resistance\n"
			"\nForce Angles:\n"
			"Horizontal, Upward, Downward\n"
			"\nPush Modes:\n"
			"Constant, Sudden, Increasing"
		), bg="#252540", fg="white", justify="left", wraplength=280).pack(padx=10, pady=10)

	def run_simulation(self):
		try:
			F = float(self.entries["force"].get()) if self.entries["force"].get() else None
			d = float(self.entries["distance"].get()) if self.entries["distance"].get() else None
			m = float(self.entries["mass"].get()) if self.entries["mass"].get() else None
			angle = float(self.entries["angle"].get()) if self.entries["angle"].get() else 0
		except ValueError:
			messagebox.showerror("Input Error", "Enter valid numbers!")
			return

		if d is None:
			messagebox.showerror("Input Error", "Distance is required for simulation!")
			return

		g = 9.81
		scenario = self.scenario.get()

		surface_mu_map = {
			"Ice": 0.1,
			"Tile": 0.3,
			"Wood": 0.5,
			"Concrete": 0.7,
			"Sand": 0.9,
		}
		selected_surface = self.surface_material.get()
		base_mu = surface_mu_map.get(selected_surface, 0.5)

		shape_friction_factor = {
			"Box": 1.0,
			"Cylinder": 0.15,
			"Sphere": 0.05,
		}
		selected_shape = self.object_shape.get()
		mu = base_mu * shape_friction_factor.get(selected_shape, 1.0)

		force_angle_mode = self.force_angle_mode.get()
		force_angle_degrees = 0
		if force_angle_mode == "Horizontal":
			force_angle_degrees = 0
		elif force_angle_mode == "Upward":
			force_angle_degrees = 30
		elif force_angle_mode == "Downward":
			force_angle_degrees = -30

		solution = ""

		if m is None:
			if scenario == "Lifting Object" and F is not None:
				m = F / g
				solution += f"Mass auto-calculated: m = F / g = {m:.2f} kg\n\n"

			elif scenario == "Inclined Plane" and F is not None:
				sin_theta = math.sin(math.radians(angle))
				if sin_theta == 0:
					messagebox.showerror("Input Error", "Inclined angle cannot be 0 for mass calculation.")
					return
				m = F / (g * sin_theta)
				solution += f"Mass auto-calculated: m = F / (g × sin θ) = {m:.2f} kg\n\n"

			elif scenario == "Pushing Object" and F is not None and mu != 0:
				m = F / (mu * g)
				solution += f"Mass auto-calculated: m = F / (μ × g) = {m:.2f} kg\n\n"

			else:
				messagebox.showerror("Input Error", "Mass is required!")
				return

		F_applied = F if F is not None else 0
		weight_force = m * g

		Fn = weight_force - F_applied * math.sin(math.radians(force_angle_degrees))
		Fn = max(Fn, 0)

		F_friction = mu * Fn

		if scenario == "Lifting Object":
			F_req = m * g
			formula = "F_required = m × g"
		elif scenario == "Inclined Plane":
			F_req = m * g * math.sin(math.radians(angle))
			formula = "F_required = m × g × sin(θ)"
		else:
			F_req = F_friction
			formula = "F_required = μ × Normal Force"

		if F is None:
			F = F_req
			solution += f"Force auto-calculated using formula:\n{formula}\nF = {F:.2f} N\n\n"

		if F < F_req:
			self.feedback.config(text="⚠️ Not enough force! Object won’t move.", fg="#ff8080")
			self.delta_ke_label.config(text="")
			self.solution_box.delete(1.0, tk.END)
			self.solution_box.insert(tk.END,
									solution + f"Required force is {F_req:.2f} N but applied force is {F:.2f} N.\nNo movement occurs.")
			return

		net_work = (F - F_req) * d
		ke = net_work
		v = math.sqrt(2 * abs(ke) / m) if m and ke > 0 else 0
		power_interval = 3
		p = net_work / power_interval if net_work > 0 else 0

		self.feedback.config(text=f"✅ Net Work={net_work:.2f}J | KE={ke:.2f}J | Power={p:.2f}W", fg="#00e6e6")
		self.delta_ke_label.config(text=f"🔥 Change in Kinetic Energy: ΔKE = {ke:.2f} J", fg="#ffaa00")

		solution += (
			f"Force required calculation:\n{formula}\n"
			f"Step 1: Net Work = (F - F_req) × d = ({F:.2f} - {F_req:.2f}) × {d:.2f} = {net_work:.2f} J\n"
			f"Step 2: ΔKE = Net Work = {ke:.2f} J (Work-Energy Theorem)\n"
			f"Step 3: Velocity v = √(2 × ΔKE / m) = √(2 × {ke:.2f} / {m:.2f}) = {v:.2f} m/s\n"
			f"Step 4: Power = Net Work / time = {net_work:.2f} / {power_interval} = {p:.2f} W\n"
			f"\nNormal Force (Fn) adjusted for force angle: {Fn:.2f} N\n"
			f"Friction coefficient (μ) adjusted for surface and shape: {mu:.2f}\n"
		)
		self.solution_box.delete(1.0, tk.END)
		self.solution_box.insert(tk.END, solution)

		self.update_background(mu, scenario, angle)
		push_mode = self.push_mode.get()
		threading.Thread(target=self.animate_motion,
						 args=(scenario, d, angle, force_angle_degrees, push_mode),
						 daemon=True).start()

	def update_background(self, mu, scenario, angle):
		self.canvas.delete("all")

		base_x = 100
		base_y = 350

		if scenario == "Pushing Object":
			if mu <= 0.15:
				color = "#b3e5fc"
				surface = "❄️ ICE"
			elif mu <= 0.35:
				color = "#f0f0f0"
				surface = "🏠 TILE"
			elif mu <= 0.6:
				color = "#deb887"
				surface = "🪵 WOOD"
			elif mu <= 0.8:
				color = "#a9a9a9"
				surface = "🏗️ CONCRETE"
			else:
				color = "#e69f00"
				surface = "🌋 SAND"

			self.canvas.create_rectangle(0, 350, 600, 400, fill=color)
			self.canvas.create_text(500, 20, text=f"Surface: {surface}", fill="black", font=("Consolas", 12, "bold"))

			shape = self.object_shape.get()

			if shape == "Box":
				self.object = self.canvas.create_rectangle(base_x, 300, base_x + 50, 350, fill="#ff6f61")
			elif shape == "Cylinder":
				self.object_rect = self.canvas.create_rectangle(base_x, 310, base_x + 50, 350, fill="#ff6f61")
				self.object_oval_top = self.canvas.create_oval(base_x, 300, base_x + 50, 320, fill="#ff6f61")
				self.object_oval_bottom = self.canvas.create_oval(base_x, 340, base_x + 50, 360, fill="#ff6f61")
				self.object = [self.object_rect, self.object_oval_top, self.object_oval_bottom]
			elif shape == "Sphere":
				radius = 25
				cx = base_x + radius
				cy = 325
				self.object = self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#ff6f61")

		elif scenario == "Lifting Object":
			self.canvas.create_rectangle(0, 350, 600, 400, fill="#9ecae1")
			self.canvas.create_text(500, 20, text="🏗️ Lifting Crane", fill="black", font=("Consolas", 12, "bold"))
			self.object = self.canvas.create_rectangle(280, 300, 330, 350, fill="#f4a261")

		elif scenario == "Inclined Plane":
			incline_height = math.tan(math.radians(angle)) * 600
			self.canvas.create_polygon(0, 400, 600, 400, 600, 400 - incline_height,
									   fill="#c7e9b4")
			self.canvas.create_text(500, 20, text=f"⛰️ Incline θ={angle}°", fill="black", font=("Consolas", 12, "bold"))
			obj_y = 400 - (math.tan(math.radians(angle)) * 100) - 50

			base_x = 100
			shape = self.object_shape.get()
			if shape == "Box":
				self.object = self.canvas.create_rectangle(base_x, obj_y, base_x + 50, obj_y + 50, fill="#d95f02")
			elif shape == "Cylinder":
				rect = self.canvas.create_rectangle(base_x, obj_y + 10, base_x + 50, obj_y + 50, fill="#d95f02")
				oval_top = self.canvas.create_oval(base_x, obj_y, base_x + 50, obj_y + 30, fill="#d95f02")
				oval_bottom = self.canvas.create_oval(base_x, obj_y + 30, base_x + 50, obj_y + 60, fill="#d95f02")
				self.object = [rect, oval_top, oval_bottom]
			elif shape == "Sphere":
				radius = 25
				cx = base_x + radius
				cy = obj_y + 25
				self.object = self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill="#d95f02")

			self.draw_force_vectors(scenario, angle)

		else:
			self.canvas.delete("all")

	def draw_force_vectors(self, scenario, angle):
		if scenario != "Inclined Plane":
			return

		coords = None
		if isinstance(self.object, list):
			coords = self.canvas.coords(self.object[0])
		else:
			coords = self.canvas.coords(self.object)

		x_center = (coords[0] + coords[2]) / 2
		y_bottom = coords[3]

		length_factor = 60

		# Gravity (Fg)
		Fg_x_end = x_center
		Fg_y_end = y_bottom + length_factor
		self.canvas.create_line(x_center, y_bottom, Fg_x_end, Fg_y_end, arrow=tk.LAST, fill="green", width=3)
		self.canvas.create_text(Fg_x_end + 10, Fg_y_end, text="Gravity (Fg)", fill="green", font=("Consolas", 10, "bold"), anchor="w")

		incline_angle = math.radians(angle)

		# Normal Force (Fn)
		Fn_dx = length_factor * math.cos(incline_angle)
		Fn_dy = -length_factor * math.sin(incline_angle)
		Fn_x_end = x_center + Fn_dx
		Fn_y_end = y_bottom + Fn_dy
		self.canvas.create_line(x_center, y_bottom, Fn_x_end, Fn_y_end, arrow=tk.LAST, fill="orange", width=3)
		label_x = Fn_x_end + 10 * math.cos(incline_angle)
		label_y = Fn_y_end - 10 * math.sin(incline_angle)
		self.canvas.create_text(label_x, label_y, text="Normal Force (Fn)", fill="orange", font=("Consolas", 10, "bold"), anchor="w")

		# Net Force (Fnet)
		Fnet_dx = length_factor * math.cos(incline_angle)
		Fnet_dy = length_factor * math.sin(incline_angle)
		Fnet_x_end = x_center + Fnet_dx
		Fnet_y_end = y_bottom + Fnet_dy
		self.canvas.create_line(x_center, y_bottom, Fnet_x_end, Fnet_y_end, arrow=tk.LAST, fill="#00e6e6", width=3)
		label_x = Fnet_x_end + 10 * math.cos(incline_angle)
		label_y = Fnet_y_end + 10 * math.sin(incline_angle)
		self.canvas.create_text(label_x, label_y, text="Net Force (Fnet)", fill="#00e6e6", font=("Consolas", 10, "bold"), anchor="w")

	def animate_motion(self, scenario, distance, angle, force_angle_degrees, push_mode):
		steps = max(1, int(distance * 10))
		for step in range(steps):
			move_val = 0
			if push_mode == "Constant Force":
				move_val = 5
			elif push_mode == "Sudden Push":
				move_val = 15 if step < 5 else 0
			elif push_mode == "Increasing Force":
				move_val = 5 * (step / steps)

			if scenario == "Lifting Object":
				self._move_object(0, -move_val)
			elif scenario == "Inclined Plane":
				dx = move_val * math.cos(math.radians(angle))
				dy = -move_val * math.sin(math.radians(angle))
				self._move_object(dx, dy)
			else:
				dx = move_val * math.cos(math.radians(force_angle_degrees))
				dy = -move_val * math.sin(math.radians(force_angle_degrees))
				self._move_object(dx, dy)

			self.canvas.update()
			time.sleep(0.03)

		self.draw_ke_line()

	def _move_object(self, dx, dy):
		if isinstance(self.object, list):
			for part in self.object:
				self.canvas.move(part, dx, dy)
		else:
			self.canvas.move(self.object, dx, dy)

	def draw_ke_line(self):
		self.canvas.delete("ke_line")
		self.canvas.delete("ke_text")
		coords = None
		if isinstance(self.object, list):
			xs = []
			ys = []
			for part in self.object:
				c = self.canvas.coords(part)
				xs += c[::2]
				ys += c[1::2]
			x1, x2 = min(xs), max(xs)
			y1, y2 = min(ys), max(ys)
			coords = [x1, y1, x2, y2]
		else:
			coords = self.canvas.coords(self.object)

		x1 = coords[0]
		x2 = coords[2]
		y = coords[3] + 20

		self.canvas.create_line(x1, y, x2, y, fill="#ffaa00", width=3, tags="ke_line")
		ke_text = self.delta_ke_label.cget("text")
		if isinstance(ke_text, str) and ke_text.startswith("🔥 Change in Kinetic Energy: ΔKE = "):
			ke_val = ke_text.split("=")[1].strip().split(" ")[0]
		else:
			ke_val = "0.00"

		self.canvas.create_text((x1 + x2) / 2, y + 15, text=f"ΔKE = {ke_val} J", fill="#ffaa00", font=("Consolas", 12, "bold"), tags="ke_text")

	def show_plot(self):
		try:
			d = float(self.entries["distance"].get())
			F = float(self.entries["force"].get())
			m = float(self.entries["mass"].get())
			angle = float(self.entries["angle"].get()) if self.entries["angle"].get() else 0
			surface_mu_map = {
				"Ice": 0.1,
				"Tile": 0.3,
				"Wood": 0.5,
				"Concrete": 0.7,
				"Sand": 0.9,
			}
			selected_surface = self.surface_material.get()
			base_mu = surface_mu_map.get(selected_surface, 0.5)
			shape_friction_factor = {
				"Box": 1.0,
				"Cylinder": 0.15,
				"Sphere": 0.05,
			}
			selected_shape = self.object_shape.get()
			mu = base_mu * shape_friction_factor.get(selected_shape, 1.0)
			scenario = self.scenario.get()
		except Exception:
			messagebox.showerror("Error", "Enter all required values (Force, Distance, Mass) first!")
			return

		g = 9.81
		force_angle_mode = self.force_angle_mode.get()
		force_angle_degrees = 0
		if force_angle_mode == "Horizontal":
			force_angle_degrees = 0
		elif force_angle_mode == "Upward":
			force_angle_degrees = 30
		elif force_angle_mode == "Downward":
			force_angle_degrees = -30

		weight_force = m * g
		F_applied = F

		Fn = weight_force - F_applied * math.sin(math.radians(force_angle_degrees))
		Fn = max(Fn, 0)
		F_friction = mu * Fn

		if scenario == "Lifting Object":
			F_req = m * g
		elif scenario == "Inclined Plane":
			F_req = m * g * math.sin(math.radians(angle))
		else:
			F_req = F_friction

		x = np.linspace(0, d, 50)
		net_work = (F - F_req) * x
		plt.plot(x, net_work, color="#00e6e6", linewidth=2)
		plt.title("Net Work / ΔKE vs Distance")
		plt.xlabel("Distance (m)")
		plt.ylabel("Net Work / ΔKE (J)")
		plt.grid(True)
		plt.show()


if __name__ == "__main__":
	root = tk.Tk()
	app = ForceQuestApp(root)
	root.mainloop()
