#Ensure long paths are enabled
#Ensure RSAT is installed "get-windowsfeature | where name -like RSAT-AD-Powershell | Install-WindowsFeature"

import-module activedirectory
$Logfile = "~\Desktop\actions.log"
$UserData = Import-Csv -Path "~\Desktop\deletions.csv"
$HomePaths = $UserData | Select-Object HomeDirectory
$Usernames = $UserData | Select-Object sAmAccountName
$StorageSpace = 0
$Count = 1 #The number of elements in the CSV. Arrays are 0 indexed
$DeletionCount = 0 #The number of directories to actually be deleted
$DeletedUsers = 0
#Test every directory to see if they exist and add it to the DeletionCount
ForEach ($Dir in $HomePaths) {
    if ($Dir.HomeDirectory -ne '') {
        $temp = Test-Path $Dir.HomeDirectory
        if ($temp -eq $true) {
            $DeletionCount = $DeletionCount + 1
        }
    }
}
Write-Host "Number of directories to be deleted: " $DeletionCount
Write-Host "Number of accounts to be deleted: " ($Usernames.Count - 1)

#We test the directory exists again so there is room for improvement
#If the directory exists, get the size, add it to StorageSpace, then delete all child items, then delete the directory
ForEach ($Dir in $HomePaths) {
    if ($Dir.HomeDirectory -ne '') {
        $temp = Test-Path $Dir.HomeDirectory
        if ($temp -eq $true) {
            #Write-Output "Processing path: " $Dir.HomeDirectory ": " $Count " of " $DeletionCount >> $Logfile
            Write-Output "Processing path: $($Dir.HomeDirectory): $Count of $DeletionCount" >> $Logfile
            $amt = "{0}" -f ((Get-ChildItem $Dir.HomeDirectory -Recurse | Measure-Object -Property Length -Sum -ErrorAction Inquire).Sum / 1MB)
            $StorageSpace = [int]$StorageSpace + [int]$amt
            $Count = $Count + 1
            Get-ChildItem $Dir.HomeDirectory -Recurse -Force | Remove-Item -Recurse -Force
            Remove-Item $Dir.HomeDirectory -Force
        }
    }
}

ForEach ($User in $Usernames) {

    Try {
        Get-ADUser $User.sAmAccountName | Out-Null
        Remove-ADUser $User.sAmAccountName -Confirm:$false
        Write-Output "Deleted user: $($User.sAmAccountName)" >> $Logfile
        $DeletedUsers = $DeletedUsers + 1
    }
    Catch {
        Write-Output "Failed to delete user: $($User.sAmAccountName) because it did not exist"  >> $Logfile
    }
}



$GB = $StorageSpace/1024
Write-Host "Estimated storage reclaimed: " $GB " GB"
Write-Host "Number of users deleted: " $DeletedUsers
Write-Host "Please check actions.log for more details"
