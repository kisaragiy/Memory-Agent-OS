import React from 'react';
import { Box, Button, Chip, Stack, Typography } from '@mui/material';
import { useControl } from '../context/ControlContext';
import type { ControlMode } from '../lib/api';

const MODES: { id: ControlMode; label: string }[] = [
  { id: 'user', label: '普通模式' },
  { id: 'developer', label: '开发者模式' },
  { id: 'debug', label: '调试 Trace' },
];

export function ModeBar() {
  const {
    mode,
    demo,
    health,
    statusLine,
    setMode,
    toggleDemo,
    autonomousSession,
    toggleAutonomous,
  } = useControl();

  return (
    <Box
      sx={{
        px: 2,
        py: 1,
        borderBottom: 1,
        borderColor: 'divider',
        bgcolor: 'background.paper',
      }}
    >
      <Stack direction="row" alignItems="center" flexWrap="wrap" gap={1}>
        <Typography variant="caption" color="text.secondary">
          运行模式
        </Typography>
        {MODES.map((m) => (
          <Button
            key={m.id}
            size="small"
            variant={mode === m.id && !demo ? 'contained' : 'outlined'}
            onClick={() => setMode(m.id)}
          >
            {m.label}
          </Button>
        ))}
        <Button
          size="small"
          variant={demo ? 'contained' : 'outlined'}
          color="secondary"
          onClick={toggleDemo}
        >
          演示模式
        </Button>
        <Button
          size="small"
          variant={autonomousSession ? 'contained' : 'outlined'}
          color="info"
          onClick={toggleAutonomous}
          disabled={demo || mode === 'user'}
        >
          Phase5 自主循环
        </Button>
        <Chip
          size="small"
          label={health === 'ok' ? '服务在线' : health === 'offline' ? '服务离线' : '…'}
          color={health === 'ok' ? 'success' : health === 'offline' ? 'error' : 'default'}
        />
        <Typography variant="caption" color="primary" sx={{ ml: 'auto' }}>
          {statusLine}
        </Typography>
      </Stack>
    </Box>
  );
}
