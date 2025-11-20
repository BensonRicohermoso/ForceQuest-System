# ⚙️ ForceQuest — Physics Adventure Mode



**ForceQuest** is a comprehensive Python application built with **Tkinter** for the GUI, and powered by **Matplotlib** and **NumPy** for plotting and calculations. It simulates and visualizes fundamental physics concepts related to **Work, Energy, and Power (W.E.P.)**. It allows users to manipulate physical parameters and instantly see the results, including a visual animation, detailed calculations, and an integrated quiz to test their knowledge.

---

## ✨ Features

* **Interactive UI (Tkinter):** A modern, dark-themed graphical user interface for easy parameter input and simulation control.
* **Physics Simulation:** Calculates key W.E.P. metrics (Net Work, Kinetic Energy, Velocity, Power) for different scenarios.
    * **Scenarios:** Pushing Object (Horizontal), Lifting Object (Vertical), Inclined Plane.
    * **Customizable Parameters:** Force, Distance, Mass, Angle, Friction Coefficient ($\mu$).
* **Real-time Animation:** Visually tracks the object's movement on a canvas, showing the effect of the applied forces and customizable push modes.
* **Detailed Solution Output:** Provides a step-by-step breakdown of the physics calculations, including Net Force analysis.
* **Energy Plotting (Matplotlib):** Generates a graph showing the relationship between Distance, Work, and Kinetic Energy.
* **Physics Quiz:** An integrated multiple-choice quiz feature to test the user's understanding of W.E.P. concepts.

---

## 🚀 Getting Started

### Prerequisites

You need **Python 3.x** installed on your system.

This project relies on the following Python libraries:
* `tkinter` (Usually included with standard Python installations)
* `numpy`
* `matplotlib`

### Installation

1.  **Clone the repository (or save the code):**
    ```bash
    git clone [https://github.com/yourusername/forcequest.git](https://github.com/yourusername/forcequest.git)
    cd forcequest
    ```
2.  **Install the required dependencies:**
    ```bash
    pip install numpy matplotlib
    ```

    ## 🔬 How to Use the Simulator

1.  **Select a Scenario:** Choose between **"Pushing Object," "Lifting Object,"** or **"Inclined Plane."**
2.  **Input Parameters:** Enter values for **Force (N)**, **Distance (m)**, **Mass (kg)**, **Angle (°)**, and **Friction $\mu$**.
    * **Tip:** The application can calculate a missing variable (e.g., Mass or Force) if you leave **one** of the primary input fields blank, provided enough other parameters are given.
3.  **Customize:** Adjust the **Surface Material** (affects $\mu$), **Object Shape** (affects rolling friction), **Force Angle**, and **Push Mode** to modify the simulation dynamics.
4.  **Run:** Click the **`▶ Run Simulation`** button.
5.  **Analyze:**
    * View the animated motion and the final $\Delta KE$ indicator.
    * Check the **Solution Box** for detailed force and work calculations.
    * Click **`📊 Show Energy Graph`** to see the work-energy relationship visualized.
    * Test your knowledge with the **`✅ Start Physics Quiz`**.
  
---

## 💡 Key Physics Formulas

The simulation's primary calculation is based on the **Work-Energy Theorem**: 

[Image of the Work-Energy Theorem concept]


$$W_{net} = F_{net} \times d = \Delta KE$$

The final velocity ($v_f$) is then calculated from the change in kinetic energy ($\Delta KE$) and mass ($m$):

$$v_f = \sqrt{\frac{2 \times \Delta KE}{m}}$$

```bash

🤝 Contributing
This project is primarily an educational tool for learning Work, Energy, and Power.

Feel free to open an issue or submit a pull request if you want to:

Add more detailed friction models.

Expand the quiz question pool (QUIZ_QUESTIONS).

Improve the canvas visualization or vector drawing functionality.
