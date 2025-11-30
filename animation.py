import math
import time
import threading
from config import ANIMATION_DELAY


class AnimationController:
    """Handles animation of physics simulations

    Backwards-compatible API:
    - `AnimationController(canvas_component, update_callback, toggle_run_callback, on_complete)`
      is the interface used by `app.py`.
    - Internally the controller still uses `start_animation`/`stop_animation`.
    """

    def __init__(self, canvas_component, update_callback=None, toggle_run_callback=None, on_complete_callback=None):
        # canvas_component may be a SimulationCanvas instance or a tk.Canvas
        self.canvas_component = canvas_component
        self.canvas = getattr(canvas_component, 'canvas', canvas_component)
        self.update_callback = update_callback
        self.toggle_run_callback = toggle_run_callback
        self.on_complete_callback = on_complete_callback
        self.is_animating = False
        self.animation_thread = None
        self.object_refs = None

    def start_animation(self, results, anim_speed, object_refs):
        """Start animation in separate thread"""
        if self.is_animating:
            return False

        self.object_refs = object_refs
        self.is_animating = True
        self.animation_thread = threading.Thread(
            target=self._animate_motion,
            args=(results, anim_speed)
        )
        self.animation_thread.start()
        return True

    # Compatibility wrapper expected by app.py
    def start(self, results, anim_speed):
        # Determine object refs from canvas component
        object_refs = getattr(self.canvas_component, 'object', None)
        # Toggle run button off if callback provided
        if self.toggle_run_callback:
            try:
                self.toggle_run_callback(False)
            except Exception:
                pass
        # Start the internal animation
        started = self.start_animation(results, anim_speed, object_refs)
        return started

    def stop_animation(self):
        """Stop ongoing animation"""
        self.is_animating = False

    # Compatibility wrapper expected by app.py
    def stop(self):
        self.stop_animation()

    def _animate_motion(self, results, anim_speed):
        """Animation loop running in separate thread"""
        params = results['params']
        scenario = params['scenario']
        distance = params['d']
        angle = params['angle']
        push_mode = params['push_mode']
        force_angle = params['force_angle']

        steps = int(distance * 15)
        speed_factor = 1.0 / anim_speed

        for step in range(steps):
            if not self.is_animating:
                break

            # Calculate movement based on push mode
            move_val = self._calculate_movement(push_mode, step, steps)

            # Calculate displacement based on scenario
            dx, dy = self._calculate_displacement(scenario, move_val, angle, force_angle)

            # Move object on canvas
            self._move_object(dx, dy)

            try:
                self.canvas.update()
            except Exception:
                pass
            time.sleep(ANIMATION_DELAY * speed_factor)

        # Animation complete
        self.is_animating = False
        # Re-enable run button
        if self.toggle_run_callback:
            try:
                self.toggle_run_callback(True)
            except Exception:
                pass

        if self.on_complete_callback:
            try:
                self.on_complete_callback(results)
            except Exception:
                pass

    def _calculate_movement(self, push_mode, step, total_steps):
        """Calculate movement value based on push mode"""
        if push_mode == "Constant Force":
            return 4
        elif push_mode == "Sudden Push":
            return 20 if step < 5 else 0.5
        elif push_mode == "Increasing Force":
            return 2 + (step / total_steps) * 6
        return 4

    def _calculate_displacement(self, scenario, move_val, angle, force_angle):
        """Calculate dx and dy based on scenario"""
        if scenario == "Lifting Object":
            return 0, -move_val
        elif scenario == "Inclined Plane":
            dx = move_val * math.cos(math.radians(angle))
            dy = -move_val * math.sin(math.radians(angle))
            return dx, dy
        else:  # Pushing Object
            dx = move_val * math.cos(math.radians(force_angle))
            dy = -move_val * math.sin(math.radians(force_angle))
            return dx, dy

    def _move_object(self, dx, dy):
        """Move object on canvas"""
        if isinstance(self.object_refs, list):
            for part in self.object_refs:
                try:
                    self.canvas.move(part, dx, dy)
                except Exception:
                    pass
        else:
            try:
                self.canvas.move(self.object_refs, dx, dy)
            except Exception:
                pass