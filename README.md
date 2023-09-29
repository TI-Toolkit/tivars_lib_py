# tivars_lib_py

`tivars_lib_py` is a Python package for interacting with TI-(e)z80 (82/83/84 series) calculator files, i.e. lists, programs, matrices, appvars, etc.

Much of the functionality of this package has been ported over from [tivars_lib_cpp](https://github.com/adriweb/tivars_lib_cpp). However, a number of changes have made to the API to better suit Python's strengths and capabilities as a language (e.g. scripting).

## Installation

The current release version is `v0.8.1`. All versions require Python 3.10+ to run.

### As a Package

Install the `tivars` package from PyPI using `pip`:
```
pip install tivars
```

Alternatively, you can clone this repository or [download a release](https://github.com/TI-Toolkit/tivars_lib_py/tags) and extract the `tivars` directory to include it in your next project. Once downloaded, you can also use `pip` to install it locally.

### As a Submodule

Include this repository in your next project as a submodule using `git submodule` or manually cloning and writing the following in `.gitmodules`:

```
[submodule "tivars_lib_py"]
	path = path/to/tivars_lib_py
	url = https://github.com/TI-Toolkit/tivars_lib_py.git
```

Then, add the following to any file which imports `tivars`:

```py
import sys

sys.path.insert(1, 'tivars_lib_py/')
```

Check out [this tool](https://github.com/TI-Toolkit/token_translation_extractor) for an example.

### Unit Testing

You can run the test suite via `__main__.py`, or run individual tests found in `tests/` with `unittest`. Tests for optional package extensions (e.g. PIL) will be skipped if the package cannot be found.

Note that the PyPI distribution does _not_ include the test suite.

## How to Use

### Creating vars

Every var file has two parts: a _header_ and a number of _entries_, where an entry contains the data for a single variable. Usually, var files contain just one entry; in these cases, there's not much distinction between a var and an entry for the purposes of messing with its data.

To create an empty entry, instantiate its corresponding type from `tivars.types`. You can specify additional parameters as you like:

```python
from tivars.models import *
from tivars.types import *

my_program = TIProgram(name="HELLO")
```

If you're not sure of an entry's type, instantiate a base `TIEntry`:

```python
my_entry = TIEntry()
```

If you want to create an entire var or just a header, use `TIVar` or `TIHeader` instead:

```python
from tivars.var import *

my_var = TIVar()
my_var_for84pce = TIVar(model=TI_84PCE)

my_header = TIHeader()
my_header_with_a_cool_comment = TIHeader(comment="Wow! I'm a comment!")
```

### Reading and writing

Vars can be loaded from files or raw bytes:

```python
my_var = TIVar.open("HELLO.8xp")

# Note binary mode!
with open("HELLO.8xp", 'rb') as file:
    my_var.load_var_file(file)
    
    file.seek(0)
    my_var.load_bytes(file.read())
```

Entries can be loaded from files or raw bytes. When loading from a file, you may specify which entry to load if there are multiple:

```python
# Raises an error if the var has multiple entries; use load_from_file instead
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

Export a var as bytes or straight to a file:

```python
my_var.save("HELLO.8xp")

# Infer the filename and extension
my_var.save()

with open("HELLO.8xp", 'wb+') as file:
    file.write(my_var.bytes())
```

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

Data types corresponding to built-in Python types can be obtained from the built-in constructors:

```python
assert str(my_program) == "Disp \"HELLO WORLD!\""

assert float(my_real) == 1.23
```

### Data Sections

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

### Models

All TI-82/83/84 series calcs are represented as `TIModel` objects stored in `tivars.models`. Each model contains its name, metadata, and features; use `has` on a `TIFeature` to check that a model has a given a feature. Models are also used to determine var file extensions and token sheets.

For these reasons, it is _not_ recommended to instantiate your own models.

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

Functions to decode and encode strings into tokens can be found in `tivars.tokenizer`. Support currently exists for all models in the 82/83/84 series as well as the TI-73; PR's concerning the sheets themselves should be directed upstream to [TI-Toolkit/tokens](https://github.com/TI-Toolkit/tokens).

## Documentation

Library documentation can be found on [GitHub Pages](https://ti-toolkit.github.io/tivars_lib_py/).

The var file format(s) and data sections can be found in a readable format on the [repository wiki](https://github.com/TI-Toolkit/tivars_lib_py/wiki). Much of the information is copied from the [TI-83 Link Guide](http://merthsoft.com/linkguide/ti83+/vars.html), though has been updated to account for color models.

## Examples

You can find more sample code in `examples` that details common operations on each of the entry types. There are also examples for interfacing with popular external libraries (e.g. NumPy, PIL). Contributions welcome!
