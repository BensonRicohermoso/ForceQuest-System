"""
Plotting utilities for energy graphs
"""
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox


class GraphGenerator:
    """Generates matplotlib graphs for physics data"""
    
    @staticmethod
    def show_energy_graph(physics_results, params):
        """Display Work and Kinetic Energy vs Distance graph"""
        try:
            if not physics_results or not physics_results.get('moves'):
                messagebox.showerror("Error", "Run a successful simulation first!")
                return
            
            d = params['d']
            F_req = physics_results['F_req']
            F = params['F']
            
            # Calculate net force
            net_force = F - F_req
            
            # Generate data
            x = np.linspace(0, d, 50)
            work = net_force * x
            ke = work  # W_net = ΔKE
            
            # Create plot
            plt.figure(figsize=(10, 6))
            plt.plot(x, work, 'b-', linewidth=2, label='Net Work (W_net)')
            plt.plot(x, ke, 'r--', linewidth=2, label='Kinetic Energy (ΔKE)')
            plt.title('Energy vs Distance (Work-Energy Theorem)', 
                     fontsize=14, fontweight='bold')
            plt.xlabel('Distance (m)', fontsize=12)
            plt.ylabel('Energy (J)', fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not generate graph: {str(e)}")