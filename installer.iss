#define MyAppName "Whisper Transcriber"
#define MyAppVersion "1.0.1"
#define MyAppPublisher "Whisper for Windows Team"
#define MyAppURL "https://github.com/yourusername/whisper-for-windows"
#define MyAppExeName "Run Whisper Transcriber.bat"
#define RequiredPythonVersion "3.12.7"

[Setup]
AppId={{738D9A98-D71E-4748-AD2D-D7125D97835B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=no
LicenseFile=LICENSE
OutputDir=release
OutputBaseFilename=WhisperTranscriber_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
; Comment out the icon if you don't have one yet
; SetupIconFile=resources\app_icon.ico
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

; Check for Python before installation
[Code]
// Custom function to run a command and get its output
function ExecGetOutput(const Filename, Params: string; var ResultStr: string): Boolean;
var
  TempFilename: string;
  ResultCode: Integer;
  Contents: TArrayOfString;
begin
  Result := False;
  ResultStr := '';
  TempFilename := ExpandConstant('{tmp}\execoutput.txt');
  
  // Execute the command, redirecting output to our temp file
  if Exec(Filename, Params + ' > "' + TempFilename + '"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
  begin
    if ResultCode = 0 then
    begin
      if LoadStringsFromFile(TempFilename, Contents) then
      begin
        if GetArrayLength(Contents) > 0 then
        begin
          ResultStr := Contents[0];
          Result := True;
        end;
      end;
    end;
  end;
  
  // Clean up temp file
  if FileExists(TempFilename) then
    DeleteFile(TempFilename);
end;

// Function to check if a string exactly matches the required version
function IsExactVersion(InstalledVersion, RequiredVersion: string): Boolean;
begin
  // Simple exact string comparison
  Result := (CompareText(Trim(InstalledVersion), Trim(RequiredVersion)) = 0);
end;

// Function to check if Visual C++ Redistributable is installed
function IsVCRedistInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  // Check for Visual C++ 2015-2022 Redistributable
  Result := RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.0') or
           RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\VisualStudio\14.0') or
           RegKeyExists(HKLM, 'SOFTWARE\Microsoft\VisualStudio\14.1') or 
           RegKeyExists(HKLM, 'SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0');
           
  if not Result then
  begin
    // Also check for installation via registry
    Result := RegKeyExists(HKLM, 'SOFTWARE\Microsoft\DevDiv\VC\Servicing\14.0\RuntimeMinimum');
  end;
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
  PythonInstalled, VCRedistInstalled: Boolean;
  PythonVersion, RequiredVersion: String;
  PythonDownloadURL: String;
begin
  RequiredVersion := '{#RequiredPythonVersion}';
  PythonDownloadURL := 'https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe';
  
  // Try to execute Python to check if it's installed and get its version
  if ExecGetOutput('cmd.exe', '/c python -c "import sys; print(sys.version.split()[0])"', PythonVersion) then
  begin
    PythonVersion := Trim(PythonVersion);
    
    // Check if installed version matches required version exactly
    if IsExactVersion(PythonVersion, RequiredVersion) then
    begin
      // Exact match - Python 3.12.7 is installed
      PythonInstalled := True;
    end
    else
    begin
      // Not an exact match
      MsgBox('Python ' + PythonVersion + ' detected, but version ' + RequiredVersion + ' is required.' + #13#10 +
             'Please install Python ' + RequiredVersion + ' from python.org before installing Whisper Transcriber.' + #13#10 +
             'Make sure to check "Add Python to PATH" during installation.', mbError, MB_OK);
      PythonInstalled := False;
    end;
  end
  else
  begin
    // Python not found
    PythonInstalled := False;
    MsgBox('Python ' + RequiredVersion + ' is required but not detected on your system.' + #13#10 +
           'Please install Python ' + RequiredVersion + ' from python.org before installing Whisper Transcriber.' + #13#10 +
           'Make sure to check "Add Python to PATH" during installation.', mbError, MB_OK);
  end;
  
  // Check for Visual C++ Redistributable
  VCRedistInstalled := IsVCRedistInstalled();
  if not VCRedistInstalled then
  begin
    MsgBox('Microsoft Visual C++ Redistributable is required but not detected.' + #13#10 + 
           'This is needed for PyQt6 and other dependencies to work properly.' + #13#10 +
           'Please install the Microsoft Visual C++ Redistributable 2015-2022 (x64).' + #13#10 +
           'It can be downloaded from: https://aka.ms/vs/17/release/vc_redist.x64.exe', mbInformation, MB_OK);
           
    // Ask if they want to download it now
    if MsgBox('Would you like to download and install the Microsoft Visual C++ Redistributable now?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://aka.ms/vs/17/release/vc_redist.x64.exe', '', '', SW_SHOW, ewNoWait, ResultCode);
      MsgBox('Please complete the installation of the Visual C++ Redistributable before continuing.', 
             mbInformation, MB_OK);
    end;
    
    // We still allow installation to proceed, but warn the user
    Result := MsgBox('The application may not work correctly without the Visual C++ Redistributable.' + #13#10 +
                     'Do you want to continue with the installation anyway?', 
                     mbConfirmation, MB_YESNO) = IDYES;
  end
  else
    Result := True;
  
  // If Python is not correctly installed, show message and guide
  if not PythonInstalled then
  begin
    // Ask if they want to download Python now
    if MsgBox('Would you like to download Python ' + RequiredVersion + ' now?', 
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Open the Python download page
      ShellExec('open', PythonDownloadURL, '', '', SW_SHOW, ewNoWait, ResultCode);
      MsgBox('Please complete the installation of Python ' + RequiredVersion + 
             ' before continuing. Make sure to check "Add Python to PATH" during installation.', 
             mbInformation, MB_OK);
    end;
    
    Result := False;  // Abort setup
  end;
end;

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon"; Description: "Create Start Menu shortcut"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; Source files - from the staging directory
Source: "dist\staging\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Check Prerequisites"; Filename: "{app}\check_prerequisites.bat"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
; Option to check prerequisites after installation
Filename: "{app}\check_prerequisites.bat"; Description: "Check prerequisites for the application"; Flags: postinstall skipifsilent

; Option to run the application after installation
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent