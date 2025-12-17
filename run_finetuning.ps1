param(
    [Parameter(Mandatory=$false)]
    [string]$ModelPath
)

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

if (-not (Test-Path .\.venv)) {
    Write-Host "Error: Virtual environment not found. Please run setup first." -ForegroundColor Red
    exit 1
}

$TrainScript = "src\finetuning\train.py"
if (-not (Test-Path $TrainScript)) {
     Write-Host "Error: Training script not found at $TrainScript" -ForegroundColor Red
     exit 1
}

$Args = @()
if ($ModelPath) {
    $Args += "--model_path"
    $Args += $ModelPath
}

Write-Host "Starting Fine-tuning..." -ForegroundColor Green
if ($ModelPath) {
    Write-Host "Using Local Model: $ModelPath" -ForegroundColor Cyan
} else {
    Write-Host "Using Default Model Configuration" -ForegroundColor Cyan
}

& .\.venv\Scripts\python.exe $TrainScript @Args
