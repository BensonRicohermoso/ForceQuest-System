"""
Timer utility for tracking simulation time
"""
import time


class SimulationTimer:
    """Manages simulation timing

    Backwards-compatible constructor:
    - `SimulationTimer(update_callback)` where `update_callback(text)` updates the UI
    - `SimulationTimer(root, label_or_callback)` where `label_or_callback` may
      be a `tk.Label` or a callable; `start()` then requires no arguments.
    """

    def __init__(self, *args):
        self.is_running = False
        self.start_time = 0.0
        self.timer_id = None
        self.root = None

        # Handle constructor overloads
        if len(args) == 1:
            # old style: SimulationTimer(update_callback)
            self.update_callback = args[0]
        elif len(args) == 2:
            # new style used by app.py: SimulationTimer(root, label_or_callback)
            self.root = args[0]
            label_or_callback = args[1]
            if callable(label_or_callback):
                self.update_callback = label_or_callback
            else:
                # assume it's a tk.Label-like object with .config
                self.update_callback = lambda text: label_or_callback.config(text=text)
        else:
            raise TypeError("SimulationTimer expects 1 or 2 positional arguments")

    def start(self):
        """Start the timer. If `root` was not provided at init, caller must set it before.
        """
        if not self.is_running:
            if self.root is None:
                raise RuntimeError("SimulationTimer.start() missing root; provide root in constructor")
            self.start_time = time.time()
            self.is_running = True
            self._tick()
    
    def stop(self):
        """Stop the timer"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.is_running = False
    
    def reset(self):
        """Reset timer to 00:00.00"""
        self.stop()
        if self.update_callback:
            self.update_callback("00:00.00")
    
    def _tick(self):
        """Update timer display"""
        if not self.is_running:
            return
        
        elapsed_time = time.time() - self.start_time
        
        # Format time as MM:SS.cc
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        hundredths = int((elapsed_time % 1) * 100)
        
        time_str = f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
        
        if self.update_callback:
            self.update_callback(time_str)
        
        # Schedule next update
        self.timer_id = self.root.after(50, self._tick)