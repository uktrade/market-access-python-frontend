class FileCache:
    """
    Caches the contents of files.
    Avoids reading files repeatedly from disk by holding onto the
    contents of each file as a list of strings.
    """
    def __init__(self):
        self.filecache = {}

    def open(self, filename):
        """
        Stores - contents of a file (new line characters are removed)
        Returns - contents of a stored file as a string (new line characters restored)
        """
        if not self.filecache.get(filename):
            with open(filename) as file:
                content = file.read()
                self.filecache[filename] = content.split("\n")

        return "\n".join(self.filecache.get(filename))


memfiles = FileCache()
