import React, { useMemo } from 'react';
import { Box, Paper, Typography } from '@mui/material';
import type { ExecutionGraphData } from '../../lib/api';

interface ExecutionGraphProps {
  graph: ExecutionGraphData | null;
  loading?: boolean;
}

export function ExecutionGraph({ graph, loading }: ExecutionGraphProps) {
  const layout = useMemo(() => {
    if (!graph?.nodes?.length) return null;
    const n = graph.nodes.length;
    const w = 400;
    const h = 120;
    const gap = n > 1 ? w / (n - 1) : w / 2;
    const nodes = graph.nodes.map((node, i) => ({
      ...node,
      cx: n > 1 ? 40 + i * gap : w / 2,
      cy: h / 2,
    }));
    const edges = (graph.edges || []).map((e) => {
      const from = nodes.find((x) => x.id === e.from);
      const to = nodes.find((x) => x.id === e.to);
      return { from, to };
    });
    return { nodes, edges, w, h };
  }, [graph]);

  return (
    <Paper elevation={0} sx={{ p: 2, borderRadius: 2, bgcolor: 'background.paper' }}>
      <Typography variant="subtitle2" color="primary" sx={{ mb: 1 }}>
        执行流程图
      </Typography>
      <Box
        sx={{
          width: '100%',
          height: 140,
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {loading && (
          <Typography variant="caption" color="text.secondary">
            加载中…
          </Typography>
        )}
        {!loading && !layout && (
          <Typography variant="caption" color="text.secondary">
            发送任务后显示执行链
          </Typography>
        )}
        {layout && (
          <svg width="100%" height="100%" viewBox={`0 0 ${layout.w} ${layout.h}`}>
            {layout.edges.map((e, i) =>
              e.from && e.to ? (
                <line
                  key={i}
                  x1={e.from.cx}
                  y1={e.from.cy}
                  x2={e.to.cx}
                  y2={e.to.cy}
                  stroke="#555"
                  strokeWidth={2}
                />
              ) : null
            )}
            {layout.nodes.map((node) => (
              <g key={node.id}>
                <circle cx={node.cx} cy={node.cy} r={8} fill="#1976d2" />
                <text
                  x={node.cx}
                  y={node.cy - 14}
                  textAnchor="middle"
                  fill="#ccc"
                  fontSize={9}
                >
                  {node.name.length > 12 ? `${node.name.slice(0, 10)}…` : node.name}
                </text>
              </g>
            ))}
          </svg>
        )}
      </Box>
    </Paper>
  );
}
