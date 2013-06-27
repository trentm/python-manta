A Python SDK for [the Joyent Manta
Service](http://www.joyent.com/products/manta) (a.k.a. Manta). This provides
a Python 'manta' package (for using the [Manta REST
API](http://apidocs.joyent.com/manta/api.html) and a 'mantash' (MANTA SHell)
CLI and shell. For an introduction to Manta in general, see [Manta getting
started docs](http://apidocs.joyent.com/manta/index.html).


# Current Status

Tested mostly on Mac and SmartOS using Python 2.6 or 2.7. Linux should work.
The *intention* is to support Windows as well. Python 3 is not currently
supported (currently because the dependency paramiko does not work with
Python 3).

Feedback and issues here please: <https://github.com/joyent/python-manta/issues>


# Installation

## 1. pycrypto dependency

The 'pycrypto' (aka 'Crypto') Python module is a binary dependency. If you
use SmartOS and Python 2.7, then the Crypto module is included already and
you don't need a separate install.

Python module installation is a bit of a gong show, in general, but here are
some things to try:

    # Mac (using the system python at /usr/bin/python)
    sudo easy_install pycrypto

    # SmartOS with recent pkgsrc has a working Crypto package:
    #       py27-crypto-2.6
    pkgin install py27-crypto

    # Older pkgsrc repositories have a crypto package that is insufficient
    # (the `Crypto.Signature` subpackage is missing).
    #       py27-crypto-2.4.1
    # To get a working Crypto for mantash you can do the following, or
    # similarly for other Python versions:
    pkgin rm py27-crypto   # must get this out of the way
    pkgin install py27-setuptools
    easy_install-2.7 pycrypto

    # Any platform using the ActivePython distribution of Python (available
    # for most platforms).
    pypm install pycrypto

    # Other
    # Often one of the following will do it:
    easy_install pycrypto
    pip install pycrypto


Please [let me
know](https://github.com/joyent/python-manta/issues/new?title=PyCrypto+install+notes+for+XXX)
if there are better instructions that I can provide for your system, so I can
add them here.


## 2. python-manta

    git clone git://github.com/joyent/python-manta.git
    # or `git clone git@github.com:joyent/python-manta.git`
    cd python-manta

The `mantash` CLI and `manta` Python module can be used directly out of this
install:

    export PATH=$PATH:`pwd`/bin
    export PYTHONPATH=$PYTHONPATH:`pwd`/lib

Or you should be able to install to your Python prefix via:

    python setup.py install


## 3. verify it works

The 'mantash' CLI should now work:

    $ mantash help
    ...

For Python usage you need to get the 'lib' directory on your Python Path.
One way is:

    $ python -c "import manta; print(manta.__version__)"
    1.4.0


# Setup

First setup your environment to match your Joyent Manta account. Adjust
accordingly for your SSH key and Manta login. The SSH key here must match
one of keys uploaded for your Joyent Public Cloud account.

    export MANTA_KEY_ID=`ssh-keygen -l -f ~/.ssh/id_rsa.pub | awk '{print $2}' | tr -d '\n'`
    export MANTA_URL=https://us-east.manta.joyent.com
    export MANTA_USER=jill

`mantash` uses these environment variables (as does the [Manta Node.js SDK
CLI](http://wiki.joyent.com/wiki/display/Manta/Manta+CLI+Reference)).
Alternatively you can specify these parameters to `mantash` via command-line
options -- see `mantash --help` for details.

For a colourful `mantash` prompt you can also set:

    export MANTASH_PS1='\e[90m[\u@\h \e[34m\w\e[90m]$\e[0m '


# Python Usage


```python
import os
import logging
import manta

# Manta logs at the debug level, so the logging env needs to be setup.
logging.basicConfig()

url = os.environ['MANTA_URL']
account = os.environ['MANTA_USER']
key_id = os.environ['MANTA_KEY_ID']

# This handles ssh-key signing of requests to Manta. Manta uses
# the HTTP Signature scheme for auth.
# http://tools.ietf.org/html/draft-cavage-http-signatures-00
signer = manta.SSHAgentSigner(key_id)

client = manta.MantaClient(url, account, signer)

content = client.get_object('/%s/stor/foo.txt' % account)
print content

print dir(client)   # list all methods, better documentation coming (TODO)
```


# CLI

This package also provides a `mantash` (MANTA SHell) CLI for working with
Manta:

```shell
$ mantash help
Usage:
    mantash COMMAND [ARGS...]
    mantash help [COMMAND]
...
Commands:
    cat            print objects
    cd             change directory
    find           find paths
    get            get a file from manta
    job            Run a Manta job
...

# This is a local file.
$ ls
numbers.txt

# Mantash single commands can be run like:
#       mantash ls
# Or you can enter the mantash interactive shell and run commands from
# there. Let's do that:
$ mantash
[jill@us-east /jill/stor]$ ls
[jill@us-east /jill/stor]$                      # our stor is empty
[jill@us-east /jill/stor]$ put numbers.txt ./   # upload local file
[jill@us-east /jill/stor]$ ls
numbers.txt
[jill@us-east /jill/stor]$ cat numbers.txt
one
two
three
four

# List available commands. A number of the typical Unix-y commands are
# there.
[jill@us-east /jill/stor]$ help
...

# Manta jobs.
#
# Note: The '^' is used as an alternative pipe separator to '|'.
# The primary reason is to avoid Bash eating the pipe when running
# one-off `mantash job ...` commands in Bash.

# Run a Manta job. Here `grep t` is our map phase.
[jill@us-east /jill/stor]$ job numbers.txt ^ grep t
two
three

# Add a reduce phase, indicated by '^^'.
[jill@us-east /jill/stor]$ job numbers.txt ^ grep t ^^ wc -l
2
```



# License

MIT. See LICENSE.txt.

Some pure Python dependencies are included in this distribution (to
reduce install dependency headaches). They are covered by their
respective licenses:

- paramiko (http://www.lag.net/paramiko/): LGPL
- httplib2 (http://code.google.com/p/httplib2/): MIT
- cmdln (https://github.com/trentm/cmdln): MIT
- appdirs (https://github.com/ActiveState/appdirs): MIT


# Troubleshooting

### `ImportError: No module named Signature`

If you see this attempting to run mantash on SmartOS:

    $ ./bin/mantash
    * * *
    See <https://github.com/joyent/python-manta#1-pycrypto-dependency>
    for help installing PyCrypto (the Python 'Crypto' package)
    * * *
    Traceback (most recent call last):
      File "./bin/mantash", line 24, in <module>
        import manta
      File "/root/joy/python-manta/lib/manta/__init__.py", line 7, in <module>
        from .auth import PrivateKeySigner, SSHAgentSigner, CLISigner
      File "/root/joy/python-manta/lib/manta/auth.py", line 18, in <module>
        from Crypto.Signature import PKCS1_v1_5
    ImportError: No module named Signature

then you have an insufficient PyCrypto package, likely from an old pkgsrc.
For example, the old "sdc6/2011Q4" pkgsrc is not supported:

    $ cat /opt/local/etc/pkg_install.conf
    PKG_PATH=http://pkgsrc.joyent.com/sdc6/2011Q4/i386/All


# Limitations

The python-manta Python API isn't currently well-suited to huge objects
or huge directory listings (>10k dirents) because responses are fully
buffered in memory rather than being streamed. If streaming is a requirement
for your use case, you could consider the [Manta Node.js
bindings](https://github.com/joyent/node-manta).

For other limitations (also planned work) see TODO.txt.
