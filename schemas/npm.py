class Npm(Schema):
    url = 'http://registry.npmjs.org/npm/-/npm-1.1.44.tgz'
    homepage = 'http://npmjs.org/'

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

