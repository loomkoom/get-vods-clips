@Echo off
for /f "tokens=1-2 delims=-" %%A in ('
    git rev-parse --abbrev-ref HEAD
') Do Set "Var=%%A-%%B"
Echo:%Var%
pause