# tivars_lib_py

`tivars_lib_py` is a Python package for interacting with TI-(e)z80 (82/83/84 series) calculator files, i.e. lists, programs, matrices, appvars, etc.

Much of the functionality of this package has been ported over from [tivars_lib_cpp](https://github.com/adriweb/tivars_lib_cpp). However, a number of changes have been made to the API to better suit Python's strengths and capabilities as a language (e.g. scripting, dynamic typing).

## Installation

The current release version is `v0.8.2`. All versions require Python 3.10+ to run.

### As a Package

Install the `tivars` package from PyPI using `pip`:
```
pip install tivars
```

Alternatively, you can clone this repository or [download a release](https://github.com/TI-Toolkit/tivars_lib_py/tags) and extract the `tivars` directory to include it in your next project. Once downloaded, you can also use `pip` to install it locally.

### As a Submodule

Include this repository in your next project as a submodule using the `git submodule` command. Then, add the following to any file which imports `tivars`:

```py
import sys

sys.path.insert(1, 'tivars_lib_py/')
```

Check out [this tool](https://github.com/TI-Toolkit/token_translation_extractor) for an example.

### Unit Testing

You can run the test suite via `__main__.py`, or run individual tests found in `tests/` with `unittest`. Tests for optional package extensions (e.g. PIL) will be skipped if the package cannot be found.

> [!WARNING]
> The PyPI distribution does _not_ include the test suite.

## How to Use

### Creating objects

### Var basics

Every var file has two parts: a _header_ and a number of _entries_, where an entry contains the data for a single variable. Usually, var files contain just one entry; in these cases, there's not much distinction between a var and an entry for the purposes of messing with its data.

### Entries

To create an empty entry, instantiate its corresponding type from `tivars.types`. You can specify additional parameters as you like:

```python
from tivars.models import *
from tivars.types import *

my_program = TIProgram(name="HELLO")
```

> [!TIP]
> If you're not sure of an entry's type, you can instantiate a base `TIEntry`.

### Vars and Headers

If you want to create an entire var or just a header, use `TIVar` or `TIHeader` instead:

```python
from tivars.var import *

my_var = TIVar()
my_var_for84pce = TIVar(model=TI_84PCE)

my_header = TIHeader()
my_header_with_a_cool_comment = TIHeader(comment="Wow! I'm a comment!")
```

### Reading files

#### Vars

Vars can be loaded from files or raw bytes:

```python
my_var = TIVar.open("HELLO.8xp")

with open("HELLO.8xp", 'rb') as file:
    my_var.load_var_file(file)
    
    file.seek(0)
    my_var.load_bytes(file.read())
```

> [!IMPORTANT]
> When loading from a file object, make sure the file is opened in binary mode.

#### Entries

Entries can be loaded from files or raw bytes. When loading from a file, you may specify which entry to load if there are multiple:

```python
# Raises an error if the var has multiple entries
my_program = TIProgram.open("HELLO.8xp")

with open("HELLO.8xp", 'rb') as file:
    # Offset counts the number of entries to skip; defaults to zero
    my_program.load_from_file(file, offset=1)
    
    file.seek(0)
    my_program.load_bytes(file.read())
```

Most entry types also support loading from other natural data types. Any data can be passed to the constructor directly and be delegated to the correct loader:

```python
my_program = TIProgram("Disp \"HELLO WORLD!\"")
my_program.load_string("Disp \"HELLO WORLD!\"")

my_real = TIReal(1.23)
my_real.load_float(1.23)
```

Base `TIEntry` objects, as well other parent types like `TIGDB`, will be automatically coerced to the correct type:

```python
# Coerces to a TIProgram
my_entry = TIEntry.open("HELLO.8xp")
```

> [!TIP]
> Any entry type can be cast to any other by setting the object's `__class__`.

### Exporting objects

#### Vars

Export a var as bytes or straight to a file:

```python
my_var.save("HELLO.8xp")

# Infer the filename and extension
my_var.save()

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_var.bytes())
```

> [!IMPORTANT]
> `.save()` uses the var's name as the filename, saving to the current working directory.

#### Entries

Entries can be passed an explicit header to attach or model to target when exporting:

```python
my_program.save("HELLO.8xp")
my_program.save()

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_program.export(header=my_header).bytes())
```

Any input data type can also be exported to:

```python
assert my_program.string() == "Disp \"HELLO WORLD!\""

assert my_real.float() == 1.23
```

> [!TIP]
> Built-in types can be exported to using the standard constructors, e.g. `str(my_program)`.

### Data Manipulation

#### Data sections

Vars are comprised of individual _sections_ which represent different forms of data, split across the header and entries. The var itself also contains the total entry length and checksum sections, but these are read-only to prevent file corruption.

You can read and write to individual sections of an entry or header as their "canonical" type:

```python
my_header.comment = "This is my (even cooler) comment!"
my_program.archived = True

assert my_program.type_id == 0x05
```

Data sections can also be other entry types:

```python
my_gdb = TIGDB()
my_gdb.Xmin = TIReal(0)

assert my_gdb.Xmax == TIReal(10)
```

Each section is annotated with the expected type.

> [!TIP]
> Data sections can accept any subtype of their expected type.

#### Raw containers

All vars store their data sections as raw bytes in the format interpreted by the calculator. Access any data section as a member of the `.raw` attribute to view and edit these bytes directly.

```python
my_header.raw.comment = "This is my (even rawer) comment!".encode('utf-8')
my_program.raw.archived = b'\x80'

assert my_program.raw.type_id == b'\x05'
```

> [!WARNING]
> Edits to read-only bytes like the checksum are reset whenever any other data in the var is updated.

### Models

All TI-82/83/84 series calcs are represented as `TIModel` objects stored in `tivars.models`. Each model contains its name, metadata, and features; use `has` on a `TIFeature` to check that a model has a given a feature. Models are also used to determine var file extensions and token sheets.

### Flash Files

Flash files such as apps, OSes, and certificates can be loaded using the `TIFlashHeader` base class or its children. A flash file is composed of one to three headers (though usually only one); these are not to be confused with var headers. A flash header does _not_ need to be "packaged" into a larger file format like an entry in a regular var; see `TIFlashHeader.open` and `TIFlashHeader.save`.

> [!TIP]
> Loading flash files into a `TIEntry` probably won't work very well.

## Other Functionalities

### PIL

The `tivars.PIL` package can be used to interface with PIL, the Python Imaging Library. Simply import the package to register codecs for each of the TI image types. You can then open such images directly into a PIL `Image`:

```python
from PIL import Image
from tivars.PIL import *

img = Image.open("Pic1.8ci")
img.show()
```

### Tokenization

Functions to decode and encode strings into tokens can be found in `tivars.tokenizer`. These functions utilize the [TI-Toolkit token sheets](https://github.com/TI-Toolkit/tokens), which are kept as a submodule in `tivars.tokens`. Support currently exists for all models in the 82/83/84 series; PR's concerning the sheets themselves should be directed upstream.

> [!IMPORTANT]
> In contrast to some other tokenizers like SourceCoder, tokenization does _not_ depend on whether the content appears inside a BASIC string literal. Text is always assigned to the _longest_ permissible token.

## Documentation

Library documentation can be found on [GitHub Pages](https://ti-toolkit.github.io/tivars_lib_py/).

The var file format(s) and data sections can be found in a readable format on the [repository wiki](https://github.com/TI-Toolkit/tivars_lib_py/wiki). Much of the information is copied from the [TI-83 Link Guide](http://merthsoft.com/linkguide/ti83+/vars.html), though has been updated to account for color models.

> [!NOTE]
> The wiki is still a work-in-progress. Why not [contribute a page](https://github.com/TI-Toolkit/tivars_lib_py/wiki)?

## Examples

You can find more sample code in `examples` that details common operations on each of the entry types. There are also examples for interfacing with popular external libraries (e.g. NumPy, PIL). Contributions welcome!
