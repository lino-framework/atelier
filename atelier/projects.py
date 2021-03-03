# -*- coding: UTF-8 -*-
# Copyright 2011-2020 Rumma & Ko Ltd
# License: BSD, see LICENSE for more details.
"""A minimalistic command-line project management.

See :doc:`/usage`.

"""
import os

# import pkg_resources
from pathlib import Path
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

from atelier.invlib.utils import SphinxTree

config_files = ['~/.atelier/config.py', '/etc/atelier/config.py',
                '~/_atelier/config.py']

_PROJECT_INFOS = []
_PROJECTS_DICT = {}


def load_inv_namespace(root_dir):
    """
    Execute the :xfile:`tasks.py` file of this project and return its
    `ns`.
    """
    # self._tasks_loaded = True

    tasks_file = root_dir / 'tasks.py'
    if not tasks_file.exists():
        return None
        # raise Exception("No tasks.py file in {}".format(root_dir))
        # return

    # print("20180428 load tasks.py from {}".format(root_dir))
    # http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    # http://stackoverflow.com/questions/19009932/import-arbitrary-python-source-file-python-3-3
    # fqname = 'atelier.prj_%s' % self.index
    cwd = Path().resolve()
    os.chdir(root_dir)
    m = dict()
    m["__file__"] = str(tasks_file)
    with open(tasks_file) as f:
        exec(f.read(), m)
    os.chdir(cwd)
    return m['ns']



def add_project(root_dir, nickname=None):
    """
    To be called from your :xfile:`config.py` file.

    `root_dir` is the name of a directory which is expected to contain
    a :xfile:`tasks.py`.

    If no `nickname` is specified, the nickname will be the leaf name
    of that directory.

    Returns a :class:`Project` instance describing the project.
    """
    i = len(_PROJECT_INFOS)
    root_dir = Path(root_dir).absolute().resolve()
    if not root_dir.exists():
        raise Exception("Invalid root directory {}".format(root_dir))
    p = Project(i, root_dir, nickname=None)
    _PROJECT_INFOS.append(p)
    _PROJECTS_DICT[root_dir] = p
    return p


def get_project_info_from_mod(modname):
    """Find the project info for the given Python module."""
    m = import_module(modname)
    if m.__file__ is None:
        raise Exception("Invalid module name {} (is it installed?)".format(modname))
    fn = Path(m.__file__)
    prj = get_project_from_tasks(fn.parent.parent)
    if prj is None:
        # package installed in site-packages without tasks.py file
        root_dir = fn.parent.absolute().resolve()
        prj = _PROJECTS_DICT.get(root_dir)
        if prj is None:
            prj = add_project(root_dir)
            # raise Exception("20191003 dynamically added from {}".format(root_dir))
    # root_dir = Path(m.__file__).parent.parent
    # prj = add_project(root_dir)
    prj.set_main_package(m)
    # assert prj.main_package is not None
    return prj

def get_project_from_nickname(name):
    "Find the project info for the given nickname."
    for p in _PROJECT_INFOS:
        if p.nickname == name:
            return p

def get_project_from_tasks(root_dir):
    "Find the project info for the given directory."
    root_dir = root_dir.absolute().resolve()
    prj = _PROJECTS_DICT.get(root_dir)
    if prj is None:
        if (root_dir / 'tasks.py').exists():
            return add_project(root_dir)
        # if no config.py found, add current working directory.
        # p = Path().resolve()
        # while p:
        #     if (p / 'tasks.py').exists():
        #         prj = add_project(p)
        #         break
        #     if p == p.parent:
        #         return  # reached the file system's root
        #     p = p.parent
        # raise Exception("No %s in %s" % (root_dir, _PROJECTS_DICT.keys()))
    return prj


def load_projects():
    for p in _PROJECT_INFOS:
        yield p


