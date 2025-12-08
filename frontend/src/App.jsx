import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import SharedLayout from './components/SharedLayout/SharedLayout';
import LandingPage from './components/LandingPage/LandingPage';
import AboutPage from './components/AboutPage/AboutPage';

import ContactPage from './components/ContactPage/ContactPage';
import LoginPage from './components/Auth/LoginPage';
import SignupPage from './components/Auth/SignupPage';
import DashboardPage from './components/Dashboard/DashboardPage';
import ProjectWizard from './components/ProjectWizard/ProjectWizard';
import ProjectDetails from './components/Dashboard/ProjectDetails';
import LandModule from './components/Modules/LandModule';
import InteriorModule from './components/Modules/InteriorModule/InteriorModule';
import VastuModule from './components/Modules/VastuModule/VastuModule';
import ExteriorModule from './components/Modules/ExteriorModule/ExteriorModule';
import ProfilePage from './components/Profile/ProfilePage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<SharedLayout />}>
            <Route index element={<LandingPage />} />
            <Route path="about" element={<AboutPage />} />

            <Route path="contact" element={<ContactPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="signup" element={<SignupPage />} />
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="profile" element={<ProfilePage />} />
            <Route path="new-project" element={<ProjectWizard />} />
            <Route path="project/:id" element={<ProjectDetails />} />
            <Route path="project/:id/land" element={<LandModule />} />
            <Route path="project/:id/vastu" element={<VastuModule />} />
            <Route path="project/:id/interior" element={<InteriorModule />} />
            <Route path="project/:id/exterior" element={<ExteriorModule />} />
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
