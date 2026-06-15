@echo off
title PlayerReportManager — Crystalfbft
echo Checking dependencies...
python -m pip install -r requirements.txt -q
echo.
python main.py
pause
