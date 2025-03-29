import { AppShell, Title, SimpleGrid, Card, Text, Group, Paper, LoadingOverlay, Alert } from '@mantine/core';
import { IconUsers, IconFolders, IconDatabase, IconAlertCircle } from '@tabler/icons-react';
import { AppNavbar } from './Navbar';
import { useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { users, projects, containers } from '../api/client';

interface StatsCardProps {
  title: string;
  value: number | string;
  icon: React.ReactNode;
  loading?: boolean;
}

function StatsCard({ title, value, icon, loading }: StatsCardProps) {
  return (
    <Card withBorder p="md" radius="md" shadow="sm" pos="relative">
      <LoadingOverlay visible={loading || false} />
      <Group justify="space-between" align="center">
        <div>
          <Text size="sm" c="dimmed" fw={500}>
            {title}
          </Text>
          <Text size="xl" fw={700} mt="sm">
            {value}
          </Text>
        </div>
        <div style={{ color: 'var(--mantine-color-blue-filled)' }}>
          {icon}
        </div>
      </Group>
    </Card>
  );
}

export function DashboardLayout() {
  const [stats, setStats] = useState({
    users: 0,
    projects: 0,
    containers: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching dashboard stats...');
        
        const [usersList, projectsList, containersList] = await Promise.all([
          users.list(),
          projects.list(),
          containers.list(),
        ]);

        console.log('Stats fetched successfully:', {
          users: usersList.length,
          projects: projectsList.length,
          containers: containersList.length,
        });

        setStats({
          users: usersList.length,
          projects: projectsList.length,
          containers: containersList.length,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        setError('Failed to load dashboard statistics. Please try refreshing the page.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{ width: 300, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Header p="md">
        <Group justify="space-between">
          <Title order={2}>Annotation Backend Admin</Title>
        </Group>
      </AppShell.Header>

      <AppShell.Navbar p="md">
        <AppNavbar />
      </AppShell.Navbar>

      <AppShell.Main>
        <Paper p="md" radius="sm" mb="lg">
          {error ? (
            <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" mb="lg">
              {error}
            </Alert>
          ) : (
            <SimpleGrid cols={3}>
              <StatsCard
                title="Total Users"
                value={loading ? '...' : stats.users}
                icon={<IconUsers size={32} />}
                loading={loading}
              />
              <StatsCard
                title="Total Projects"
                value={loading ? '...' : stats.projects}
                icon={<IconFolders size={32} />}
                loading={loading}
              />
              <StatsCard
                title="Total Containers"
                value={loading ? '...' : stats.containers}
                icon={<IconDatabase size={32} />}
                loading={loading}
              />
            </SimpleGrid>
          )}
        </Paper>
        <Outlet />
      </AppShell.Main>
    </AppShell>
  );
} 