@echo off
for /r %%i in (Main_*.tex) do texify --engine=luatex  -cp %%i
