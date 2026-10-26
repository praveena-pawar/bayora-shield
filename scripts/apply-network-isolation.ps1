$ErrorActionPreference = "Stop"

Write-Host "Applying Bayora Shield network isolation rules..."

docker run --rm --privileged --pid=host `
    -v "${PWD}/scripts:/scripts:ro" `
    nicolaka/netshoot `
    sh -c "nsenter -t 1 -n sh /scripts/network-isolation.sh"

if ($LASTEXITCODE -ne 0) {
    throw "Failed to apply network isolation rules."
}

Write-Host "Network isolation setup completed."
