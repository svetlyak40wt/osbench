import re
import subprocess
import tempfile
import os
import shutil

from logbook import Logger
from .utils import higher_log_indent


class Schema(object):
    url = None
    version = None
    homepage = None
    deps = []
    dirs_to_symlink = ['bin', 'sbin', 'etc', 'lib', 'include']

    def __init__(self, env):
        self.env = env.copy()
        self.log = Logger()

        if self.version is None:
            if self.url is not None:
                self.version = re.search(r'(\d+\.\d+\.\d+)', self.url).group(1)
            else:
                # TODO output warning about missing URL and version
                self.version = 'dev'

        self.env['prefix'] = os.path.join(
            env['osbench_root'],
            'workbench',
            '%s-%s' % (env['schema'], self.version)
        )

    def _get_source(self):
        if not self.url:
            return

        self.log.info('Getting source code')

        with higher_log_indent():
            self.call('wget "{0}"'.format(self.url))
            files = os.listdir('.')
            assert len(files) == 1

            self.call('tar -jxvf "{0}"'.format(files[0]))
            os.unlink(files[0])

            dirs = os.listdir('.')
            assert len(dirs) == 1

            os.chdir(dirs[0])

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

        data = data.replace('OSBENCH_ROOT', self.env['osbench_root'])
        data = data.replace('OSBENCH_PREFIX', self.env['prefix'])
        return data

    def _install_deps(self):
        if self.deps:
            self.log.info('Installing dependencies')

            with higher_log_indent():
                for dep in self.deps:
                    self.call('sudo apt-get install %s' % dep)

    def _install(self, interactive=False):
        self.log.info('Installing "{schema}"'.format(**self.env))

        with higher_log_indent():
            self._install_deps()

            root = tempfile.mkdtemp(prefix='diy-')
            try:
                os.chdir(root)

                self._get_source()

                if interactive:
                    self.log.info('Entering into the interactive mode')
                    with higher_log_indent():
                        shell = os.environ['SHELL']
                        self.call('git init')
                        self.call('git add -A')
                        self.call(shell)
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

    def _link(self):
        self.log.info('Making symlinks')

        with higher_log_indent():
            for dir_name in self.dirs_to_symlink:
                s_dir = os.path.join(self.env['prefix'], dir_name)
                t_dir = os.path.join(self.env['osbench_root'], dir_name)

                if not os.path.exists(t_dir):
                    self.log.debug('Creating directory "{0}"', t_dir)
                    os.makedirs(t_dir)

                if os.path.exists(s_dir):
                    for root, dirs, files in os.walk(s_dir):
                        # making root, relative
                        root = os.path.relpath(root, s_dir)

                        for dir_name in dirs:
                            full_dir_name = os.path.join(
                                t_dir, root, dir_name
                            )
                            if not os.path.exists(full_dir_name):
                                self.log.debug('Creating directory "{0}"', full_dir_name)
                                os.makedirs(full_dir_name)


                        for filename in files:
                            source = os.path.join(s_dir, root, filename)
                            target = os.path.join(t_dir, root, filename)

                            if not os.path.exists(target):
                                self.log.debug('Creating symlink from "{1}" to {0}', source, target)
                                os.symlink(source, target)

    def _unlink(self):
        self.log.info('Removing symlinks')
        with higher_log_indent():
            for dir_name in self.dirs_to_symlink:
                s_dir = os.path.join(self.env['prefix'], dir_name)
                t_dir = os.path.join(self.env['osbench_root'], dir_name)

                if os.path.exists(s_dir):
                    # TODO check if topdown=False needed
                    for root, dirs, files in os.walk(s_dir):
                        # making root, relative
                        root = os.path.relpath(root, s_dir)

                        for filename in files:
                            target = os.path.join(t_dir, root, filename)

                            if os.path.exists(target):
                                os.unlink(target)

                        for dir_name in dirs:
                            full_dir_name = os.path.join(
                                t_dir, root, dir_name
                            )
                            try:
                                os.rmdir(full_dir_name)
                            except IOError:
                                pass


    # Utilities
    def call(self, command):
        command = command.format(**self.env)
        self.log.info('Running "{0}"'.format(command))

        with higher_log_indent():
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )

            for line in proc.stdout:
                self.log.debug(line.decode('utf-8').strip(u'\n'))

    def make_dirs(self, *dirs):
        """Makes dirs inside the prefix.

        Use this command inside your `install` method.
        """
        for d in dirs:
            fullname = os.path.join(self.env['prefix'], d)
            if not os.path.exists(fullname):
                os.makedirs(fullname)

    def create_file(self, filename, content):
        """Creates a file inside 'prefix'.

        Use this command inside your `install` method.
        Note: Source directory should exists.
        Warning: if there is some file already, it will be overwritten.
        """
        with open(os.path.join(self.env['prefix'], filename), 'w') as f:
            f.write(content)

