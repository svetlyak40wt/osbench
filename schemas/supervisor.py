class Supervisor(PythonSchema):
    url = 'supervisor==3.0a12'
    homepage = 'http://supervisord.org/'

    def install(self):
        self.make_dirs(
            'etc/init.d',
            'etc/supervisor.d',
            'var/run',
            'var/log',
        )
        self.copy_file('{schema_dir}/configs/etc/init.d/supervisor', 'etc/init.d/supervisor', mode=755)
        self.copy_file('{schema_dir}/configs/etc/supervisord.conf', 'etc/supervisord.conf')

