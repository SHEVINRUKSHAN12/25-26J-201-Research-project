# Integrated Home Design & Planning Platform

## Project Overview
This project is a web-based AI-assisted home design platform that supports users from early land analysis to detailed interior and exterior layout planning. The system integrates multiple intelligent modules to assist users in evaluating design feasibility, space efficiency, and compliance with architectural and cultural constraints.

The system is modular, meaning each component can work independently or as part of a full workflow.

## Modules

### 1. Land Rules & Regulation Analysis + Land Optimization
This component accepts land dimensions or a survey plan and evaluates compliance with building regulations such as setbacks and usable area limits. Based on these constraints, it calculates the usable land area and generates land or floor-plan-ready layouts. The output is structured JSON data containing land polygons, room boundaries, and constraints.

### 2. Interior Space Optimization (Core Component)
This module receives room geometry (polygon), doors, windows, and a list of user-selected furniture items. Each furniture item has default dimensions (width, depth, height), but users can optionally modify these dimensions before optimization. A constraint-based optimization algorithm is used to place furniture inside the room while ensuring:
- No furniture overlaps
- Minimum walkway and clearance requirements
- Efficient space utilization

The output includes optimized furniture positions (JSON), KPI scores (free space, walkway, clearance), and visual outputs in 2D (top view), 3D, and AR modes.

*Note: Machine learning is not used to generate layouts. Optimization algorithms are the core engine.*

### 3. Exterior Space Optimization
This module applies similar optimization logic to outdoor spaces such as gardens, parking areas, pathways, and entrances. It optimizes object placement within exterior boundaries while maintaining accessibility and spacing rules.

### 4. Vastu Compliance Detection
This module performs rule-based validation to check whether the generated layouts comply with predefined Vastu principles. It only detects and reports compliance or non-compliance. It does not modify or correct the layout.

## System Architecture

```mermaid
graph TD
    User[User] -->|Interacts with| Frontend[Frontend (React + Vite)]
    
    subgraph "Frontend Layer"
        Frontend
    end
    
    subgraph "Backend Layer"
        Backend[Backend (FastAPI)]
    end
    
    subgraph "Data & Storage Layer"
        Firestore[(Firebase Firestore)]
        Storage[(Firebase Storage)]
    end
    
    Frontend -->|API Requests| Backend
    Frontend -->|Direct Access (Auth/Data)| Firestore
    Backend -->|Optimization Logic & Validation| Firestore
    Backend -->|Store/Retrieve Assets| Storage
    Frontend -->|Load 3D Models/Images| Storage
```

- **Frontend**: React (Vite) web application for UI, user interaction, and 2D/3D/AR visualization.
- **Backend**: FastAPI services that handle optimization logic, validation, and data processing.
- **Database**: Firebase Firestore for storing users, projects, layouts, and configuration data.
- **Storage**: Firebase Storage for furniture icons, images, and 3D models.

## Dependencies

### Frontend
- **Core**: `react`, `react-dom`, `vite`
- **Routing**: `react-router-dom`
- **State/API**: `axios`, `firebase`
- **Visualization**: `three`, `@react-three/fiber`, `@react-three/drei`, `konva`, `react-konva`
- **UI/Animation**: `framer-motion`, `lucide-react`

### Backend
- **Framework**: `fastapi`, `uvicorn[standard]`
- **Database**: `firebase-admin`
- **Data Processing**: `numpy`, `pandas`
- **Utilities**: `pydantic`, `pydantic-settings`, `python-dotenv`, `httpx`

## Getting Started

### Prerequisites
- Node.js (v18+ recommended)
- Python (v3.9+ recommended)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository-url>
    ```

2.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Backend Setup**
    ```bash
    cd backend
    # Create virtual environment (optional but recommended)
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Run server
    uvicorn app.main:app --reload
    ```
