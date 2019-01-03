# componentstack impl
class FileSystemError(Exception):
    """Error resulting from (mis)use of the file system"""
    @classmethod
    def wrapping(cls, exception):
        return cls(exception.errno, exception.strerror, exception.filename)

    @classmethod
    def unsupported(cls, operation):
        return UnsupportedFileSystemOperationError(operation)

    def __init__(self, *args):
        super(FileSystemError, self).__init__()
        if len(args) == 0:
            self.errno = 0
            self.strerror = ""
            self.filename = ""
        elif len(args) == 1:
            self.errno = 0
            self.strerror = str(args[0])
            self.filename = ""
        elif len(args) == 2:
            self.errno = 0
            self.filename = str(args[0])
            self.strerror = str(args[1])
        elif len(args) == 3:
            self.errno = args[0]
            self.strerror = args[1]
            self.filename = args[2]

    def __str__(self):
        s = self.filename or ""
        if self.strerror:
            if s:
                s += ": "
            s += self.strerror
        if self.errno:
            if s:
                s += " (errno {})".format(self.errno)
            else:
                s = str(self.errno)
        return s

class UnsupportedFileSystemOperationError(FileSystemError):
    """unsupported file system operation error"""
    pass
