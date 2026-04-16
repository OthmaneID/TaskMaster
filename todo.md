# TaskMaster TODO (Roadmap)

1. Normalize config and runtime state in `core/Program.py`.   DONE

2. Fix process IO handling and PID logic in `core/Program.py`.

3. Move supervision logic into `core/supervisor.py` with a single `run_forever()` loop. DONE

4. Implement restart policy states: `exited`, `backoff`, `fatal`. DONE
 
5. Add graceful stop: signals + per-program `stopsignal` and `stoptime`.     DOING (not signals but just cli commands (todo when finishing the cli))

6. Implement `numprocs`, `workingdir`, `umask`, and `env`.DONE

7. Add logging: global logfile and per-program stdout/stderr.  DONE

8. Provide a minimal CLI: `start`, `stop`, `restart`, `status`. DOING       <----------

9. Add test script or basic tests for restart policy and exit codes.  DONE (workers dir)

10. make the config automaticly reload when it is changed (check every 3 seconds).  DONE

11. add validation for the config file  


12 . add a client side (cli) to interact with the server (DONE)