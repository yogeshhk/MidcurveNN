@echo off
for /r %%i in (DevFest_Brunei_MidcurveNN_*.tex) do texify -cp %%i
