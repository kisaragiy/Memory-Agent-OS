/**
 * Agent OS Desktop — spawns python -m agent_service and loads UI.
 * Windows: use native Python for pyautogui; set PYTHON env if needed.
 */

const { app, BrowserWindow, shell } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

const PORT = process.env.AGENT_SERVICE_PORT || '8787';
const HOST = process.env.AGENT_SERVICE_HOST || '127.0.0.1';
const ROOT = path.resolve(__dirname, '..');
const isDev = process.env.AGENT_ELECTRON_DEV === '1';
const UI_URL = isDev
  ? 'http://127.0.0.1:5173'
  : `http://${HOST}:${PORT}/app/`;

let pyProc = null;
let mainWindow = null;

function waitForServer(url, attempts = 60) {
  return new Promise((resolve, reject) => {
    let n = 0;
    const tick = () => {
      const req = http.get(url, (res) => {
        res.resume();
        if (res.statusCode && res.statusCode < 500) resolve();
        else retry();
      });
      req.on('error', retry);
      req.setTimeout(2000, () => {
        req.destroy();
        retry();
      });
    };
    const retry = () => {
      n += 1;
      if (n >= attempts) reject(new Error('Agent service did not start'));
      else setTimeout(tick, 500);
    };
    tick();
  });
}

function startPythonService() {
  if (isDev) return Promise.resolve();
  const python = process.env.AGENT_PYTHON || 'python';
  const env = {
    ...process.env,
    AGENT_SERVICE_PORT: PORT,
    AGENT_SERVICE_HOST: HOST,
    AGENT_STATIC_DIR: path.join(ROOT, 'web'),
    AGENT_REACT_DIST: path.join(ROOT, 'web', 'frontend', 'dist'),
  };
  pyProc = spawn(python, ['-m', 'agent_service'], {
    cwd: ROOT,
    env,
    stdio: isDev ? 'inherit' : 'pipe',
  });
  pyProc.on('error', (err) => console.error('Python spawn failed:', err));
  return waitForServer(`http://${HOST}:${PORT}/api/health`);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    title: 'Agent OS',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  mainWindow.loadURL(UI_URL);
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

app.whenReady().then(async () => {
  try {
    await startPythonService();
    if (isDev) await waitForServer('http://127.0.0.1:5173');
    createWindow();
  } catch (e) {
    console.error(e);
    app.quit();
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', () => {
  if (pyProc) {
    pyProc.kill();
    pyProc = null;
  }
});
