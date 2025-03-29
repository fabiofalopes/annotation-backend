import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Title,
  Stack,
  FileInput,
  TextInput,
  Button,
  Group,
  Alert,
  Progress,
  Text,
  JsonInput,
  LoadingOverlay,
} from '@mantine/core';
import { useInterval } from '@mantine/hooks';
import { IconAlertCircle, IconUpload, IconCheck } from '@tabler/icons-react';
import { imports } from '../api/client';
import type { ImportProgress, ValidateCSVResponse } from '../api/client';

interface ImportDataViewProps {
  projectId?: number;
}

export function ImportDataView({ projectId: propProjectId }: ImportDataViewProps) {
  const { projectId: paramProjectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const projectId = propProjectId || (paramProjectId ? parseInt(paramProjectId) : undefined);
  const [file, setFile] = useState<File | null>(null);
  const [name, setName] = useState('');
  const [validationResult, setValidationResult] = useState<ValidateCSVResponse | null>(null);
  const [metadataColumns, setMetadataColumns] = useState('');
  const [importId, setImportId] = useState<string | null>(null);
  const [importProgress, setImportProgress] = useState<ImportProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isValidating, setIsValidating] = useState(false);
  const [isImporting, setIsImporting] = useState(false);

  // Redirect if no projectId
  useEffect(() => {
    if (!projectId) {
      navigate('/');
    }
  }, [projectId, navigate]);

  // Poll for import progress
  const interval = useInterval(() => {
    if (importId && importProgress?.status !== 'completed' && importProgress?.status !== 'failed') {
      checkImportProgress();
    }
  }, 1000);

  useEffect(() => {
    if (importId) {
      interval.start();
      return interval.stop;
    }
  }, [importId]);

  const validateFile = async () => {
    if (!file) return;
    setError(null);
    setIsValidating(true);

    try {
      const result = await imports.validateCSV(file, metadataColumns || undefined);
      setValidationResult(result);
      if (!result.valid) {
        setError('File validation failed. Please check the column mappings.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'File validation failed');
      setValidationResult(null);
    } finally {
      setIsValidating(false);
    }
  };

  const startImport = async () => {
    if (!file || !name || !projectId) return;
    setError(null);
    setIsImporting(true);

    try {
      const result = await imports.importChatRoom(
        projectId,
        file,
        name,
        metadataColumns || undefined
      );
      setImportId(result.import_id);
      await checkImportProgress();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Import failed to start');
    } finally {
      setIsImporting(false);
    }
  };

  const checkImportProgress = async () => {
    if (!importId) return;
    try {
      const progress = await imports.getProgress(importId);
      setImportProgress(progress);
      if (progress.error) {
        setError(progress.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check import progress');
    }
  };

  const cancelImport = async () => {
    if (!importId) return;
    try {
      await imports.cancel(importId);
      await checkImportProgress();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel import');
    }
  };

  const retryImport = async () => {
    if (!importId) return;
    try {
      const result = await imports.retry(importId);
      setImportId(result.import_id);
      await checkImportProgress();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to retry import');
    }
  };

  const resetImport = () => {
    setFile(null);
    setName('');
    setValidationResult(null);
    setMetadataColumns('');
    setImportId(null);
    setImportProgress(null);
    setError(null);
  };

  const renderProgress = () => {
    if (!importProgress) return null;

    const progress = Math.round((importProgress.processed_rows / importProgress.total_rows) * 100);
    const isComplete = importProgress.status === 'completed';
    const isFailed = importProgress.status === 'failed';
    const isCancelled = importProgress.status === 'cancelled';

    return (
      <Stack>
        <Progress
          value={progress}
          color={isComplete ? 'green' : isFailed || isCancelled ? 'red' : 'blue'}
          striped
          animated={!isComplete && !isFailed && !isCancelled}
        />
        <Group justify="space-between">
          <Text size="sm">
            {importProgress.processed_rows} / {importProgress.total_rows} rows processed
          </Text>
          <Text size="sm" c={isComplete ? 'green' : isFailed ? 'red' : 'blue'}>
            {importProgress.status.toUpperCase()}
          </Text>
        </Group>
        {!isComplete && !isFailed && !isCancelled && (
          <Button color="red" onClick={cancelImport}>
            Cancel Import
          </Button>
        )}
        {(isFailed || isCancelled) && (
          <Button color="blue" onClick={retryImport}>
            Retry Import
          </Button>
        )}
        {isComplete && (
          <Button color="green" onClick={resetImport}>
            Start New Import
          </Button>
        )}
      </Stack>
    );
  };

  if (!projectId) {
    return (
      <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
        No project ID provided
      </Alert>
    );
  }

  return (
    <Paper p="md" radius="sm" pos="relative">
      <LoadingOverlay visible={isValidating || isImporting} />
      <Stack>
        <Title order={2}>Import Data</Title>

        {error && (
          <Alert icon={<IconAlertCircle size={16} />} title="Error" color="red">
            {error}
          </Alert>
        )}

        {!importId && (
          <>
            <FileInput
              label="CSV File"
              placeholder="Choose file"
              accept=".csv"
              value={file}
              onChange={setFile}
              leftSection={<IconUpload size={14} />}
              required
            />

            <TextInput
              label="Container Name"
              placeholder="Enter a name for the data container"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <JsonInput
              label="Metadata Columns"
              placeholder="Enter metadata column mappings as JSON"
              value={metadataColumns}
              onChange={setMetadataColumns}
              formatOnBlur
              autosize
              minRows={4}
            />

            <Group>
              <Button
                onClick={validateFile}
                disabled={!file}
                leftSection={<IconUpload size={14} />}
              >
                Validate File
              </Button>

              {validationResult?.valid && (
                <Button
                  onClick={startImport}
                  disabled={!name}
                  leftSection={<IconCheck size={14} />}
                  color="green"
                >
                  Start Import
                </Button>
              )}
            </Group>

            {validationResult && (
              <Alert
                icon={validationResult.valid ? <IconCheck size={16} /> : <IconAlertCircle size={16} />}
                title={validationResult.valid ? 'Validation Successful' : 'Validation Failed'}
                color={validationResult.valid ? 'green' : 'red'}
              >
                <Stack>
                  <Text>Total Rows: {validationResult.total_rows}</Text>
                  <Text>Available Columns:</Text>
                  <Text size="sm" style={{ whiteSpace: 'pre-wrap' }}>
                    {validationResult.columns.join(', ')}
                  </Text>
                </Stack>
              </Alert>
            )}
          </>
        )}

        {importId && renderProgress()}
      </Stack>
    </Paper>
  );
} 