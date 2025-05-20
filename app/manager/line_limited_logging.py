# Name: line_limited_logging.py
# Version: 0.1.0
# Created: 250519
# Modified: 250519
# Creator: ParcoAdmin
# Modified By: ParcoAdmin
# Description: Custom logging handler for line-limited logs
# Location: /home/parcoadmin/parco_fastapi/app/manager
# Role: Backend
# Status: Active
# Dependent: TRUE

import logging
import os
from typing import Optional

class LineLimitedFileHandler(logging.Handler):
    def __init__(self, filename: str, max_lines: int = 999, backup_count: int = 4):
        super().__init__()
        self.filename = filename
        self.max_lines = max_lines
        self.backup_count = backup_count
        self.current_lines = 0
        self.file = None
        self.open_file()

    def open_file(self):
        """Opens the log file in append mode and counts existing lines."""
        if os.path.exists(self.filename):
            with open(self.filename, 'r', encoding='utf-8') as f:
                self.current_lines = sum(1 for _ in f)
        self.file = open(self.filename, 'a', encoding='utf-8')

    def emit(self, record: logging.LogRecord):
        """Writes a log record and rotates if max_lines is reached."""
        try:
            msg = self.format(record)
            self.current_lines += 1
            self.file.write(msg + '\n')
            self.file.flush()

            if self.current_lines >= self.max_lines:
                self.rotate()
        except Exception as e:
            self.handleError(record)

    def rotate(self):
        """Rotates log files, keeping up to backup_count archives."""
        self.file.close()
        # Shift existing backups (e.g., .4 -> .5, .3 -> .4, etc.)
        for i in range(self.backup_count - 1, 0, -1):
            src = f"{self.filename}.{i}"
            dst = f"{self.filename}.{i+1}"
            if os.path.exists(src):
                if os.path.exists(dst):
                    os.remove(dst)
                os.rename(src, dst)
        # Move current log to .1
        if os.path.exists(self.filename):
            os.rename(self.filename, f"{self.filename}.1")
        # Reset current_lines and reopen file
        self.current_lines = 0
        self.open_file()

    def close(self):
        """Closes the file handle."""
        if self.file:
            self.file.close()
            self.file = None
        super().close()