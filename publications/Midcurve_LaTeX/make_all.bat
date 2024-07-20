@echo off
for %%i in (Main_*.tex) do texify -cp %%i
