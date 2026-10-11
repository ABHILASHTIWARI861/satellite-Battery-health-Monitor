$word = [System.Runtime.InteropServices.Marshal]::GetActiveObject("Word.Application")
foreach ($d in $word.Documents) {
    Write-Host "DOC_FOUND:" $d.FullName
}
