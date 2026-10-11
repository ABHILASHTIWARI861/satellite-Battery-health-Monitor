$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0

$docPath = "C:\Users\LENOVO\OneDrive\Desktop\test_copy.docx"
$doc = $word.Documents.Open($docPath)

$findText = "volttage"
$replaceText = "voltage"

$find = $doc.Content.Find
$find.ClearFormatting()
$find.Replacement.ClearFormatting()

# Parameters for Execute:
# FindText, MatchCase, MatchWholeWord, MatchWildcards, MatchSoundsLike, MatchAllWordForms, Forward, Wrap, Format, ReplaceWith, Replace
$matchCase = $false
$matchWholeWord = $false
$matchWildcards = $false
$matchSoundsLike = $false
$matchAllWordForms = $false
$forward = $true
$wrap = 1 # wdFindContinue
$format = $false
$replace = 2 # wdReplaceAll

$result = $find.Execute($findText, $matchCase, $matchWholeWord, $matchWildcards, $matchSoundsLike, $matchAllWordForms, $forward, $wrap, $format, $replaceText, $replace)

Write-Host "Replacement result for $findText -> $replaceText : $result"

$doc.Save()
$doc.Close()
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
