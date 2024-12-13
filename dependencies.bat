@echo off

echo:
echo Installing dependencies...

@echo on
pip install PyQt5
pip install -U matplotlib
pip install pandas

echo:
echo Finished.
@echo off
timeout 15