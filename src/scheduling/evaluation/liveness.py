"""OS-held run activity, separate from durable exclusive-create protection.

A killed process releases flock but leaves .lock behind. Only manual recovery may
remove an abandoned lock; probing never edits it or authorizes another attempt.
"""

import errno
import fcntl
import os
from pathlib import Path
import stat


_MARKER = b"cs3263-run-lock-v1\n"


def _same_file(path, descriptor):
    try:
        current = path.lstat()
    except FileNotFoundError:
        return False
    held = os.fstat(descriptor)
    return (stat.S_ISREG(current.st_mode) and current.st_nlink == 1
            and (current.st_dev, current.st_ino) == (held.st_dev, held.st_ino))


class RunLock:
    """Exclusively create a run lock and keep its descriptor held for the run."""

    def __init__(self, path):
        self.path = Path(path)
        self.fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if os.write(self.fd, _MARKER) != len(_MARKER):
                raise OSError("Incomplete run lock marker write")
            os.fsync(self.fd)
            if not _same_file(self.path, self.fd):
                raise ValueError("Run lock changed during acquisition")
        except BaseException:
            # Preserve the exclusive-create tombstone if initialization failed.
            os.close(self.fd)
            self.fd = None
            raise

    def release(self):
        if self.fd is None:
            return
        try:
            if not _same_file(self.path, self.fd):
                raise ValueError("Run lock replaced or removed; replacement left unchanged")
            # Keep the advisory lock held until the original pathname is removed.
            self.path.unlink()
        finally:
            os.close(self.fd)
            self.fd = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.release()


def probe_run_liveness(directory):
    """Return active/inactive/unknown_legacy without changing run files."""
    path = Path(directory) / ".lock"
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return "inactive"
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("Run lock must not be a symlink") from None
        raise
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError("Run lock must be a single-link regular file")
        marker = os.read(fd, len(_MARKER) + 1)
        if marker != _MARKER:
            state = "unknown_legacy"
        else:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                if exc.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                state = "active"
            else:
                state = "inactive"
                fcntl.flock(fd, fcntl.LOCK_UN)
        if not _same_file(path, fd):
            raise ValueError("Run lock changed during activity check; refresh required")
        return state
    finally:
        os.close(fd)
