@echo off
for /r %%i in (Main_Seminar_Midcurve_*.tex) do texify --engine=luatex  -cp %%i
