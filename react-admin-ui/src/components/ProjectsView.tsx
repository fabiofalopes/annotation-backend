import { useState, useEffect } from 'react';
import { Table, Button, Modal, TextInput, Group, Title, Stack, Paper, LoadingOverlay, Alert, Select } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconPlus, IconTrash, IconAlertCircle } from '@tabler/icons-react';
import { projects } from '../api/client';
import type { Project } from '../api/client';
import { useNavigate } from 'react-router-dom';

const PROJECT_TYPES = [
  { value: 'chat_disentanglement', label: 'Chat Disentanglement' },
  { value: 'image_annotation', label: 'Image Annotation' },
  { value: 'text_classification', label: 'Text Classification' },
];

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Never';
  try {
    return new Date(dateStr).toLocaleString();
  } catch (e) {
    return 'Invalid date';
  }
}

export function ProjectsView() {
  const [projectsList, setProjectsList] = useState<Project[]>([]);
  const [opened, { open, close }] = useDisclosure(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    type: '',
  });
  const navigate = useNavigate();

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching projects...');
      const data = await projects.list();
      console.log('Projects fetched:', data);
      setProjectsList(data);
    } catch (error) {
      console.error('Error fetching projects:', error);
      setError('Failed to load projects. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const validateForm = () => {
    if (!newProject.name.trim()) {
      setFormError('Project name is required');
      return false;
    }
    if (!newProject.type) {
      setFormError('Project type is required');
      return false;
    }
    setFormError(null);
    return true;
  };

  const handleCreateProject = async () => {
    if (!validateForm()) return;

    try {
      setError(null);
      console.log('Creating project:', newProject);
      await projects.create(newProject);
      close();
      fetchProjects();
      setNewProject({ name: '', description: '', type: '' });
    } catch (error) {
      console.error('Error creating project:', error);
      setError('Failed to create project. Please try again.');
    }
  };

  const handleDeleteProject = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this project?')) return;

    try {
      setError(null);
      console.log('Deleting project:', id);
      await projects.delete(id);
      fetchProjects();
    } catch (error) {
      console.error('Error deleting project:', error);
      setError('Failed to delete project. Please try again.');
    }
  };

  return (
    <Paper p="md" radius="sm" pos="relative">
      <LoadingOverlay visible={loading} />
      <Stack>
        {error && (
          <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
            {error}
          </Alert>
        )}
        
        <Group justify="space-between" mb="md">
          <Title order={2}>Projects Management</Title>
          <Button
            leftSection={<IconPlus size={14} />}
            onClick={open}
          >
            Create Project
          </Button>
        </Group>

        <Table highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Name</Table.Th>
              <Table.Th>Type</Table.Th>
              <Table.Th>Description</Table.Th>
              <Table.Th>Created</Table.Th>
              <Table.Th>Last Updated</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {projectsList.map((project) => (
              <Table.Tr 
                key={project.id}
                style={{ cursor: 'pointer' }}
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                <Table.Td>{project.id}</Table.Td>
                <Table.Td>{project.name}</Table.Td>
                <Table.Td>{project.type}</Table.Td>
                <Table.Td>{project.description || '-'}</Table.Td>
                <Table.Td>{formatDate(project.created_at)}</Table.Td>
                <Table.Td>{formatDate(project.updated_at)}</Table.Td>
                <Table.Td>
                  <Button
                    variant="subtle"
                    color="red"
                    size="xs"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteProject(project.id);
                    }}
                    leftSection={<IconTrash size={14} />}
                  >
                    Delete
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>

        <Modal opened={opened} onClose={close} title="Create New Project">
          <Stack>
            {formError && (
              <Alert icon={<IconAlertCircle size={16} />} title="Validation Error" color="red">
                {formError}
              </Alert>
            )}
            <TextInput
              label="Name"
              placeholder="Enter project name"
              value={newProject.name}
              onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
              required
            />
            <Select
              label="Type"
              placeholder="Select project type"
              data={PROJECT_TYPES}
              value={newProject.type}
              onChange={(value) => setNewProject({ ...newProject, type: value || '' })}
              required
            />
            <TextInput
              label="Description"
              placeholder="Enter project description"
              value={newProject.description}
              onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
            />
            <Button onClick={handleCreateProject}>Create Project</Button>
          </Stack>
        </Modal>
      </Stack>
    </Paper>
  );
} 