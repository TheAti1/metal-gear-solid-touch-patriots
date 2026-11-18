param([string]$PackageRoot='D:\Patriots_MGS_Touch_PC\package')
$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot '..\..\launcher\build.ps1') -PackageRoot $PackageRoot
