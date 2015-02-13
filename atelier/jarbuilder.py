# -*- coding: UTF-8 -*-
# Copyright 2013-2015 by Luc Saffre.
# License: BSD, see LICENSE for more details.

"""This is an extension for :mod:`atelier.fablib` for managing Java
projects.


Using the JarBuilder class
==========================

Usage examples are the :xfile:`fabfile.py` files of `eidreader
<https://github.com/lsaffre/eidreader/blob/master/fabfile.py>`_ and
`davlink <https://github.com/lsaffre/davlink/blob/master/fabfile.py>`_.

The :command:`fab jars` command is used to build and sign all jar files of
a project.

.. command:: fab jars

    Build the .jar file.

.. command:: fab classes

    Compile the .java files to .class files.

Setting up the Java keystore
============================

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

"""

from unipath import Path
from fabric.api import local


class JarBuilder(object):
    """Used by my Java projects :ref:`davlink` and :ref:`eidreader`.

    """

    def __init__(self, jarfile, sourcedir, tsa):
        self.libjars = []
        self.tsa = tsa
        self.jarfile = Path(jarfile)
        self.sourcedir = Path(sourcedir)
        self.sources = list(self.sourcedir.listdir('*.java'))

        self.jarcontent = [Path('Manifest.txt')]
        self.jarcontent += [
            Path(x) for x in self.sourcedir.listdir('*.class')]

    def add_lib(self, pth):
        self.libjars.append(Path(pth))

    def build_jar(self, outdir, alias):
        flags = '-storepass "`cat ~/.secret/.keystore_password`"'
        if self.tsa:
            flags += ' -tsa {0}'.format(self.tsa)

        def run_signer(jarfile):
            local("jarsigner %s %s %s" % (flags, jarfile, alias))
            local("jarsigner -verify %s" % jarfile)

        outdir = Path(outdir)
        jarfile = outdir.child(self.jarfile)
        if jarfile.needs_update(self.jarcontent):
            jarcontent = [x.replace("$", r"\$") for x in self.jarcontent]
            local("jar cvfm %s %s" % (jarfile, ' '.join(jarcontent)))
        run_signer(jarfile)
        for libfile in self.libjars:
            jarfile = outdir.child(libfile.name)
            if not jarfile.exists() or libfile.needs_update([jarfile]):
                libfile.copy(jarfile)
            run_signer(jarfile)

    def build_classes(self):
        flags = "-Xlint:unchecked"
        if len(self.libjars):
            cp = ':'.join(self.libjars)
            flags += " -classpath %s" % cp
        for src in self.sources:
            local("javac %s %s" % (flags, src))


