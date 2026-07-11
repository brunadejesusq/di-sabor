param(
    [ValidateSet('customer','restaurant','delivery')]
    [string]$App = 'customer',
    [System.Security.SecureString]$CredentialsPath
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $root 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    Write-Host 'Erro: Python do ambiente virtual não encontrado em:' -ForegroundColor Red
    Write-Host $python
    exit 1
}

if ($CredentialsPath) {
    $ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToGlobalAllocUnicode($CredentialsPath)
    try {
        $credentialPath = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($ptr)
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeGlobalAllocUnicode($ptr)
    }

    if (-not (Test-Path $credentialPath)) {
        Write-Host 'Erro: caminho de credenciais não encontrado:' -ForegroundColor Red
        Write-Host $credentialPath
        exit 1
    }
    $env:FIREBASE_CREDENTIALS = $credentialPath
} elseif (-not $env:FIREBASE_CREDENTIALS) {
    $defaultCred = Join-Path $root 'firebase_credentials.json'
    if (Test-Path $defaultCred) {
        $env:FIREBASE_CREDENTIALS = $defaultCred
    }
}

if (-not $env:FIREBASE_CREDENTIALS) {
    Write-Host 'Aviso: FIREBASE_CREDENTIALS não está definido e firebase_credentials.json não foi encontrado.' -ForegroundColor Yellow
    Write-Host 'Defina o caminho antes de executar ou use -CredentialsPath.'
}

switch ($App) {
    'customer' { $script = 'customer_app.py' }
    'restaurant' { $script = 'restaurant_app.py' }
    'delivery' { $script = 'delivery_app.py' }
    default {
        Write-Host "App inválido: $App" -ForegroundColor Red
        exit 1
    }
}

$scriptPath = Join-Path $root $script
if (-not (Test-Path $scriptPath)) {
    Write-Host 'Erro: script da aplicação não encontrado:' -ForegroundColor Red
    Write-Host $scriptPath
    exit 1
}

Write-Host "Executando $script..."
Write-Host "FIREBASE_CREDENTIALS=$env:FIREBASE_CREDENTIALS"
& $python $scriptPath
