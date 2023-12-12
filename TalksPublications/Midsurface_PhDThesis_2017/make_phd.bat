@echo off
for /r %%i in (Main_PhD*.tex) do texify -cp --engine=xetex %%i
