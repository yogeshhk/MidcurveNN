@echo off
for /r %%i in (Main_Paper_*.tex) do texify --engine=luatex  -cp %%i
