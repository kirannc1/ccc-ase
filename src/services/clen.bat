@echo off
echo Deleting Dockerignored Python clutter...

:: Delete Python cache folders and files
FOR /d /r . %%d IN (__pycache__) DO @IF EXIST "%%d" rd /s /q "%%d"
del /s /q /f *.pyc *.pyo *.pyd

:: Delete Virtual Environments
FOR /d /r . %%d IN (venv) DO @IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r . %%d IN (.venv) DO @IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r . %%d IN (env) DO @IF EXIST "%%d" rd /s /q "%%d"

:: Delete Test and Coverage cache
FOR /d /r . %%d IN (.pytest_cache) DO @IF EXIST "%%d" rd /s /q "%%d"
FOR /d /r . %%d IN (.tox) DO @IF EXIST "%%d" rd /s /q "%%d"
del /s /q /f .coverage
FOR /d /r . %%d IN (htmlcov) DO @IF EXIST "%%d" rd /s /q "%%d"

:: Delete OS junk
del /s /q /f /a:h .DS_Store
del /s /q /f *.log

echo Cleanup complete!
pause
