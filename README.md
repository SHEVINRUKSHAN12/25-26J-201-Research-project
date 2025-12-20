# Integrated Home Design & Planning Platform

## Project Overview
This is a web-based tool designed to help users plan their dream home from the ground up—literally. It takes you from analyzing a raw piece of land all the way to detailed interior and exterior planning. The idea is to combine feasibility checks, space optimization, and even rule validation (like Vastu) into one smooth workflow.

You can use each part of this system on its own, or go through the full flow.

**Land Analysis & Optimization**
First, we look at the land itself. You feed in the dimensions or a survey plan, and the system checks local regulations—like setbacks and buildable area limits—to figure out exactly how much space you can actually use. It then generates a layout that maximizes that potential.

**Interior Space Optimization**
This is the core of the project. You give it a room shape, add doors and windows, and list the furniture you want. The system then uses a constraint-based optimizer (not AI/ML, but pure logic) to arrange everything perfectly. It ensures:
- Furniture doesn't overlap
- There's enough walking space
- The room feels balanced and practical

You get a 2D plan, a 3D view, and even an AR visualization to see how it looks.

**Exterior Space Optimization**
Just like the interior, we optimize the outdoors too. Gardens, parking spots, pathways—the system arranges them within your boundaries while keeping everything accessible and looking good.

**Vastu Compliance**
For those who follow Vastu Shastra, there's a built-in checker. It scans your generated layout and lets you know if it follows the rules. It won't move things for you, but it'll tell you what's right and what might need a tweak.

## System Architecture

Here is how the different parts of the system talk to each other:

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
    git clone <repository-url>
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
