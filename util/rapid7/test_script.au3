#include <AutoItConstants.au3>
#pragma compile(Console, True)

Run("C:\Program Files (x86)\Rapid7\AppSpider7\UI\AppSpider.exe")

WinWait("AppSpider", "")
WinSetOnTop ( "AppSpider", "", $WINDOWS_ONTOP )
WinActivate("AppSpider", "")


If Not WinActive("AppSpider") Then
   ConsoleWrite("Waiting")
   WinWaitActive("AppSpider", "", 3)
   WinActivate("AppSpider", "")
EndIf

If Not WinActive("AppSpider") Then
   ConsoleWrite("Waiting")
   WinWaitActive("AppSpider", "", 3)
   WinActivate("AppSpider", "")
EndIf

If Not WinActive("AppSpider") Then
   ConsoleWrite("Waiting")
   WinWaitActive("AppSpider", "", 3)
   WinActivate("AppSpider", "")
EndIf

If Not WinActive("AppSpider") Then
   WinClose("AppSpider", "")
   WinKill("AppSpider", "")
   Exit
EndIf

ConsoleWrite("It passed?")

WinSetState ( "AppSpider", "", @SW_MAXIMIZE )

Opt("MouseCoordMode", 0)
MouseClick($MOUSE_CLICK_PRIMARY, 294, 210, 1)
Sleep(2)
MouseClick($MOUSE_CLICK_PRIMARY, 362, 99, 1)


Sleep(13400000)
WinClose("AppSpider")
WinKill("AppSpider")
