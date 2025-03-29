import { NavLink } from 'react-router-dom';
import { Stack, UnstyledButton, Group, Text, Title, Box, Divider } from '@mantine/core';
import {
  IconFolders,
  IconUsers,
  IconBox,
  IconUpload,
  IconLogout,
} from '@tabler/icons-react';
import { auth } from '../api/client';

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  to: string;
}

function NavItem({ icon, label, to }: NavItemProps) {
  return (
    <NavLink
      to={to}
      style={({ isActive }) => ({
        backgroundColor: isActive ? 'var(--mantine-color-blue-light)' : 'transparent',
        color: isActive ? 'var(--mantine-color-blue-filled)' : 'inherit',
        textDecoration: 'none',
        borderRadius: 'var(--mantine-radius-sm)',
      })}
    >
      <UnstyledButton
        p="xs"
        style={{
          width: '100%',
          borderRadius: 'var(--mantine-radius-sm)',
        }}
      >
        <Group>
          {icon}
          <Text size="sm">{label}</Text>
        </Group>
      </UnstyledButton>
    </NavLink>
  );
}

export function AppNavbar() {
  const handleLogout = () => {
    auth.logout();
    window.location.href = '/login';
  };

  return (
    <Stack p="md" h="100%">
      <Box mb="md">
        <Title order={3}>Annotation Backend</Title>
      </Box>

      {/* Main Navigation */}
      <NavItem icon={<IconFolders size={20} />} label="Projects" to="/" />
      <NavItem icon={<IconUsers size={20} />} label="Users" to="/users" />
      <NavItem icon={<IconBox size={20} />} label="Containers" to="/containers" />

      <Divider my="sm" />

      {/* Data Management */}
      <Text size="sm" c="dimmed" fw={500} mb="xs">Data Management</Text>
      <NavItem icon={<IconUpload size={20} />} label="Import Data" to="/import" />

      {/* Logout Button */}
      <UnstyledButton
        onClick={handleLogout}
        p="xs"
        style={{
          marginTop: 'auto',
          borderRadius: 'var(--mantine-radius-sm)',
        }}
      >
        <Group>
          <IconLogout size={20} />
          <Text size="sm">Logout</Text>
        </Group>
      </UnstyledButton>
    </Stack>
  );
} 