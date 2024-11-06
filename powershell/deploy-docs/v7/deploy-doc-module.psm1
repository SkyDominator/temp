# DeployDoc.psm1
# handling module import errors:
# Remove-Module DeployDocModule -Force -ErrorAction SilentlyContinue
# Import-Module -Name DeployDocModule -Force -Verbose
# Get-Command -Module DeployDocModule

function Get-CurrentBranchName {
    return git rev-parse --abbrev-ref HEAD
}

function Sync-WithOrigin {
    param (
        [string]$branchName
    )
    Write-Output "`n:::Raykim's Deployment Helper: Start synching with origin/$branchName.`n"
    Write-Output "`n:::Raykim's Deployment Helper: If any conflicts occur, YOU MUST SOLVE CONFLICTS FIRST and then continue.`n"
    Write-Output "`n:::Raykim's Deployment Helper: Start git pull origin $branchName.`n"

    git pull origin $branchName

    # Check for merge conflicts
    if (git status --porcelain | Select-String -Pattern "UU") {
        Write-Output "`n:::Raykim's Deployment Helper: Merge conflicts detected. Please resolve them before continuing.`n"
        return
    }

    # Check for unstaged changes
    if (git status --porcelain) {
        Write-Output "`n:::Raykim's Deployment Helper: Unstaged changes detected. Discarding these changes.`n"
        git reset --hard HEAD
    }
    Write-Output "`n:::Raykim's Deployment Helper: Finished synching with origin/$branchName.`n"
}

function Deploy-Document {
    param (
        [string]$deployPrefix,
        [string]$version,
        [string]$tag
    )

    if ($tag -eq "latest") {
        Write-Output "`n:::Raykim's Deployment Helper: Start deploying the latest version.`n"
        & mike deploy -b release --deploy-prefix $deployPrefix --config-file config/$deployPrefix/mkdocs.yml --push -u $version $tag
    } elseif ($tag -eq "old") {
        Write-Output "`n:::Raykim's Deployment Helper: Start deploying the old version.`n"
        & mike deploy -b release --deploy-prefix $deployPrefix --config-file config/$deployPrefix/mkdocs.yml --push $version
    } else {
        Write-Output "`n:::Raykim's Deployment Helper: Invalid arguments. Please use 'latest' or 'old'.`n"
        return
    }
}

function Run-Deploy-Preview {
    param (
        [string]$deployPrefix,
        [string]$version,
        [string]$tag
    )

    if ($tag -eq "latest") {
        # 최신 버전으로 배포
        Write-Output "`n:::Raykim's Deployment Helper: Start deploying the latest preview version.`n"
        & mike deploy --deploy-prefix $deployPrefix --config-file config/$deployPrefix/mkdocs.yml --push -u $version $tag
    } elseif ($tag -eq "old") {
        Write-Output "`n:::Raykim's Deployment Helper: Start deploying the old version preview.`n"
        & mike deploy --deploy-prefix $deployPrefix --config-file config/$deployPrefix/mkdocs.yml --push $version
    } else {
        Write-Output "`n:::Raykim's Deployment Helper: Invalid arguments. Please use 'latest' or 'old'.`n"
        return
    }
}

function Post-DeploymentTasks {
    param (
        [string]$currentBranchName
    )

    Write-Output "`n:::Raykim's Deployment Helper: Start post-deployment tasks.`n"
    Write-Output "`n:::Raykim's Deployment Helper: Check out to local master.`n"
    git checkout master

    Write-Output "`n:::Raykim's Deployment Helper: Start git pull origin master.`n"
    git pull origin master

    Write-Output "`n:::Raykim's Deployment Helper: merge feature branch to local master.`n"
    git merge $currentBranchName

    Write-Output "`n:::Raykim's Deployment Helper: Start git push origin master.`n"
    git push origin master

    Write-Output "`n:::Raykim's Deployment Helper: Get back to $currentBranchName.`n"
    git checkout $currentBranchName
}

function Get-LatestVersion {
    param ([string]$deployPrefix)
    
    # Run the command and capture the output
    $versions = mike list -b release --deploy-prefix $deployPrefix --config-file config/$deployPrefix/mkdocs.yml

    # Split the output into lines
    $lines = $versions -split "`n"

    # Loop through each line and parse the versions
    foreach ($line in $lines) {
        # Trim whitespace
        $trimmedLine = $line.Trim()

        # Check if the line contains version info
        if ($trimmedLine -match '(v\d+\.\d+\.\d+\.\d+) \[latest\]') {
            $latestVersion = $matches[1]
            break  # Exit loop once found
        }
    }
    
    return $latestVersion
}

