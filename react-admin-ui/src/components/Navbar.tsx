import { useState } from 'react';
import { AppShell, UnstyledButton, Stack, rem } from '@mantine/core';
import { useNavigate, useLocation } from 'react-router-dom';
import { IconUsers, IconFolders, IconDatabase, IconUpload, IconLogout } from '@tabler/icons-react';
import { auth } from '../api/client';

interface NavItemProps {
  icon: React.ElementType;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

function NavItem({ icon: Icon, label, active, onClick }: NavItemProps) {
  return (
    <UnstyledButton
      onClick={onClick}
      style={{
        display: 'block',
        width: '100%',
        padding: '0.5rem',
        borderRadius: '0.25rem',
        color: active ? '#1c7ed6' : '#495057',
        backgroundColor: active ? '#e7f5ff' : 'transparent',
        '&:hover': {
          backgroundColor: '#f8f9fa',
        },
      }}
    >
      <Stack gap="xs" align="center">
        <Icon size={rem(24)} stroke={1.5} />
        {label}
      </Stack>
    </UnstyledButton>
  );
}

export function AppNavbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [active, setActive] = useState(location.pathname);

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Users', icon: IconUsers, path: '/users' },
    { label: 'Projects', icon: IconFolders, path: '/projects' },
    { label: 'Containers', icon: IconDatabase, path: '/containers' },
    { label: 'Import Data', icon: IconUpload, path: '/import' },
  ];

  return (
    <AppShell.Navbar p="md">
      <Stack h="100%" justify="space-between">
        <Stack gap="xs">
          {navItems.map((item) => (
            <NavItem
              key={item.path}
              icon={item.icon}
              label={item.label}
              active={active === item.path}
              onClick={() => {
                setActive(item.path);
                navigate(item.path);
              }}
            />
          ))}
        </Stack>

        <NavItem
          icon={IconLogout}
          label="Logout"
          onClick={handleLogout}
        />
      </Stack>
    </AppShell.Navbar>
  );
} 