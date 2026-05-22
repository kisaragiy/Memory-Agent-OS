# Playwright Chromium 手动安装（WSL）

自动 `python3 -m playwright install chromium` 失败时，按本文把浏览器放到固定目录，测试脚本即可继续截图。

---

## 一、要放到哪里（最重要）

在 **WSL Ubuntu** 里，默认路径是：

```text
/home/zwq/.cache/ms-playwright/
```

你的项目用户若不是 `zwq`，把 `zwq` 换成 `echo $USER` 的结果。

### 可选：自定义目录

若不想用 `.cache`，可设环境变量（写入 `~/.bashrc`）：

```bash
export PLAYWRIGHT_BROWSERS_PATH=/home/zwq/playwright-browsers
```

然后把浏览器解压到 **`/home/zwq/playwright-browsers/`**（与上面变量一致即可）。

---

## 二、目录里应该长什么样

解压/拷贝完成后，大致结构如下（中间 `chromium-1091` 数字随 Playwright 版本变化，**以你包里的文件夹名为准**）：

```text
/home/zwq/.cache/ms-playwright/
├── chromium-1091/              ← 必须有，名字以 chromium- 开头
│   └── chrome-linux/
│       ├── chrome              ← 可执行文件（必须存在）
│       ├── libvk_swiftshader.so
│       └── …
└── ffmpeg-1009/                ← 可选，没有有时也能跑截图
```

在 WSL 执行权限（**必做**）：

```bash
chmod -R +x /home/zwq/.cache/ms-playwright/chromium-*/chrome-linux/chrome
```

---

## 三、怎么拿到这个文件夹

### 方法 A：在能联网的电脑用 Playwright 下载（推荐）

任意一台 **Linux 或 WSL**（能访问外网）：

```bash
pip install playwright
python3 -m playwright install chromium
# 查看打好的包
ls ~/.cache/ms-playwright/
```

把整个 `ms-playwright` 目录打成 zip，拷到本机 WSL：

```bash
# 在 WSL 里
mkdir -p ~/.cache
unzip ms-playwright.zip -d ~/.cache/
# 或: cp -a /mnt/c/Users/你的用户名/Downloads/ms-playwright ~/.cache/
chmod -R +x ~/.cache/ms-playwright/chromium-*/chrome-linux/chrome
```

### 方法 B：从 Windows 已安装的 Playwright 拷贝（仅当也是 Linux 包时）

Windows 默认在：

```text
C:\Users\<用户名>\AppData\Local\ms-playwright\
```

注意：里面是 **win32** 的 `chrome.exe`，**不能**给 WSL 里的 Linux Python 用。  
WSL 必须用 **chrome-linux** 那一套，请仍用方法 A 在 WSL/另一台 Linux 下载。

### 方法 C：同事/镜像机拷贝

直接复制对方 WSL 的 `~/.cache/ms-playwright` 整个文件夹到你的同路径。

---

## 四、验证是否放好

在项目根目录 WSL 执行：

```bash
cd /home/zwq/AgentOSSystem
pip install -r requirements-test-capture.txt
python3 scripts/print_playwright_paths.py
python3 -c "from playwright.sync_api import sync_playwright; p=sync_playwright().start(); b=p.chromium.launch(headless=True); print('OK'); b.close(); p.stop()"
```

看到 `OK` 即可运行：

```bash
python3 scripts/fast_hr_test.py
```

或 Windows 双击：`desktop-os-tests/后台自动测试截图.cmd`

---

## 五、查看本机需要的精确路径

```bash
python3 scripts/print_playwright_paths.py
```

会打印当前 Playwright 版本和 `chromium-xxxx` 是否已存在。

---

## 六、常见问题

| 现象 | 处理 |
|------|------|
| `Executable doesn't exist at .../chrome-linux/chrome` | 路径错或 chmod 未执行 |
| 只有 `chromium_headless_shell-xxxx` | Playwright 1.46+ 可能用这个目录，把整个 `ms-playwright` 原样拷贝即可 |
| 下载极慢 | 用方法 A 在别的网络环境打好包再 U 盘/网盘拷入 |

放好并验证 `OK` 后，告诉我一声或再跑「后台自动测试截图」，我会继续用浏览器截图生成 HR 报告。
