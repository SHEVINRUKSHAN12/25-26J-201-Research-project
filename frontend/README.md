# Frontend - Interior Space Optimization

A modern React application built with Vite for interior space optimization with 2D canvas editing and 3D visualization capabilities.

## 🚀 Technology Stack

### Core Framework
- **React 19.2.0** - JavaScript library for building user interfaces
- **Vite 7.2.4** - Next-generation frontend build tool for fast development

### Key Dependencies

#### Routing & Navigation
- **react-router-dom 7.10.1** - Declarative routing for React applications

#### HTTP Client
- **axios 1.13.2** - Promise-based HTTP client for API requests

#### Backend & Authentication
- **firebase 12.6.0** - Firebase SDK for authentication, database, and cloud services

#### 2D Canvas & Layout Editor
- **konva 10.0.12** - HTML5 2D canvas library for desktop and mobile applications
- **react-konva 19.2.1** - React components for Konva framework

#### 3D Visualization
- **three 0.181.2** - JavaScript 3D library
- **@react-three/fiber 9.4.2** - React renderer for Three.js
- **@react-three/drei 10.7.7** - Useful helpers and abstractions for react-three-fiber

### Development Tools
- **ESLint 9.39.1** - JavaScript linting utility
- **@vitejs/plugin-react 5.1.1** - Official Vite plugin for React

---

## 📦 Installation Guide

### Prerequisites
- **Node.js** (v18 or higher recommended)
- **npm** (comes with Node.js)

### Step 1: Initial Setup

The project was initialized using Vite with the React template:

```bash
npm create vite@latest frontend -- --template react
```

This command:
- Creates a new directory called `frontend`
- Sets up a React project with Vite
- Installs base dependencies (React, React DOM, Vite)
- Configures ESLint for code quality

### Step 2: Navigate to Project Directory

```bash
cd frontend
```

### Step 3: Install Required Dependencies

All required packages were installed with a single command:

```bash
npm install react-router-dom axios firebase konva react-konva three @react-three/fiber @react-three/drei
```

This installs:
- **react-router-dom** - For client-side routing
- **axios** - For HTTP requests to backend APIs
- **firebase** - For authentication and database services
- **konva** & **react-konva** - For 2D canvas-based layout editor
- **three**, **@react-three/fiber**, **@react-three/drei** - For 3D visualization

### Step 4: Additional Recommended Packages (Optional)

Consider installing these packages based on your needs:

```bash
# State Management
npm install zustand
# or
npm install @reduxjs/toolkit react-redux

# UI Component Library
npm install @mui/material @emotion/react @emotion/styled
# or
npm install antd

# Form Handling
npm install react-hook-form
npm install yup  # for validation

# Date/Time Utilities
npm install date-fns
# or
npm install dayjs

# Notifications/Toasts
npm install react-hot-toast
# or
npm install react-toastify

# Icons
npm install react-icons
# or
npm install @mui/icons-material

# UUID Generation
npm install uuid

# Environment Variables
npm install dotenv
```

---

## 🛠️ Available Scripts

### Development Server
```bash
npm run dev
```
Starts the development server at `http://localhost:5173/`
- Hot Module Replacement (HMR) enabled
- Fast refresh for instant updates

### Build for Production
```bash
npm run build
```
Creates an optimized production build in the `dist` folder

### Preview Production Build
```bash
npm run preview
```
Locally preview the production build

### Lint Code
```bash
npm run lint
```
Run ESLint to check code quality and find issues

---

## 📁 Project Structure

```
frontend/
├── node_modules/          # Installed dependencies
├── public/                # Static assets
├── src/                   # Source files
│   ├── assets/           # Images, fonts, etc.
│   ├── App.jsx           # Main App component
│   ├── App.css           # App styles
│   ├── index.css         # Global styles
│   └── main.jsx          # Application entry point
├── .gitignore            # Git ignore rules
├── eslint.config.js      # ESLint configuration
├── index.html            # HTML entry point
├── package.json          # Project dependencies and scripts
├── package-lock.json     # Locked dependency versions
├── README.md             # This file
└── vite.config.js        # Vite configuration
```

---

## 🔧 Configuration Files

### vite.config.js
Vite configuration for React plugin and build settings

### eslint.config.js
ESLint rules and configuration for code quality

### package.json
Contains all project metadata, dependencies, and npm scripts

---

## 🌟 Key Features to Implement

Based on the installed packages, you can build:

1. **2D Layout Editor** (using Konva)
   - Drag-and-drop furniture placement
   - Room layout design
   - Interactive canvas manipulation

2. **3D Visualization** (using Three.js)
   - 3D room preview
   - Camera controls
   - Realistic rendering

3. **Routing** (using React Router)
   - Multi-page navigation
   - Protected routes
   - Dynamic routing

4. **Backend Integration** (using Axios & Firebase)
   - API calls to backend services
   - User authentication
   - Real-time database updates

---

## 🔐 Firebase Setup (Next Steps)

1. Create a Firebase project at [https://console.firebase.google.com/](https://console.firebase.google.com/)
2. Register your web app
3. Copy the Firebase configuration
4. Create a `.env` file in the root directory:

```env
VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_auth_domain
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_storage_bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

5. Initialize Firebase in your app (create `src/firebase.js`):

```javascript
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);
```

---

## 📚 Documentation Links

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vite.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Konva Documentation](https://konvajs.org/)
- [React Konva Documentation](https://konvajs.org/docs/react/)
- [Three.js Documentation](https://threejs.org/docs/)
- [React Three Fiber Documentation](https://docs.pmnd.rs/react-three-fiber/)
- [Drei Documentation](https://github.com/pmndrs/drei)

---

## 🚦 Getting Started

1. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open browser** and navigate to `http://localhost:5173/`

4. **Start building** your interior space optimization application!

---

## 📝 Notes

- This project uses **Vite** for blazing-fast development experience
- **React 19** is the latest version with improved performance
- All dependencies are installed and ready to use
- The project is configured with **ESLint** for code quality
- **Hot Module Replacement (HMR)** is enabled for instant updates

---

## 🤝 Next Steps

1. Set up Firebase configuration
2. Create folder structure for components, pages, and utilities
3. Implement routing with React Router
4. Build 2D canvas editor with Konva
5. Create 3D visualization with Three.js
6. Integrate backend API calls with Axios
7. Add authentication with Firebase

---

## 📄 License

This project is private and proprietary.

---

**Happy Coding! 🎉**
