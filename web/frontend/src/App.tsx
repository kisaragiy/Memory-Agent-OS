import React from 'react';
import { Box, Grid } from '@mui/material';
import { ModeBar } from './components/ModeBar';
import { useControl } from './context/ControlContext';
import { ChatPanel } from './features/chat/ChatPanel';
import { DebugPanel } from './features/debug/DebugPanel';
import { MemoryPanel } from './features/memory/MemoryPanel';
import { ToolInspector } from './features/tools/ToolInspector';
import { TraceViewer } from './features/trace/TraceViewer';
import { DesktopLivePanel } from './features/desktop/DesktopLivePanel';

export default function App() {
  const { sessionId, mode, isUserMode, refreshToken } = useControl();

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: 'background.default' }}>
      <Box
        sx={{
          width: 320,
          borderRight: 1,
          borderColor: 'divider',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
        }}
      >
        <MemoryPanel sessionId={sessionId} mode={mode} refreshToken={refreshToken} />
        {!isUserMode && <ToolInspector sessionId={sessionId} mode={mode} />}
        {!isUserMode && <DebugPanel />}
      </Box>

      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <ModeBar />
        <Grid container sx={{ flex: 1, minHeight: 0 }}>
          <Grid item xs={12} md={isUserMode ? 12 : 7} sx={{ display: 'flex', flexDirection: 'column', p: 2, minHeight: 0 }}>
            <ChatPanel />
          </Grid>
          {!isUserMode && (
            <Grid item xs={12} md={5} sx={{ p: 2, pt: 0, overflow: 'auto', borderLeft: 1, borderColor: 'divider' }}>
              <DesktopLivePanel />
              <TraceViewer />
            </Grid>
          )}
        </Grid>
      </Box>
    </Box>
  );
}
