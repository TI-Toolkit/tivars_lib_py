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

### Data Sections

The var is composed of individual _sections_ which represent different forms of data. All sections belong to either the _header_, _entry_, or _checksum_. These sections are then divided into their own sections (except the checksum).

You can read and write to individual sections of the var as their "canonical" type.

```python
my_program.comment = "This is my comment!"
my_program.archived = True

assert my_program.type_id == b'\x05'
```

`TIVar` objects are also inherently arrays of bytes, meaning you can interface with them using any `bytearray` methods to access the raw bytes. Slicing using section attributes or names is also supported.

```python
my_program[TIVar.comment] = b'This is my comment!'.ljust(42, b'\x00')
my_program["archived"] = b'\x80'

assert my_program[59] == b'\x05'
```

### Metadata and Corrupt Files

Some data sections are considered _metadata_, meaning they exist only to describe other sections of data. Thus, for a file to be valid, its metadata must match the sections it describes.

Whenever you access a metadata field or export the entire var, its metadata is updated. You may explicitly update all metadata using `update`. Metadata fields cannot be set directly.

To prevent updates to the metadata, or to set explicitly corrupt metadata, interface with the var object as a `bytearray`. In doing so, no checks will be performed on the validity of the var.

### Models

All TI-82/83/84 series calcs are represented as `TIModel` objects stored in `tivars.models`. Each model contains its name, file magic, and feature flags; use `has` on a `TIFeature` to check that a model has a given a feature. Models are also used to determine var file extensions and token sheets.

For these reasons, it is _not_ recommended to instantiate your own models.

## Other Functionalities

### Tokenization

Functions to decode and encode strings from various token sheets can be found in `tivars.tokenizer`. Support currently exists for all forms of 82/83/84 series BASIC as well as custom token sheets; PR's concerning the sheets themselves should be directed upstream to [TI-Toolkit/tokens](https://github.com/TI-Toolkit/tokens).
