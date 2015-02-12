Using the JarBuilder
====================

Usage examples are the :xfile:`fabfile.py` files of `eidreader
<https://github.com/lsaffre/eidreader/blob/master/fabfile.py>`_ and
`davlink <https://github.com/lsaffre/davlink/blob/master/fabfile.py>`_.

The :command:`fab jars` command is to build and sign all jar files of
a project.

There must be a key identified by alias in your keystore.

See what's in my keystore::
    
    $ keytool -list
    $ keytool -list -v -alias meykey

Generate a new key::

    $ keytool -genkey -alias mykey
    
Self-sign the new key::
    
    $ keytool -selfcert -alias mykey -validity 360

This sets mykey to expire in 360 days.  6 months later I'll get a
warning :message:`The signer certificate will expire within six
months.` when I run :command:`fab jars` to sign a jar file.

