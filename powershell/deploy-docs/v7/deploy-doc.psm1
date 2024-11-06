# deploy-doc.psm1

function deploy-doc {
    param (
        [string]$deployPrefix,
        [string]$mode,
        [string]$_version = "",
        [string]$tag = ""
    )

    
    # 변수 Trim
    $deployPrefix = $deployPrefix.Trim()
    $mode = $mode.Trim()
    $_version = $_version.Trim()
    $tag = $tag.Trim()
    
    Import-Module -Name DeployDocModule

    $currentBranchName = Get-CurrentBranchName
    
    # 인자 확인
    if ($deployPrefix -eq "" -or $mode -eq ""){
        Write-Output "AUTO MODE Usage: deploy-doc <language> <auto>"
        Write-Output "MANUAL MODE Usage: deploy-doc <language> <manual> <Hive SDK version> <latest|old>"
        Write-Output "The parameter format was invalid. Try again."
        return
    }

    if ($mode -eq "manual"){
        if ($tag.Trim() -ne "latest" -and $tag.Trim() -ne "old" -or $_version.Trim() -notmatch 'v\d+\.\d+\.\d+\.\d+') {
            Write-Output "Usage: deploy-doc <language> <auto|manual> <Hive SDK version> <latest|old>"
            Write-Output "The parameter format was invalid. Try again."
            return  # 인자가 부족한 경우 종료
        }
    }

    # AUTO 모드 설정: 자동으로 최신 버전 탐색
    if ($mode -eq "auto") {

        $latestVersion = Get-LatestVersion -deployPrefix $deployPrefix

        Write-Output "`nLanguage: $deployPrefix"
        Write-Output "Hive SDK Version: $latestVersion"
        Write-Output "Deployment Branch: $currentBranchName`n"

        $confirmation = Read-Host ":::Raykim's Deployment Helper: Are you sure to deploy with the above settings? (yes or Press Enter/no)"
        if ($confirmation -ne "yes" -and $confirmation -ne "") {
            Write-Output ":::Raykim's Deployment Helper: Terminate the deployment process."
            return
        }
        $version = $latestVersion
        $tag = "latest"
    }
    # MANUAL 모드 설정: 수동으로 버전 입력 시 버전 확인
    else{
        Write-Output "`n:::Raykim's Deployment Helper: MANUAL MODE: The document will be deployed with the following settings."
        Write-Output "`nLanguage: $($deployPrefix)"
        Write-Output "Hive SDK Version: $($_version)"
        Write-Output "Latest/Old: $($tag)"
        Write-Output "Deployment Branch: $currentBranchName`n"

        $confirmation = Read-Host ":::Raykim's Deployment Helper: Are you sure to deploy with the above settings? (yes or Press Enter/no)"
        if ($confirmation -ne "yes" -and $confirmation -ne "") {
            Write-Output ":::Raykim's Deployment Helper: Terminate the deployment process."
            return
        }
        $version = $_version
    }

    # release 브랜치 수동 배포 가능 상태인지 확인
    Prepare-Deployment -branchName release

    # 배포 준비: 원래 브랜치로 돌아간 후, origin master와 동기화
    Write-Output "`n:::Raykim's Deployment Helper: Going back to the $currentBranchName branch to deploy contents.`n"
    git checkout $currentBranchName

    Sync-WithOrigin -branchName master

    Sync-WithOrigin -branchName $currentBranchName

    # 문서 배포
    Deploy-Document -deployPrefix $deployPrefix -version $version -tag $tag

    Create-Push-Tag -version $version -branchName $currentBranchName

    Post-DeploymentTasks -currentBranchName $currentBranchName
}

Export-ModuleMember -Function deploy-doc