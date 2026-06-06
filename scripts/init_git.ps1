param(
    [string]$DefaultBranch = "main",
    [string]$DevBranch = "dev"
)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "git is not installed or not in PATH"
    exit 1
}

git init
git add .
git commit -m "chore: initial project scaffold"
git branch -M $DefaultBranch
git checkout -b $DevBranch

Write-Host "Initialized git repository with branches: $DefaultBranch (main), $DevBranch (dev)"
