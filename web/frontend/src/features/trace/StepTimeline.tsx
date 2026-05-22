import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  Paper,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import type { TraceStep } from '../../lib/api';

interface StepTimelineProps {
  steps: TraceStep[];
  loading?: boolean;
  onRefresh?: () => void;
}

function formatTime(ts?: string | number): string {
  if (!ts) return '—';
  try {
    return new Date(ts).toLocaleString();
  } catch {
    return String(ts);
  }
}

export function StepTimeline({ steps, loading, onRefresh }: StepTimelineProps) {
  return (
    <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Typography
        variant="subtitle2"
        color="primary"
        sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}
      >
        步骤时间线
        {onRefresh && (
          <Tooltip title="刷新 trace">
            <IconButton size="small" onClick={onRefresh} disabled={loading}>
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        )}
      </Typography>
      {loading && (
        <Typography variant="caption" color="text.secondary">
          加载中…
        </Typography>
      )}
      {!loading && steps.length === 0 && (
        <Typography variant="caption" color="text.secondary">
          暂无步骤
        </Typography>
      )}
      <List dense disablePadding>
        {steps.map((step, i) => (
          <ListItem key={`${step.step}-${i}`} disableGutters sx={{ py: 0.5 }}>
            <ListItemText
              primary={step.step}
              secondary={formatTime(step.timestamp)}
              primaryTypographyProps={{ variant: 'body2' }}
              secondaryTypographyProps={{ variant: 'caption' }}
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}
