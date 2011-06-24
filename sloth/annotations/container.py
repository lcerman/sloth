import os
import fnmatch
import time
from sloth.core.exceptions import \
    ImproperlyConfigured, NotImplementedException, InvalidArgumentException
from sloth.core.utils import import_callable
try:
    import cPickle as pickle
except:
    import pickle
try:
    import json
except:
    pass
try:
    import yaml
except:
    pass
import okapy
import logging
LOG = logging.getLogger(__name__)


class AnnotationContainerFactory:
    def __init__(self, containers):
        """
        Initialize the factory with the mappings between file pattern and
        the container.

        Parameters
        ==========
        containers: tuple of tuples (str, str/class)
            The mapping between file pattern and container class responsible
            for loading/saving.
        """
        self.containers_ = []
        for pattern, item in containers:
            if type(item) == str:
                item = import_callable(item)
            self.containers_.append((pattern, item))

    def patterns(self):
        return [pattern for pattern, item in self.containers_]

    def create(self, filename, *args, **kwargs):
        """
        Create a container for the filename.

        Parameters
        ==========
        filename: str
            Filename for which a matching container should be created.
        *args, **kwargs:
            Arguments passed to constructor of the container.
        """
        for pattern, container in self.containers_:
            if fnmatch.fnmatch(filename, pattern):
                return container(*args, **kwargs)
        raise ImproperlyConfigured(
            "No container registered for filename %s" % filename
        )


class AnnotationContainer:
    """
    Annotation Container base class.
    """

    def __init__(self):
        self.clear()

    def filename(self):
        return self.filename_

    def clear(self):
        self.annotations_ = []
        self.filename_ = None

    def load(self, filename):
        """
        Load the annotations.
        """
        if not filename:
            raise InvalidArgumentException("filename cannot be empty")
        self.filename_ = filename
        start = time.time()
        ann = self.parseFromFile(filename)
        diff = time.time() - start
        LOG.info("Loaded annotations from %s in %.2fs" % (filename, diff))
        return ann

    def parseFromFile(self, filename):
        """
        Read the annotations from disk. Must be implemented in the subclass.
        """
        raise NotImplementedException(
            "You need to implement parseFromFile() in your subclass " +
            "if you use the default implementation of " +
            "AnnotationContainer.load()"
        )

    def save(self, annotations, filename=""):
        """
        Save the annotations.
        """
        if not filename:
            filename = self.filename()
        self.serializeToFile(filename, annotations)
        self.filename_ = filename

    def serializeToFile(self, filename, annotations):
        """
        Serialize the annotations to disk. Must be implemented in the subclass.
        """
        raise NotImplementedException(
            "You need to implement serializeToFile() in your subclass " +
            "if you use the default implementation of " +
            "AnnotationContainer.save()"
        )

    def _fullpath(self, filename):
        """
        Calculate the fullpath to the file, assuming that
        the filename is given relative to the label file's
        directory.
        """
        if self.filename() is not None:
            basedir = os.path.dirname(self.filename())
            fullpath = os.path.join(basedir, filename)
        else:
            fullpath = filename
        return fullpath

    def loadImage(self, filename):
        """
        Load and return the image referenced to by the filename.  In the
        default implementation this will try to load the image from a path
        relative to the label file's directory.
        """
        fullpath = self._fullpath(filename)
        return okapy.loadImage(fullpath)

    def loadFrame(self, filename, frame_number):
        """
        Load the video referenced to by the filename, and return frame
        ``frame_number``.  In the default implementation this will try to load
        the video from a path relative to the label files directory.
        """
        fullpath = self._fullpath(filename)
        #TODO load video


class PickleContainer(AnnotationContainer):
    """
    Simple container which pickles the annotations to disk.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read pickle files.
        """
        f = open(fname, "rb")
        return pickle.load(f)

    def serializeToFile(self, fname, annotations):
        """
        Overwritten to write pickle files.
        """
        # TODO make all image filenames relative to the label file
        f = open(fname, "wb")
        pickle.dump(annotations, f)


class JsonContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk in JSON format.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read JSON files.
        """
        f = open(fname, "r")
        return json.load(f)

    def serializeToFile(self, fname, annotations):
        """
        Overwritten to write JSON files.
        """
        # TODO make all image filenames relative to the label file
        f = open(fname, "w")
        json.dump(annotations, f, indent=4)


class YamlContainer(AnnotationContainer):
    """
    Simple container which writes the annotations to disk in YAML format.
    """

    def parseFromFile(self, fname):
        """
        Overwritten to read YAML files.
        """
        f = open(fname, "r")
        return yaml.load(f)

    def serializeToFile(self, fname, annotations):
        """
        Overwritten to write YAML files.
        """
        # TODO make all image filenames relative to the label file
        f = open(fname, "w")
        yaml.dump(annotations, f)


class FileNameListContainer(AnnotationContainer):
    """
    Simple container to initialize the files to be annotated.
    """

    def parseFromFile(self, filename):
        self.basedir_ = os.path.dirname(filename)
        f = open(filename, "r")

        annotations = []
        for line in f:
            line = line.strip()
            fileitem = {
                'filename':    line,
                'type':        'image',
                'annotations': [],
            }
            annotations.append(fileitem)

        return annotations

    def serializeToFile(self, filename, annotations):
        raise NotImplemented(
                "FileNameListContainer.save() is not implemented yet.")


class FeretContainer(AnnotationContainer):
    """
    Container for Feret labels.
    """

    def parseFromFile(self, filename):
        """
        Overwritten to read Feret label files.
        """
        f = open(filename)

        annotations = []
        for line in f:
            s = line.split()
            fileitem = {
                'filename': s[0] + ".bmp",
                'type': 'image',
            }
            fileitem['annotations'] = [
                {'type': 'point', 'class': 'left_eye',
                 'x': int(s[1]), 'y': int(s[2])},
                {'type': 'point', 'class': 'right_eye',
                 'x': int(s[3]), 'y': int(s[4])},
                {'type': 'point', 'class': 'mouth',
                 'x': int(s[5]), 'y': int(s[6])}
            ]
            annotations.append(fileitem)

        return annotations

    def serializeToFile(self, filename, annotations):
        """
        Not implemented yet.
        """
        # TODO make sure the image paths are
        # relative to the label file's directory
        raise NotImplemented(
            "FeretContainer.serializeToFile() is not implemented yet."
        )
