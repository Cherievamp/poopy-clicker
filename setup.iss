; Inno Setup script — requer PyInstaller .exe em dist/
; Rode primeiro:
;   pip install pyinstaller
;   pyinstaller --onefile --windowed ^
;     --add-data "poopy_clicker/assets;assets" ^
;     --hidden-import PyQt6.QtMultimedia ^
;     --hidden-import PyQt6.QtMultimediaWidgets ^
;     --collect-data poopy_clicker ^
;     poopy_clicker/__main__.py --name PoopyClicker

[Setup]
AppName=Poopy Clicker
AppVersion=1.0.0
DefaultDirName={autopf}\Poopy Clicker
DefaultGroupName=Poopy Clicker
UninstallDisplayIcon={app}\PoopyClicker.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer
OutputBaseFilename=PoopyClicker_Setup

[Files]
Source: "dist\PoopyClicker.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Poopy Clicker"; Filename: "{app}\PoopyClicker.exe"
Name: "{group}\Desinstalar Poopy Clicker"; Filename: "{uninstallexe}"
Name: "{commondesktop}\Poopy Clicker"; Filename: "{app}\PoopyClicker.exe"

[Run]
Filename: "{app}\PoopyClicker.exe"; Description: "Jogar Poopy Clicker agora"; Flags: postinstall nowait skipifsilent
