"""
Logging utility for booking system
Saves all console output to log files with Windows-compatible paths
"""
import os
import sys
from datetime import datetime
import pytz


class DualLogger:
    """Logger that outputs to both terminal and file"""

    def __init__(self, log_dir="logs", user_id=None):
        """
        Initialize dual logger

        Args:
            log_dir: Directory to save log files
            user_id: Optional user ID for unique log file naming
        """
        self.terminal = sys.stdout
        self.log_file = None
        self.log_dir = log_dir
        self.user_id = user_id

        # Create log directory if it doesn't exist
        os.makedirs(self.log_dir, exist_ok=True)

        # Generate log filename with HKT timestamp
        hkt = pytz.timezone('Asia/Hong_Kong')
        timestamp = datetime.now(hkt).strftime('%Y%m%d_%H%M%S')

        if user_id:
            log_filename = f"booking_log_{timestamp}_{user_id}.txt"
        else:
            log_filename = f"booking_log_{timestamp}.txt"

        # Use os.path.join for Windows compatibility
        self.log_path = os.path.join(self.log_dir, log_filename)

        # Open log file
        try:
            self.log_file = open(self.log_path, 'w', encoding='utf-8')
            self._log_header()
        except Exception as e:
            print(f"Warning: Could not create log file: {e}")
            self.log_file = None

    def _log_header(self):
        """Write log file header"""
        if self.log_file:
            hkt = pytz.timezone('Asia/Hong_Kong')
            now = datetime.now(hkt)
            header = f"""
{'='*70}
PolyU Booking System - Log File
{'='*70}
Started: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}
User ID: {self.user_id if self.user_id else 'N/A'}
Log File: {self.log_path}
{'='*70}

"""
            self.log_file.write(header)
            self.log_file.flush()

    def write(self, message):
        """Write message to both terminal and log file"""
        # Write to terminal
        self.terminal.write(message)
        self.terminal.flush()

        # Write to log file
        if self.log_file:
            try:
                self.log_file.write(message)
                self.log_file.flush()
            except Exception:
                pass  # Silently fail if log write fails

    def flush(self):
        """Flush both terminal and log file"""
        self.terminal.flush()
        if self.log_file:
            try:
                self.log_file.flush()
            except Exception:
                pass

    def close(self):
        """Close the log file"""
        if self.log_file:
            try:
                hkt = pytz.timezone('Asia/Hong_Kong')
                now = datetime.now(hkt)
                footer = f"""
{'='*70}
Log ended: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}
{'='*70}
"""
                self.log_file.write(footer)
                self.log_file.flush()
                self.log_file.close()
            except Exception:
                pass

    def __del__(self):
        """Cleanup when object is destroyed"""
        self.close()


def setup_logging(log_dir="logs", user_id=None):
    """
    Set up dual logging (terminal + file)

    Args:
        log_dir: Directory to save log files
        user_id: Optional user ID for unique log file naming

    Returns:
        DualLogger instance
    """
    logger = DualLogger(log_dir=log_dir, user_id=user_id)
    sys.stdout = logger
    sys.stderr = logger  # Also capture error output
    return logger


def restore_logging(logger):
    """
    Restore original stdout/stderr

    Args:
        logger: DualLogger instance to close
    """
    if logger:
        sys.stdout = logger.terminal
        sys.stderr = sys.__stderr__
        logger.close()


# Example usage
if __name__ == "__main__":
    # Test the logger
    logger = setup_logging(user_id="test_user")

    print("This will appear in both terminal and log file")
    print("Testing multiple lines...")
    print("All console output is being saved!")

    restore_logging(logger)
    print("This only appears in terminal (logging restored)")
