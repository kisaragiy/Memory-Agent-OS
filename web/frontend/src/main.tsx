import React from 'react';
import ReactDOM from 'react-dom/client';
import { CssBaseline, GlobalStyles, ThemeProvider } from '@mui/material';
import App from './App';
import { theme } from './theme';
import { ControlProvider } from './context/ControlContext';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <GlobalStyles styles={{ html: { height: '100%' }, body: { height: '100%', margin: 0 }, '#root': { height: '100%' } }} />
      <ControlProvider>
        <App />
      </ControlProvider>
    </ThemeProvider>
  </React.StrictMode>
);
