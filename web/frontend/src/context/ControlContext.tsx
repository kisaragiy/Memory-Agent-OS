import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import {
  ControlMode,
  fetchHealth,
  setControl as apiSetControl,
} from '../lib/api';

const SESSION_KEY = 'agentos-session';
const MODE_KEY = 'agentos-control-mode';
const DEMO_KEY = 'agentos-demo';
const AUTONOMOUS_KEY = 'agentos-autonomous';

interface ControlContextValue {
  sessionId: string;
  mode: ControlMode;
  demo: boolean;
  autonomousSession: boolean;
  isUserMode: boolean;
  health: 'unknown' | 'ok' | 'offline';
  statusLine: string;
  refreshToken: number;
  lastTraceId: string | null;
  setMode: (mode: ControlMode) => void;
  toggleDemo: () => void;
  toggleAutonomous: () => void;
  setStatusLine: (text: string) => void;
  bumpRefresh: () => void;
  setLastTraceId: (id: string | null) => void;
}

const ControlContext = createContext<ControlContextValue | null>(null);

function loadSessionId(): string {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = `web-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function ControlProvider({ children }: { children: React.ReactNode }) {
  const [sessionId] = useState(loadSessionId);
  const [mode, setModeState] = useState<ControlMode>(
    () => (localStorage.getItem(MODE_KEY) as ControlMode) || 'user'
  );
  const [demo, setDemo] = useState(() => localStorage.getItem(DEMO_KEY) === '1');
  const [health, setHealth] = useState<'unknown' | 'ok' | 'offline'>('unknown');
  const [statusLine, setStatusLine] = useState('就绪');
  const [refreshToken, setRefreshToken] = useState(0);
  const [lastTraceId, setLastTraceId] = useState<string | null>(null);

  const isUserMode = mode === 'user' && !demo;

  const syncControl = useCallback(async () => {
    try {
      await apiSetControl(sessionId, { mode, demo });
    } catch {
      /* API may be down during dev */
    }
  }, [sessionId, mode, demo]);

  useEffect(() => {
    syncControl();
  }, [syncControl]);

  useEffect(() => {
    const tick = async () => {
      try {
        const h = await fetchHealth();
        setHealth(h.status === 'ok' ? 'ok' : 'offline');
      } catch {
        setHealth('offline');
      }
    };
    tick();
    const id = setInterval(tick, 30000);
    return () => clearInterval(id);
  }, []);

  const setMode = useCallback((m: ControlMode) => {
    setModeState(m);
    setDemo(false);
    localStorage.setItem(MODE_KEY, m);
    localStorage.setItem(DEMO_KEY, '0');
  }, []);

  const toggleAutonomous = useCallback(() => {
    setAutonomousSession((prev) => {
      const next = !prev;
      localStorage.setItem(AUTONOMOUS_KEY, next ? '1' : '0');
      return next;
    });
  }, []);

  const toggleDemo = useCallback(() => {
    setDemo((prev) => {
      const next = !prev;
      localStorage.setItem(DEMO_KEY, next ? '1' : '0');
      if (next) {
        setModeState('user');
        localStorage.setItem(MODE_KEY, 'user');
      }
      return next;
    });
  }, []);

  const bumpRefresh = useCallback(() => {
    setRefreshToken((n) => n + 1);
  }, []);

  const value = useMemo(
    () => ({
      sessionId,
      mode,
      demo,
      autonomousSession,
      isUserMode,
      health,
      statusLine,
      refreshToken,
      lastTraceId,
      setMode,
      toggleDemo,
      toggleAutonomous,
      setStatusLine,
      bumpRefresh,
      setLastTraceId,
    }),
    [
      sessionId,
      mode,
      demo,
      autonomousSession,
      isUserMode,
      health,
      statusLine,
      refreshToken,
      lastTraceId,
      setMode,
      toggleDemo,
      toggleAutonomous,
    ]
  );

  return (
    <ControlContext.Provider value={value}>{children}</ControlContext.Provider>
  );
}

export function useControl(): ControlContextValue {
  const ctx = useContext(ControlContext);
  if (!ctx) throw new Error('useControl must be used within ControlProvider');
  return ctx;
}
