@echo off

rmdir /s /q Glossolalia

pyinstaller --onefile --noconsole --icon assets/icon.bmp --name Glossolalia main.py

rmdir /s /q build
mkdir dist\assets\
mkdir dist\data\
xcopy assets dist\assets /s /e /y
xcopy data dist\data /s /e /y
rename dist Glossolalia
del Glossolalia.spec