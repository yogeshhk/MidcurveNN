echo off
"C:\Program Files\gs\gs9.20\bin"\gswin64.exe -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dNOPAUSE -dQUIET -dBATCH -sOutputFile=%2 %1