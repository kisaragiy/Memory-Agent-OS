@echo off
chcp 65001 >nul
pip install reportlab pypdf -q
python C:\面试\build_resume_pdf.py
if exist C:\面试\resume_verify.txt type C:\面试\resume_verify.txt
pause
