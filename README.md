# Integrated Home Design & Planning Platform

## 📌 Project Overview

The **Integrated Home Design & Planning Platform** is a web-based decision-support system designed to assist users during the early stages of residential planning. The system supports users from initial land evaluation through interior and exterior space planning, combining feasibility analysis, spatial optimization, and rule-based validation into a unified workflow.

Each module can be used independently or as part of a complete end-to-end process, allowing flexibility based on user needs.

The platform is intended to support planning, evaluation, and visualization, rather than replacing professional architectural design.

## 🧩 System Modules & Responsibilities

The system consists of four main functional modules, each developed by a designated team member.

### 1️⃣ Land Rules & Regulations Analysis with Land Optimization
**Researcher & Developer:** Sunkalpani S M D R — IT2291499

This module analyzes land dimensions or survey plans against applicable building rules and regulations such as setbacks, coverage limits, and usable area constraints. Based on these constraints, it identifies the buildable area and produces optimized, layout-ready land data.

**Key functions:**
- Land feasibility analysis
- Regulation compliance checking
- Usable land area identification
- Optimized land layout generation

### 2️⃣ Vastu Compliance Detection
**Researcher & Developer:** Dinetha K A V — IT22924278

This module evaluates generated layouts against predefined Vastu principles. It performs rule-based compliance detection only and does not modify or correct layouts. The system reports whether a design complies with Vastu guidelines and highlights any violations.

**Key functions:**
- Directional and spatial validation
- Compliance / non-compliance reporting
- Automatic layout correction

### 3️⃣ Interior Space Optimization
**Researcher & Developer:** Rathnasinghe S. J. R — IT22908124

It accepts room geometry (from land optimization or manual input), along with doors, windows, and user-selected furniture items. Furniture items are provided with default dimensions, which users may optionally customize.

The system optimizes furniture placement to ensure efficient space utilization, accessibility, and functional layout design.

**Key functions:**
- Constraint-based furniture placement
- Collision and overlap avoidance
- Walkway and clearance management
- KPI-based layout evaluation
- Visualization in 2D, 3D, and AR formats

### 4️⃣ Exterior Space Optimization
**Researcher & Developer:** Hansika J A J — IT22346018

This module focuses on optimizing outdoor spaces such as gardens, parking areas, walkways, and access paths. It ensures balanced space usage and accessibility within the available exterior boundaries.

**Key functions:**
- Outdoor layout planning
- Accessibility-aware object placement
- Space-efficient exterior design

## System Architecture

Here is how the different parts of the system talk to each other:

![System Architecture](assets/architecture_diagram.png)

## Dependencies

Here is the complete list of libraries and tools powering the project:

### Frontend (React + Vite)
**Core & Architecture**
- `react`, `react-dom`: UI Library
- `vite`: Build tool and dev server
- `react-router-dom`: Routing

**State, API & Backend Integration**
- `axios`: HTTP Client
- `firebase`: Authentication & Database SDK

**3D, Graphics & Visualization**
- `three`: Core 3D library
- `@react-three/fiber`: React renderer for Three.js
- `@react-three/drei`: Helpers for R3F
- `konva`: 2D Canvas library
- `react-konva`: React bindings for Konva

**UI & Animation**
- `framer-motion`: Animation library
- `lucide-react`: Icon set

**Development & Build Tools**
- `eslint`, `@eslint/js`, `globals`: Linting
- `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`: React-specific linting rules
- `@vitejs/plugin-react`: Vite React plugin
- `@types/react`, `@types/react-dom`: TypeScript definitions

### Backend (FastAPI)
**Core Framework**
- `fastapi`: Web framework
- `uvicorn[standard]`: ASGI server

**Database & Authentication**
- `firebase-admin`: Firebase Admin SDK

**Data Processing & Math**
- `numpy`: Numerical computing
- `pandas`: Data manipulation

**Utilities & Configuration**
- `pydantic`, `pydantic-settings`: Data validation & settings
- `python-dotenv`: Environment variable management
- `httpx`: Async HTTP client

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
