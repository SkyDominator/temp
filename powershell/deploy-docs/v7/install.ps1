# install.ps1

# 관리자 권한 확인
$identity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object System.Security.Principal.WindowsPrincipal($identity)

if (-not $principal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "This script must be run as an administrator."
    exit
}

# 아래 모듈들은 모두 같은 경로에 위치해야 함
$moduleNames = @{
    "DeployDocModule" = "deploy-doc-module.psm1"
    "DeployDocTr" = "deploy-doc-tr.psm1"
    "DeployDoc" = "deploy-doc.psm1"
    "DeployPreview" = "deploy-preview.psm1"
    "RemovePreview" = "remove-preview.psm1"
    "CheckoutLastTag" = "checkout-last-tag.psm1"
    "Test" = "test.psm1"
}
foreach ($key in $moduleNames.Keys) {
    $scriptName = $moduleNames[$key]

    # 모듈 이름과 경로 설정
    $moduleName = $key
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
    $modulePath = "$HOME\Documents\WindowsPowerShell\Modules\$moduleName"

    # 모듈 디렉토리 생성
    if (-not (Test-Path -Path $modulePath)) {
        New-Item -ItemType Directory -Path $modulePath
    }

    # deploy-doc.psm1 파일을 모듈 폴더에 복사
    $sourceScript = Join-Path -Path $scriptPath -ChildPath $scriptName
    $destinationScript = Join-Path -Path $modulePath -ChildPath "$moduleName.psm1"

    Copy-Item -Path $sourceScript -Destination $destinationScript -Force

    Write-Host "$moduleName module has been installed. It is now available for use in PowerShell."
}