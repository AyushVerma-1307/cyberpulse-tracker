$port = 8000
$root = $PWD.Path
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Server running at http://localhost:$port"
Write-Host "Press Ctrl+C to stop"
while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $req = $ctx.Request
    $res = $ctx.Response
    $path = $req.Url.LocalPath.TrimStart('/')
    if (-not $path) { $path = 'index.html' }
    $file = Join-Path $root $path
    if (Test-Path $file) {
        $data = [IO.File]::ReadAllBytes($file)
        $ext = [IO.Path]::GetExtension($file)
        $mime = @{
            '.html' = 'text/html'; '.css' = 'text/css'
            '.js' = 'application/javascript'; '.png' = 'image/png'
            '.json' = 'application/json'; '.txt' = 'text/plain'
        }
        $res.ContentType = if ($mime.ContainsKey($ext)) { $mime[$ext] } else { 'application/octet-stream' }
        $res.OutputStream.Write($data, 0, $data.Length)
    } else {
        $res.StatusCode = 404
    }
    $res.Close()
}
