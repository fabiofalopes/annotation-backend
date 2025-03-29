import { useState, useEffect } from 'react';
import { Table, Button, Modal, TextInput, Group, Title, Stack, Paper, LoadingOverlay, Alert, Select } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { IconPlus, IconTrash, IconAlertCircle } from '@tabler/icons-react';
import { users } from '../api/client';
import type { User } from '../api/client';

const USER_ROLES = [
  { value: 'admin', label: 'Admin' },
  { value: 'annotator', label: 'Annotator' },
];

export function UsersView() {
  const [usersList, setUsersList] = useState<User[]>([]);
  const [opened, { open, close }] = useDisclosure(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    role: 'annotator',
    is_active: true,
  });

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Fetching users...');
      const data = await users.list();
      console.log('Users fetched:', data);
      setUsersList(data);
    } catch (error) {
      console.error('Error fetching users:', error);
      setError('Failed to load users. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const validateForm = () => {
    if (!newUser.username.trim()) {
      setFormError('Username is required');
      return false;
    }
    if (!newUser.email.trim()) {
      setFormError('Email is required');
      return false;
    }
    if (!newUser.email.includes('@')) {
      setFormError('Please enter a valid email address');
      return false;
    }
    if (!newUser.password.trim()) {
      setFormError('Password is required');
      return false;
    }
    if (newUser.password.length < 8) {
      setFormError('Password must be at least 8 characters long');
      return false;
    }
    setFormError(null);
    return true;
  };

  const handleCreateUser = async () => {
    if (!validateForm()) return;

    try {
      setError(null);
      console.log('Creating user:', { ...newUser, password: '***' });
      await users.create(newUser);
      close();
      fetchUsers();
      setNewUser({
        username: '',
        email: '',
        password: '',
        role: 'annotator',
        is_active: true,
      });
    } catch (error) {
      console.error('Error creating user:', error);
      setError('Failed to create user. Please try again.');
    }
  };

  const handleDeleteUser = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this user?')) return;

    try {
      setError(null);
      console.log('Deleting user:', id);
      await users.delete(id);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user. Please try again.');
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
          <Title order={2}>Users Management</Title>
          <Button
            leftSection={<IconPlus size={14} />}
            onClick={open}
          >
            Create User
          </Button>
        </Group>

        <Table highlightOnHover withTableBorder>
          <Table.Thead>
            <Table.Tr>
              <Table.Th>ID</Table.Th>
              <Table.Th>Username</Table.Th>
              <Table.Th>Email</Table.Th>
              <Table.Th>Role</Table.Th>
              <Table.Th>Status</Table.Th>
              <Table.Th>Actions</Table.Th>
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {usersList.map((user) => (
              <Table.Tr key={user.id}>
                <Table.Td>{user.id}</Table.Td>
                <Table.Td>{user.username}</Table.Td>
                <Table.Td>{user.email}</Table.Td>
                <Table.Td>{user.role}</Table.Td>
                <Table.Td>{user.is_active ? 'Active' : 'Inactive'}</Table.Td>
                <Table.Td>
                  <Button
                    variant="subtle"
                    color="red"
                    size="xs"
                    onClick={() => handleDeleteUser(user.id)}
                    leftSection={<IconTrash size={14} />}
                  >
                    Delete
                  </Button>
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>

        <Modal opened={opened} onClose={close} title="Create New User">
          <Stack>
            {formError && (
              <Alert icon={<IconAlertCircle size={16} />} title="Validation Error" color="red">
                {formError}
              </Alert>
            )}
            <TextInput
              label="Username"
              placeholder="Enter username"
              value={newUser.username}
              onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
              required
            />
            <TextInput
              label="Email"
              type="email"
              placeholder="Enter email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
              required
            />
            <TextInput
              label="Password"
              type="password"
              placeholder="Enter password"
              value={newUser.password}
              onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
              required
            />
            <Select
              label="Role"
              placeholder="Select user role"
              data={USER_ROLES}
              value={newUser.role}
              onChange={(value) => setNewUser({ ...newUser, role: value || 'annotator' })}
            />
            <Button onClick={handleCreateUser}>Create User</Button>
          </Stack>
        </Modal>
      </Stack>
    </Paper>
  );
} 