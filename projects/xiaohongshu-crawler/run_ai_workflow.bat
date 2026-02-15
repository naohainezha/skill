@echo off
chcp 65001 >nul
echo ============================================
echo 小红书AI采集与生成 - 完整工作流
echo ============================================
echo.

echo 正在检查API密钥...
echo.

REM 检查环境变量
if defined ZHIPU_API_KEY (
    echo [GLM-4] 已配置
) else (
    echo [GLM-4] 未配置 - 请设置 ZHIPU_API_KEY
)

if defined MOONSHOT_API_KEY (
    echo [Kimi K2] 已配置
) else (
    echo [Kimi K2] 未配置 - 请设置 MOONSHOT_API_KEY
)

echo.
echo ============================================
echo.

REM 提示输入关键词
set /p KEYWORD="请输入搜索关键词: "
if "%KEYWORD%"=="" (
    echo 错误：关键词不能为空
    pause
    exit /b 1
)

REM 提示输入数量
set /p CRAWL_COUNT="采集数量 (默认10): "
if "%CRAWL_COUNT%"=="" set CRAWL_COUNT=10

set /p GEN_COUNT="生成数量 (默认5): "
if "%GEN_COUNT%"=="" set GEN_COUNT=5

echo.
echo ============================================
echo 开始执行工作流
echo ============================================
echo 关键词: %KEYWORD%
echo 采集数量: %CRAWL_COUNT%
echo 生成数量: %GEN_COUNT%
echo.
echo 模型配置:
echo   采集阶段: GLM-4
echo   分析阶段: Kimi K2
echo   生成阶段: Kimi K2
echo ============================================
echo.

REM 切换到爬虫目录
cd /d "D:\xiaohongshu-crawler"

REM 运行工作流
python ai_workflow.py "%KEYWORD%" --crawl %CRAWL_COUNT% --generate %GEN_COUNT%

echo.
echo ============================================
echo 工作流执行完成
echo ============================================
echo.
echo 查看输出文件: D:\xiaohongshu-crawler\output\
echo.
pause
