import React, { useCallback, useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Divider,
  TextField,
  Button,
  IconButton,
  Stack,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import { MemoryViewer } from './MemoryViewer';
import {
  fetchMemory,
  rememberFact,
  mutateMemory,
  createMemorySnapshot,
  type MemoryPayload,
} from '../../lib/api';

export interface MemoryPanelProps {
  sessionId: string;
  refreshToken?: number;
  mode?: 'user' | 'developer' | 'debug';
}

export function MemoryPanel({ sessionId, refreshToken = 0, mode = 'user' }: MemoryPanelProps) {
  const [memory, setMemory] = useState<MemoryPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [factInput, setFactInput] = useState('');
  const [saving, setSaving] = useState(false);
  const [recordId, setRecordId] = useState('');
  const isDev = mode === 'developer' || mode === 'debug';

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const snap = await fetchMemory(sessionId, mode);
      setMemory(snap.memory ?? null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load memory');
    } finally {
      setLoading(false);
    }
  }, [sessionId, mode]);

  useEffect(() => {
    load();
  }, [load, refreshToken, mode]);

  const handleRemember = async () => {
    const text = factInput.trim();
    if (!text) return;
    setSaving(true);
    try {
      await rememberFact(text, sessionId);
      setFactInput('');
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Remember failed');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ flex: 1, overflow: 'auto', px: 2, pt: 2 }}>
      <Paper elevation={0} sx={{ p: 2, borderRadius: 2, backgroundColor: '#1e1e1e' }}>
        <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 1 }}>
          <Typography variant="h6" color="primary.main">
            Memory
          </Typography>
          <IconButton size="small" onClick={load} disabled={loading} aria-label="refresh">
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Stack>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
          Agent: {sessionId}
        </Typography>

        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <TextField
            size="small"
            fullWidth
            placeholder="Remember a fact…"
            value={factInput}
            onChange={(e) => setFactInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRemember()}
            disabled={saving}
            sx={{ '& .MuiInputBase-root': { fontSize: 14 } }}
          />
          <Button
            variant="contained"
            size="small"
            onClick={handleRemember}
            disabled={saving || !factInput.trim()}
          >
            Save
          </Button>
        </Stack>

        {isDev && (
          <Stack spacing={1} sx={{ mb: 2 }}>
            <Typography variant="caption" color="warning.main">
              开发者治理（经内核 execute_memory_op）
            </Typography>
            <TextField
              size="small"
              placeholder="record_id（删除/覆盖）"
              value={recordId}
              onChange={(e) => setRecordId(e.target.value)}
            />
            <Stack direction="row" flexWrap="wrap" gap={0.5}>
              <Button
                size="small"
                color="error"
                disabled={!recordId}
                onClick={async () => {
                  try {
                    await mutateMemory(
                      {
                        target: 'semantic',
                        action: 'delete',
                        record_id: recordId,
                      },
                      sessionId
                    );
                    await load();
                  } catch (e) {
                    setError(e instanceof Error ? e.message : 'Delete failed');
                  }
                }}
              >
                删除
              </Button>
              <Button
                size="small"
                onClick={async () => {
                  try {
                    await createMemorySnapshot(sessionId);
                    await load();
                  } catch (e) {
                    setError(e instanceof Error ? e.message : 'Snapshot failed');
                  }
                }}
              >
                快照
              </Button>
            </Stack>
          </Stack>
        )}

        <Divider sx={{ mb: 2, borderColor: '#333' }} />
        <MemoryViewer memory={memory} loading={loading} error={error} showIds={isDev} />
      </Paper>
    </Box>
  );
}
