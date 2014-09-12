import re
import subprocess
import tempfile
import os
import shutil

from logbook import Logger
from .utils import higher_log_indent
from .exceptions import BadExitCode


def _figureout_version(url):
    # TODO output warning about missing URL and version
    patterns = (
        r'(\d+\.\d+\.\d+)',
        r'(\d+\.[a-z0-9]+)',
    )
    for pattern in patterns:
        try:
            return re.search(pattern, url).group(1)
        except:
            pass

    return 'dev'


class Schema(object):
    url = None
    version = None
    homepage = None
    deps = []
    dirs_to_symlink = ['bin', 'sbin', 'etc', 'lib', 'include', 'var']

    def __init__(self, env):
        self.env = env.copy()
        self.log = Logger()

        if self.version is None:
            self.version = _figureout_version(self.url)

        if self.url.startswith('git://'):
            self.deps.append('git')
            self.retriver = self.git
        else:
            self.retriver = self.wget

        self.env['prefix'] = os.path.join(
            env['osbench_root'],
            'workbench',
            env['schema'],
            self.version
        )
        self.env['version'] = self.version

    # Methods to override
    def install(self):
        pass

    def is_installed(self):
        """Right now we'll simple check if program
        was built and installed into workbench."""
        return os.path.exists(self.env['prefix'])

    # Internals
    def _get_source(self):
        if not self.url:
            return

        self.log.info('Getting source code')

        with higher_log_indent():
            self.retriver(self.url)

            patch_names = sorted(name for name in dir(self) if name.startswith('patch_'))

            for name in patch_names:
                filename = name.replace('_', '-') + '.diff'
                with open(filename, 'w') as f:
                    f.write(self._get_patch(name))
                self.call('patch -p1 < ' + filename)

    def _get_patch(self, name):
        data = getattr(self, name)

        if len(data[:200].split('\n')) == 1:
            # then probably this is a file or URL
            patch_filename = os.path.join(
                os.path.dirname(self.env['schema_filename']),
                data
            )
            if os.path.exists(patch_filename):
                data = open(patch_filename).read()
        
        data = self._substitute_vars(data)
        return data

    def _get_environment_vars(self):
        """ Returns dict with variables to set in shell and to replace in the templates.
        """
        return dict(
            OSBENCH_ROOT=self.env['osbench_root'],
            OSBENCH_PREFIX=self.env['prefix'],
        )

    def _substitute_vars(self, text):
        for name, value in self._get_environment_vars().items():
            text = text.replace(name, value)
        return text


    def wget(self, url):
        self.call('wget "{0}"'.format(self.url))
        files = os.listdir('.')
        assert len(files) == 1

        filename = files[0]
        # remove url params if they was added to the filename
        stripped_filename = filename.split('?', 1)[0]

        if stripped_filename.endswith('.gz') or \
           stripped_filename.endswith('.tgz'):
            tar_options = '-zxvf'
        elif stripped_filename.endswith('.bz2'):
            tar_options = '-jxvf'
        else:
            raise RuntimeError('Unknown archive format.')

        self.call('tar {0} "{1}"'.format(tar_options, filename))
        os.unlink(filename)

        dirs = os.listdir('.')
        assert len(dirs) == 1

        os.chdir(dirs[0])

    def git(self, url):
        self.call("git clone '{0}'".format(url))
        dirs = os.listdir('.')
        assert len(dirs) == 1
        os.chdir(dirs[0])

    def _install_deps(self):
        if self.deps:
            self.log.info('Installing dependencies')

            with higher_log_indent():
                for dep in self.deps:
                    if dep.startswith('system.'):
                        self.call('sudo apt-get --yes install %s' % dep[7:])

    def _install(self, interactive=False):
        self.log.info('Installing "{schema}"'.format(**self.env))

        with higher_log_indent():
            self._install_deps()

            root = tempfile.mkdtemp(prefix='diy-')

            if not os.path.exists(self.env['prefix']):
                os.makedirs(self.env['prefix'])

            try:
                os.chdir(root)

                self._get_source()

                if interactive:
                    self.log.info('Entering into the interactive mode')
                    with higher_log_indent():
                        shell = os.environ['SHELL']
                        self.call('git init')
                        self.call('git add -A')
                        for name, value in self._get_environment_vars().items():
                            os.environ[name] = value
                        self.call(shell, pass_output=True)
                else:
                    self.log.info('Running schema\'s install method')
                    with higher_log_indent():
                        self.install()

                self._link()

            finally:
                self.call('rm -fr "{0}"'.format(root))

    def _uninstall(self):
        """Uninstalls the schema from the prefix.

        It removes symlinks and deletes installed files from workbenches.
        """
        self.log.info('Uninstalling "{schema}"'.format(**self.env))
        with higher_log_indent():
            self._unlink()
            self._delete()

    def _delete(self):
        shutil.rmtree(self.env['prefix'])

    def _join_path(self, *args):
        return os.path.normpath(os.path.join(*args))

    def _link(self):
        self.log.info('Making symlinks')

        with higher_log_indent():
            for dir_name in self.dirs_to_symlink:
                s_dir = self._join_path(self.env['prefix'], dir_name)
                t_dir = self._join_path(self.env['osbench_root'], dir_name)

                if not os.path.exists(t_dir):
                    self.log.debug('Creating directory "{0}"', t_dir)
                    os.makedirs(t_dir)

                if os.path.exists(s_dir):
                    for root, dirs, files in os.walk(s_dir):
                        # making root, relative
                        root = os.path.relpath(root, s_dir)

                        for dir_name in dirs:
                            full_dir_name = self._join_path(
                                t_dir, root, dir_name
                            )
                            if not os.path.exists(full_dir_name):
                                self.log.debug('Creating directory "{0}"', full_dir_name)
                                os.makedirs(full_dir_name)


                        for filename in files:
                            source = self._join_path(s_dir, root, filename)
                            target = self._join_path(t_dir, root, filename)

                            if os.path.exists(target):
                                if os.path.islink(target):
                                    if os.readlink(target) == source:
                                        self.log.debug('Symlink {target} already exists', target=target)
                                        continue
                                    else:
                                        self.log.warning('Unlinking file {target}, pointing to {source}',
                                                         target=target, source=source)
                                        os.unlink(target)
                                else:
                                    self.log.warning('File {target} already exists and it is not a link',
                                                     target=target)

                            if not os.path.exists(target):
                                self.log.debug('Creating symlink from "{source}" to {target}',
                                               source=source, target=target)
                                os.symlink(source, target)


    def _unlink(self):
        self.log.info('Removing symlinks')
        for ftype, name in self.get_files_to_unlink():
            if ftype == 'file':
                os.unlink(name)
            else:
                try:
                    os.rmdir(name)
                except OSError:
                    pass

    def get_files_to_unlink(self):
        with higher_log_indent():
            for dir_name in self.dirs_to_symlink:
                s_dir = self._join_path(self.env['prefix'], dir_name)
                t_dir = self._join_path(self.env['osbench_root'], dir_name)

                if os.path.exists(s_dir):
                    for root, dirs, files in os.walk(s_dir, topdown=False):
                        # making root, relative
                        root = os.path.relpath(root, s_dir)

                        for filename in files:
                            source = self._join_path(s_dir, root, filename)
                            target = self._join_path(t_dir, root, filename)

                            if os.path.islink(target) and \
                                os.path.realpath(target) == source:
                                yield ('file', target)

                        for dir_name in dirs:
                            full_dir_name = self._join_path(
                                t_dir, root, dir_name
                            )
                            yield ('dir', full_dir_name)

    # Utilities
    def call(self, command, pass_output=False):
        command = command.format(**self.env)
        self.log.info('Running "{0}"'.format(command))

        with higher_log_indent():
            options = dict(
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
            if pass_output:
                del options['stdout']
                del options['stderr']

            proc = subprocess.Popen(
                command,
                **options
            )

            full_output = []
            if not pass_output:
                for line in proc.stdout:
                    line = line.decode('utf-8').strip(u'\n')
                    full_output.append(line)
                    self.log.debug(line)

            return_code = proc.wait()
            if return_code != 0:
                for line in full_output:
                    self.log.error(line)
                raise BadExitCode('subprogram exit with non zero exit code')

    def makedirs(self, *dirs):
        """Makes dirs inside the prefix.

        Use this command inside your `install` method.
        """
        for d in dirs:
            fullname = os.path.join(self.env['prefix'], d)
            if not os.path.exists(fullname):
                self.log.info('Creating directory "{0}".'.format(fullname))
                os.makedirs(fullname)

    def create_file_with_content(self, filename, content, mode=None):
        """Creates a file inside 'prefix'.

        Use this command inside your `install` method.
        Note: Source and target directory should exists.
        Warning: if there is some file already, it will be overwritten.
        """
        filename = os.path.join(self.env['prefix'], filename)

        self.log.info('Creating file "{0}"'.format(filename))

        with open(filename, 'w') as f:
            f.write(self._substitute_vars(content))

        if mode is not None:
            self.call('chmod "{0}" "{1}"'.format(mode, filename))

    def copy_file(self, from_filename, to_filename, mode=None):
        """Copies file, to a directory inside 'prefix'.

        from_filename could be relative to the current directory, or 
        use variables to be expanded to self.env.

        Use this command inside your `install` method.
        Note: Source and target directory should exists.
        Warning: if there is some file already, it will be overwritten.
        """
        with open(from_filename.format(**self.env), 'r') as f:
            self.create_file_with_content(to_filename, f.read(), mode=mode)


class PythonSchema(Schema):
    def __init__(self, *args, **kwargs):
        super(PythonSchema, self).__init__(*args, **kwargs)
        self.deps.append('system.python-virtualenv')
        
    def _install(self, interactive=False):
        self.log.info('Installing "{schema}"'.format(**self.env))

        with higher_log_indent():
            self._install_deps()

            self.log.info('Creating virtual env')
            with higher_log_indent():
                self.call('virtualenv "{prefix}"')

            self.log.info('Installing package {0}'.format(self.url))
            with higher_log_indent():
                self.call('"{{prefix}}"/bin/pip install "{0}"'.format(self.url))


            self.log.info('Running schema\'s install method')
            with higher_log_indent():
                self.install()

            self._link()

