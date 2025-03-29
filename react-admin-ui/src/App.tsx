import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import { DashboardLayout } from './components/DashboardLayout';
import { ProjectsView } from './components/ProjectsView';
import { UsersView } from './components/UsersView';
import { ProjectDetailsView } from './components/ProjectDetailsView';
import { ImportDataView } from './components/ImportDataView';
import { ContainersView } from './components/ContainersView';
import { LoginForm } from './components/LoginForm';
import { useAuth } from './hooks/useAuth';

export function App() {
  const { isAuthenticated } = useAuth();

  return (
    <MantineProvider>
      <Router>
        <Routes>
          <Route path="/login" element={!isAuthenticated ? <LoginForm /> : <Navigate to="/" />} />
          <Route path="/" element={isAuthenticated ? <DashboardLayout /> : <Navigate to="/login" />}>
            <Route index element={<ProjectsView />} />
            <Route path="projects" element={<ProjectsView />} />
            <Route path="projects/:projectId" element={<ProjectDetailsView />} />
            <Route path="users" element={<UsersView />} />
            <Route path="containers" element={<ContainersView />} />
            <Route path="import" element={<ImportDataView />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </MantineProvider>
  );
}
