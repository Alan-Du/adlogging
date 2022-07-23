import logging

##################################################
class _PrintHandler(logging.StreamHandler):
    """
    Special handler turns anything to printing
    until logging is initiated. Until then all
    methods will only print the message.
    """
    # --------------------------------------------------
    def emit(self, record):
        try:
            msg = self.format(record)
            try:
                if isinstance(msg, unicode):
                    print(u'%s' % msg)
                else:
                    print(msg)
            except UnicodeError:
                print(msg.encode("UTF-8"))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

##################################################
class LevelBasedFormatter(logging.Formatter):
    """
    Auto formatting doing extensive log for level
    ERROR or above and regular formatting for below.
    """
    _err_fmt = "".join((
        "%(asctime)s %(levelname)s %(name)s ",
        "| %(funcName)s(..) | line %(lineno)s @ %(filename)s",
        " -- %(message)s"
    ))
    # --------------------------------------------------
    def format(self, record):
        # switch formatter based on level
        format_ori = self._fmt
        if record.levelno >= logging.ERROR:
            self._fmt = self._err_fmt
        res = logging.Formatter.format(self, record)
        self.format = format_ori
        return res

##################################################
class ErrorFileHandler(logging.FileHandler):
    """
    ERROR level file handler not passing anything
    ERROR with guarantee even after setLevel
    """
    def emit(self, record):
        if record.levelno >= logging.ERROR:
            return logging.FileHandler.emit(self, record)