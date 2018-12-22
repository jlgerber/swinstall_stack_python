__all__ = ("FileMetadataBase",)

class FileMetadataBase(object):
    def element(self):
        """construct an element from self

        :returns: xml element
        :rtype: ElementTree.Element
        """
        raise NotImplementedError()

    @property
    def is_current(self):
        """returns whether or not the FileMetadata refers to a current file or not.

        :returns: true or false, depending
        :rtype: bool
        """
        raise NotImplementedError()

    @property
    def version(self):
        """Return the version of the element

        :returns: version
        :rtype: version type (depends)
        """
        raise NotImplementedError()

    @property
    def versionless_path(self):
        """Return the path to the versionless file that the swinstall_stack
        manages.

        :returns: path to versionless file
        :rtype: str
        """
        raise NotImplementedError()
    @property
    def path(self):
        raise NotImplementedError()

    def __eq__(self, other):
        raise NotImplementedError()

    def __ne__(self, other):
        raise NotImplementedError()