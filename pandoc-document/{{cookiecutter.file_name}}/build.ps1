# Get the current script directory
$currentFolderPath = Split-Path -Parent $MyInvocation.MyCommand.Definition

# Find all markdown files in the directory
$markdownFiles = Get-ChildItem -Path $currentFolderPath -Filter *.md -File

# Loop through each markdown file and run the command
foreach ($file in $markdownFiles) {
    Write-Host "Building PDF from $($file.Name)"
    pandoc "$($file.FullName)" -o "$($file.BaseName).pdf" --from markdown --template ./pandoc_latex_template --listings
}

# Get subfolders starting with "tex2pdf" and remove them
$subfolders = Get-ChildItem -Path $currentFolderPath -Directory |
              Where-Object { $_.Name -like "tex2pdf*" }

if ($subfolders.Count -eq 0) {
    Write-Host "No subfolders starting with 'tex2pdf' found."
} else {
    foreach ($folder in $subfolders) {
        try {
            Remove-Item -Path $folder.FullName -Recurse -Force
            Write-Host "Deleted folder: $($folder.FullName)"
        } catch {
            Write-Host "Failed to delete folder: $($folder.FullName)"
        }
    }
}