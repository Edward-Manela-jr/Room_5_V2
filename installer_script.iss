[Setup]
AppName=Image Organizer Pro
AppVersion=1.0.0
AppPublisher=Edward Manela Jr
AppPublisherURL=https://github.com/Edward-Manela-jr/Room_5
AppSupportURL=https://github.com/Edward-Manela-jr/Room_5
AppUpdatesURL=https://github.com/Edward-Manela-jr/Room_5
DefaultDirName={pf}\Image Organizer Pro
DefaultGroupName=Image Organizer Pro
AllowNoIcons=yes
LicenseFile=LICENSE.txt
OutputDir=installer
OutputBaseFilename=ImageOrganizerProSetup
; SetupIconFile removed (icon.ico not present). Add this line back if you provide an icon.ico
Compression=lzma
SolidCompression=yes

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ImageOrganizerPro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Image Organizer Pro"; Filename: "{app}\ImageOrganizerPro.exe"
Name: "{commondesktop}\Image Organizer Pro"; Filename: "{app}\ImageOrganizerPro.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\ImageOrganizerPro.exe"; Description: "{cm:LaunchProgram}"; Flags: nowait postinstall skipifsilent