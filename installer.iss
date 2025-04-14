#define MyAppName "Whisper Transcriber"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Your Name or Organization"
#define MyAppURL "https://github.com/yourusername/whisper-for-windows"
#define MyAppExeName "Whisper Transcriber.exe"

[Setup]
AppId={{738D9A98-D71E-4748-AD2D-D7125D97835B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=release
OutputBaseFilename=WhisperTranscriber_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Comment out the icon if you don't have one yet
; SetupIconFile=resources\app_icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; For directory-based PyInstaller build
Source: "dist\Whisper Transcriber\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent