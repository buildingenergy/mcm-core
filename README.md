mcm-core
========

Core MCM - Map Clean Merge


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
