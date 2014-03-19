class Circus(PythonSchema):
    url = 'circus==0.10.0'
    homepage = 'http://circus.readthedocs.org/'

    def install(self):
        self.makedirs(
            'etc/init.d',
            'etc/circus.d',
            'var/run',
            'var/log',
        )
        self.copy_file('{schema_dir}/configs/etc/init.d/circus', 'etc/init.d/circus', mode=755)
        self.copy_file('{schema_dir}/configs/etc/circus.conf', 'etc/circus.conf')

