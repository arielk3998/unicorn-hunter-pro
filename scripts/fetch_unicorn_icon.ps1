<#
.SYNOPSIS
Fetches an open-source unicorn icon (OpenMoji) and converts to ICO.

.DESCRIPTION
Downloads the OpenMoji unicorn (emoji) PNG (publicly available under CC BY-SA 4.0) and converts it to
`assets/unicorn.ico` for use with PyInstaller and desktop shortcuts.

.Requires
- PowerShell 5+ (Windows) or 7+
- Either ImageMagick's `magick` CLI on PATH OR no external dependency (fallback .NET ico builder for a single image size).

.Attribution
If you distribute publicly include: "Unicorn icon © OpenMoji – CC BY-SA 4.0".

.PARAMETER Size
Pixel size for the PNG to fetch (default 512). Fallback converter will downscale to 64.

.EXAMPLE
./scripts/fetch_unicorn_icon.ps1

.EXAMPLE
./scripts/fetch_unicorn_icon.ps1 -Size 128
#>
[CmdletBinding()]
param(
    [int]$Size = 512
)

$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$assetDir = Join-Path $repoRoot 'assets'
if (-not (Test-Path $assetDir)) { New-Item -ItemType Directory -Path $assetDir | Out-Null }

$pngPath = Join-Path $assetDir 'unicorn.png'
$icoPath = Join-Path $assetDir 'unicorn.ico'

# OpenMoji base URL pattern (unicorn emoji U+1F984)
$codePoint = '1F984'
$url = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/svg/$codePoint.svg"
Write-Host "Downloading unicorn SVG from OpenMoji..." -ForegroundColor Cyan

$svgPath = Join-Path $assetDir 'unicorn.svg'
Invoke-WebRequest -Uri $url -OutFile $svgPath

# Convert SVG to PNG
function Convert-SvgToPng {
    param([string]$Svg, [string]$Png, [int]$Px)
    if (Get-Command magick -ErrorAction SilentlyContinue) {
        Write-Host "Converting SVG -> PNG using ImageMagick" -ForegroundColor Green
        magick convert -background none -size ${Px}x${Px} "$Svg" "$Png"
    }
    else {
        Write-Host "ImageMagick not found; attempting fallback conversion via .NET (Windows only, requires System.Drawing)." -ForegroundColor Yellow
        Add-Type -AssemblyName System.Drawing
        # Very naive rasterization: render SVG as text fallback
        $bmp = New-Object System.Drawing.Bitmap($Px, $Px)
        $gfx = [System.Drawing.Graphics]::FromImage($bmp)
        $gfx.Clear([System.Drawing.Color]::White)
        $font = New-Object System.Drawing.Font('Segoe UI Emoji', [float]($Px/2))
        $gfx.DrawString("🦄", $font, [System.Drawing.Brushes]::Black, [System.Drawing.PointF]::new($Px/4, $Px/4))
        $bmp.Save($Png, [System.Drawing.Imaging.ImageFormat]::Png)
        $gfx.Dispose(); $bmp.Dispose()
    }
}

Convert-SvgToPng -Svg $svgPath -Png $pngPath -Px $Size

# Convert PNG to ICO
function Convert-PngToIco {
    param([string]$Png, [string]$Ico)
    if (Get-Command magick -ErrorAction SilentlyContinue) {
        Write-Host "Converting PNG -> ICO using ImageMagick" -ForegroundColor Green
        magick convert "$Png" -define icon:auto-resize=256,128,64,48,32,16 "$Ico"
    }
    else {
        Write-Host "ImageMagick not found; building single-size ICO via .NET." -ForegroundColor Yellow
        Add-Type -AssemblyName System.Drawing
        $img = [System.Drawing.Image]::FromFile($Png)
        # Downscale to 64x64
        $targetSize = 64
        $thumb = New-Object System.Drawing.Bitmap($targetSize, $targetSize)
        $g = [System.Drawing.Graphics]::FromImage($thumb)
        $g.DrawImage($img, 0, 0, $targetSize, $targetSize)
        $g.Dispose(); $img.Dispose()
        $fs = [System.IO.File]::Create($Ico)
        # ICO header for single image
        $writer = New-Object System.IO.BinaryWriter($fs)
        $writer.Write([byte]0); $writer.Write([byte]0)            # Reserved
        $writer.Write([byte]1); $writer.Write([byte]0)            # Type = icon
        $writer.Write([byte]1); $writer.Write([byte]0)            # Count = 1
        $writer.Write([byte]$targetSize)                          # Width
        $writer.Write([byte]$targetSize)                          # Height
        $writer.Write([byte]0)                                    # Color count
        $writer.Write([byte]0)                                    # Reserved
        $writer.Write([UInt16]0)                                  # Planes
        $writer.Write([UInt16]32)                                 # Bit count
        $imgBytes = [System.IO.File]::ReadAllBytes((Join-Path $assetDir 'temp.png'))
        # Actually need raw PNG bytes in place of BMP/XOR+AND mask for simplest hack; we'll save PNG as temp.png
        $thumb.Save((Join-Path $assetDir 'temp.png'), [System.Drawing.Imaging.ImageFormat]::Png)
        $imgBytes = [System.IO.File]::ReadAllBytes((Join-Path $assetDir 'temp.png'))
        $writer.Write([UInt32]$imgBytes.Length)                   # Size of data
        $writer.Write([UInt32](22))                               # Offset to data (6+16)
        $writer.Write($imgBytes)
        $writer.Flush(); $writer.Dispose(); $fs.Close()
        Remove-Item (Join-Path $assetDir 'temp.png') -ErrorAction SilentlyContinue
    }
}

Convert-PngToIco -Png $pngPath -Ico $icoPath

if (Test-Path $icoPath) {
    Write-Host "Icon created: $icoPath" -ForegroundColor Cyan
} else {
    Write-Warning "Failed to create icon."
}

Write-Host "Done. You can now rebuild your executable with --icon assets/unicorn.ico or rerun shortcut installer." -ForegroundColor Cyan
