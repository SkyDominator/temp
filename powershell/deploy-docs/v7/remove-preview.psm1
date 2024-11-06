
# 빌드 명령어: Invoke-ps2exe .\solve-preview.ps1 .\solve-preview.exe
# gh-pages 브랜치 수동 배포 가능 상태인지 확인

Import-Module -Name DeployDocModule -Verbose

function remove-preview {
    
    param(
        [string[]]$names #GCPPDG-687
    )
    # 인자 확인
    if (-not $names -or $names.Length -eq 0) {
        Write-Output "Usage: remove-preview -names GCPPDG-601 GCPPDG-602 GCPPDG-603 GCPPDG-604 GCPPDG-605"
        return  # 인자가 부족한 경우 종료
    }

    $currentBranchName = Get-CurrentBranchName

    for ($i = 0; $i -lt $names.Length; $i++) {
        $name = $names[$i]
        $name = $name.Trim()

        Prepare-Deployment -branchName gh-pages

        Write-Output "`n:::Raykim's Deployment Helper: Start deleting preview $name.`n"

        git checkout $currentBranchName

        & mike delete $name --deploy-prefix=ko --config-file=config/ko/mkdocs.yml --push

        Write-Output "`n:::Raykim's Deployment Helper: Finished deleting preview $name.`n`n"
    }

}

Export-ModuleMember -Function remove-preview