# Script for initializing Git and pushing to GitHub

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Green
git init

# Add remote repository
Write-Host "Adding remote repository..." -ForegroundColor Green
git remote add origin https://github.com/Sepahkar/SD.TNB.1404.05.1.git

# Add all files
Write-Host "Adding files..." -ForegroundColor Green
git add .

# Commit files
Write-Host "Committing files..." -ForegroundColor Green
git commit -m "Initial commit: Django project with SQLite database"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

Write-Host "Done! Your project has been pushed to GitHub." -ForegroundColor Green

