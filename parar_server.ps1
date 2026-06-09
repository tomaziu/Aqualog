param(
    [int]$Porta = 8000,
    [switch]$WhatIf
)

$ErrorActionPreference = 'SilentlyContinue'

function Get-CommandLineText($Process) {
    if ($Process -and $Process.CommandLine) {
        return [string]$Process.CommandLine
    }
    return ''
}

function Has-AllText($Text, [string[]]$Parts) {
    foreach ($part in $Parts) {
        if ($Text -notlike "*$part*") {
            return $false
        }
    }
    return $true
}

function Get-TargetPriority($Process, $Reason) {
    $cmd = Get-CommandLineText $Process
    if ($Process.Name -ieq 'cmd.exe' -and (Has-AllText $cmd @('uvicorn', 'main:app', '--port', '8000'))) { return 10 }
    if (($Process.Name -ieq 'python.exe' -or $Process.Name -ieq 'pythonw.exe') -and (Has-AllText $cmd @('uvicorn', 'main:app', '--port', '8000'))) { return 20 }
    if ($Process.Name -ieq 'cloudflared.exe') { return 30 }
    if ($Process.Name -ieq 'cmd.exe' -and (Has-AllText $cmd @('cloudflared', 'tunnel', '8000'))) { return 40 }
    if (($Process.Name -ieq 'python.exe' -or $Process.Name -ieq 'pythonw.exe') -and (Has-AllText $cmd @('multiprocessing.spawn', 'parent_pid='))) { return 50 }
    return 90
}

function Add-Target($Map, $Process, [string]$Reason) {
    if (-not $Process) { return }
    if ([int]$Process.ProcessId -eq $PID) { return }

    $allowedNames = @('python.exe', 'pythonw.exe', 'cloudflared.exe', 'cmd.exe')
    if ($allowedNames -notcontains $Process.Name.ToLowerInvariant()) { return }

    $id = [int]$Process.ProcessId
    if (-not $Map.ContainsKey($id)) {
        $Map[$id] = [pscustomobject]@{
            Id = $id
            ParentId = [int]$Process.ParentProcessId
            Name = $Process.Name
            Reason = $Reason
            Priority = Get-TargetPriority $Process $Reason
            CommandLine = Get-CommandLineText $Process
        }
    }
}

$processes = @(Get-CimInstance Win32_Process)
$targets = @{}

foreach ($process in $processes) {
    $cmd = Get-CommandLineText $process

    if (($process.Name -ieq 'python.exe' -or $process.Name -ieq 'pythonw.exe') -and
        (Has-AllText $cmd @('uvicorn', 'main:app', '--port', "$Porta"))) {
        Add-Target $targets $process 'Servidor AquaLog uvicorn'
    }

    if ($process.Name -ieq 'cloudflared.exe' -and
        ((Has-AllText $cmd @('tunnel', '--url', "127.0.0.1:$Porta")) -or
         (Has-AllText $cmd @('tunnel', '--url', "localhost:$Porta")))) {
        Add-Target $targets $process 'Tunel AquaLog cloudflared'
    }

    if ($process.Name -ieq 'cmd.exe' -and
        ((Has-AllText $cmd @('uvicorn', 'main:app', '--port', "$Porta")) -or
         (Has-AllText $cmd @('cloudflared', 'tunnel', "$Porta")))) {
        Add-Target $targets $process 'Janela AquaLog'
    }
}

$serverParents = @($targets.Values | Where-Object {
    ($_.Name -ieq 'python.exe' -or $_.Name -ieq 'pythonw.exe') -and $_.Reason -like '*uvicorn*'
})

foreach ($parent in $serverParents) {
    foreach ($process in $processes) {
        $cmd = Get-CommandLineText $process
        if (($process.Name -ieq 'python.exe' -or $process.Name -ieq 'pythonw.exe') -and
            ([int]$process.ParentProcessId -eq [int]$parent.Id -or $cmd -like "*parent_pid=$($parent.Id)*")) {
            Add-Target $targets $process 'Processo filho do uvicorn'
        }
    }
}

$listeners = @(Get-NetTCPConnection -LocalPort $Porta -State Listen -ErrorAction SilentlyContinue)
foreach ($listener in $listeners) {
    $ownerId = [int]$listener.OwningProcess
    if ($ownerId -le 0) { continue }
    $owner = $processes | Where-Object { [int]$_.ProcessId -eq $ownerId } | Select-Object -First 1
    $cmd = Get-CommandLineText $owner

    if (($owner.Name -ieq 'python.exe' -or $owner.Name -ieq 'pythonw.exe') -and
        ((Has-AllText $cmd @('uvicorn', 'main:app')) -or (Has-AllText $cmd @('multiprocessing.spawn', 'parent_pid=')))) {
        Add-Target $targets $owner 'Processo Python ouvindo na porta do AquaLog'

        if (Has-AllText $cmd @('multiprocessing.spawn', 'parent_pid=')) {
            $parentPid = [regex]::Match($cmd, 'parent_pid=(\d+)').Groups[1].Value
            if ($parentPid) {
                $parent = $processes | Where-Object { [int]$_.ProcessId -eq [int]$parentPid } | Select-Object -First 1
                $parentCmd = Get-CommandLineText $parent
                if (($parent.Name -ieq 'python.exe' -or $parent.Name -ieq 'pythonw.exe') -and
                    (Has-AllText $parentCmd @('uvicorn', 'main:app'))) {
                    Add-Target $targets $parent 'Processo pai do uvicorn'
                }
            }
        }
    } elseif ($owner) {
        Write-Host "Porta $Porta esta ocupada por $($owner.Name) PID $ownerId, mas nao foi encerrada por seguranca."
    }
}

$orderedTargets = @($targets.Values | Sort-Object Priority, Id)
if (-not $orderedTargets.Count) {
    Write-Host 'Nenhum processo do AquaLog encontrado.'
    exit 0
}

Write-Host 'Processos selecionados para encerrar:'
foreach ($target in $orderedTargets) {
    Write-Host ("- PID {0} {1}: {2}" -f $target.Id, $target.Name, $target.Reason)
}

if ($WhatIf) {
    Write-Host 'Modo WhatIf: nenhum processo foi encerrado.'
    exit 0
}

foreach ($target in $orderedTargets) {
    $running = Get-Process -Id $target.Id -ErrorAction SilentlyContinue
    if ($running) {
        Write-Host ("Encerrando PID {0} ({1})" -f $target.Id, $target.Name)
        Stop-Process -Id $target.Id -Force -ErrorAction SilentlyContinue
    }
}

Start-Sleep -Milliseconds 900

$remaining = @(Get-NetTCPConnection -LocalPort $Porta -State Listen -ErrorAction SilentlyContinue)
if ($remaining.Count -gt 0) {
    foreach ($listener in $remaining) {
        $owner = Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)"
        if ($owner) {
            Write-Host "A porta $Porta ainda esta ocupada por $($owner.Name) PID $($owner.ProcessId). Nao encerrei por seguranca."
        }
    }
    exit 1
}

Write-Host 'AquaLog parado com seguranca.'
