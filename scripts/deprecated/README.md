# Deprecated Scripts

These scripts are no longer used in the current plugin architecture but are preserved for reference.

## Deprecated Files

### `ensure-dependencies.sh`
- **Previously**: Installed dependencies in background with nohup
- **Replaced by**: `scripts/install-all-dependencies.py`
- **Reason**:
  - New flow installs ALL dependencies during `/project-planner:setup` (synchronous, with progress)
  - No longer uses background installation
  - Better user visibility and control

### `wait-for-dependencies.py`
- **Previously**: Monitored background installation progress
- **Replaced by**: Direct installation feedback in `install-all-dependencies.py`
- **Reason**:
  - No longer needed with synchronous installation
  - Progress shown directly during setup

## Migration

Old flow (v1.3.1 and earlier):
```bash
# SessionStart hook triggered on /full-plan
nohup ensure-dependencies.sh full &
# Later...
python wait-for-dependencies.py  # Block until ready
```

New flow (v1.3.2+):
```bash
# User runs setup first
/project-planner:setup
# → Validates API keys
# → Installs all dependencies synchronously
# → Shows capability matrix

# Then use any command
/full-plan
/tech-plan
```

## Date Deprecated
2026-01-15 (Plugin v1.3.2)
