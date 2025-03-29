import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Title,
  Stack,
  Group,
  Text,
  Alert,
  LoadingOverlay,
  Table,
  Badge,
} from '@mantine/core';
import { IconAlertCircle } from '@tabler/icons-react';
import { containers } from '../api/client';
import type { Container } from '../api/client';

interface DataItem {
  id: number;
  content: string;
  metadata?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

interface ContainerWithItems extends Container {
  items: DataItem[];
}

export function ContainerDetailsView() {
  const { projectId, containerId } = useParams<{ projectId: string; containerId: string }>();
  const navigate = useNavigate();
  const [container, setContainer] = useState<ContainerWithItems | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !containerId) {
      navigate('/');
      return;
    }
    loadContainerDetails();
  }, [projectId, containerId]);

  const loadContainerDetails = async () => {
    if (!projectId || !containerId) return;

    setLoading(true);
    setError(null);

    try {
      const containerData = await containers.get(parseInt(containerId));
      const itemsData = await containers.listItems(parseInt(containerId));
      
      setContainer({
        ...containerData,
        items: itemsData,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load container details');
    } finally {
      setLoading(false);
    }
  };

  if (!projectId || !containerId) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
        Invalid project or container ID
      </Alert>
    );
  }

  return (
    <Paper p="md" radius="sm" pos="relative">
      <LoadingOverlay visible={loading} />
      
      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
          {error}
        </Alert>
      )}

      {container && (
        <Stack gap="md">
          <Title order={2}>{container.name}</Title>

          <Group gap="md">
            <Text>Created: {new Date(container.created_at).toLocaleString()}</Text>
            <Text>Updated: {new Date(container.updated_at).toLocaleString()}</Text>
          </Group>

          <Title order={3}>Items</Title>
          
          {container.items.length === 0 ? (
            <Text c="dimmed">No items found in this container</Text>
          ) : (
            <Table>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th>ID</Table.Th>
                  <Table.Th>Content</Table.Th>
                  <Table.Th>Metadata</Table.Th>
                  <Table.Th>Created</Table.Th>
                  <Table.Th>Updated</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {container.items.map((item) => (
                  <Table.Tr key={item.id}>
                    <Table.Td>{item.id}</Table.Td>
                    <Table.Td>{item.content}</Table.Td>
                    <Table.Td>
                      {Object.entries(item.metadata || {}).map(([key, value]) => (
                        <Badge key={key} mr={5}>
                          {`${key}: ${String(value)}`}
                        </Badge>
                      ))}
                    </Table.Td>
                    <Table.Td>{new Date(item.created_at).toLocaleString()}</Table.Td>
                    <Table.Td>{new Date(item.updated_at).toLocaleString()}</Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
        </Stack>
      )}
    </Paper>
  );
} 