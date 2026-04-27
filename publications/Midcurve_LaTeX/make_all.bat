@echo off
for %%i in (Main_Midcurve_*.tex Main_TopoVal_*.tex) do (
    echo.
    echo === Compiling %%i ===
    pdflatex -interaction=nonstopmode %%i
    pdflatex -interaction=nonstopmode %%i
)
