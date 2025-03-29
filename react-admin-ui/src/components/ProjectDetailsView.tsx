import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Title,
  Tabs,
  Stack,
  Group,
  Button,
  Text,
  Alert,
  LoadingOverlay,
  Box,
  Table,
} from '@mantine/core';
import { IconAlertCircle, IconArrowLeft } from '@tabler/icons-react';
import { projects } from '../api/client';
import type { Project, Container } from '../api/client';
import { ImportDataView } from './ImportDataView';

export function ProjectDetailsView() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [containers, setContainers] = useState<Container[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string | null>('overview');

  useEffect(() => {
    if (!projectId) return;
    loadProjectDetails();
  }, [projectId]);

  const loadProjectDetails = async () => {
    if (!projectId) return;
    setLoading(true);
    setError(null);

    try {
      const projectData = await projects.get(parseInt(projectId));
      setProject(projectData);
      const containersData = await projects.listContainers(parseInt(projectId));
      setContainers(containersData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load project details');
    } finally {
      setLoading(false);
    }
  };

  if (!projectId) {
    return (
      <Alert color="red" title="Error">
        No project ID provided
      </Alert>
    );
  }

  return (
    <Paper p="md" radius="sm" pos="relative">
      <LoadingOverlay visible={loading} />
      <Stack>
        <Group justify="space-between">
          <Group>
            <Button
              variant="subtle"
              leftSection={<IconArrowLeft size={14} />}
              onClick={() => navigate('/projects')}
            >
              Back to Projects
            </Button>
            <Title order={2}>{project?.name || 'Project Details'}</Title>
          </Group>
        </Group>

        {error && (
          <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
            {error}
          </Alert>
        )}

        {project && (
          <Tabs value={activeTab} onChange={setActiveTab}>
            <Tabs.List>
              <Tabs.Tab value="overview">Overview</Tabs.Tab>
              <Tabs.Tab value="import">Import Data</Tabs.Tab>
              <Tabs.Tab value="containers">Containers</Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="overview">
              <Stack mt="md">
                <Text><strong>Type:</strong> {project.type}</Text>
                <Text><strong>Description:</strong> {project.description || '-'}</Text>
                <Text><strong>Created:</strong> {new Date(project.created_at).toLocaleString()}</Text>
                <Text><strong>Last Updated:</strong> {new Date(project.updated_at).toLocaleString()}</Text>
              </Stack>
            </Tabs.Panel>

            <Tabs.Panel value="import">
              <Box mt="md">
                <ImportDataView projectId={parseInt(projectId)} />
              </Box>
            </Tabs.Panel>

            <Tabs.Panel value="containers">
              <Stack mt="md">
                <Title order={3}>Data Containers</Title>
                {containers.length === 0 ? (
                  <Text c="dimmed">No containers found. Import some data to get started.</Text>
                ) : (
                  <Table>
                    <Table.Thead>
                      <Table.Tr>
                        <Table.Th>Name</Table.Th>
                        <Table.Th>Type</Table.Th>
                        <Table.Th>Items</Table.Th>
                        <Table.Th>Actions</Table.Th>
                      </Table.Tr>
                    </Table.Thead>
                    <Table.Tbody>
                      {containers.map((container) => (
                        <Table.Tr key={container.id}>
                          <Table.Td>{container.name}</Table.Td>
                          <Table.Td>{container.type}</Table.Td>
                          <Table.Td>{container.items_count || 0}</Table.Td>
                          <Table.Td>
                            <Button
                              variant="subtle"
                              size="xs"
                              onClick={() => navigate(`/containers/${container.id}`)}
                            >
                              View Details
                            </Button>
                          </Table.Td>
                        </Table.Tr>
                      ))}
                    </Table.Tbody>
                  </Table>
                )}
              </Stack>
            </Tabs.Panel>
          </Tabs>
        )}
      </Stack>
    </Paper>
  );
} 