function Create-Push-Tag {
    param(
        [string]$version,
        [string]$branchName
    )
    Write-Output "`n:::Raykim's Deployment Helper: Start creating and pushing a tag $tagName for the release.`n"
    $lastCommitHash = git rev-parse $branchName
    $tagName = "$version-$branchName"
    git tag -a $tagName $lastCommitHash -m "Release $version"
    git push origin $tagName
}

function Prepare-Deployment {
    param (
        [string]$branchName
    )
    
    # release 브랜치 수동 배포 가능 상태인지 확인
    $gitlabApiUrl = "https://xgit.withhive.com/api/v4"
    
    # Ensure this ID is correct and accessible
    $projectId = "1072"  
   
   # Ensure Get-Secret is configured correctly in your environment
   try {
       $accessToken = Get-Secret -Name "RayKimGitLabProjectAcessToken" -AsPlainText 
   } catch {
       Write-Warning "Failed to retrieve GitLab access token."
       return
   }

   try {
       $branchUrl = "$gitlabApiUrl/projects/$projectId/repository/branches/$branchName"
       $branchInfo = Invoke-RestMethod -Uri $branchUrl -Headers @{ "PRIVATE-TOKEN" = $accessToken }
       $latestCommitId = $branchInfo.commit.id
       $localLatestCommitId = git rev-parse $branchName

       if ($latestCommitId -eq $localLatestCommitId) {
           Write-Output "`n:::Raykim's Deployment Helper: $branchName branch is up-to-date!`nProceed with the deployment to live server`n"
       } else {
           Write-Output "`n:::Raykim's Deployment Helper: $branchName branch needs to be updated.`nProceed with updating release branch with origin/$branchName`n"
           Write-Output "`n:::Raykim's Deployment Helper: Start git checkout $branchName.`n"
           Start-Process git -ArgumentList "checkout", "$branchName" -NoNewWindow -Wait

           Write-Output "`n:::Raykim's Deployment Helper: Start git fetch origin.`n"
           Start-Process git -ArgumentList "fetch", "origin" -NoNewWindow -Wait

           Write-Output "`n:::Raykim's Deployment Helper: Start git reset --hard origin/$branchName.`n"
           Start-Process git -ArgumentList "reset", "--hard", "origin/$branchName" -NoNewWindow -Wait

           Write-Output "`n:::Raykim's Deployment Helper: Finished updating release branch with origin/release`n"
       }
   } catch {
       Write-Warning "An error occurred during deployment preparation."
   }
}

function Search-Tag {
    param (
        [string]$searchTerm
    )
    
    Write-Output "`n:::Raykim's Deployment Helper: Fetching all tags from origin.`n"
    git fetch --tags
    
    Write-Output "`n:::Raykim's Deployment Helper: Searching for tags that include '$searchTerm'.`n"
    $tags = git tag -l | Where-Object { $_ -like "*$searchTerm*" }
    
    if (!$tags) {
        Write-Output "`n:::Raykim's Deployment Helper: No tags found including the term '$searchTerm'.`n"
        return
    }
    return $tags
}

function Checkout-LatestTag {
    param (
        [string[]]$tags,
        [string]$branchName
    )

    # Sort the tags to find the latest one
    $latestTag = $tags | Sort-Object { $_ -replace '[^\d]', '' } -Descending | Select-Object -First 1
    
    Write-Output "`n:::Raykim's Deployment Helper: Latest tag found: $latestTag.`n"
    Write-Output "`n:::Raykim's Deployment Helper: Checking out to tag $latestTag.`n"
    git checkout tags/$latestTag
    
    Write-Output "`n:::Raykim's Deployment Helper: Checked out to $latestTag.`n"

    Write-Output "`n:::Raykim's Deployment Helper: Creating and switching to new branch $branchName.`n"
    git checkout -b $branchName
}

Export-ModuleMember -Function Get-CurrentBranchName, Sync-WithOrigin, Deploy-Document, Post-DeploymentTasks, Get-LatestVersion, Prepare-Deployment, Create-Push-Tag, Run-Deploy-Preview, Search-Tag, Checkout-LatestTag