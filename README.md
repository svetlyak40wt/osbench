OS Bench
========

This is a naive attempt to create a package manager for Unix-like systems.
It is inspired by [Homebrew](https://github.com/mxcl/homebrew), but is written
in a language for a human being.

Right now, it is no more than a prototype.

Installation
------------

Oneliner: `bash -c "$(curl -s https://raw.githubusercontent.com/svetlyak40wt/osbench/master/bin/bench-oneliner)"`

Or [clone it] anywhere, add `bin` directory to the `PATH` environment variable
and run `bench-bootstrap`.

Plans
-----

* To make it available under most Linuxes, BSDs and OSXes.
* Allow easy usage of many custom schema repositories.
* Conquer the World! Mu-ha-ha!!!

Development
-----------

### Unit-Testing

    bin/pip install nose
    bin/nosetests lib/benchlib



[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/svetlyak40wt/osbench/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

