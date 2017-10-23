:<<"::CMDLITERAL"
@echo off
goto :CMDSCRIPT
::CMDLITERAL
#!/bin/bash
set -euo pipefail
IFS=$'\n\t'

script_dir=$(cd $(dirname $0); pwd -P)

$script_dir/bootstrap $script_dir/sniptool.py $*

exit $?
:CMDSCRIPT
@echo off
call "%~dp0bootstrap.cmd" "%~dp0sniptool.py" %*
if errorlevel 1 (
    echo script failed
    exit /b 1
)
