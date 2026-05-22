# -*- coding: utf-8 -*-
"""打印本机 Playwright Chromium 应放置的目录（便于手动拷贝）。"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> int:
    try:
        from playwright._impl._driver import compute_driver_executable, get_driver_env
        from playwright._impl._api_structures import ClientInfo
    except Exception:
        pass

    home = Path.home()
    env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "").strip()
    if env_path:
        base = Path(env_path)
        print("使用环境变量 PLAYWRIGHT_BROWSERS_PATH:")
    else:
        base = home / ".cache" / "ms-playwright"
        print("默认浏览器缓存目录（WSL/Linux）:")

    print(f"  {base}")
    print()
    print("手动放置方式:")
    print("  1. 在能联网的机器执行: pip install playwright && python3 -m playwright install chromium")
    print("  2. 将整个 ms-playwright 文件夹打包")
    print(f"  3. 解压到 WSL: {base}")
    print("  4. 赋予执行权限:")
    print(f"     chmod -R +x {base}/chromium-*/chrome-linux/chrome")
    print()
    if base.is_dir():
        print("当前目录内容:")
        for p in sorted(base.iterdir()):
            print(f"  - {p.name}/")
            if p.name.startswith("chromium"):
                chrome = list(p.glob("chrome-linux/chrome"))
                if chrome:
                    print(f"      chrome: {chrome[0]} ({'存在' if chrome[0].is_file() else '缺失'})")
    else:
        print("(目录尚不存在，解压后应自动出现 chromium-xxxx/)")
    print()
    try:
        import playwright

        print(f"playwright 版本: {playwright.__version__}")
    except Exception as e:
        print(f"playwright 未安装: {e}")
        print("  pip install -r requirements-test-capture.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
