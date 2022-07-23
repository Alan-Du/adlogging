import logging
import sys

##################################################
class PrintCaptureHandler(object):
    """
    Replacement of stdout and stderr
    It takes inputs from system stream flow
    then output to console also to log file
    Additional keys supported:
        - name: overwrite the log file which
        by default is the stream or "print"
    """
    # --------------------------------------------------
    def __init__(self, *args, **kwargs):
        if "name" in kwargs:
            self.logger_name = kwargs["name"]
        else:
            self.logger_name = "print"
        if "original_stream" in kwargs:
            self._original_stream = kwargs["original_stream"]
        self.initLevel = kwargs.get("level", 20)
        self.level = self.initLevel
        self.currentLevel = kwargs.get("currentLevel", 20)
        self.currentLevelBack = self.currentLevel
        self._write_counter = 0

    # --------------------------------------------------
    def write(self, msg):
        """
        redirect msg to both console and logger
        """
        self._write_counter += 1
        try:
            if self.currentLevel <= self.level:
                try:
                    if not isinstance(msg, basestring):
                        msg = "%s\n" % repr(msg)
                    self._write_console(msg)
                    self._write_to_logging(msg)
                except Exception as e:
                    pass
        finally:
            self._write_counter -= 1

    # --------------------------------------------------
    def _write_console(self, msg):
        # send to normal console output
        sys.stdout.write(msg)

    # --------------------------------------------------
    def _write_to_logging(self, msg):
        # send to log file output
        write_level = self.currentLevel
        file_name, line_no, co_name = logging.Logger.findCaller(logging.root)[:3]
        this_caller_info = (file_name, line_no, co_name, write_level)
        logger = logging.getLogger(self.logger_name)
        logger.log(write_level, msg)

    # --------------------------------------------------
    def setLevel(self, level, propagate=True):
        self.level = int(level)
        if propagate and hasattr(self._original_stream, "setLevel"):
            self._original_stream.setLevel(level)

    # --------------------------------------------------
    def setWriteLevel(self, level, propagate=True):
        self.currentLevel = level
        if propagate and hasattr(self._original_stream, "setWriteLevel"):
            self._original_stream.setWriteLevel(level)