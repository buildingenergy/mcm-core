mcm-core
========

Core MCM - Map Clean Merge


Installing
----------

Once it's hosted on Pypi:
```bash
    pip install mcm-core
```

Integration
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

Developing
----------

1. Clone.
2. Create a virtualenv; if you use virtualenv wrapper you'll need to
    1. Run ``python setup.py develop`` to hardlink your files into your env.


Testing
-------

Unfortunately, there are some directory path issues still baked in.
To run tests you have to be in the ``tests`` directory:

```bash
    cd tests && nosetests
```
