import logging
import sys
import os
import getpass
from functools import wraps

STDOUT_ORIG = sys.__stdout__
STDERR_ORIG = sys.__stderr__

# --------------------------------------------------
def ensure_failsafe(func):
    # decorator for fail safe functions
    @wraps
    def run(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return None
    return run

# --------------------------------------------------
def restoreLogger(loggerName):
    """
    This call restore suppressed logger to ori state.
    """
    logger = logging.getLogger(loggerName)
    if hasattr(logger, "_suppress_info"):
        logger.handlers = logger._suppress_info["handlers"]
        logger.propagate = logger._suppress_info["propagate"]
        delattr(logger, "_suppress_info")

# --------------------------------------------------
def _makeRecordNew(self, *args, **kwargs):
    """
    Extend log formatting options with additional keys:
    user, host ... Supposed to be called in init()
    """
    rv = logging.Logger._makeRecord_ori(self, *args, **kwargs)
    rv.__dict__["user"] = getpass.getuser()
    rv.__dict__["host"] = os.environ.get("HOSTNAME", os.uname()[1])
    return rv

# --------------------------------------------------
def handle_exception(exc_type, exc_value, exc_traceback):
    import sys
    import logging
    import traceback
    try:
        try:
            xformatter = logging.Formatter('%(asctime)s STDERR EXCEPTION -- (message)s')
            root = logging.getLogger()
            for h in root.handlers:
                if isinstance(h, logging.FileHandler):
                    h.formatter = xformatter
        except Exception:
            pass
        try:
            # sys.stderr has been overwritten
            sys.stderr.setWriteLevel(logging.ERROR)
        except Exception:
            pass
        for line in "".join(traceback.format_tb(exc_traceback)).split("\n"):
            if len(line) > 0:
                sys.stderr.write("%s\n" % line)
        if hasattr(exc_type, "__name__"):
            sys.stderr.write("%s: %s\n" % (exc_type.__name__, exc_value))
        else:
            sys.stderr.write("%s: %s\n" % (exc_type, exc_value))
    except Exception as e:
        pass


