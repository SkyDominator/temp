function checkout-last-tag {
    param (
        [string]$tagPattern
    )

    if($tagPattern -eq ""){
        Write-Output "Usage: deploy-test <tagPattern>"
        Write-Output "The parameter format was invalid. Try again."
        return
    }

    Import-Module -Name DeployDocModule

    $currentBranchName = Get-CurrentBranchName

    $tags = Search-Tag $tagPattern
    
    $branchName = "$tagPattern-last"
    Checkout-LatestTag -tags $tags -branchName $branchName
}

Export-ModuleMember -Function checkout-last-tag