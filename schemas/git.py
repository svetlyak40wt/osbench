class Git(Schema):
    url = 'https://www.kernel.org/pub/software/scm/git/git-2.2.0.tar.gz'
    homepage = 'http://git-scm.com/'
    deps = ['system.tcl8.5', 'system.gettext']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')
