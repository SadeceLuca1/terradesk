; TerraDesk – Inno Setup Script
; Generates: TerraDesk_Setup.exe
; Inno Setup 6+ required: https://jrsoftware.org/isinfo.php

#define AppName      "TerraDesk"
#define AppVersion   "1.0.0"
#define AppPublisher "SadeceLuca1"
#define AppURL       "https://github.com/SadeceLuca1/terradesk"
#define AppExeName   "TerraDesk.exe"
#define SourceDir    "..\dist"
#define IconFile     "..\icon.ico"

[Setup]
AppId={{A3F8C2D1-4B7E-4F2A-9C3D-TerraDesk1000}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
; Output
OutputDir=..\release
OutputBaseFilename=TerraDesk_Setup
SetupIconFile={#IconFile}
; Compression
Compression=lzma2/ultra64
SolidCompression=yes
; UI
WizardStyle=modern
WizardResizable=no
; Windows version requirement
MinVersion=10.0
; UAC
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english";   MessagesFile: "compiler:Default.isl"
Name: "turkish";   MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon";      Description: "{cm:CreateDesktopIcon}";      GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startmenuicon";    Description: "Create Start Menu shortcut";   GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce
Name: "startup";          Description: "Start TerraDesk with Windows"; GroupDescription: "Options"; Flags: unchecked

[Files]
Source: "{#SourceDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";                Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\Uninstall {#AppName}";      Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";          Filename: "{app}\{#AppExeName}"; Tasks: desktopicon; IconFilename: "{app}\{#AppExeName}"
Name: "{userstartup}\{#AppName}";          Filename: "{app}\{#AppExeName}"; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Auto-select Turkish if system is Turkish
procedure InitializeWizard();
begin
  if Pos('tr', LowerCase(GetLocaleStr(GetSystemDefaultLCID(), 2048 {LOCALE_SISO639LANGNAME}, 'en'))) > 0 then
    ActiveLanguage := 'turkish';
end;
