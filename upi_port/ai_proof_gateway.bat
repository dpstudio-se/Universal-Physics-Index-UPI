@echo off
setlocal enabledelayedexpansion

REM === Input parameters ===
set "AGENT_ID=%1"
set "DOMAIN=%2"
set "CHANGE_TYPE=%3"
set "PROPOSED_CHANGE=%4"
set "PROOF=%5"
set "ROUNDTRIP=%6"

REM === Log path ===
set "LOG_PATH=upi_port\logs\ai_proof_log.jsonl"

REM === Create folder if missing ===
if not exist "upi_port" mkdir "upi_port"
if not exist "upi_port\logs" mkdir "upi_port\logs"

REM === Timestamp ===
for /f "tokens=1-2 delims= " %%a in ("%date% %time%") do (
    set "TS=%%aT%%b"
)

REM === Append JSON entry ===
>> "%LOG_PATH%" echo {
>> "%LOG_PATH%" echo   "timestamp": "%TS%",
>> "%LOG_PATH%" echo   "agent_id": "%AGENT_ID%",
>> "%LOG_PATH%" echo   "domain": "%DOMAIN%",
>> "%LOG_PATH%" echo   "change_type": "%CHANGE_TYPE%",
>> "%LOG_PATH%" echo   "proposed_change": "%PROPOSED_CHANGE%",
>> "%LOG_PATH%" echo   "proof": "%PROOF%",
>> "%LOG_PATH%" echo   "roundtrip_verification": "%ROUNDTRIP%",
>> "%LOG_PATH%" echo   "status": "accepted_for_review",
>> "%LOG_PATH%" echo   "human_review_required": true
>> "%LOG_PATH%" echo }

echo AI/LLM-förslag loggat. Bevisbördan ligger på agenten. Ingen automatisk ändring sker.

endlocal
