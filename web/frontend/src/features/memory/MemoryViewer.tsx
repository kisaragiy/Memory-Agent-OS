import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Stack,
  CircularProgress,
  Alert,
} from '@mui/material';
import type { MemoryPayload } from '../../lib/api';

interface MemoryViewerProps {
  memory: MemoryPayload | null;
  loading?: boolean;
  error?: string | null;
  showIds?: boolean;
}

function formatSecondary(item: {
  importance?: number;
  access_count?: number;
  timestamp?: string;
  role?: string;
}): string {
  const parts: string[] = [];
  if (item.role) parts.push(`role: ${item.role}`);
  if (item.importance != null) parts.push(`importance: ${item.importance}`);
  if (item.access_count != null) parts.push(`access: ${item.access_count}`);
  if (item.timestamp) parts.push(item.timestamp);
  return parts.join(' · ') || '—';
}

export function MemoryViewer({ memory, loading, error, showIds }: MemoryViewerProps) {
  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
        <CircularProgress size={28} />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  if (!memory) {
    return (
      <Typography variant="body2" color="text.secondary">
        No memory loaded. Run the agent or add a fact.
      </Typography>
    );
  }

  const facts = memory.facts || [];
  const episodes = memory.episodes || [];
  const conversation = memory.conversation || [];

  return (
    <Box>
      {facts.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
            Facts ({facts.length})
          </Typography>
          <List dense disablePadding>
            {facts.map((f, i) => (
              <ListItem key={f.id || `fact-${i}`} disableGutters>
                <ListItemText
                  primary={
                    showIds && f.id
                      ? `${f.content} [${f.id.slice(0, 8)}…]`
                      : f.content
                  }
                  secondary={formatSecondary(f)}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {episodes.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
            Episodes ({episodes.length})
          </Typography>
          <List dense disablePadding>
            {episodes.slice(-8).reverse().map((ep, i) => (
              <ListItem key={ep.id || `ep-${i}`} disableGutters>
                <ListItemText
                  primary={ep.summary || ep.content || '(episode)'}
                  secondary={formatSecondary(ep)}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {conversation.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
            Conversation ({conversation.length})
          </Typography>
          <List dense disablePadding>
            {conversation.slice(-6).map((t, i) => (
              <ListItem key={i} disableGutters>
                <ListItemText
                  primary={
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Chip label={t.role} size="small" />
                      <Typography variant="body2" component="span">
                        {t.content.slice(0, 120)}
                        {t.content.length > 120 ? '…' : ''}
                      </Typography>
                    </Stack>
                  }
                  secondary={formatSecondary(t)}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {facts.length === 0 && episodes.length === 0 && conversation.length === 0 && (
        <Typography variant="body2" color="text.secondary">
          Memory store is empty for this agent.
        </Typography>
      )}

      {memory.world_state && Object.keys(memory.world_state).length > 0 && (
        <Box sx={{ mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            World: {JSON.stringify(memory.world_state).slice(0, 200)}…
          </Typography>
        </Box>
      )}
    </Box>
  );
}