def get_setup_info(root_dir):
    """
    Return `SETUP_INFO` defined in the :xfile:`setup.py` file of the
    specified `root_dir`.
    """
    setup_file = root_dir / 'setup.py'
    if not setup_file.exists():
        # print("20180118 no setup.py file in {}".format(root_dir.absolute()))
        return {}
        # raise RuntimeError(
        #     "You must call 'inv' from a project's root directory.")
    # sys.path.insert(0, root_dir)
    # setup_module = __import__('setup')
    # print 20140610, root_dir
    # del sys.path[0]
    # return getattr(setup_module, 'SETUP_INFO', None)
    g = dict()
    g['__name__'] = 'not_main'
    # g['__file__'] = setup_file
    cwd = Path().resolve()
    os.chdir(root_dir)
    with open("setup.py") as f:
        code = compile(f.read(), "setup.py", 'exec')
        try:
            exec(code, g)
        except SystemExit:
            os.chdir(cwd)
            raise Exception(
                "Oops, {} called sys.exit().\n"
                "Atelier requires the setup() call to be in a "
                "\"if __name__ == '__main__':\" condition.".format(
                    setup_file))
    os.chdir(cwd)
    info = g.get('SETUP_INFO')
    if info is None:
        raise Exception(
            "Oops, {} doesn't define a name SETUP_INFO.".format(
                setup_file))
    return info

    # # Expected to define global SETUP_INFO.
    # # Note that main_package may be "sphinxcontrib.dailyblog"
    # args = env.main_package.split('.')
    # args.append('project_info.py')
    # file =env.ROOTDIR / ('/'.join(args))
    # with open(file) as f:
    #    code = compile(f.read(), file, 'exec')
    #    exec(code, globals())
    # #execfile(env.ROOTDIR / ('/'.join(args)), globals())
    # env.SETUP_INFO = SETUP_INFO


