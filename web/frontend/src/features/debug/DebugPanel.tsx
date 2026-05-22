import React from 'react';
import { Box, Paper, Typography } from '@mui/material';
import { useControl } from '../../context/ControlContext';

export function DebugPanel() {
  const { sessionId, mode, demo, health, lastTraceId } = useControl();

  return (
    <Box sx={{ px: 2, pb: 2 }}>
      <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
          调试信息
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          会话: {sessionId}
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          模式: {mode} {demo ? '(演示)' : ''}
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          服务: {health}
        </Typography>
        <Typography variant="caption" display="block" color="text.secondary">
          最近 Trace: {lastTraceId || '—'}
        </Typography>
      </Paper>
    </Box>
  );
}
