# TaskMaster Project Roadmap

## Project Overview
TaskMaster is a process supervisor and manager that handles running, monitoring, and controlling multiple programs with dynamic configuration and runtime management capabilities.

---

## Phase 1: Core Foundation

### 1.1 Configuration System [HIGH PRIORITY]
- [*] **Design YAML configuration schema** (Status: To Do)
  - Define all required and optional fields
  - Document configuration examples
  
- [ ] **Write YAML config parser using PyYAML** (Status: To Do)
  - Parse configuration file
  - Validate configuration format
  - Handle configuration errors gracefully

- [ ] **Implement dynamic config reload** (Status: To Do)
  - Add SIGHUP signal handler
  - Reload configuration without stopping running processes
  - Remove/add/modify program configurations at runtime
  - Preserve unmodified process instances

### 1.2 Process Management [HIGH PRIORITY]
- [ ] **Implement process spawning with subprocess** (Status: To Do)
  - Launch programs as specified in config
  - Track process instances (PIDs)
  - Manage multiple instances per program

- [ ] **Add process lifecycle management** (Status: To Do)
  - Start/stop/restart capabilities
  - Graceful shutdown with configurable signals
  - Force kill after timeout
  - Handle unexpected exits

---

## Phase 2: Monitoring & Restart Logic

### 2.1 Process Monitoring [MEDIUM PRIORITY]
- [ ] **Implement process health tracking** (Status: To Do)
  - Monitor process status continuously
  - Detect unexpected exits
  - Track uptime

- [ ] **Add restart policies** (Status: To Do)
  - Always restart on exit
  - Never restart
  - Restart only on unexpected exits
  - Define expected vs unexpected exit codes
  - Set minimum uptime threshold for "successful start"
  - Configurable restart attempt limits

### 2.2 Logging System [MEDIUM PRIORITY]
- [ ] **Implement comprehensive logging** (Status: To Do)
  - Log program start/stop/restart events
  - Log unexpected exits with details
  - Log configuration reload events
  - Log signal handling
  - Support file redirection or discard of stdout/stderr

---

## Phase 3: User Interaction

### 3.1 Command Line Interface [MEDIUM PRIORITY]
- [ ] **Build CLI interface** (Status: To Do)
  - List all programs and their status
  - Start/stop/restart individual programs
  - Reload configuration file
  - Shutdown supervisor
  - View logs/history
  - Track command execution history

---

## Configuration Schema Details

### Required Program Configuration Fields
- [ ] Program name/identifier
- [ ] Command to execute
- [ ] Number of processes to maintain (pool size)
- [ ] Auto-start on system launch (boolean)
- [ ] Restart policy (always/never/on-error)
- [ ] Expected exit codes list
- [ ] Minimum successful uptime duration
- [ ] Maximum restart attempts
- [ ] Graceful stop signal (SIGTERM, SIGINT, etc.)
- [ ] Kill timeout (seconds to wait after signal)
- [ ] Output handling (file, discard, or inherit)
- [ ] Environment variables dictionary
- [ ] Working directory
- [ ] Process umask

---

## Implementation Notes
- All features follow supervisor-like patterns
- Configuration changes during runtime must be non-disruptive
- Process pools can be scaled independently
- Comprehensive logging for audit trail and debugging
