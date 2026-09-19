$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$required = @(
    'README.md'
    'PROJECTS.md'
    'ROADMAP.md'
    'SECURITY.md'
    'CONTRIBUTING.md'
    'docs/project-template.md'
    'docs/projects/enterprise-rag-evals.md'
)

foreach ($relative in $required) {
    $path = Join-Path $root $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Missing required file: $relative"
    }
}

$readme = Get-Content -LiteralPath (Join-Path $root 'README.md') -Raw
foreach ($heading in @('AI Engineer', 'Featured project', 'Projects', 'What I prove')) {
    if ($readme -notmatch [regex]::Escape($heading)) {
        throw "README is missing required text: $heading"
    }
}

$tracked = @(git -C $root ls-files '*.md' '*.ps1')
$secretPattern = '(?i)(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|ghp_[A-Za-z0-9]{20,})'
foreach ($relative in $tracked) {
    $path = Join-Path $root $relative
    $content = Get-Content -LiteralPath $path -Raw
    if ($content -match $secretPattern) {
        throw "Secret-shaped value found in tracked file: $relative"
    }
}

$markdownPaths = @(
    (Join-Path $root 'README.md')
    (Join-Path $root 'PROJECTS.md')
)
$localLinks = foreach ($path in $markdownPaths) {
    $content = Get-Content -LiteralPath $path -Raw
    foreach ($match in [regex]::Matches($content, '\]\(([^)#]+)\)')) {
        $match.Groups[1].Value
    }
}

foreach ($target in $localLinks) {
    if ($target -match '^(https?://|#)') {
        continue
    }

    $targetPath = Join-Path $root $target
    if (-not (Test-Path -LiteralPath $targetPath)) {
        throw "Broken local Markdown link: $target"
    }
}

Write-Output 'Portfolio validation passed.'
