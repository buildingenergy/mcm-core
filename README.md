![CircleCI Status][]

[CircleCI Status]: https://circleci.com/gh/buildingenergy/mcm-core.png?circle-token=e0d90d702fb615d2a6ab2ce2dbaa05a173ca06a1


mcm-core
========

Core MCM - Map Clean Merge




Overview
-----------

MCM has two main peices, a reader and a mapper.

- Reader
  * Reads csv files, returns a generator of DictCSVReader parsed rows.
  * Optionally chunks the rows into groupings of specified sizes.
- Mapper
  * Can build a probabalistic column mapping given a schema and some raw data.
    * Will substitute saved values for suggested mapping (e.g. pulling a previous mapping from DB).
    * Totally flexible, you pass a callable which takes the raw data and returns a mapping.
  * Will clean data based on a Cleaner object for a given type. Type is inferred from the mapping schema.
  * Ability to set "initial_data"
    * If you always need to set some information in the object that you're mapping data into, this is useful.
  * Concatenate rows together with a specified delimiter character.
  * Data which doesn't match a given schema's mapping is still saved. It's put in a dictionary called ``extra_data``.


Installing
----------

Once it's hosted on Pypi:
```bash
    pip install mcm
```

Integration
-----------

```python
from mcm import cleaners, mapper, reader

# Here our mapping is just a dictionary where our keys are raw data representations
# and our values are our normalized attributes that we're mapping to.
mapping = {'Thing': 'thing_1', 'Other thing': 'thing_2'}

# model_class can be any type of object.
model_class = object

# Reading and mapping from a CSV file, simple case.
parser = reader.MCMParser(csv_file_handle)
mapped_objs = [m for m in parser.map_rows(mapping, model_class)]
```


Developing
----------

1. Clone.
2. Create a virtualenv; if you use virtualenv wrapper you'll need to
    1. Run ``python setup.py develop`` to hardlink your files into your env.


Testing
-------

Unfortunately, there are some directory path issues still baked in.
To run tests you have to be in the ``tests`` directory:

```console
$ flake8 mcm --exclude=data
$ cd mcm/tests && nosetests
```
