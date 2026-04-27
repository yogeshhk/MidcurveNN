@echo off
for %%i in (Main_Midcurve_Presentation*.tex) do (
    pdflatex -interaction=nonstopmode %%i
    pdflatex -interaction=nonstopmode %%i
)
