$ErrorActionPreference = 'Stop'
$assetDir = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\assets_v1'))
$voice = New-Object -ComObject SAPI.SpVoice
$voiceTokens = $voice.GetVoices()
for ($voiceIndex = 0; $voiceIndex -lt $voiceTokens.Count; $voiceIndex++) {
    $candidateVoice = $voiceTokens.Item($voiceIndex)
    if ($candidateVoice.Id -match 'ZH-TW_HANHAN') { $voice.Voice = $candidateVoice; break }
}
if ($voice.Voice.Id -notmatch 'ZH-TW_HANHAN') { throw 'Taiwan Chinese offline voice unavailable' }
$voice.Rate = 0
$voice.Volume = 100
$narrations = @(
    '帶孩子看看自然，讓好奇心，成為旅行的起點。',
    '和喜歡的人，走進庭園與文化，留一點時間，好好相處。',
    '陪家人照自己的步調旅行。告訴我們日期與偏好，一起討論安排。'
)
for ($narrationIndex = 0; $narrationIndex -lt $narrations.Count; $narrationIndex++) {
    $wavePath = Join-Path $assetDir ('vo-{0:00}.wav' -f ($narrationIndex + 1))
    $stream = New-Object -ComObject SAPI.SpFileStream
    $format = New-Object -ComObject SAPI.SpAudioFormat
    $format.Type = 22
    $stream.Format = $format
    $stream.Open($wavePath, 3, $false)
    $voice.AudioOutputStream = $stream
    [void]$voice.Speak($narrations[$narrationIndex])
    $stream.Close()
    Write-Output ('Created ' + [System.IO.Path]::GetFileName($wavePath))
}
Write-Output ('Voice: ' + $voice.Voice.GetDescription())
