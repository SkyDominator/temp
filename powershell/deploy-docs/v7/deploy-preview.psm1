
# 빌드 명령어: Invoke-ps2exe .\solve-preview.ps1 .\solve-preview.exe
# gh-pages 브랜치 수동 배포 가능 상태인지 확인

function deploy-preview {
    param(
        [string]$deployPrefix, #ko, en
        [string]$version, # v4.24.3.0
        [string]$tag #latest, old
    )

    # 변수 Trim
    $deployPrefix = $deployPrefix.Trim()
    $version = $version.Trim()
    $tag = $tag.Trim()

    Import-Module -Name DeployDocModule -Verbose

    $currentBranchName = Get-CurrentBranchName

    # 인자 확인
    if ($deployPrefix -eq "" -or $version -eq "" -or $tag -eq ""){
        Write-Output "Usage: deploy-preview <language> <Hive SDK version> <latest/old>"
        return  # 인자가 부족한 경우 종료
    }

    Write-Output "`n:::Raykim's Deployment Helper: MANUAL MODE: The preview will be deployed with the following settings."
    Write-Output "`nLanguage: $($deployPrefix)"
    Write-Output "Hive SDK Version: $($version)"
    Write-Output "Latest/Old: $($tag)"
    Write-Output "Deployment Branch: $currentBranchName`n"

    $confirmation = Read-Host ":::Raykim's Deployment Helper: Are you sure to deploy preview with the above settings? (yes or Press Enter/no)"
    if ($confirmation -ne "yes" -and $confirmation -ne "") {
        Write-Output ":::Raykim's Deployment Helper: Terminate the deployment process."
        return
    }

    Prepare-Deployment -branchName gh-pages

    # 프리뷰 배포 시작

    # 먼저 배포할 원래 브랜치로 복귀
    Write-Output "`n:::Raykim's Deployment Helper: Going back to the $currentBranchName branch to deploy contents.`n"
    git checkout $currentBranchName

    # 최신 커밋으로 업데이트
    Sync-WithOrigin -branchName $currentBranchName

    Run-Deploy-Preview -deployPrefix $deployPrefix -version $version -tag $tag
}

Export-ModuleMember -Function deploy-preview