class Git(Schema):
    url = 'http://git-core.googlecode.com/files/git-1.7.10.2.tar.gz'
    homepage = 'http://git-scm.com/'

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

