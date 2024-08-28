"""
    File for file or path related tools or functionality
    @author: Pablo Guillén Marquina (@drakopablo)
"""
import mimetypes
import os
from pathlib import Path, PurePath, PureWindowsPath

from chardet import UniversalDetector
from string import Template
import json

from GUI.tools.text_tools import rreplace


def str2path(path : str) -> PurePath :
    """
        Checks if path is a pure Windows path or a posix path. It returns
        the constructed with the correct path separators.
    """
    # Returns a pure path checking between windows's and posix's like paths
    return PurePath(PureWindowsPath(path) if ("\\" == os.sep) else Path(path))

def path2posix(path : str | PurePath) -> str:
    """
        Transforms a Path like object into a string following POSIX path standards
    """
    return Path(str2path(os.path.normpath(path))).resolve().as_posix()
    #return Path(str2path(path)).resolve().as_posix()


def check_if_file_exists(given_path: str) -> bool :
    """
        Checks if given path exists.

        given_path: path to check.
    """
    if (given_path is None or len(given_path) == 0):
        raise ValueError("Given path must not be empty")
    try:
        try:
            # First we check in strict mode if the given path exists (Windows: only checks current drive, by default is "C:")
            return Path(str2path(given_path)).resolve(strict=True).exists()
        except NotADirectoryError:
            # Now we check without strict mode for checking other drives (Windows)
            return Path(str2path(given_path)).resolve(strict=False).exists()
    except FileNotFoundError as ex2:
        #print(f"Could not find an existing dataset in \"{given_path}\"")
        print(ex2)
    except Exception as ex3:
        # If there's an infinite loop (unprobably), Path.resolve() may raise a RuntimeError exception. However, this is catched by Exception.
        print(ex3)
    return False

def join_paths(*args : tuple[str, ...]) -> str:
    '''
        Construct the path to the dataset with POSIX syntax.

        *args: tuple of strings representing the dataset relative path without the OS path separator

        # TODO: Check if it's a hidden folder for the path.startswith(".") case (CASE 3)
        # TODO: Check if accessing a remote directory is allowed (for building later de KG) (CASE 4)
    '''
    parts : list[str] = list(args)
    if len(parts) == 0:
        return "./" # If it's empty, return the current directory
    # CASE 1: Windows path with C: drive (or other). We check if the first part is a drive letter without a separator
    if parts[0].endswith(':') and not parts[0].endswith(':\\'):
        parts[0] += os.sep
    # Construct the path for both Windows and Unix systems
    path = os.path.join(*parts)
    true_path = str2path(path)
    # CASE 2: We check what king of relative path is, if it's the case
    true_path = ("../" if path.startswith("..") else ("./" if path.startswith(".") else "")) + true_path.as_posix() # noqa
    # We return the corrected formated path
    return true_path

def parse_dataset_path(given_path: str, /, verbose: bool = False) -> tuple[str, str, str]:
    """
        Method that separates the given path into its components:
        base path, dataset folder, and dataset filename (with extension).

        given_path: absolute path of the dataset
        verbose: whether to print the output or not
    """
    if not check_if_file_exists(given_path):
        raise FileNotFoundError(f"Could not find an existing dataset in \"{given_path}\"")
    # Split the given path into (base_path, dataset_folder, dataset_file)
    aux_path : str = given_path
    path_parts = aux_path.split(os.sep)
    aux_path = join_paths(*path_parts)
    # Handle the dataset folder and the dataset file
    dataset_folder, dataset_file = aux_path.split("/")[-2:]
    # Handle the base path
    base_path = rreplace(aux_path, "/".join([dataset_folder, dataset_file]))
    if len(aux_path.split("/")) <= 2:
        base_path = dataset_folder
        dataset_folder = ""
    if base_path.endswith("/"):
        base_path = rreplace(base_path, "/")
    #os.path.splitext(dataset_file)[0] # Removing the file extensiond
    # Output
    if verbose:
        print(f'base_path : "{base_path}"')
        print(f'dataset_folder : "{dataset_folder}"')
        print(f'dataset_file : "{dataset_file}"')
    # Return the tuple
    return (base_path, dataset_folder, dataset_file)

def has_common_path(path1: str, path2: str) -> bool:
    """
        Checks if path1 and path2 shares a common ancestor in their path.
        The path is standarized into POSIX format before comparing.
        The order of the inputed paths doesn't alter the result of this function.

        Args:
            path1: First path to compare with the second
            path2: Second path to be compared with the first

        NOTE: It doesn't check if paths are valid
    """
    # Resolve paths before comparing them
    a = path2posix(path1)
    b = path2posix(path2)
    c = path2posix(os.path.commonpath((a, b)))
    # Return comparision between common ancestors
    return a == c

def is_safe_path(basedir : str, path : str, follow_symlinks : bool = True) -> bool:
    """
        Checks if a path is safe to avoid "path traversal" attacks.
        Source: https://security.openstack.org/guidelines/dg_using-file-paths.html

        Args:
            basedir: The directory base of the file
            path: The new directory to be checked
            follow_symlinks: Whether to follow symlinks or not
    """
    # Resolves symbolic links
    if follow_symlinks:
        matchpath = os.path.realpath(path)
    else:
        matchpath = os.path.abspath(path)
    # Checks if they share a common ancestor path
    return has_common_path(basedir, matchpath)

def check_file_encoding_mime_type(file: str, default_encoding: str = 'utf-8', default_mime_type: str = 'text/plain') -> tuple[str, str]:
    """
        Checks the given file encoding (if exists), and the mime type and returns them.

        NOTE: It may check the file byte order mark (BOM): https://www.w3.org/International/questions/qa-byte-order-mark.en
        More info about this can be found here: https://en.wikipedia.org/wiki/Byte_order_mark
        For a python library that supports BOM encoding see this: https://docs.python.org/3/library/codecs.html#codecs.BOM
        It may be useful for knowing if the file must be read in "little endian" or "big endian" format.
        Also, for the file system encoding is recommended to check this: https://docs.python.org/es/3.10/library/sys.html#sys.platform:~:text=Disponibilidad%3A%20Unix.-,sys.getfilesystemencoding(),-%C2%B6

        file: path of the file with its extension
        default_encoding: by default we'll use utf-8 encoding
        default_mime_type: by default we'll use text/pain mime type
    """
    encoding : str = ''
    mime_type : str = ''
    try:
        # It asummes that the file exists and is readable
        # File size
        size = os.path.getsize(file)
        # Mime Type (optional)
        mime_type, _ = mimetypes.guess_type(file) # Second result is encoding but is not reliable
        # Encoding
        detector : UniversalDetector = UniversalDetector()
        detector.reset()
        for line in open(file, 'rb'):
            detector.feed(line)
            if detector.done: break
        detector.close()
        encoding = detector.result['encoding']
        # Warning about file
        if (size == 0 or encoding is None or len(encoding) == 0):
            print(f"*WARNING*: File of size {size} bytes might be empty or have an invalid encoding")
    except Exception as e:
        print(e) # TODO: Change to less generic error
    return (encoding or default_encoding, mime_type or default_mime_type)


def interpolate_json(json_path: str, data : dict, encoding='utf-8', verbose:bool=False) -> dict:
    configuration = None
    try:
        with open(json_path, 'r', encoding=encoding) as json_file:
            content = ''.join(json_file.readlines())
            template = Template(content)
            configuration = json.loads(template.substitute(data))
            if verbose:
                print(configuration)
    except Exception as e:
        print(e) # TODO: Change to less generic
    return configuration