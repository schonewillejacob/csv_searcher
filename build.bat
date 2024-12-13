@echo off
set TARGET_SCRIPT="bin\CSVSearchTool.pyw"
set TARGET_ICON="assets\csv_icon_2.ico"


echo:
del CSVSearchTool.exe


echo Running pyinstaller...
pyinstaller -F %TARGET_SCRIPT%

echo:
echo Cleanup of pyinstaller...
move dist\*.exe .

rd /s /q dist


echo:
timeout 15

@echo on