# TaskMaster

A process supervisor for managing and monitoring services. Think of it as a simpler, more lightweight alternative to supervisord with a web dashboard.

## What it does

TaskMaster lets you:
- Define services in a YAML config file
- Start, stop, and restart multiple processes per service
- Monitor process status and RAM usage from a web dashboard
- Control processes individually or in groups
- Auto-restart failed processes (with configurable retry logic)
- Send commands via a CLI shell

## Architecture

```
              ┌─────────────┐
              │ Supervisor  │
              │  (Python)   │
              │             │
              │   Process   │
              │  Management │
              └──────┬──────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────┐        ┌──────────────┐
│  CLI Shell   │        │   Backend    │
│ (TcpClient)  │        │  (FastAPI)   │
└──────────────┘        │  API routes  │
                        └──────┬───────┘
                               │
                               ▼
                        ┌─────────────┐
                        │  Frontend   │
                        │  (React)    │
                        │  Dashboard  │
                        └─────────────┘

Workers managed by Supervisor
```

## Getting started

1. Define your services in `server/workers/conf.yaml`
2. Start the supervisor: `python server/main.py server/workers/conf.yaml`
3. Start the backend API: `python -m webapp.backend`
4. Start the frontend: `cd webapp/frontend && npm run dev`
5. Or use the CLI shell: `python client/main.py`

## Configuration

Each service in `conf.yaml` can have:
- `cmd` - Command to run
- `numprocs` - Number of processes to spawn
- `autostart` - Start on supervisor launch
- `autorestart` - "always", "never", or "unexpected"
- `startretries` - Max restart attempts
- `exitcodes` - Expected exit codes
- `stopsignal` - Signal to stop (TERM, KILL, etc.)
- `env` - Environment variables
- `stdout/stderr` - Log file paths

## API endpoints

- `GET /programs/list` - List all processes
- `GET /programs/status/{service_name}` - Get detailed status
- `POST /programs/start/{service_name}/{process_num?}` - Start process(es)
- `POST /programs/stop/{service_name}/{process_num?}` - Stop process(es)
- `POST /programs/restart/{service_name}/{process_num?}` - Restart process(es)
- `GET /programs/ramUsage` - Get RAM usage per process

## CLI commands

- `list` - List all services
- `status <service>` - Show detailed status
- `start <service> [process_num]` - Start process(es)
- `stop <service> [process_num]` - Stop process(es)
- `restart <service> [process_num]` - Restart process(es)

## Notes

- The supervisor monitors processes and can auto-restart them based on config
- Config file changes are detected via SIGHUP or polling
- Processes are tracked by name and process number
- RAM usage is read from `/proc/{pid}/status` when available
