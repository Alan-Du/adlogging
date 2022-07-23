"""
Logging setup and utilities: customized logging configuration
    The logging is set up with init() method when this module
    is called. The call of init() can take config dictionary
    as a parameter in which case the logging will be configured
    by setupDefaultLogging() method, otherwise only necessary
    steps to enable logging will be taken while the configuration
    of the logging will be left to caller.

Parameters dictionary of the default setup description:
LOGGING_CONFIG = {
    # Logging attributes intensity (like line numbers, source files...)
    "STYLE": "VOID" | "SIMPLE" | "LIGHT" | "MEDIUM" | "HEAVY"

    # Style of logging to console: whether print prefix to console
    "CONSOLE_STYLE": "MINIMAL" | ...

    # Log to same daily file or to separate file per process or not.
    # default is PROCESS
    "FILE": "PROCESS" | "DAILY" | "NONE"

    # Log to specific file overwrite FILE and FILE_PREFIX
    "FILE_NAME": [str]

    # Which folder should have log files, ~/logs/ is default
    "PATH": path of the log file directory

    # Which class to use for main file handler. The default is logging.FileHandler
    "FILE_HANDLER_CLASS": alternative handler class

    # Which model log files will be open/created
    # "A" mode will append if log exists.
    # "O" mode will replace the log info and write from begining.
    "FILE_MODE": "A(PPEND)" | "O(VERWRITE)"

    # Should ERROR loglevel and above to file or not, default is FALSE
    "ERRORS_FILE": "FALSE" | "TRUE"

    # Should separately output print go to console or not default is FALSE
    "PRINT_TO_CONSOLE": "FALSE" | "TRUE"

    # Should root logging go to console, default is FALSE
    "ROOT_TO_CONSOLE": "FALSE" | "TRUE"

    # Should rotating mem buffer be used and where to dump it, default is FALSE
    "MEM_BUFER": "FILE" | "FILE+CONSOLE" | "CONSOLE" | "NONE"
}
Note: all keys and values could be lower case or upper case - it doesnt matter

Example:
    import adlogging
    adlogging.init({"STYLE": "SIMPLE", "FILE":"SAME"})

Author: Shaolun Du
Contact: Shaolun.du@gmail.com
"""
import getpass
import logging
import os.path
import datetime
import sys
from . import output2log
from . import handlers
from . import log_utils
from .log_utils import STDOUT_ORIG, STDERR_ORIG
from .log_utils import restoreLogger
from .handlers import LevelBasedFormatter, ErrorFileHandler

# Global falg to avoid re-init
_LOGGING_INIT_STATUS = False

# Before init() we setup the logging level to INFO
# as .info() and above would be printed in case init()
# is not called
root_logger = logging.getLogger()
root_logger.setLevel(logging.NOTSET)

h = handlers._PrintHandler()
h.setLevel(logging.INFO)
root_logger.addHandler(h)

# addin DEBUG level = 5
logging.addLevelName(5, "DEBUG")
logging.DEBUG = 21
# addin INFO level = 21
logging.addLevelName(21, "INFO_PRINT")
logging.INFO_PRINT = 21

# Expose logging aliases
getLogger = logging.getLogger()
NOTEST = logging.NOTSET
DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL

# setup pre-defined formatters
default_formatter_void = LevelBasedFormatter('%(message)s')
default_formatter_simple = LevelBasedFormatter(
    '%(asctime)s %(levelname)s %(name)s -- %(message)s'
)
default_formatter_light = LevelBasedFormatter(
    '%(asctime)s %(levelname)s | line %(line)s @ %(filename)s -- %(message)s'
)
default_formatter_medium = LevelBasedFormatter(
    '%(asctime)s %(levelname)s %(name)s ' +
    '| %(funcName)s(..) | line %(line)s @ %(filename)s -- %(message)s'
)
default_formatter_heavy = LevelBasedFormatter(
    '%(asctime)s.%(msecs)03d %(levelname)1.1s' +
    '|%(lineno)4s.%(filename)-10.10s -- %(message)s'
    , datefmt="%d%H:%M:%S"
)
default_formatter = default_formatter_simple

logging_formatters = dict(
    VOID = default_formatter_void,
    SIMPLE = default_formatter_simple,
    LIGHT = default_formatter_light,
    MEDIUM = default_formatter_medium,
    HEAVY = default_formatter_heavy,
)

# logfile default name
log_file_name = None

