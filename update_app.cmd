@echo off
cd /d "%~dp0"

echo ==========================================
echo  Prompt Aggregator - Data Update Tool
echo ==========================================
echo.
echo Step 1: Crawling data from nanyo-city.jpn.org...
python scripts/crawl_prompts.py
if errorlevel 1 goto error

echo.
echo Step 2: Categorizing prompts...
python scripts/categorize_prompts.py
if errorlevel 1 goto error

echo.
echo Step 3: Generating single-file HTML app...
python scripts/generate_html.py
if errorlevel 1 goto error

echo.
echo ==========================================
echo  SUCCESS! App has been updated.
echo  Open 'prompt-aggregator.html' to use.
echo ==========================================
pause
exit /b 0

:error
echo.
echo [ERROR] Something went wrong. Please check the logs.
pause
exit /b 1
