' VBScript to launch Plover from source without showing console
' Double-click this file to run Plover silently

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")
strScriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\") - 1)
strPython = strScriptDir & "\.venv3.10\Scripts\python.exe"

' Check if Python exists
If Not objFSO.FileExists(strPython) Then
    MsgBox "Python 3.10 virtual environment not found:" & vbCrLf & strPython, vbCritical, "Plover Error"
    WScript.Quit 1
End If

' Build command with any passed arguments
strCommand = strPython & " -m plover.scripts.dist_main"
If WScript.Arguments.Count > 0 Then
    For i = 0 To WScript.Arguments.Count - 1
        strCommand = strCommand & " """ & WScript.Arguments(i) & """"
    Next
End If

' Run Plover with hidden window (0 = hidden, False = don't wait)
objShell.Run strCommand, 0, False
