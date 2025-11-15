# 🌱 Micro-Organism Evolution Simulator  
### **Agent-Based, Neural-Net-Driven Life Simulation With CUDA Acceleration, Dreams, Nurture, Sexual Reproduction & Weather**

This project is an evolving **biological + cognitive** simulation where organisms move, perceive, eat, sleep, dream, reproduce, and adapt over time.  
It blends **agent-based modeling**, **neural networks**, **evolutionary genetics**, and **Earth-like environmental cycles** — all accelerated by **PyTorch CUDA** on your RTX GPU.

You begin with a primordial pair (“Adam & Eve”), and across hundreds of generations, the world produces emergent instincts, strategies, social behavior, and proto-intelligence.

---

# 🔥 Key Features

## 🧬 **1. Sexual & Asexual Reproduction**
- Organisms are **male or female**  
- Sexual reproduction requires:
  - compatible partners  
  - proximity  
  - sufficient energy  
  - mate-seeking behavior (not random)  
- Offspring traits emerge through:
  - genome crossover  
  - controlled mutation  
  - heritable neural traits  
- Asexual mode is also supported (config flag)

---

## 🧠 **2. GPU-Accelerated Neural Brains (PyTorch + CUDA)**
Each organism has a **PyTorch neural network**:
- Runs on **CUDA** when available  
- Input: sensory signals (vision, hunger, temperature, season, enemies, mates)  
- Output:  
  - movement vector  
  - turning  
  - reproduction attempts  
  - home-building behavior  
  - sleep decision  
  - energy budgeting  

Neural weights evolve over generations based on survival success.

---

## 💤 **3. Sleep & Dream Replay**
Organisms require sleep cycles:
- Sleep restores energy  
- While sleeping:
  - Brain enters “dream mode”  
  - Experiences from the day replay  
  - Small training loop reinforces important patterns  
  - Leads to **offline learning** similar to RL replay buffers  

Dreams = adaptive evolution accelerator.

---

## 🍼 **4. Family, Homes & Nurture**
- Organisms build **homes** (shelters)  
- Homes protect young organisms  
- Parents bring food to children  
- Dependents follow parents  
- Some lineages evolve strong social nurture behavior  

This creates a primitive **culture layer** emerging from simple rules.

---

## 🌦️ **5. Earth-Like Weather & Seasons**
Includes:
- **Day/night cycle**
- **Seasonal temperature curve**
- **Latitude-based temperature variation**
- **Precipitation cycles**
- **Food regrowth based on weather**

Regrowth formula:

```
growth_rate = base * temp_factor * precip_factor * day_night_factor + noise
```

Environmental pressure shapes evolutionary strategies.

---

## 👁️ **6. Vision System (FOV)**
- Each organism has a field of view
- FOV angle and range are heritable traits  
- FOV influences hunting, mating, parenting, threat avoidance  

---

## 📊 **7. Logging & Stats**
Automatically logs via `logger.py`:
- population  
- births / deaths  
- weather metrics  
- trait averages  
- food count  
- CUDA device info  

`stats.py` gives snapshots for charts or dashboards.

---

## 🎮 **8. Real-Time Visualization (pygame)**
- Organisms drawn with direction indicators  
- FOV arcs  
- Homes  
- Trails  
- Weather overlays  
- Debug layers (optional)

---

# 🚀 Tech Stack

| Component | Technology |
|----------|------------|
| Neural nets | **PyTorch (CUDA)** |
| Simulation | Custom Python engine |
| Rendering | **pygame** |
| Evolution | Mutating genomes + crossover |
| Learning | Dream replay neural updates |
| Logging | CSV + console |
| Analytics | stats.py (pure functions) |

---

# 📦 Installation

### Requirements
- Python 3.10+
- NVIDIA GPU (RTX 3080 recommended)
- pip

Install dependencies:

```bash
pip install numpy pygame
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

---

# 🧪 Verify CUDA

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

You should see:

```
CUDA: True
Device: NVIDIA GeForce RTX 3080
```

---

# ▶️ Running the Simulation

```bash
python main.py
```

Controls:
- `R` — reset world  
- `+ / -` — speed up / slow down sim  
- `ESC` — quit  

---

# 🗂️ Project Structure

```
Micro-Organism-Sim/
│
├── brain.py            # CUDA neural nets (awake & dream modes)
├── organism.py         # Behavior, lifecycle, home, mating, evolution
├── world.py            # Environment, weather, food regrowth
├── genetics.py         # Crossover, mutation, inheritance logic
├── main.py             # Pygame loop + world update
├── config.py           # All parameters (reproduction, weather, FOV, etc.)
├── utils.py            # Helpers (math, bounds, noise)
├── master_view.py      # Debug visualization (FOV, targets)
├── stats.py            # Snapshot analytics
├── logger.py           # Console + CSV logging
└── logs/               # Auto-generated logs
```

---

# 🧱 Architecture Overview

## Core Loop
```
World.step(dt):
    env.update(dt)
    food_regrowth()
    for organism in orgs:
        organism.sense()
        organism.brain_forward()
        organism.apply_actions()
        organism.mating_behavior()
        organism.nurture_logic()
        organism.sleep_and_dream()
        organism.consume_energy()
    remove_dead()
```

## Neural Brain
- Forward pass each tick  
- Sleep mode with replay events  
- CUDA inference per organism  
- Evolution shapes weight initialization over generations  

## Weather System
- Seasonal sine waves  
- Latitude gradient  
- Precipitation cycles  
- Regrowth multiplier affects food availability  

---

# 🛣️ Roadmap

### Near-Term Features
- Social groups / tribes  
- Cooperative hunting and group parenting  
- Tool creation (sticks, rocks)  
- Territorial behavior  
- Advanced sensory perception  
- Proto-language signals  

### Advanced Cognitive Features
- Predictive coding  
- Emotional states (fear, safety, hunger satisfaction)  
- Multi-layered cortical-like nets  
- Memory consolidation patterns in dreams  
- Meta-learning over generations  

### Performance Expansions
- GPU batching of brain inference  
- Vectorized world physics  
- Headless mode for 1M+ organism evolution  
- Custom CUDA kernels for faster sensory processing  

---

# 🤝 Contributing

Pull requests welcome. Areas of interest:
- Neural architecture design  
- Evolution research  
- Rendering improvements  
- New environmental systems  
- Optimization and CUDA batching  

---

# 📜 License
MIT License — use freely for research, learning, and evolution experiments.

---

# 🌌 Final Note

This simulation explores **emergent intelligence**, **evolution under pressure**, and the boundary between instinct and adaptation.  
It is part sandbox, part scientific experiment, and part philosophical journey into artificial life.

Build the world. Watch it evolve. See what emerges. 🌍🧬🧠

