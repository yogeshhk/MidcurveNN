@echo off
for %%i in (Main*.tex) do texify -cp %%i
