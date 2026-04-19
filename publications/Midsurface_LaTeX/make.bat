@echo off
for %%i in (Main_TopoVal_expanded_v1_2026*.tex) do texify -cp %%i
