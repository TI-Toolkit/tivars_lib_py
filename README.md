# tivars_lib_py

`tivars_lib_py` is a Python package for interacting with TI-(e)z80 (82/83/84 series) calculator files, i.e. lists, programs, matrices, appvars, etc.

Much of the functionality of this package has been ported over from [tivars_lib_cpp](https://github.com/adriweb/tivars_lib_cpp). However, a number of changes have made to the API to better suit Python's strengths and capabilities as a language (e.g. scripting).

## Installation

Clone this repository into your next project and import the package via `import tivars`. You can run the test suite via `__main__.py`, or run individual tests found in `tests/` with `unittest`.

Official releases are coming soon. All versions require Python 3.10+ to run.

## How to Use

### Creating vars

Every var file has two parts: a _header_ and a number of _entries_, where entry contains the data for a single variable. Usually, var files contain just one entry; in these cases, there's not much distinction between a var and an entry for the purposes of messing with its data.

To create an empty entry, instantiate its corresponding type from `tivars.types`. You can specify additional parameters as you like:

```python
from tivars.models import *
from tivars.types import *

my_program = TIProgram(name="HELLO", model=TI_84P)
```

If you're not sure of an entry's type or model, instantiate a base `TIEntry`:

```python
my_entry = TIEntry()
my_entry_for83 = TIEntry(model=TI_83)
```

If you want to create an entire var or just a header, use `TIVar` or `TIHeader` instead:

```python
my_var = TIVar()
my_var_for84pce = TIVar(model=TI_84PCE)

my_header = TIHeader()
my_header_with_a_cool_comment = TIHeader(comment="Wow! I'm a comment!")
```

### Reading and writing

Vars can be loaded from files or raw bytes:

```python
my_var.open("HELLO.8xp")

with open("HELLO.8xp", 'rb') as file:
    my_var.load_var_file(file)
    
    file.seek(0)
    my_var.load_bytes(file.read())
```

Entries can be loaded from files, raw bytes, or strings representing their data. When loading from a file, you may specify which entry to load if there are multiple:

```python
# Raises an error if the var has multiple entries; use load_from_file instead
my_program.open("HELLO.8xp")

with open("HELLO.8xp", 'rb') as file:
    # Offset counts the number of entries to skip; defaults to zero
    my_program.load_from_file(file, offset=1)
    
    file.seek(0)
    my_program.load_bytes(file.read())

my_program.load_string("Disp \"HELLO WORLD!\"")
```

Export a var as bytes or straight to a file:

```python
my_var.save("HELLO.8xp")
my_var.save()                               # Infer the filename

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_var.bytes())
```

Entries can be passed an explicit header to attach when exporting:
```python
my_program.save("HELLO.8xp")
my_program.save()

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_program.export(header=my_header).bytes())
```

### Data Sections

Vars are comprised of individual _sections_ which represent different forms of data, split across the header and entries. The var itself also contains the total entry length and checksum sections, but these are read-only to prevent file corruption.

You can read and write to individual sections of an entry or header as their "canonical" type.

```python
my_header.comment = "This is my (even cooler) comment!"
my_program.archived = True

assert my_program.type_id == b'\x05'
```

### Models

All TI-82/83/84 series calcs are represented as `TIModel` objects stored in `tivars.models`. Each model contains its name, file magic, and feature flags; use `has` on a `TIFeature` to check that a model has a given a feature. Models are also used to determine var file extensions and token sheets.

For these reasons, it is _not_ recommended to instantiate your own models.

## Other Functionalities

### Tokenization

Functions to decode and encode strings from various token sheets can be found in `tivars.tokenizer`. Support currently exists for all forms of 82/83/84 series BASIC as well as custom token sheets; PR's concerning the sheets themselves should be directed upstream to [TI-Toolkit/tokens](https://github.com/TI-Toolkit/tokens).
