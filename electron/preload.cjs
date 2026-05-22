const { contextBridge } = require('electron');

contextBridge.exposeInMainWorld('agentOS', {
  platform: process.platform,
  isDesktop: true,
});
