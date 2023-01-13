# tivars_lib_py

`tivars_lib_py` is a Python package for interacting with TI-(e)z80 (82/83/84 series) calculator files, i.e. lists, programs, matrices, appvars, etc.

Much of the functionality of this package has been ported over from [tivars_lib_cpp](https://github.com/adriweb/tivars_lib_cpp). However, a number of changes have made to the API to better suit Python's strengths and capabilities as a language (e.g. scripting).

## Installation

Clone this repository into your next project and import the package via `import tivars`. You can run the test suite via `__main__.py`, or run individual tests found in `tests/` with `unittest`.

Official releases are coming soon. All versions require Python 3.10+ to run.

## How to Use

### Creating vars

To create an empty var, instantiate its corresponding type from `tivars.types`. You can specify additional parameters as you like:

```python
from tivars.models import *
from tivars.types import *

my_program = TIProgram(name="HELLO", model=TI_84P)
```

If you're not sure of a var's type or model, instantiate a base `TIVar`:

```python
my_var = TIVar()
my_var_for83 = TIVar(model=TI_83)
```

### Reading and writing

Vars can be loaded from files, strings, or raw bytes. If you're unsure of the input format, use `load`.

```python
my_program.open("HELLO.8xp")

with open("HELLO.8xp", 'rb') as file:
    my_program.load_file(file)
    my_program.load_bytes(file.read())

my_program.loads("Disp \"HELLO WORLD!\"")
```

Export the contents of a var as a string, bytes, or straight to a file. Use `export` to specify additional parameters without modifying the current object.

```python
my_program.save("HELLO.8xp")
my_program.save()                # Infer the filename

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_program.bytes())
    file.write(my_program.export(model=TI84PCSE))

print(my_program.string())
```

You can also read and write to individual sections of the var. Each section can be interfaced as its "canonical" type, or as a raw bytes object by appending `_bytes` to the attribute name.

```python
my_program.comment = "This is my comment!"
my_program.magic_bytes = b'\x0A\x11'

assert my_program.type_id == b'\x05'
```
### Headers and Entries

Each var is composed of a _header_ and _entry_ section, which can be exported as `TIHeader` and `TIEntry` objects respectively. They can also be instantiated on their own.

```python
header, entry = my_var.header, my_var.entry
```

Note that the header contents dependent directly on the entry section in order to be valid.

### Models

All TI-82/83/84 series calcs are represented as `TIModel` objects stored in `tivars.models`. Each model contains its name, file magic, and feature flags; use `has` on a `TIFeature` to check that a model has a given a feature. Models are also used to determine var file extensions and token sheets.

For these reasons, it is _not_ recommended to instantiate your own models.

### Corrupt files

`TIVar` objects are unable to maintain corrupted metadata. When instantiating from a corrupted file object, warnings will be raised concerning the corrupted bytes; the corrected bytes will be stored in their place.

## Other Functionalities

### Tokenization

Functions to decode and encode strings from various token sheets can be found in `tivars.tokenizer`. Support currently exists for all forms of 82/83/84 series BASIC as well as custom token sheets; PR's concerning the sheets themselves should be directed upstream to [ti-toolkit/tokens](https://github.com/ti-toolkit/tokens).
