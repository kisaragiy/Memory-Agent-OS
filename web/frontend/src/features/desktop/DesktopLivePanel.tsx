import React, { useMemo } from 'react';
import { Box, Paper, Typography, Link } from '@mui/material';
import { getApiBase } from '../../lib/api';

/** Phase 5 — live MJPEG-style desktop preview (developer only). */
export function DesktopLivePanel() {
  const streamSrc = useMemo(
    () => `${getApiBase()}/api/desktop/stream?interval_ms=1200&t=${Date.now()}`,
    []
  );
  const shotSrc = `${getApiBase()}/api/desktop/screenshot`;

  return (
    <Paper sx={{ p: 1.5, mb: 2 }} variant="outlined">
      <Typography variant="subtitle2" gutterBottom>
        桌面实况（Phase 5）
      </Typography>
      <Box
        sx={{
          position: 'relative',
          bgcolor: '#111',
          borderRadius: 1,
          overflow: 'hidden',
          minHeight: 120,
          maxHeight: 220,
        }}
      >
        <Box
          component="img"
          src={streamSrc}
          alt="Windows desktop live"
          sx={{
            width: '100%',
            height: 'auto',
            maxHeight: 220,
            objectFit: 'contain',
            display: 'block',
          }}
          onError={(e) => {
            const img = e.target as HTMLImageElement;
            img.src = `${shotSrc}?t=${Date.now()}`;
          }}
        />
      </Box>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
        流式刷新约 1.2s/帧；若黑屏请确认服务已设 AGENT_WINDOWS_DESKTOP=1。
        <Link href={shotSrc} target="_blank" rel="noreferrer" sx={{ ml: 0.5 }}>
          单帧截图
        </Link>
      </Typography>
    </Paper>
  );
}
