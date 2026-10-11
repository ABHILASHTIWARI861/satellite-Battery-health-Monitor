$word = New-Object -ComObject Word.Application
Write-Host "Word COM Object created! Version:" $word.Version
$word.Quit()
