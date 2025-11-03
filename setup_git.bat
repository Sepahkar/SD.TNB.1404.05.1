@echo off
echo Initializing Git repository...
git init

echo Adding remote repository...
git remote add origin https://github.com/Sepahkar/SD.TNB.1404.05.1.git

echo Adding files...
git add .

echo Committing files...
git commit -m "Initial commit: Django project with SQLite database"

echo Setting main branch...
git branch -M main

echo Pushing to GitHub...
git push -u origin main

echo Done! Your project has been pushed to GitHub.
pause

