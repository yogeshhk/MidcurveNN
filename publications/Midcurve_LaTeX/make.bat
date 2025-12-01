@echo off
for %%i in (Main_Midcurve_LLM_*.tex) do texify -cp %%i
