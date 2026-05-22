#!/usr/bin/env bash
# 结束卡住的测试/重复启动的服务进程
echo "结束 background_test / playwright / 重复 agent_service …"
pkill -f "background_test_capture" 2>/dev/null || true
pkill -f "fast_hr_test" 2>/dev/null || true
pkill -f "playwright.*chromium" 2>/dev/null || true
# 勿杀用户手动开的 agent_service；仅杀由本脚本标记的（可选）
echo "完成。可重新运行: bash scripts/fast_hr_test.py"
