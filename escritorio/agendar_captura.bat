@echo off
REM Cadastra a busca de intimacoes para rodar todo dia as 07:30 e as 13:30 (Agendador de Tarefas do Windows).
REM Basta dar dois cliques neste arquivo uma vez.
schtasks /Create /F /SC DAILY /ST 07:30 /TN "CSA Intimacoes manha" /TR "\"%~dp0capturar.bat\""
schtasks /Create /F /SC DAILY /ST 13:30 /TN "CSA Intimacoes tarde" /TR "\"%~dp0capturar.bat\""
echo.
echo Pronto! A busca vai rodar todo dia as 07:30 e as 13:30 (com o computador ligado).
echo Para desfazer: schtasks /Delete /TN "CSA Intimacoes manha" /F  e  schtasks /Delete /TN "CSA Intimacoes tarde" /F
pause
