@echo off
echo Starting PixelDA Server and UI...

start "PixelDA Server" cmd /k "cd /d c:\sc\projects\pixelda\projects\server && conda activate default && python app.py"

start "PixelDA UI" cmd /k "cd /d c:\sc\projects\pixelda\projects\ui && npm start"

echo Both server and UI are starting in separate windows.
pause
