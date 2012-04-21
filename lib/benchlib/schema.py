import re
import subprocess
import tempfile
import os

class Schema(object):
    url = None
    homepage = None
    deps = []

    def __init__(self, env):
        self.env = env.copy()
        version = re.search(r'(\d+\.\d+\.\d+)', self.url).group(1)
        self.env['prefix'] = os.path.join(
            env['osbench_root'],
            'workbench',
            '%s-%s' % (env['schema'], version)
        )

    def _get_source(self):
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
            print 'installing dependencies'
            for dep in self.deps:
                self.call('sudo apt-get install %s' % dep)

    def _install(self, interactive=False):
        print 'base install'

        self._install_deps()

        root = tempfile.mkdtemp(prefix='diy-')
        try:
            os.chdir(root)

            self._get_source()

            if interactive:
                shell = os.environ['SHELL']
                self.call('git init')
                self.call('git add -A')
                self.call(shell)
            else:
                self.install()

            self._symlink()

        finally:
            self.call('rm -fr "{0}"'.format(root))

    def _symlink(self):
        for dir_name in ['bin', 'sbin', 'etc', 'lib', 'include']:
            s_dir = os.path.join(self.env['prefix'], dir_name)
            t_dir = os.path.join(self.env['osbench_root'], dir_name)
            if os.path.exists(s_dir):
                if not os.path.exists(t_dir):
                    os.makedirs(t_dir)

                for filename in os.listdir(s_dir):
                    source = os.path.join(s_dir, filename)
                    target = os.path.join(t_dir, filename)

                    if os.path.exists(target):
                        os.unlink(target)

                    os.symlink(source, target)

    def call(self, command):
        subprocess.call(command.format(**self.env), shell=True)


