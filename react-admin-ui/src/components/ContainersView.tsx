import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Group,
  Button,
  Text,
  Modal,
  TextInput,
  Select,
  LoadingOverlay,
  Alert,
  Stack,
  Paper,
} from '@mantine/core';
import { IconPlus, IconTrash, IconAlertCircle, IconEye } from '@tabler/icons-react';
import { containers, projects as projectsApi } from '../api/client';
import { CONTAINER_TYPES } from '../config/constants';

interface Container {
  id: number;
  name: string;
  type: string;
  project_id: number;
  items_count?: number;
  created_at: string;
  updated_at: string;
}

interface Project {
  id: number;
  name: string;
}

export function ContainersView() {
  const navigate = useNavigate();
  const [containersList, setContainersList] = useState<Container[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [newContainer, setNewContainer] = useState({
    name: '',
    type: '',
    project_id: '',
  });
  const [formError, setFormError] = useState<string | null>(null);

  // Fetch containers and projects on component mount
  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [containersData, projectsData] = await Promise.all([
        containers.list(),
        projectsApi.list()
      ]);
      setContainersList(containersData);
      setProjects(projectsData);
    } catch (err) {
      setError('Failed to fetch data. Please try again.');
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    if (!newContainer.name.trim()) {
      setFormError('Container name is required');
      return false;
    }
    if (!newContainer.type) {
      setFormError('Container type is required');
      return false;
    }
    if (!newContainer.project_id) {
      setFormError('Project is required');
      return false;
    }
    return true;
  };

  const handleCreateContainer = async () => {
    if (!validateForm()) return;

    try {
      setLoading(true);
      setFormError(null);
      await containers.create({
        name: newContainer.name,
        type: newContainer.type,
        project_id: parseInt(newContainer.project_id),
      });
      
      // Reset form and close modal
      setNewContainer({ name: '', type: '', project_id: '' });
      setCreateModalOpen(false);
      
      // Refresh containers list
      await fetchData();
    } catch (err) {
      setFormError('Failed to create container. Please try again.');
      console.error('Error creating container:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteContainer = async (containerId: number) => {
    if (!window.confirm('Are you sure you want to delete this container? This action cannot be undone.')) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await containers.delete(containerId);
      await fetchData();
    } catch (err) {
      setError('Failed to delete container. Please try again.');
      console.error('Error deleting container:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper p="md" radius="sm" pos="relative">
      <LoadingOverlay visible={loading} />
      
      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red" mb="md">
          {error}
        </Alert>
      )}

      <Group justify="space-between" mb="md">
        <Text fw={500} size="xl">Containers</Text>
        <Button
          onClick={() => setCreateModalOpen(true)}
          leftSection={<IconPlus size={16} />}
        >
          Create Container
        </Button>
      </Group>

      <Table striped highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>ID</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Type</Table.Th>
            <Table.Th>Project</Table.Th>
            <Table.Th>Items</Table.Th>
            <Table.Th>Actions</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {containersList.map((container) => (
            <Table.Tr key={container.id}>
              <Table.Td>{container.id}</Table.Td>
              <Table.Td>{container.name}</Table.Td>
              <Table.Td>{container.type}</Table.Td>
              <Table.Td>
                {projects.find(p => p.id === container.project_id)?.name || container.project_id}
              </Table.Td>
              <Table.Td>{container.items_count || 0}</Table.Td>
              <Table.Td>
                <Group gap="xs">
                  <Button
                    variant="subtle"
                    size="xs"
                    onClick={() => navigate(`/projects/${container.project_id}/containers/${container.id}`)}
                    leftSection={<IconEye size={16} />}
                  >
                    View
                  </Button>
                  <Button
                    variant="subtle"
                    color="red"
                    size="xs"
                    onClick={() => handleDeleteContainer(container.id)}
                    leftSection={<IconTrash size={16} />}
                  >
                    Delete
                  </Button>
                </Group>
              </Table.Td>
            </Table.Tr>
          ))}
          {containersList.length === 0 && !loading && (
            <Table.Tr>
              <Table.Td colSpan={6} align="center">
                <Text c="dimmed" size="sm">No containers found</Text>
              </Table.Td>
            </Table.Tr>
          )}
        </Table.Tbody>
      </Table>

      <Modal
        opened={createModalOpen}
        onClose={() => {
          setCreateModalOpen(false);
          setFormError(null);
          setNewContainer({ name: '', type: '', project_id: '' });
        }}
        title="Create New Container"
      >
        <Stack>
          {formError && (
            <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
              {formError}
            </Alert>
          )}

          <TextInput
            label="Container Name"
            placeholder="Enter container name"
            required
            value={newContainer.name}
            onChange={(e) => setNewContainer({ ...newContainer, name: e.target.value })}
          />

          <Select
            label="Container Type"
            placeholder="Select container type"
            required
            data={CONTAINER_TYPES.map(type => ({ value: type, label: type }))}
            value={newContainer.type}
            onChange={(value) => setNewContainer({ ...newContainer, type: value || '' })}
          />

          <Select
            label="Project"
            placeholder="Select project"
            required
            data={projects.map(project => ({
              value: project.id.toString(),
              label: project.name
            }))}
            value={newContainer.project_id}
            onChange={(value) => setNewContainer({ ...newContainer, project_id: value || '' })}
          />

          <Button onClick={handleCreateContainer}>
            Create Container
          </Button>
        </Stack>
      </Modal>
    </Paper>
  );
} 