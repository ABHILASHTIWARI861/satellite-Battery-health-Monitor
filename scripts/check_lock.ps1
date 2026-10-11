$filePath = "C:\Users\LENOVO\OneDrive\Desktop\ajor_proj.docx"
try {
    $stream = [System.IO.File]::Open($filePath, [System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
    $stream.Close()
    Write-Host "STATUS: FILE_UNLOCKED"
} catch {
    Write-Host "STATUS: FILE_LOCKED: " $_.Exception.Message
}
