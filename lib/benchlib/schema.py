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
            env['diy_prefix'],
            'workbench',
            '%s-%s' % (env['schema'], version)
        )

    def _get_source(self):
        subprocess.call('wget "{0}"'.format(self.url), shell=True)
        files = os.listdir('.')
        assert len(files) == 1

        subprocess.call('tar -jxvf "{0}"'.format(files[0]), shell=True)
        os.unlink(files[0])

        dirs = os.listdir('.')
        assert len(dirs) == 1

        os.chdir(dirs[0])

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
            shell = os.environ['SHELL']
            subprocess.call(shell)

            self._get_source()

            if interactive:
                shell = os.environ['SHELL']
                subprocess.call(shell, shell=True)
            else:
                self.install()

            self._symlink()

        finally:
            subprocess.call('rm -fr "{0}"'.format(root), shell=True)

    def _symlink(self):
        for dir_name in ['bin', 'sbin', 'etc', 'lib', 'include']:
            s_dir = os.path.join(self.env['prefix'], dir_name)
            t_dir = os.path.join(self.env['diy_prefix'], dir_name)
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


