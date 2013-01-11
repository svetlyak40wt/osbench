class NodeJS(Schema):
    url = 'http://nodejs.org/dist/v0.8.3/node-v0.8.3.tar.gz'
    homepage = 'http://nodejs.org/'

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

