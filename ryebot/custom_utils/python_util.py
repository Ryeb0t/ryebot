import sys
import os
import stat
import json
import shutil
import chardet

def get_caller_module_name() -> str:
    """Returns the name of the module that called this one."""

    frame = sys._getframe(1) # frame of the function calling this function
    base_module = frame.f_globals['__name__']

    while True:
        frame = frame.f_back # go back one frame
        current_module = frame.f_globals['__name__']
        if current_module != base_module:
            return current_module


def import_constants(directory: str, filename: str=None) -> dict:
    """Imports constants data from a file.
    
    Reads the JSON file of the specified ``filename`` (without ``.json`` extension) at the specified ``directory``
    and returns its contents as a dict.
    """

    if filename is None:
        return {}
    
    filename = os.path.join(directory, f"{filename}.json")

    if not os.path.isfile(filename):
        return {}

    jsondata = {}
    with open(filename, encoding='utf-8') as f:
        jsondata = json.load(f)
    return jsondata


def clear_screen():
    """Removes all text from the console."""
    
    if sys.platform == "win32":
        os.system('cls') or None
    elif sys.platform == "linux":
        os.system('clear') or None
    return


def get_files_list(directory: str, modname: str, ext: str='cs'):
    """Returns a list of all files with the specified extension.

    Parameters
    ----------
    1. directory : str
        - The directory in which to search for the files. All subdirectories will be considered, recursively.
    2. modname : str
        - Files named like this will have ``is_item`` set to ``True`` in the result.
    3. ext : str
        - The file extension.
    
    Returns
    -------
    [[filename_no_ext, filename_with_full_dir, is_item]]
    """

    files_list = []
    for root, _, files in os.walk(directory):
        for f in files:
            name, ext = os.path.splitext(f)
            if ext == ".cs":
                is_item = name != modname
                files_list.append([name, os.path.join(root, f), is_item])

    return files_list


def list_files_w_wo_specific_extensions(without: bool, extensions: list, directory: str) -> list:
    """Returns a list of all files with or without a number extensions.
    
    Parameters
    ----------
    1. without : bool
        - Whether the list of returned files should contain files with (``False``) or without (``True``) the specified ``extensions``.
    2. extensions : list[str] 
        - The list of file extensions to consider.
    3. directory : str
        - The directory from which to fetch the files. All subdirectories will be considered, recursively.
    """

    fileslist = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            ext = os.path.splitext(f)[1]
            if (without and ext not in extensions) or (not without and ext in extensions):
                fileslist.append(os.path.join(root, f))
    return fileslist

def list_files_w_specific_extensions(extensions, directory):
    """Returns a list of all files in ``directory`` (including subdirectories, recursively) that have any of the ``extensions``."""
    return list_files_w_wo_specific_extensions(False, extensions, directory)

def list_files_wo_specific_extensions(extensions, directory):
    """Returns a list of all files in ``directory`` (including subdirectories, recursively) that do not have any of the ``extensions``."""
    return list_files_w_wo_specific_extensions(True, extensions, directory)


def remove_files(filelist: list, log):
    """Removes all files of the ``filelist``."""

    for file in filelist:
        try:
            os.remove(file)
        except:
            log("Error while deleting the file \"{}\"!".format(file))
            log(exc_info=True, s='Error message:\n')
    return


def remove_empty_directories(dirs):
    """Deletes all subdirectories of ``dirs`` (recursively) that do not contain any files."""

    for direc in list(os.walk(dirs, False))[1:]: # topdown=False for bottom-up
        # example of direc: ('project\Gores', [], ['Gore_1.png'])
        if not direc[1] and not direc[2]:
            os.rmdir(direc[0])
    return


def are_all_list_elements_equal(elemlist: list) -> bool:
    """Returns ``True`` if all items of the ``elemlist`` are equal, ``False`` if they are not, and ``None`` if the list is empty."""

    if len(elemlist) == 0:
        return None

    check = elemlist[0]
    for elem in elemlist:
        if elem != check:
            return False
    return True


def is_list_in_other_list(larger_list: list, smaller_list: list):
    """Check if one list is contained as-is in another list, and if yes, return the remainder.

    Parameters
    ----------
    1. larger_list : list
        - The "outer" list that contains the other list (or not ??? to be checked).
    2. smaller_list : list
        - The list that is contained in the other one (or not ??? to be checked).
    
    Returns
    -------
    - If the ``larger_list`` is shorter than the ``smaller_list``:
        - None
    - If the ``smaller_list`` is empty:
        - (larger_list, [])
    - Else:
        - (before_smaller_list, after_smaller_list), any or both of these might be empty
    """
    
    if False: # for debugging
        print('\nCompare:')
        print('larger_list:')
        for elem in larger_list:
            print('\t{}'.format(elem))
        print('\nsmaller_list:')
        for elem in smaller_list:
            print('\t{}'.format(elem))

    if len(larger_list) < len(smaller_list):
        return

    if len(smaller_list) == 0:
        return (larger_list, [])

    for startindex in range(0, len(larger_list)):

        for i, elem in enumerate(smaller_list):
            if elem != larger_list[startindex + i]:
                break
        else:
            before = []
            after = []
            for j, elem in enumerate(larger_list):
                if j < startindex:
                    before.append(elem)
                elif j > startindex + len(smaller_list) - 1: # endindex
                    after.append(elem)

            return (before, after)
    
    return ([], [])


