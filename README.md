# tivars_lib_py

`tivars_lib_py` is a Python package for interacting with TI-(e)z80 (82/83/84 series) calculator files, i.e. lists, programs, matrices, appvars, etc.

Much of the functionality of this package has been ported over from [tivars_lib_cpp](https://github.com/adriweb/tivars_lib_cpp). However, a number of changes have made to the API to better suit Python's strengths and capabilities as a language (e.g. scripting).

## Installation

Clone this repository into your next project and import this package via `import tivars`. You can run the test suite via `__main__.py`, or run individual tests found in `tests/` with `unittest`.

## How to Use

### Creating vars

To create an empty var, instantiate its corresponding type from `tivars.vars.types` with a name and calculator model:
```python
from tivars.models import *
from tivars.vars.types import *

my_program = TIProgram("HELLO", TI_84p)
```
If you're not sure of a var's type or model, use `TIVar.infer` to guess given a file's contents:
```python
with open("MyVar", 'rb') as file:
    my_var = TIVar.infer(file)
```

### Reading and writing

Load an existing file via `load` or interpret from a string using `loads`:
```python
with open("HELLO.8xp", 'rb') as file:
    my_program.load(file)

# See the type classes for string formats
# Programs use tokenization like you'd find in TI-Connect
my_program.loads("Disp \"HELLO WORLD!\"")
```
Write the contents of a var as a bytes or as a string with `dump` and `dumps`:
```python
with open("HELLO.8xp", 'wb+') as file:
    file.write(my_program.dumps())
    
# Alternative
my_program.save("HELLO.8xp")

# Infer the output filename
my_program.save()

print(my_program.dumps())
```