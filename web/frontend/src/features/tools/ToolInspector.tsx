import React, { useEffect, useState } from 'react';
import { Box, Chip, Paper, Stack, Typography } from '@mui/material';
import { fetchTools, type ControlMode } from '../../lib/api';

interface ToolInspectorProps {
  sessionId: string;
  mode: ControlMode;
}

export function ToolInspector({ sessionId, mode }: ToolInspectorProps) {
  const [tools, setTools] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTools(sessionId, mode)
      .then((data) => {
        const list = data.tools || [];
        setTools(
          list.map((t) => (typeof t === 'string' ? t : (t as { name: string }).name))
        );
      })
      .catch((e) => setError(e.message));
  }, [sessionId, mode]);

  return (
    <Box sx={{ px: 2, pb: 2 }}>
      <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
          已注册工具
        </Typography>
        {error && (
          <Typography variant="caption" color="error">
            {error}
          </Typography>
        )}
        <Stack direction="row" flexWrap="wrap" gap={0.5}>
          {tools.map((name) => (
            <Chip key={name} label={name} size="small" variant="outlined" />
          ))}
        </Stack>
        {!error && tools.length === 0 && (
          <Typography variant="caption" color="text.secondary">
            无工具或未连接服务
          </Typography>
        )}
      </Paper>
    </Box>
  );
}