class Project(object):
    """Represents a project.

    .. attribute:: main_package

        The main package (a Python module object).

    .. attribute:: index

        An integer representing the sequence number of this project in
        the global projects list.

    .. attribute:: config

        A dict containing the configuration options of this project.
        See :ref:`atelier.prjconf`.

    """
    main_package = None
    # srcref_url = None
    # intersphinx_urls = {}
    SETUP_INFO = None
    config = None
    inv_namespace = None
    _git_status = None

    def __init__(self, i, root_dir, nickname=None):
        # , inv_namespace=None, main_package=None):

        self.index = i
        self.root_dir = root_dir
        #~ self.local_name = local_name
        #~ self.root_dir = Path(atelier.PROJECTS_HOME,local_name)
        self.nickname = nickname or str(self.root_dir.name)
        # self.name = self.nickname  # might change in load_info()
        # self._loaded = False
        # self._tasks_loaded = False
        # print("20180428 Project {} initialized".format(self.nickname))
        #self.main_package = main_package
        #self.inv_namespace = inv_namespace
        self.config = {
            'root_dir': root_dir,
            'build_dir_name': '.build', # e.g. ablog needs '_build'
            'project_name': str(root_dir.name),
            'locale_dir': None,
            'help_texts_source': None,
            'help_texts_module': None,
            'tolerate_sphinx_warnings': False,
            'cleanable_files': [],
            'revision_control_system': None,
            'apidoc_exclude_pathnames': [],
            'editor_command': os.environ.get('EDITOR'),
            'prep_command': "",
            'build_docs_command': "",
            'test_command': "python -m unittest discover -s tests",
            'demo_projects': [],
            'demo_prep_command': "manage.py prep --noinput --traceback",
            # 'coverage_command': '{} inv prep test clean --batch bd'.format(pp),
            'coverage_command': '`which invoke` prep test clean --batch bd',
            'languages': None,
            'blog_root': root_dir / 'docs',
            'long_date_format': "%Y%m%d (%A, %d %B %Y)",
            'sdist_dir': root_dir / 'dist',
            'pypi_dir': root_dir / '.pypi_cache',
            'use_dirhtml': False,
            'doc_trees': ['docs'],
            'intersphinx_urls': {},
        }


    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.root_dir)

    def set_main_package(self, m):
        self.main_package = m

    def set_namespace(self, ns):
        self.inv_namespace = ns
        ns.configure(self.config)
        if self.main_package is None:
            # when no main_package is given, there must be a namespace
            cfg = ns.configuration()
            name = cfg.get('main_package', None)
            # if inv_name != name:
            #     raise Exception("20180428 {} != {}".format(inv_name, name))
            if name:
                # self.doc_trees = None
                # self.name = name
                self.main_package = import_module(name)
                # if self.main_package is None:
                #     raise Exception("Failed to import {}".format(name))

    def load_info(self):
        """
        The project can be:

        - Loaded from a config file: we know only the root_dir

        - instantiated by get_project_from_tasks() called in
          setup_from_tasks(): we know also the inv_namespace

        - instantiated by get_project_info_from_mod() (by
          sphinxconf.interproject) : we know also the main_package

        A project can have no inv_namespace
        """

        # inv_namespace = self.inv_namespace or load_inv_namespace(
        #     self.root_dir)

        if self.SETUP_INFO is not None:
            # load_info() has been called before
            return

        self.SETUP_INFO = get_setup_info(self.root_dir)

        # if self.main_package is None:
        #     self.config.setdefault('doc_trees', ['docs'])
        # else:
        #     self.config.update(main_package=self.main_package.__name__)

        if self.inv_namespace is None:
            ns = load_inv_namespace(self.root_dir)
            if ns is not None:
                self.set_namespace(ns)


        # if self.main_package is None:
        #     self.config.update(doc_trees=['docs'])

    def get_status(self):
        # if self.config['revision_control_system'] != 'git':
        # config = self.inv_namespace.configuration()
        self.load_info()
        if self.config['revision_control_system'] != 'git':
            return ''
        if self._git_status is not None:
            return self._git_status
        from git import Repo
        repo = Repo(self.root_dir)
        try:
            s = str(repo.active_branch)
        except TypeError:
            s = "?"
        if repo.is_dirty():
            s += "!"
        self._git_status = s
        return s

    def get_xconfig(self, name, default=None):
        """Return the specified setting from either main module or tasks.py.

        TODO: explain why we need this.
        """
        self.load_info()
        if self.inv_namespace is not None:
            cfg = self.inv_namespace.configuration()
            default = cfg.get(name, default)
        if self.main_package:
            # if name in cfg:
            #     msg = "{} configures both {} and main_package. "
            #     msg += "If you have a main_package then you must set "
            #     msg += "doc_trees there."
            #     raise Exception(msg.format(self, name))
            return getattr(self.main_package, name, default)
        return default

    def get_doc_trees(self):
        """
        Yield one DocTree instance for every item of this project's
        :envvar:`doc_trees`.
        """
        # print("20180504 {} get_doc_tree() {}".format(self, self.config))
        # if not hasattr(ctx, 'doc_trees'):
        #     return
        # cfg = self.config
        doc_trees = self.get_xconfig('doc_trees')
        if doc_trees is None or len(doc_trees) == 0:
            return
        # print("20180504 {} get_doc_tree() {} {}".format(
        #     self, self.main_package, doc_trees))
        for rel_doc_tree in doc_trees:
            if isinstance(rel_doc_tree, str):
                yield SphinxTree(self, rel_doc_tree)
            elif isinstance(rel_doc_tree, tuple):
                # (BUILDER, PATH)
                clparts = rel_doc_tree[0].split('.')
                cl = import_module(clparts[0])
                for k in clparts[1:]:
                    cl = getattr(cl, k)
                yield cl(self, rel_doc_tree[1])
            else:
                raise Exception("Invalid item {} in doc_trees".format(
                    rel_doc_tree))

def load_config():
    for fn in config_files:
        fn = os.path.expanduser(fn)
        if os.path.exists(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                exec(code)


load_config()
