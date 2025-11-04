# Micro-Organism-Sim

A biologically inspired **2D evolution simulator** built in **Python + Pygame**.

This project visualizes a world of microscopic agents that move, see, eat, burn energy, and adapt — inspired by real biological and physical principles. Each organism has a simple neural "brain" and responds to its environment, consuming resources to survive. Over time, traits like energy efficiency, vision range, and decision patterns can evolve.

---

## 🌎 Overview

The simulation creates a miniature digital ecosystem where:
- Microorganisms move through a 2D environment seeking food.
- Each has limited energy and must find resources to survive.
- Agents use sensory inputs (sight, distance, energy) to decide how to turn or accelerate.
- Physics mimic drag, thrust, and momentum.
- The world wraps around (like a torus) — no walls.
- Time runs **10× faster** than real-time for accelerated evolution.
- The simulation logs key events (births, deaths, average traits) in the console and `/logs/`.

---

## 🧠 Features
- **Neural Behavior:** Simple network-like responses to sensory input.
- **Energy & Metabolism:** Realistic energy drain and resource consumption.
- **World Physics:** Continuous motion, thrust, and drag.
- **Visual Rendering:** Built with Pygame (lightweight and smooth).
- **Console Feed:** Live evolution stats and master agent readouts.
- **Scalable:** Easily extendable for reproduction, mutation, and AI-driven evolution.

---

## ⚙️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/xboosty/Micro-Organism-Sim.git
cd Micro-Organism-Sim

### 2. Create and activate a virtual environment

python3 -m venv .venv
source .venv/bin/activate  # (Mac/Linux)
# or on Windows:
# .venv\Scripts\activate

### 3. Install dependencies

pip install -r requirements.txt

### ▶️ Run the Simulation

python main.py

