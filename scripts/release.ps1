#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script helper pour créer une release Oxy-Zen
    
.DESCRIPTION
    Ce script automatise le processus de release :
    1. Vérifie que le repo est propre (pas de changements non commités)
    2. Lit la version dans pyproject.toml
    3. Crée et push un tag Git
    4. Déclenche automatiquement le workflow GitHub Actions
    
.PARAMETER Version
    Version à releaser (optionnel). Si omis, utilise la version de pyproject.toml
    Format: 1.0.0 (sans le 'v')
    
.EXAMPLE
    .\scripts\release.ps1
    # Utilise la version de pyproject.toml (0.1.0)
    
.EXAMPLE
    .\scripts\release.ps1 -Version 1.2.3
    # Crée une release v1.2.3 (met à jour pyproject.toml d'abord)
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

# Vérifier qu'on est bien dans le répertoire racine
if (!(Test-Path "pyproject.toml")) {
    Write-Host "❌ ERREUR: Lance ce script depuis la racine du projet" -ForegroundColor Red
    exit 1
}

# Vérifier que git est installé
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ ERREUR: Git n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    exit 1
}

# Vérifier qu'on est sur une branche git
try {
    $currentBranch = git rev-parse --abbrev-ref HEAD 2>$null
} catch {
    Write-Host "❌ ERREUR: Ce n'est pas un dépôt Git" -ForegroundColor Red
    exit 1
}

Write-Host "📍 Branche actuelle: $currentBranch" -ForegroundColor Gray

# Vérifier qu'il n'y a pas de changements non commités
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "❌ ERREUR: Il y a des changements non commités:" -ForegroundColor Red
    Write-Host $status -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Commite ou stash tes changements avant de faire une release." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dépôt propre (pas de changements non commités)" -ForegroundColor Green

# Lire la version de pyproject.toml
$pyprojectContent = Get-Content "pyproject.toml" -Raw
if ($pyprojectContent -match 'version\s*=\s*"([^"]+)"') {
    $currentVersion = $matches[1]
} else {
    Write-Host "❌ ERREUR: Impossible de lire la version dans pyproject.toml" -ForegroundColor Red
    exit 1
}

# Déterminer la version à utiliser
if ($Version) {
    $targetVersion = $Version
    
    # Vérifier le format de la version
    if ($targetVersion -notmatch '^\d+\.\d+\.\d+$') {
        Write-Host "❌ ERREUR: Format de version invalide: $targetVersion" -ForegroundColor Red
        Write-Host "   Format attendu: X.Y.Z (ex: 1.0.0)" -ForegroundColor Yellow
        exit 1
    }
    
    if ($targetVersion -ne $currentVersion) {
        Write-Host ""
        Write-Host "⚠️  Version différente détectée:" -ForegroundColor Yellow
        Write-Host "   pyproject.toml: $currentVersion" -ForegroundColor Gray
        Write-Host "   Demandée: $targetVersion" -ForegroundColor Gray
        Write-Host ""
        $confirm = Read-Host "Mettre à jour pyproject.toml à $targetVersion ? (y/N)"
        
        if ($confirm -eq 'y' -or $confirm -eq 'Y') {
            # Mettre à jour pyproject.toml
            $pyprojectContent = $pyprojectContent -replace 'version\s*=\s*"[^"]+"', "version = `"$targetVersion`""
            Set-Content "pyproject.toml" $pyprojectContent -NoNewline
            
            Write-Host "✅ pyproject.toml mis à jour" -ForegroundColor Green
            
            # Commiter le changement
            git add pyproject.toml
            git commit -m "chore: bump version to $targetVersion"
            Write-Host "✅ Changement commité" -ForegroundColor Green
        } else {
            Write-Host "❌ Release annulée" -ForegroundColor Red
            exit 1
        }
    }
} else {
    $targetVersion = $currentVersion
}

$tag = "v$targetVersion"

Write-Host ""
Write-Host "📦 Version à releaser: $targetVersion" -ForegroundColor Cyan
Write-Host "🏷️  Tag Git: $tag" -ForegroundColor Cyan

# Vérifier que le tag n'existe pas déjà
$existingTag = git tag -l $tag
if ($existingTag) {
    Write-Host ""
    Write-Host "❌ ERREUR: Le tag $tag existe déjà" -ForegroundColor Red
    Write-Host "   Versions existantes:" -ForegroundColor Gray
    git tag -l "v*" | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    exit 1
}

Write-Host ""
Write-Host "Récapitulatif:" -ForegroundColor Yellow
Write-Host "  • Version: $targetVersion" -ForegroundColor White
Write-Host "  • Tag: $tag" -ForegroundColor White
Write-Host "  • Branche: $currentBranch" -ForegroundColor White
Write-Host ""
Write-Host "Actions qui seront effectuées:" -ForegroundColor Yellow
Write-Host "  1. Créer le tag $tag localement" -ForegroundColor White
Write-Host "  2. Pusher le tag vers GitHub" -ForegroundColor White
Write-Host "  3. Déclencher le workflow GitHub Actions" -ForegroundColor White
Write-Host "  4. Builder l'exe Windows automatiquement" -ForegroundColor White
Write-Host "  5. Créer une release GitHub avec l'exe" -ForegroundColor White
Write-Host ""

$confirm = Read-Host "Continuer ? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "❌ Release annulée" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🚀 Création de la release..." -ForegroundColor Cyan
Write-Host ""

# Créer le tag
Write-Host "[1/2] Création du tag $tag..." -ForegroundColor Gray
git tag -a $tag -m "Release version $targetVersion"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERREUR: Échec de la création du tag" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Tag créé localement" -ForegroundColor Green

# Pusher le tag
Write-Host "[2/2] Push du tag vers GitHub..." -ForegroundColor Gray
git push origin $tag
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ ERREUR: Échec du push du tag" -ForegroundColor Red
    Write-Host "   Tu peux le pusher manuellement: git push origin $tag" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Tag pushé vers GitHub" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   ✅ Release déclenchée avec succès !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Prochaines étapes:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Le workflow GitHub Actions est en cours:" -ForegroundColor White
Write-Host "   https://github.com/olivierruineau/oxy-zen/actions" -ForegroundColor Blue
Write-Host ""
Write-Host "2. Une fois terminé (~5 minutes), la release sera disponible:" -ForegroundColor White
Write-Host "   https://github.com/olivierruineau/oxy-zen/releases" -ForegroundColor Blue
Write-Host ""
Write-Host "3. Tu peux suivre l'avancement du build dans l'onglet Actions" -ForegroundColor White
Write-Host ""
Write-Host "💡 Astuce: Si le build échoue, tu peux supprimer le tag avec:" -ForegroundColor Gray
Write-Host "   git tag -d $tag" -ForegroundColor Gray
Write-Host "   git push origin :refs/tags/$tag" -ForegroundColor Gray
Write-Host ""