# --------------------------------------------------
@log_utils.ensure_failsafe
def setupDefaultLogging(config):
    """
    Method setup root logger to default file in ~/logs
    directory of the current user. After importing
    any logger return as getLogger("your app name") will log
    to that file. Logging at INFO level and up also goes to
    console(stdout). The default config is to create a separate
    file per process. If the first parameter is True. Logging
    will go to the common daily file for all logging processes.
    If second parameter is True, a separate file will be created
    for logging only errors and above, either daily or per process.
    We setup the following here:
        Formatters - handlers for "output" format
        Logging location and name
        root_logger adds:
        default_file_handler, error_file_handler, console_handler
    """
    # Ensure uppercase in config with a few exception
    new_config = {}
    for key in config:
        ukey = str(key).upper()
        if ukey in ("PATH", "FILE_NAME", "FILE_PREFIX"):
            new_config[ukey] = str(config[key])
        elif ukey in ("FILE_HANDLER_CLASS"):
            new_config[ukey] = config[key]
        else:
            new_config[ukey] = str(config[key]).upper()
    config = new_config

    # Handle FILE_MODE parameter
    # Overwrite default FileHandler setup
    f_mode = config.get("FILE_MODE", "A")
    if f_mode.startswith("A"):
        _d = list(logging.FileHandler.__init__.__defaults__)
        _d[0] = "a"
        logging.FileHandler.__init__.__defaults__ = _d
    elif f_mode.startswith("O"):
        _d = list(logging.FileHandler.__init__.__defaults__)
        _d[0] = "w"
        logging.FileHandler.__init__.__defaults__ = _d

    # Formatters
    if config.get("CONSOLE_STYLE", "MINIMAL") == "MINIMAL":
        console_formatter = logging.Formatter('%(message)s')
    else:
        console_formatter = logging.Formatter('line %(lineno)s in @ %(filename)s -- %(message)s')
    global default_formatter
    logging_style = config.get("STYLE", "SIMPLE")
    default_formatter = logging_formatters.get(logging_style, default_formatter_heavy)

    # logging files
    log_file_dir = config.get("PATH", "~/logs")
    if "~" in log_file_dir:
        log_file_dir = os.path.expanduser(log_file_dir)
    try:
        # make sure the directory exists
        if not os.path.exists(log_file_dir):
            os.makedirs(log_file_dir)
            os.chmod(log_file_dir, 0o770)
    except OSError:
        pass
    print(config)
    global log_file_name
    file_prefix = config.get("FILE_PREFIX", "").strip().replace(" ","")
    if "FILE_NAME" in config:
        log_file_name = os.path.join(log_file_dir, config["FILE_NAME"])
    elif config.get("FILE", "PROCESS") == "SAME":
        # all logging goes to same file
        log_file_name = os.path.join(
            log_file_dir,
            '%s%s.log' % (file_prefix, datetime.date.today().strftime("%y%m%d"))
        )
    elif config.get("FILE", "PROCESS") != "NONE":
        log_file_name = os.path.join(
            log_file_dir,
            '%s%s_%s.log' % (file_prefix, datetime.date.today().strftime("%y%m%d"), os.getpid())
        )

    # root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.NOTSET)
    root_logger.handlers = []
    # print logger
    print_logger = logging.getLogger("print")
    print_logger.setLevel(logging.NOTSET)
    print_logger.handlers = []
    # error logger
    error_logger = logging.getLogger("stderr")
    error_logger.setLevel(logging.NOTSET)
    error_logger.handlers = []

    if config.get("FILE", "PROCESS") != "NONE":
        FileHandlerClass = config.get("FILE_HANDLER_CLASS", logging.FileHandler)
        default_file_handler = FileHandlerClass(log_file_name)
        log_file_name = getattr(default_file_handler, "baseFilename", log_file_name)
        default_file_handler.setLevel(logging.NOTSET)
        default_file_handler.setFormatter(default_formatter)
        root_logger.addHandler(default_file_handler)

    if config.get("ERRORS_FILE", "FALSE") in ("TRUE", 1):
        error_file_handler = ErrorFileHandler(log_file_name[:-4]+"-ERR.log")
        error_file_handler.setLevel(logging.NOTSET)
        error_file_handler.setFormatter(default_formatter)
        root_logger.addHandler(error_file_handler)

    console_handler = logging.StreamHandler(STDOUT_ORIG)
    console_handler.setLevel(logging.NOTSET)
    console_handler.setFormatter(console_formatter)
    if config.get("PRINT_TO_CONSOLE", "FALSE") in ("TRUE", "1"):
        print_logger.addHandler(console_handler)
    if config.get("STDERR_TO_CONSOLE", "FALSE") in ("TRUE", "1"):
        error_logger.addHandler(console_handler)
    if config.get("ROOT_TO_CONSOLE", "TRUE") in ("TRUE", "1"):
        root_logger.addHandler(console_handler)

# --------------------------------------------------
def init(config=None):
    """
    Initiation of logging, optional parameter config will cause
    default configuration setup based on the passed dictionary
    values. Please call this before using logging module
    """
    global _LOGGING_INIT_STATUS
    # avoid re-init
    if _LOGGING_INIT_STATUS:
        root = logging.getLogger()
        if config:
            root.warning("logging is already configured")
        else:
            root.warning("re-configure logging now...")
            restoreLogger("")
            root.handlers = []
            logging.Logger.manager = logging.Manager(root)
            # use the new config
            setupDefaultLogging(config)
        return None
    # remove temporary handlers from root
    root = logging.getLogger()
    root.handlers = []
    # redo makeRecord to handle more inputs
    logging.Logger._makeRecord_ori = logging.Logger.makeRecord
    logging.Logger.makeRecord = log_utils._makeRecordNew
    # replace standard streams with print wrappers
    sys.stdout = output2log.PrintCaptureHandler(sys.stdout, name="print")
    sys.stdout.setLevel(0, propagate=False)

    sys.stderr = output2log.PrintCaptureHandler(sys.stderr, name="stderr")
    sys.stderr.setLevel(0, propagate=False)
    sys.stderr.setWriteLevel(logging.ERROR, propagate=False)

    sys.excepthook = log_utils.handle_exception
    # if get config use it
    if config is not None:
        setupDefaultLogging(config)
        root.info("Logging start: %s @ %s | Py:%s | pid:%s | cmd:%s" % (
            getpass.getuser(),
            os.environ.get("HOSTNAME", os.uname()[1]),
            "%s.%s.%s" %(sys.version_info.major, sys.version_info.minor, sys.version_info.micro),
            os.getpid(),
            " ".join(sys.argv)
        ))
    _LOGGING_INIT_STATUS = True

