# deploy-doc-tr.psm1

function deploy-doc-tr {

    param(
        [string]$mode,
        [string]$_version = "",
        [string]$tag = ""
    )

    # 변수 trim
    $mode = $mode.Trim()
    $_version = $_version.Trim()
    $tag = $tag.Trim()

    Import-Module -Name DeployDocModule -Verbose

    $currentBranchName = Get-CurrentBranchName

    # # Debug output
    # Write-Output "Mode: $mode"
    # Write-Output "Version: $_version"
    # Write-Output "Tag: $tag"

    # 인자 확인
    if ($mode.Trim() -eq "auto"){
        if ($_version -ne "" -or $tag -ne ""){
            Write-Output "AUTO MODE Usage: deploy-doc-tr <auto>"
            Write-Output "The parameter format was invalid. Try again."
            return  # 인자가 부족한 경우 종료
        }

        # 언어 정보 가져오기
        $mode = $mode.Trim()
    }
    elseif ($mode.Trim() -eq "manual"){
        if ($_version -eq "" -or $tag -eq ""){
            Write-Output "MANUAL MODE Usage: deploy-doc-tr <manual> <Hive SDK version> <latest|old>"
            Write-Output "The parameter format was invalid. Try again."
            return  # 인자가 부족한 경우 종료
        }
        if ($tag.Trim() -ne "latest" -and $tag.Trim() -ne "old" -or $_version.Trim() -notmatch 'v\d+\.\d+\.\d+\.\d+') {
            Write-Output "Usage: deploy-doc-tr <auto|manual> <Hive SDK version> <latest|old>"
            Write-Output "The parameter format was invalid. Try again."
            return  # 인자가 부족한 경우 종료
        }

        # 언어 정보 가져오기
        $mode = $mode.Trim()
        $_version = $_version.Trim()
        $tag = $tag.Trim()
    }
    else{
        Write-Output "AUTO MODE Usage: deploy-doc-tr <auto>"
        Write-Output "MANUAL MODE Usage: deploy-doc-tr <manual> <Hive SDK version> <latest|old>"
        Write-Output "The parameter format was invalid. Try again."
        return
    }

    $deployPrefixes = @("ja", "zh", "zh-Hant", "th")

    # AUTO 모드 설정: 자동으로 최신 버전 탐색
    if ($mode -eq "auto") {
        Write-Output "`n:::Raykim's Deployment Helper: AUTO MODE: The document will be deployed with the following settings. (the latest version)"
        
        $latestVersion = Get-LatestVersion -deployPrefix $deployPrefixes[0]

        Write-Output "`nLanguage: $($deployPrefixes)"
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
        Write-Output "`nLanguage: $($deployPrefixes)"
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

    foreach ($deployPrefix in $deployPrefixes) {
        Write-Output "`n:::Raykim's Deployment Helper: Start deploying task for Language: $deployPrefix`n"
        # Hold execution for a few seconds
        Start-Sleep -Seconds 5

        Prepare-Deployment -branchName release

        Write-Output "`n:::Raykim's Deployment Helper: Going back to the $currentBranchName branch to deploy contents.`n"
        git checkout $currentBranchName

        Sync-WithOrigin -branchName master

        Sync-WithOrigin -branchName $currentBranchName

        Deploy-Document -deployPrefix $deployPrefix -version $version -tag $tag

        Write-Output "`n:::Raykim's Deployment Helper: Finished deploying task for Language: $deployPrefix`n"

        Create-Push-Tag -version $version -branchName $currentBranchName
    }

    Post-DeploymentTasks -currentBranchName $currentBranchName
}

Export-ModuleMember -Function deploy-doc-tr