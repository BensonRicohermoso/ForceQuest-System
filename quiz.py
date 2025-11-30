"""
ForceQuest Quiz Module
Handles the interactive physics quiz feature
"""
import tkinter as tk
from tkinter import ttk, messagebox
import random
from data.quiz_questions import QUIZ_QUESTIONS
from config import COLORS, FONTS

class ForceQuestQuiz:
    """Interactive physics quiz window"""
    
    def __init__(self, master):
        self.master = master
        self.score = 0
        self.current_question = 0
        self.question_pool = QUIZ_QUESTIONS.copy()
        
        # Shuffle questions for randomization
        random.shuffle(self.question_pool)
        
        # Create the new window (Toplevel)
        self.quiz_window = tk.Toplevel(master)
        self.quiz_window.title("💡 ForceQuest Quiz Time!")
        self.quiz_window.geometry("800x600")
        self.quiz_window.configure(bg=COLORS['bg_primary'])
        self.quiz_window.grab_set()  # Forces user to interact with the quiz window
        
        self.style = ttk.Style()
        self.style.configure("Quiz.TButton", font=FONTS['button'], padding=10,
                             background="#3e82e5", foreground="black")
        
        self.setup_quiz_ui()
        self.load_question()
    
    def setup_quiz_ui(self):
        """Setup the quiz user interface"""
        # --- Header ---
        header_frame = tk.Frame(self.quiz_window, bg=COLORS['bg_primary'], pady=10)
        header_frame.pack(fill='x')
        
        tk.Label(header_frame, text="FORCEQUEST QUIZ", font=FONTS['header'],
                 bg=COLORS['bg_primary'], fg=COLORS['accent_cyan']).pack()
        
        self.score_label = tk.Label(header_frame, text="Score: 0", font=FONTS['button'],
                                     bg=COLORS['bg_primary'], fg=COLORS['accent_green'])
        self.score_label.pack()
        
        # --- Question Area ---
        question_frame = tk.Frame(self.quiz_window, bg=COLORS['bg_secondary'], pady=30, padx=20)
        question_frame.pack(pady=20, padx=20, fill='both', expand=True)
        
        self.question_label = tk.Label(question_frame, text="Question text goes here...",
                                        font=('Segoe UI', 16), bg=COLORS['bg_secondary'],
                                        fg=COLORS['text_white'], wraplength=700)
        self.question_label.pack(pady=10)
        
        # --- Choices Area ---
        self.choice_frame = tk.Frame(question_frame, bg=COLORS['bg_secondary'])
        self.choice_frame.pack(pady=20)
        
        self.selected_choice = tk.StringVar()
        self.choice_buttons = []
        
        # Create 4 choice buttons
        for i in range(4):
            btn = ttk.Button(self.choice_frame, text=f"Choice {i+1}", style="Quiz.TButton",
                             command=lambda i=i: self.check_answer(self.choice_buttons[i].cget("text")))
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, ipadx=50, ipady=10, sticky="ew")
            self.choice_buttons.append(btn)
        
        # Ensure grid columns can expand
        self.choice_frame.grid_columnconfigure(0, weight=1)
        self.choice_frame.grid_columnconfigure(1, weight=1)
    
    def load_question(self):
        """Load the current question into the UI"""
        if self.current_question >= len(self.question_pool):
            self.show_results()
            return
        
        q_data = self.question_pool[self.current_question]
        self.question_label.config(text=f"Q{self.current_question + 1}: {q_data['q']}")
        
        choices = q_data['choices']
        random.shuffle(choices)  # Shuffle choices for each question
        
        for i, choice in enumerate(choices):
            self.choice_buttons[i].config(text=choice, state='normal')
    
    def check_answer(self, user_answer):
        """Check if the user's answer is correct"""
        q_data = self.question_pool[self.current_question]
        correct_answer = q_data['ans']
        
        is_correct = (user_answer == correct_answer)
        
        # Configure styles for immediate feedback
        self.style.configure("Correct.TButton", background=COLORS['accent_green'], foreground="black")
        self.style.configure("Incorrect.TButton", background=COLORS['accent_red'], foreground="white")
        
        # Visually indicate correct/incorrect answer
        for btn in self.choice_buttons:
            if btn.cget("text") == correct_answer:
                btn.config(style="Correct.TButton")
            else:
                btn.config(style="Incorrect.TButton")
            btn.config(state='disabled')  # Disable buttons after selection
        
        # Scoring Logic
        if is_correct:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score} - Correct!")
        else:
            self.score_label.config(text=f"Score: {self.score} - Incorrect.")
        
        # Move to next question after a brief delay
        self.quiz_window.after(1000, self.next_question)
    
    def next_question(self):
        """Move to the next question"""
        # Reset button styles to default quiz style
        for btn in self.choice_buttons:
            btn.config(style="Quiz.TButton")
        
        self.current_question += 1
        self.load_question()
    
    def show_results(self):
        """Display final quiz results"""
        total = len(self.question_pool)
        messagebox.showinfo(
            "Quiz Complete! 🎉",
            f"You finished the quiz!\n\nFinal Score: {self.score} out of {total}.",
            parent=self.quiz_window
        )
        self.quiz_window.destroy()