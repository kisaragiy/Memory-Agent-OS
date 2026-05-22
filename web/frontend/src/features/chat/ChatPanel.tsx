import React, { useEffect, useState } from 'react';
import { Box, Button, Paper, Typography } from '@mui/material';
import { Send } from '@mui/icons-material';
import { useControl } from '../../context/ControlContext';
import { extractDisplayFromStream, streamAgent, type StreamStep } from '../../lib/api';
import { Input } from './input';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
  status: 'pending' | 'completed' | 'error';
}

export function ChatPanel() {
  const {
    sessionId,
    mode,
    demo,
    autonomousSession,
    isUserMode,
    setStatusLine,
    bumpRefresh,
    setLastTraceId,
  } = useControl();

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    const saved = localStorage.getItem(`agentos-chat-${sessionId}`);
    if (saved) setMessages(JSON.parse(saved));
  }, [sessionId]);

  useEffect(() => {
    localStorage.setItem(`agentos-chat-${sessionId}`, JSON.stringify(messages));
  }, [messages, sessionId]);

  const handleSendMessage = async () => {
    const text = input.trim();
    if (!text) return;

    const userMsg: Message = {
      id: String(Date.now()),
      role: 'user',
      content: text,
      timestamp: Date.now(),
      status: 'completed',
    };
    const assistantId = String(Date.now() + 1);
    const assistantMsg: Message = {
      id: assistantId,
      role: 'assistant',
      content: demo ? '演示运行中…' : '正在思考…',
      timestamp: Date.now(),
      status: 'pending',
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput('');
    setStatusLine(demo ? '演示模式' : '正在执行任务…');

    const steps: StreamStep[] = [];
    let finalResult: unknown = null;

    try {
      for await (const ev of streamAgent(text, sessionId, {
        mode,
        demo,
        autonomousSession,
        userConfirmed: autonomousSession,
      })) {
        steps.push(ev);
        if (ev.step === 'status' && typeof ev.data?.label === 'string') {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantId ? { ...m, content: ev.data.label as string } : m
            )
          );
          setStatusLine(ev.data.label as string);
        }
        if (ev.step === 'display') {
          const display =
            (ev.data?.text as string) || (ev.data?.label as string) || '';
          if (display) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === assistantId ? { ...m, content: display } : m
              )
            );
          }
        }
        if (ev.step === 'execution_complete') {
          finalResult = ev.data?.result;
          const tid =
            finalResult &&
            typeof finalResult === 'object' &&
            'trace_id' in (finalResult as object)
              ? String((finalResult as { trace_id: string }).trace_id)
              : sessionId;
          setLastTraceId(tid);
        }
      }

      const reply = extractDisplayFromStream(steps, finalResult, isUserMode);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { ...m, content: reply, status: 'completed' }
            : m
        )
      );
      setStatusLine('就绪');
      bumpRefresh();
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: isUserMode
                  ? '任务未能完成，请稍后重试。'
                  : '请求失败',
                status: 'error',
              }
            : m
        )
      );
      setStatusLine('就绪');
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', minHeight: 0 }}>
      <Box sx={{ flex: 1, overflow: 'auto', mb: 2 }}>
        {messages.map((message) => (
          <Box
            key={message.id}
            sx={{
              mb: 2,
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            }}
          >
            <Paper
              elevation={0}
              sx={{
                p: 2,
                maxWidth: '85%',
                borderRadius: 2,
                bgcolor: message.role === 'user' ? '#1b5e20' : 'background.paper',
              }}
            >
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {message.content}
              </Typography>
              {message.status === 'error' && (
                <Typography variant="caption" color="error">
                  请稍后重试
                </Typography>
              )}
            </Paper>
          </Box>
        ))}
      </Box>
      <Box sx={{ display: 'flex', gap: 1 }}>
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onSend={handleSendMessage}
        />
        <Button
          variant="contained"
          onClick={handleSendMessage}
          disabled={!input.trim()}
          startIcon={<Send />}
        >
          发送
        </Button>
      </Box>
    </Box>
  );
}
