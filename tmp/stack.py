# componentstack impl
class FileSystemError(Exception):
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
    pass

class ComponentStack(object):
    def __init__(self, path, component_name):
        """
        :param path: path to component_swinstall_stack
        :param component_name: versionless component name
        """

    def __copy__(self):
        import copy
        new = self.__class__.__new__(self.__class__)
        # initialize instance data
        # eg
        # new.stack = copy.copy(self.stack)
        return new

    def __deepcopy__(self, memo):
        import copy
        new = self.__class__.__new__(self.__class__)
        memo[id(self)] = new
        # initialize instance data
        # new.stack = copy.deepcopy(self.stack, memo)
        return new

    def getStack(self):
        """return current stack"""

    def getStackLength(self):
        """return size of stack"""

    def getCurrent(self):
        """return current version from stack"""

    def __getitem__(self, index):
        """used for getting pars of the stack. either individual elements or ranges"""
        return self.stack[key]

    def setCurrentIndex(self, index):
        """set the current index of the stack. does not error check"""

    def pushVersion(self, version):
        """put a new version after current"""

    def clearRedo(self):
        """remove all versions past the current one"""

    def filterVersion(self, version):
        """remove all occuarnces of a version. If athat is the current one,
        raises a RuntimeError"""

    def previousVersion(self, count=1):
        """return the version count versions before the current one"""

    def nextVersion(self, count=1):
        """get the version count versions past the current index. returns the last version
        if we encounter an IndexError"""

    def rollBack(self, count=1):
        """Roll the current back count elements. If it hist the fist element, sets
        curren to first element and raises a runtimeerror. this seems weird"""

    def rollForward(self, count=1):
        """roll the ucrrent forward count leements. If that is past th last element,
        sets current co last element and raises a runtimerror"""

    def saveFile(self, fileSystem):
        """sav the file. COmpares date stamp before saving. IF the date stamp on teh
        file on disk has changed, raises a RuntimeError"""

        try:
            st = fileSystem.statFile(self.file_path)
        except FileSystemError:
            pass
        else:
            if st.modificationDateTime != self.timestamp:
                raise RuntimeError("File {} has changed. Cannot save data".format(self.file_path))

        # write xml file

    def reloadFile(self, fileSystem):
        """Load the file. FI the file doesn't exist, set everyting to empty and store
        file's time stamp for later checking"""