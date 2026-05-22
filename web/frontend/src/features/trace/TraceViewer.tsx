import React, { useCallback, useEffect, useState } from 'react';
import { Alert, Box, Button, Paper, Typography } from '@mui/material';
import { useControl } from '../../context/ControlContext';
import {
  fetchReplay,
  fetchTrace,
  type ExecutionGraphData,
  type TraceStep,
} from '../../lib/api';
import { ExecutionGraph } from './ExecutionGraph';
import { StepTimeline } from './StepTimeline';

export function TraceViewer() {
  const { sessionId, mode, lastTraceId, refreshToken } = useControl();
  const [trace, setTrace] = useState<TraceStep[]>([]);
  const [graph, setGraph] = useState<ExecutionGraphData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const target = lastTraceId || sessionId;
      let steps: TraceStep[] = [];
      let g: ExecutionGraphData | null = null;

      if (lastTraceId && lastTraceId !== sessionId) {
        const replay = await fetchReplay(lastTraceId, mode);
        steps = replay.steps || [];
      } else {
        const data = await fetchTrace(sessionId, mode);
        steps = data.trace || [];
        g = data.graph || null;
      }

      setTrace(steps);
      setGraph(g);
    } catch (e) {
      setError(e instanceof Error ? e.message : '无法加载 trace');
      setTrace([]);
      setGraph(null);
    } finally {
      setLoading(false);
    }
  }, [sessionId, mode, lastTraceId]);

  useEffect(() => {
    load();
  }, [load, refreshToken]);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
      <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
        <Typography variant="h6" color="primary" sx={{ mb: 1 }}>
          执行链
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Trace: {lastTraceId || sessionId}
        </Typography>
        <Button size="small" onClick={load} disabled={loading} sx={{ mt: 1 }}>
          刷新
        </Button>
      </Paper>
      {error && <Alert severity="warning">{error}</Alert>}
      <ExecutionGraph graph={graph} loading={loading} />
      <StepTimeline steps={trace} loading={loading} onRefresh={load} />
    </Box>
  );
}
