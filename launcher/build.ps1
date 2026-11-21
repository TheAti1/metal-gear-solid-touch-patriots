param([string]$PackageRoot=(Join-Path $PSScriptRoot '..\package'))
$ErrorActionPreference='Stop'
$package=[IO.Path]::GetFullPath($PackageRoot)
New-Item -ItemType Directory -Path (Join-Path $package 'Arayuz') -Force | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '..\recomplauncher.json') -Destination (Join-Path $package 'recomplauncher.json') -Force
foreach($name in @('game.ico','patriots.jpg','hero.png','touch_wordmark.png')){
  Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('..\assets\'+$name)) -Destination (Join-Path $package ('Arayuz\'+$name)) -Force
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'TouchTheme.xaml') -Destination (Join-Path $package 'Arayuz\TouchTheme.xaml') -Force
$sdkVersion='9.0.320'
$sdkLine=@(& dotnet --list-sdks | Where-Object {$_ -match ('^'+[regex]::Escape($sdkVersion)+' \[')})
if($sdkLine.Count -ne 1){throw "Install .NET SDK $sdkVersion to build the launcher (the game still uses .NET Framework 4.8)."}
$sdkRoot=($sdkLine[0] -replace '^.*\[','' -replace '\]$','')
$compiler=Join-Path $sdkRoot ($sdkVersion+'\Roslyn\bincore\csc.dll')
$framework=Join-Path ${env:ProgramFiles(x86)} 'Reference Assemblies\Microsoft\Framework\.NETFramework\v4.8'
if(!(Test-Path -LiteralPath (Join-Path $framework 'mscorlib.dll'))){throw '.NET Framework 4.8 Developer Pack reference assemblies are required.'}
$sourceRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$argsForCompiler=@('/nologo','/noconfig','/nostdlib+','/target:winexe','/main:TouchEntry','/platform:x64','/optimize+','/deterministic+','/langversion:7.3','/utf8output',('/pathmap:'+$sourceRoot+'=/src'))
foreach($name in @('mscorlib','System','System.Core','System.Xml','System.Web.Extensions','System.Drawing','System.IO.Compression','System.IO.Compression.FileSystem','System.Xaml','PresentationFramework','PresentationCore','WindowsBase')){$argsForCompiler+=('/r:'+(Join-Path $framework ($name+'.dll')))}
$argsForCompiler+=('/win32manifest:'+(Join-Path $PSScriptRoot 'app.manifest'))
$argsForCompiler+=('/win32icon:'+(Join-Path $package 'Arayuz\game.ico'))
$argsForCompiler+=('/out:'+(Join-Path $package 'Metal Gear Solid Touch.exe'))
foreach($entry in @(@('launcher/launcher.en.json','launcher'),@('localization/game/game.en.json','game'),@('localization/metal_gear_solid_touch_english.json','source'))){$argsForCompiler+=('/resource:'+(Join-Path $PSScriptRoot ('..\'+$entry[0]))+',Patriots.touch.'+$entry[1]+'.json')}
Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.cs' | Sort-Object Name | ForEach-Object {$argsForCompiler+=$_.FullName}
& dotnet exec $compiler $argsForCompiler
if($LASTEXITCODE -ne 0){throw 'Launcher build failed'}
