@echo off
for /r %%i in (Main_PhD_*.tex) do texify -cp --engine=xetex %%i
