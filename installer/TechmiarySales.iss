; Inno Setup script — builds TechmiarySales-Setup.exe (Start menu + desktop shortcut + uninstaller).
#define AppName "Techmiary Sales Manager"
#ifndef AppVersion
  #define AppVersion "1.0.0"
#endif

[Setup]
AppId={{6F1C2B7A-4E2D-4C8B-9B1E-7A3D5C2E9F10}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=Techmiary Technology Concepts
AppPublisherURL=https://techmiary.tech
DefaultDirName={autopf}\Techmiary Sales Manager
DefaultGroupName=Techmiary
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=..\dist
OutputBaseFilename=TechmiarySales-Setup
SetupIconFile=..\assets\techmiary.ico
UninstallDisplayIcon={app}\TechmiarySales.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Shortcuts:"

[Files]
Source: "..\dist\TechmiarySales.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\TechmiarySales.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\TechmiarySales.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\TechmiarySales.exe"; Description: "Open {#AppName} now"; Flags: nowait postinstall skipifsilent

; Sales records live in %APPDATA%\TechmiarySales and are kept when the program is uninstalled.
