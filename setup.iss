; Inno Setup installer script for Le Sablenda
; This script creates an installer that deploys Sablenda to AppData\Local\Programs
; and sets up a shortcut in the Startup folder for background execution

#define MyAppName "Le Sablenda"
#define MyAppVersion "1.0"
#define MyAppPublisher "Vincent Le Goff"
#define MyAppURL "https://github.com/example/sablenda"
#define MyAppExeName "sablenda.exe"
#define SourceDir "sablenda.dist"

[Setup]
; Basic installer information
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={localappdata}\Programs\Sablenda
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=Sablenda-Setup
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
; No optional tasks

[Files]
; Source files: the entire sablenda.dist directory
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Desktop shortcut (user desktop, optional, unchecked by default)
Name: "{userdesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: ; Flags: createonlyiffileexists

; Start menu shortcut (user start menu)
Name: "{userprograms}\{#MyAppName}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Flags: createonlyiffileexists

[Run]
; No post-install tasks to run

[Code]
{ This code section handles the startup folder setup }

{ Helper procedure to create shortcuts using Windows Script Host }
procedure CreateShortcut(
  ShortcutPath: String;
  ExePath: String;
  Arguments: String;
  WorkingDir: String;
  IconIndex: Integer;
  ShowCmd: Integer;
  Description: String
);
var
  Shell: Variant;
  ShortcutObj: Variant;
begin
  Shell := CreateOleObject('WScript.Shell');
  ShortcutObj := Shell.CreateShortcut(ShortcutPath);
  ShortcutObj.TargetPath := ExePath;
  ShortcutObj.Arguments := Arguments;
  ShortcutObj.WorkingDirectory := WorkingDir;
  ShortcutObj.Description := Description;
  ShortcutObj.WindowStyle := ShowCmd;
  ShortcutObj.Save;
  Log('Created shortcut: ' + ShortcutPath);
end;

procedure CreateStartupShortcut();
var
  StartupDir: String;
  ShortcutPath: String;
  ExePath: String;
begin
  { Get the Startup folder path for current user }
  StartupDir := ExpandConstant('{userstartup}');

  { Ensure the startup directory exists }
  if not DirExists(StartupDir) then
  begin
    if not CreateDir(StartupDir) then
    begin
      Log('Warning: Could not create startup directory: ' + StartupDir);
      Exit;
    end;
  end;

  ShortcutPath := StartupDir + '\' + '{#MyAppName}.lnk';
  ExePath := ExpandConstant('{app}\{#MyAppExeName}');

  { Create the shortcut using Windows Script Host }
  { This is safe for non-elevated installations when writing to user startup folder }
  try
    CreateShortcut(
      ShortcutPath,
      ExePath,
      '--tray',
      ExpandConstant('{app}'),
      0,
      2,
      'Sablenda background service'
    );
  except
    Log('Warning: Failed to create startup shortcut: ' + GetExceptionMessage);
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    CreateStartupShortcut();
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  StartupDir: String;
  ShortcutPath: String;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    { Remove the startup shortcut if it exists }
    StartupDir := ExpandConstant('{userstartup}');
    ShortcutPath := StartupDir + '\' + '{#MyAppName}.lnk';
    if FileExists(ShortcutPath) then
    begin
      DeleteFile(ShortcutPath);
      Log('Removed startup shortcut');
    end;
  end;
end;
