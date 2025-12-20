# Integrated Home Design & Planning Platform

## 📌 Project Overview

The **Integrated Home Design & Planning Platform** is a web-based decision-support system designed to assist users during the early stages of residential planning. The system supports users from initial land evaluation through interior and exterior space planning, combining feasibility analysis, spatial optimization, and rule-based validation into a unified workflow.

Each module can be used independently or as part of a complete end-to-end process, allowing flexibility based on user needs.

The platform is intended to support planning, evaluation, and visualization, rather than replacing professional architectural design.

## 🧩 System Modules & Responsibilities

The system consists of four main functional modules, each developed by a designated team member.

### 1️⃣ Land Rules & Regulations Analysis with Land Optimization
**Developer:** Sunkalpani S M D R — IT2291499

This module analyzes land dimensions or survey plans against applicable building rules and regulations such as setbacks, coverage limits, and usable area constraints. Based on these constraints, it identifies the buildable area and produces optimized, layout-ready land data.

**Key functions:**
- Land feasibility analysis
- Regulation compliance checking
- Usable land area identification
- Optimized land layout generation

### 2️⃣ Vastu Compliance Detection
**Developer:** Dinetha K A V — IT22924278

This module evaluates generated layouts against predefined Vastu principles. It performs rule-based compliance detection only and does not modify or correct layouts. The system reports whether a design complies with Vastu guidelines and highlights any violations.

**Key functions:**
- Directional and spatial validation
- Compliance / non-compliance reporting
- Automatic layout correction

### 3️⃣ Interior Space Optimization
**Developer:** Rathnasinghe S. J. R — IT22908124

It accepts room geometry (from land optimization or manual input), along with doors, windows, and user-selected furniture items. Furniture items are provided with default dimensions, which users may optionally customize.

The system optimizes furniture placement to ensure efficient space utilization, accessibility, and functional layout design.

**Key functions:**
- Constraint-based furniture placement
- Collision and overlap avoidance
- Walkway and clearance management
- KPI-based layout evaluation
- Visualization in 2D, 3D, and AR formats

### 4️⃣ Exterior Space Optimization
**Developer:** Hansika J A J — IT22346018

This module focuses on optimizing outdoor spaces such as gardens, parking areas, walkways, and access paths. It ensures balanced space usage and accessibility within the available exterior boundaries.

**Key functions:**
- Outdoor layout planning
- Accessibility-aware object placement
- Space-efficient exterior design

## System Architecture

Here is how the different parts of the system talk to each other:

![System Architecture](assets/architecture_diagram.png)

## Dependencies

We've kept the tech stack modern and efficient. Here is the full list of what we're using:

### Frontend
Built with **React** and **Vite**.
- **Core Framework:** `react`, `react-dom`, `vite`
- **Routing:** `react-router-dom`
- **State & API:** `axios`, `firebase`
- **3D & Visualization:**
  - `three`
  - `@react-three/fiber`
  - `@react-three/drei`
  - `konva`
  - `react-konva`
- **UI & Animation:** `framer-motion`, `lucide-react`
- **Dev Tools:** `eslint`

### Backend
Powered by **Python** and **FastAPI**.
- **Web Framework:** `fastapi`, `uvicorn[standard]`
- **Database & Auth:** `firebase-admin`
- **Data Processing:** `numpy`, `pandas`
- **Utilities:** `pydantic`, `pydantic-settings`, `python-dotenv`, `httpx`

## Project History
The full development history, including all changes and updates, is maintained in this repository's Git history. You can view the commit logs to see how the project has evolved over time.

## How to Run It

**Prerequisites**
You'll need Node.js (v18+) and Python (v3.9+) installed.

**Installation**

1.  **Clone the repo**
    ```bash
    git clone https://github.com/SHEVINRUKSHAN12/25-26J-201-Research-project.git
    ```

2.  **Start the Frontend**
    Go into the `frontend` folder, install the dependencies, and start the dev server:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Start the Backend**
    Head over to the `backend` folder. It's best to use a virtual environment:
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```