def pstring_to_list(pstring, is_bytearray=False):
    """Converts a Pascal string to a list.
    
    Parameters
    ----------
    1. pstring
        - The Pascal string to convert.
    2. is_bytearray : bool
        - Whether the ``pstring`` is a bytearray.
    """

    string_list = []
    while pstring:
        if is_bytearray:
            lengthbyte = pstring[0]
        else:
            lengthbyte = pstring[0].encode() # convert char to byte
        pstring = pstring[1:] # remove the first byte, which holds the length of the following string part
        if is_bytearray:
            length = lengthbyte
        else:
            length = int.from_bytes(lengthbyte, byteorder='big') # byte to int
        #string_list.append("{} {}".format(length, pstring[:length])) # for debug: prepend length of string
        string_list.append(pstring[:length])
        pstring = pstring[length:]
    return string_list


def get_next_list_elem(list: list, elem):
    """Returns the element that immediately follows the specified one."""

    try:
        index = list.index(elem)
    except ValueError:
        pass
    else:
        try:
            return list[index + 1]
        except IndexError:
            pass
    return


def compare_lists(list1: list, list2: list):
    """Returns the diff of the two lists.

    Returns
    -------
    - (added, removed)

    ``added`` is a list of elements that are in ``list2`` but not in ``list1``.

    ``removed`` is a list of elements that are in ``list1`` but not in ``list2``.
    """

    added = []
    removed = []
    for elem in list1:
        if elem not in list2:
            removed.append(elem)
    for elem in list2:
        if elem not in list1:
            added.append(elem)
    return (added, removed)


def convert_file_encoding(filename: str, target_encoding: str):
    """Convert the text encoding of the file to the desired one. The file may already be in the target encoding, in which case nothing is changed.
    
    Parameters
    ----------
    1. filename : str
        - The full path and name of the file in question.
    2. target_encoding : str
        - The target encoding, e.g. ``utf-8``.
    
    Returns
    -------
    A tuple ``(bool, str)`` which contains a hint as to whether a conversion took place (``True``) or not (``False``), and a log string.
    """
    
    # method is based on https://stackoverflow.com/a/53851783

    # get encoding of the file
    with open(filename, 'rb') as f:
        filecontents = f.read()
    src_encoding = chardet.detect(filecontents)['encoding']

    if src_encoding == target_encoding:
        logstr = 'The file "{}" was already encoded with "{}".'.format(filename, target_encoding)
        return (False, logstr)
    
    # take the content of the file into memory (we're not expecting to be handling very large files)
    with open(filename, 'r', encoding=src_encoding) as f:
        filetext = f.read()
    
    # write the content into the file again, but opened with the target encoding
    with open(filename, 'w', encoding=target_encoding) as f:
        f.write(filetext)
    
    # TODO: maybe extend functionality: save a copy of the file with the old encoding?

    logstr = 'Converted the encoding of the file "{}" from "{}" to "{}".'.format(filename, src_encoding, target_encoding)

    return (True, logstr)


def get_dict_key_by_value(source_dict: dict, dict_value):
    """Return the first key of the ``source_dict`` that has the ``dict_value`` as value."""

    for k, v in source_dict.items():
        if v == dict_value:
            return k
    return


def copytree_custom(src, dst, symlinks=False, ignore=None):
    """Own implementation of the ``shutil.copytree()`` method, which fails if the target directory already exists. This method does not fail in that case, and instead just creates the directory."""
    
    # from https://stackoverflow.com/a/22331852

    if not os.path.exists(dst):
        os.makedirs(dst)
        shutil.copystat(src, dst)
    lst = os.listdir(src)
    if ignore:
        excl = ignore(src, lst)
        lst = [x for x in lst if x not in excl]
    for item in lst:
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if symlinks and os.path.islink(s):
            if os.path.lexists(d):
                os.remove(d)
            os.symlink(os.readlink(s), d)
            try:
                st = os.lstat(s)
                mode = stat.S_IMODE(st.st_mode)
                os.lchmod(d, mode)
            except:
                pass # lchmod not available
        elif os.path.isdir(s):
            copytree_custom(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)
    return


def copytree_robocopy(src, dst):
    """Copy a tree, similarly to ``shutil.copytree()``, using Windows's ``robocopy`` command."""

    if os.system != "win32":
        raise Exception('Attempting to use the Windows-exclusive "robocopy" command!')

    cmd = r'"robocopy "{src}" "{dst}" /E /NFL /NDL /NJH /NJS /NC /NS /NP"'.format(src=src, dst=dst)
    os.system(cmd)
    
    return


def sepdelimited_keydata_to_json(data: dict, sep: str='.'):
        """Store a dict to JSON that originally has the following format:

        {
            "a.bc.def": "value1",
            "a.bc.ghi": "value2",
            "j": "value3"
        }

        The resulting JSON will be as follows:

        {
            "a": {
                "bc": {
                    "def": "value1",
                    "ghi": "value2"
                }
            },
            "j": "value3"
        }
        
        The keypart separator can be specified via the ``sep`` parameter.
        """

        jsondata = {}

        for key, value in list(data.items()):

            if key.find(sep) < 0:
                # the key is not nested, just store it as-is
                jsondata[key] = value
                continue

            jsonsubdict = jsondata
            keyparts = key.split(sep)
            max_i = len(keyparts)
            for i in range(max_i):
                keypart = keyparts[i]
                if i+1 < max_i:
                    # we've not reached the last keypart yet
                    try:
                        jsonsubdict = jsonsubdict[keypart]
                    except KeyError:
                        jsonsubdict[keypart] = {}
                        jsonsubdict = jsonsubdict[keypart]
                else:
                    # this is the last keypart
                    jsonsubdict[keypart] = value

        return jsondata


def find_file(base_directory: str, filename: str):
    """Return the full path of the given ``filename`` in the ``base_directories`` or any of its subdirectories (recursively; file must match exactly)."""

    for root, dirs, files in os.walk(base_directory):
        if filename in files:
            return os.path.join(root, filename)

    return ''
