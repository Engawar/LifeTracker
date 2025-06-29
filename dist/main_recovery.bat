rem lifetracker.lockを削除することで使用可能になる。
taskkill /im "main.exe"
del "C:\Users\user\AppData\Local\Temp\lifetracker.lock"
start "" "main.exe"
