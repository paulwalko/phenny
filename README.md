# notecharlie

This is notecharlie, wuvt's emasculated phenny fork. Phenny is a Python IRC bot
originally written by Sean B. Palmer, it has been ported to Python3, and
features have been slowly removed.

This version comes with many new modules, IPv6 support, TLS support, and unit
tests. We also include a dockerfile used as part of our own deployment.

We disable most of the snarfuri tools to leak less metadata; other features
will be axed in future releases.

Compatibility with existing phenny modules has been mostly retained, but they
will need to be updated to run on Python3 if they do not already. All of the
core modules have been ported, removed, or replaced.

## Requirements
* Python 3.4+
* [python-requests](http://docs.python-requests.org/en/latest/)

## Installation
1. Run `./phenny` - this creates a default config file
2. Edit `~/.phenny/default.py`
3. Run `./phenny` - this now runs phenny with your settings

Alternately, you can use the provided Dockerfile.

Enjoy!

## Testing
You will need the Python3 versions of `python-nose` and `python-mock`. To run
the tests, simply run `nosetests3`.

## Authors
* Sean B. Palmer, http://inamidst.com/sbp/
* mutantmonkey, http://mutantmonkey.in
