Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strScriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
strWebotsHome = "C:\Program Files\Webots"
strWebotsExe = strWebotsHome & "\msys64\mingw64\bin\webotsw.exe"
strWorld = strScriptDir & "\worlds\pista_montana_rusa.wbt"

If fso.FileExists(strWorld) Then
    strShortWorld = fso.GetFile(strWorld).ShortPath
Else
    strShortWorld = strWorld
End If

WshShell.CurrentDirectory = strWebotsHome
WshShell.Run """" & strWebotsExe & """ """ & strShortWorld & """", 1, False
