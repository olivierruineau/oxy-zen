#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script helper pour creer une release Oxy-Zen
    
.DESCRIPTION
    Ce script automatise le processus de release :
    1. Verifie que le repo est propre (pas de changements non commites)
    2. Lit la version dans pyproject.toml
    3. Cree et push un tag Git
    4. Declenche automatiquement le workflow GitHub Actions
    
.PARAMETER Version
    Version a releaser (optionnel). Si omis, utilise la version de pyproject.toml
    Format: 1.0.0 (sans le 'v')
    
.EXAMPLE
    .\scripts\release.ps1
    # Utilise la version de pyproject.toml (0.1.0)
    
.EXAMPLE
    .\scripts\release.ps1 -Version 1.2.3
    # Cree une release v1.2.3 (met a jour pyproject.toml d'abord)
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Version
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Oxy-Zen - Release Helper" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifier qu'on est bien dans le repertoire racine
if (!(Test-Path "pyproject.toml")) {
    Write-Host "[X] ERREUR: Lance ce script depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# Verifier que git est installe
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "[X] ERREUR: Git n'est pas installe ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Verifier qu'on est sur une branche git
try {
    $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
} catch {
    Write-Host "[X] ERREUR: Ce n'est pas un depot Git" -ForegroundColor Red
    exit 1
}

Write-Host "[>] Branche actuelle: $currentBranch" -ForegroundColor Gray

# Verifier qu'il n'y a pas de changements non commites
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "[X] ERREUR: Il y a des changements non commites:" -ForegroundColor Red
    Write-Host $status -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commite ou stash tes changements avant de faire une release." -ForegroundColor Yellow
    exit 1
}

Write-Host "[OK] Depot propre (pas de changements non commites)" -ForegroundColor Green

# Lire la version de pyproject.toml
$pyprojectContent = Get-Content "pyproject.toml" -Raw
if ($pyprojectContent -match 'version\s*=\s*"([^"]+)"') {
    $currentVersion = $matches[1]
} else {
    Write-Host "[X] ERREUR: Impossible de lire la version dans pyproject.toml" -ForegroundColor Red
    exit 1
}

# Determiner la version a utiliser
if ($Version) {
    $targetVersion = $Version
    
    # Verifier le format de la version
    if ($targetVersion -notmatch '^\d+\.\d+\.\d+$') {
        Write-Host "[X] ERREUR: Format de version invalide: $targetVersion" -ForegroundColor Red
        Write-Host "   Format attendu: X.Y.Z (ex: 1.0.0)" -ForegroundColor Yellow
        exit 1
    }
    
    if ($targetVersion -ne $currentVersion) {
        Write-Host ""
        Write-Host "[!] Version differente detectee:" -ForegroundColor Yellow
        Write-Host "   pyproject.toml: $currentVersion" -ForegroundColor Gray
        Write-Host "   Demandee: $targetVersion" -ForegroundColor Gray
        Write-Host ""
        $confirm = Read-Host "Mettre a jour pyproject.toml a $targetVersion ? (y/N)"
        
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            # Mettre a jour pyproject.toml
            $pyprojectContent = $pyprojectContent -replace 'version\s*=\s*"[^"]+"', "version = `"$targetVersion`""
            Set-Content "pyproject.toml" $pyprojectContent -NoNewline
            
            Write-Host "[OK] pyproject.toml mis a jour" -ForegroundColor Green
            
            # Commiter le changement
            git add pyproject.toml
            git commit -m "chore: bump version to $targetVersion"
            Write-Host "[OK] Changement commite" -ForegroundColor Green
        } else {
            Write-Host "[X] Release annulee" -ForegroundColor Red
            exit 1
        }
    }
} else {
    $targetVersion = $currentVersion
}

$tag = "v$targetVersion"

Write-Host ""
Write-Host "[#] Version a releaser: $targetVersion" -ForegroundColor Cyan
Write-Host "[#] Tag Git: $tag" -ForegroundColor Cyan

# Verifier que le tag n'existe pas deja
$existingTag = git tag -l $tag
if ($existingTag) {
    Write-Host ""
    Write-Host "[X] ERREUR: Le tag $tag existe deja" -ForegroundColor Red
    Write-Host "   Versions existantes:" -ForegroundColor Gray
    git tag -l "v*" | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    exit 1
}

Write-Host ""
Write-Host "Recapitulatif:" -ForegroundColor Yellow
Write-Host "  - Version: $targetVersion" -ForegroundColor White
Write-Host "  - Tag: $tag" -ForegroundColor White
Write-Host "  - Branche: $currentBranch" -ForegroundColor White
Write-Host ""
Write-Host "Actions qui seront effectuees:" -ForegroundColor Yellow
Write-Host "  1. Creer le tag $tag localement" -ForegroundColor White
Write-Host "  2. Pusher le tag vers GitHub" -ForegroundColor White
Write-Host "  3. Declencher le workflow GitHub Actions" -ForegroundColor White
Write-Host "  4. Builder l'exe Windows automatiquement" -ForegroundColor White
Write-Host "  5. Creer une release GitHub avec l'exe" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continuer ? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "[X] Release annulee" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "[>>] Creation de la release..." -ForegroundColor Cyan
Write-Host ""

# Creer le tag
Write-Host "[1/2] Creation du tag $tag..." -ForegroundColor Gray
git tag -a $tag -m "Release version $targetVersion"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] ERREUR: Echec de la creation du tag" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Tag cree localement" -ForegroundColor Green

# Pusher le tag
Write-Host "[2/2] Push du tag vers GitHub..." -ForegroundColor Gray
git push origin $tag
if ($LASTEXITCODE -ne 0) {
    Write-Host "[X] ERREUR: Echec du push du tag" -ForegroundColor Red
    Write-Host "   Tu peux le pusher manuellement: git push origin $tag" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Tag pushe vers GitHub" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   [OK] Release declenchee avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "[>] Prochaines etapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Le workflow GitHub Actions est en cours:" -ForegroundColor White
Write-Host "   https://github.com/olivierruineau/oxy-zen/actions" -ForegroundColor Blue
Write-Host ""
Write-Host "2. Une fois termine (~5 minutes), la release sera disponible:" -ForegroundColor White
Write-Host "   https://github.com/olivierruineau/oxy-zen/releases" -ForegroundColor Blue
Write-Host ""
Write-Host "3. Tu peux suivre l'avancement du build dans l'onglet Actions" -ForegroundColor White
Write-Host ""
Write-Host "[i] Astuce: Si le build echoue, tu peux supprimer le tag avec:" -ForegroundColor Gray
Write-Host "   git tag -d $tag" -ForegroundColor Gray
Write-Host "   git push origin :refs/tags/$tag" -ForegroundColor Gray
Write-Host ""
