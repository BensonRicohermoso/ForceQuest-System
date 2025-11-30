"""
ForceQuest - Physics Simulation Application
Entry point for the application
"""
import tkinter as tk
from app import ForceQuestApp

def main():
    root = tk.Tk()
    app = ForceQuestApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()