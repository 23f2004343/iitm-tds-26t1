# Setup Ollama with CORS
$env:OLLAMA_ORIGINS="*"
Write-Host "Starting Ollama with CORS enabled..."
start-process ollama -ArgumentList "serve" -NoNewWindow

# Wait for Ollama to initialize (optional, adjust sleep time as needed)
Start-Sleep -Seconds 5

# Start ngrok with custom headers
Write-Host "Starting ngrok..."
ngrok http 11434 --response-header-add "X-Email: 23f300XXXX@ds.study.iitm.ac.in" --response-header-add "Access-Control-Expose-Headers: *" --response-header-add "Access-Control-Allow-Headers: Ngrok-skip-browser-warning" --host-header=localhost
