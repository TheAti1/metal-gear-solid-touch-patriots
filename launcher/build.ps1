param([string]$PackageRoot=(Join-Path $PSScriptRoot '..\package'))
$ErrorActionPreference='Stop'
$package=[IO.Path]::GetFullPath($PackageRoot)
New-Item -ItemType Directory -Path (Join-Path $package 'Arayuz') -Force | Out-Null
foreach($name in @('game.ico','patriots.jpg','hero.png','touch_wordmark.png')){
  Copy-Item -LiteralPath (Join-Path $PSScriptRoot ('..\assets\'+$name)) -Destination (Join-Path $package ('Arayuz\'+$name)) -Force
}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'TouchTheme.xaml') -Destination (Join-Path $package 'Arayuz\TouchTheme.xaml') -Force
$framework=Join-Path $env:WINDIR 'Microsoft.NET\Framework64\v4.0.30319'
$argsForCompiler=@('/nologo','/target:winexe','/main:TouchEntry','/platform:x64','/optimize+','/r:System.Web.Extensions.dll','/r:System.Drawing.dll','/r:System.IO.Compression.dll','/r:System.IO.Compression.FileSystem.dll','/r:System.Xaml.dll')
foreach($name in @('PresentationFramework','PresentationCore','WindowsBase')){$argsForCompiler+=('/r:'+(Join-Path $framework ('WPF\'+$name+'.dll')))}
$argsForCompiler+=('/win32icon:'+(Join-Path $package 'Arayuz\game.ico'))
$argsForCompiler+=('/out:'+(Join-Path $package 'Metal Gear Solid Touch.exe'))
foreach($entry in @(@('launcher/launcher.en.json','launcher'),@('localization/game/game.en.json','game'),@('localization/metal_gear_solid_touch_english.json','source'))){$argsForCompiler+=('/resource:'+(Join-Path $PSScriptRoot ('..\'+$entry[0]))+',Patriots.touch.'+$entry[1]+'.json')}
Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.cs' | ForEach-Object {$argsForCompiler+=$_.FullName}
& (Join-Path $framework 'csc.exe') $argsForCompiler
if($LASTEXITCODE -ne 0){throw 'Launcher build failed'}
