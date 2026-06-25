@echo off
chcp 65001 >nul
echo 正在注册亚翔模型每日任务...
schtasks /Create /TN "亚翔集成选股模型" /XML "C:\Users\14989\Documents\Codex\2026-06-25\ni\outputs\github-deploy\task_config.xml" /F
echo.
echo 注册完成! 每天15:30自动运行。
echo 结果查看: C:\Users\14989\Documents\Codex\2026-06-25\ni\outputs\github-deploy\outputs\
echo 日志查看: C:\Users\14989\Documents\Codex\2026-06-25\ni\outputs\github-deploy\outputs\logs\
pause
