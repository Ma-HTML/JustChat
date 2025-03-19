[Setup]
AppName=Just Chat
AppVersion=1.0
DefaultDirName={pf}\Just Chat
DefaultGroupName=Just Chat
UninstallDisplayIcon={app}\justchat.exe
OutputDir=.
OutputBaseFilename=JustChatInstaller
Compression=lzma
SolidCompression=yes

[Files]
Source: "C:\Users\slemaire\Downloads\Max\JustChat\justchat.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Just Chat"; Filename: "{app}\justchat.exe"; IconFilename: "{app}\app.ico"
Name: "{commondesktop}\Just Chat"; Filename: "{app}\justchat.exe"; IconFilename: "{app}\app.ico"

[Run]
Filename: "{app}\justchat.exe"; Description: "Lancer Just Chat"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
