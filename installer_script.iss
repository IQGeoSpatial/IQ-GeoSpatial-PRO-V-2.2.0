; -- Script de Inno Setup para IQ GeoSpatial Pro --
; Creado por IQ GeoSpatial Technology

#define MyAppName "IQ GeoSpatial Pro"
#define MyAppVersion "2.2.0"
#define MyAppPublisher "IQ GeoSpatial"
#define MyAppURL "mailto:iqgeospatial@gmail.com"
#define MyAppExeName "main.exe"

[Setup]
; NOTA: El valor de AppId identifica de forma única esta aplicación.
; Genera uno nuevo desde el menú Herramientas > Generar GUID si creas otro instalador.
AppId={{A1B2C3D4-E5F6-7890-1234-567890ABCDEF}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
; Para una aplicación de 64 bits, como la mayoría de las de Python hoy en día.
ArchitecturesInstallIn64BitMode=x64
ArchitecturesAllowed=x64
; Nombre del archivo de salida del instalador.
OutputBaseFilename=setup_iq_geospatial_pro_v{#MyAppVersion}
; Ruta al icono de tu aplicación.
SetupIconFile=Assets\Icono\icono.ico
; --- Imágenes del Asistente de Instalación (Logos) ---
; Imagen grande que aparece a la izquierda del asistente. Debe ser un archivo .bmp de 164x314 píxeles.
WizardImageFile=Assets\Image\portada.bmp
; Imagen pequeña que aparece en la esquina superior derecha. Debe ser un archivo .bmp de 55x58 píxeles.
WizardSmallImageFile=Assets\Image\log-fina1.bmp
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; ¡Esta es la sección más importante!
; Toma TODO el contenido de la carpeta 'dist\main' que generó PyInstaller
; y lo empaqueta en el instalador.
Source: "dist\main\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
const
  // URL oficial y directa para la descarga del componente de Microsoft.
  VCppRedist_URL = 'https://aka.ms/vs/17/release/vc_redist.x64.exe';
  // Clave del registro que indica si el componente está instalado.
  VCppRedist_RegKey = 'SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64';

function IsVCppRedistInstalled(): Boolean;
begin
  // Comprueba si la clave de registro existe en la vista de 64 bits del registro.
  // Si existe, significa que el componente ya está instalado.
  Result := RegKeyExists(HKLM64, VCppRedist_RegKey);
end;

function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  // Comprobar si el componente necesario está instalado al inicio.
  if not IsVCppRedistInstalled() then
  begin
    // Si no está instalado, informar al usuario y ofrecer abrir el enlace de descarga.
    if MsgBox('Componente Requerido Faltante.'#13#10#13#10 +
              'IQ GeoSpatial Pro necesita "Microsoft Visual C++ Redistributable" para funcionar correctamente.'#13#10#13#10 +
              '¿Desea abrir la página de descarga oficial de Microsoft ahora?',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      // Abre la URL en el navegador por defecto del usuario.
      ShellExec('open', VCppRedist_URL, '', '', SW_SHOWNORMAL, ewNoWait, ResultCode);
    end;

    // Informar al usuario que la instalación se cancelará de todos modos.
    MsgBox('La instalación se cancelará. Por favor, instale el componente requerido y luego ejecute este instalador de nuevo.', mbInformation, MB_OK);
    Result := False; // Abortar la instalación.
  end
  else
  begin
    // Si el componente ya está instalado, la instalación continúa con normalidad.
    Result := True;
  end;
end;