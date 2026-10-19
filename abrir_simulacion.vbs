Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
strWebotsHome = "C:\Program Files\Webots"
strWebotsExe = strWebotsHome & "\msys64\mingw64\bin\webotsw.exe"
strWorld = strScriptDir & "\worlds\pista_montana_rusa.wbt"

WshShell.CurrentDirectory = strWebotsHome
WshShell.Run """" & strWebotsExe & """ """ & strWorld & """", 1, False
