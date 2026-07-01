; ============================================================
;  ES Image Studio — Windows Installer Script
;  Built with Inno Setup 6.x  (https://jrsoftware.org/isinfo.php)
;
;  To compile:
;    1. Install Inno Setup 6
;    2. Right-click this file → Compile   (or run build.bat)
;  Output: Output\ES_Image_Studio_Setup.exe
; ============================================================

#define AppName      "ES Image Studio"
#define AppVersion   "1.0.0"
#define AppPublisher "Eastern Studios"
#define AppURL       "https://easternstudios.com"
#define AppExeName   "ES Image Studios.exe"

[Setup]
; Unique app ID — do not change after first release
AppId={{3A7F2C91-B4D8-4E6A-9C02-F1A83E5D7B40}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}

; Install to Program Files\Eastern Studios\ES Image Studio
DefaultDirName={autopf}\Eastern Studios\ES Image Studio
DefaultGroupName=Eastern Studios
DisableProgramGroupPage=yes
AllowNoIcons=yes

; Output
OutputDir=Output
OutputBaseFilename=ES_Image_Studio_Setup
SetupIconFile=icon.ico

; Compression
Compression=lzma2/ultra64
SolidCompression=yes
LZMAUseSeparateProcess=yes

; Appearance
WizardStyle=modern
WizardSizePercent=110
WizardResizable=no

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Uninstall
UninstallDisplayName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
CreateUninstallRegKey=yes

; Misc
MinVersion=10.0
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nES Image Studio uses a BiRefNet AI model (~500 MB) to remove image backgrounds at full resolution. The model will be downloaded automatically on first launch — make sure you have an internet connection ready.%n%nClick Next to continue.
english.FinishedHeadingLabel=ES Image Studio is ready!
english.FinishedLabel=Setup has finished installing [name] on your computer.%n%nThe AI model will be downloaded the first time you launch the app. This is a one-time download of ~500 MB.

[Tasks]
Name: "desktopicon"; \
  Description: "Create a &Desktop shortcut"; \
  GroupDescription: "Shortcuts:"; \
  Flags: checked

Name: "startmenuicon"; \
  Description: "Create a &Start Menu shortcut"; \
  GroupDescription: "Shortcuts:"; \
  Flags: checked

[Files]
; Everything PyInstaller built
Source: "dist\ES Image Studios\*"; \
  DestDir: "{app}"; \
  Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Start Menu
Name: "{group}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  IconFilename: "{app}\{#AppExeName}"; \
  Tasks: startmenuicon

; Desktop
Name: "{commondesktop}\{#AppName}"; \
  Filename: "{app}\{#AppExeName}"; \
  IconFilename: "{app}\{#AppExeName}"; \
  Tasks: desktopicon

; Uninstall shortcut in Start Menu
Name: "{group}\Uninstall {#AppName}"; \
  Filename: "{uninstallexe}"; \
  Tasks: startmenuicon

[Run]
; Offer to launch after install
Filename: "{app}\{#AppExeName}"; \
  Description: "Launch {#AppName} now"; \
  Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Clean up the AI model cache on uninstall (optional — comment out to keep)
; Type: filesandordirs; Name: "{localappdata}\rembg"
; Type: filesandordirs; Name: "{localappdata}\huggingface"

[Code]
// Show a warning if .NET / Edge WebView2 might be missing
// (Edge WebView2 ships with Windows 11 and updated Win10 — almost always present)
procedure InitializeWizard;
begin
  WizardForm.WelcomeLabel2.Font.Size := 9;
end;
