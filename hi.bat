@echo off
powershell -NoProfile -Command "Add-Type -AssemblyName PresentationFramework;[System.Windows.MessageBox]::Show('Worked!','Warning',[System.Windows.MessageBoxButton]::OK,[System.Windows.MessageBoxImage]::Warning)"
