import { Outlet } from 'react-router-dom';
import { AppShell as MantineAppShell } from '@mantine/core';
import { AppNavbar } from './AppNavbar.tsx';

export function AppShell() {
  return (
    <MantineAppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm' }}
      padding="md"
    >
      <MantineAppShell.Navbar>
        <AppNavbar />
      </MantineAppShell.Navbar>

      <MantineAppShell.Main>
        <Outlet />
      </MantineAppShell.Main>
    </MantineAppShell>
  );
} 