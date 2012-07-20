class Less(Schema):
    version = '1.3.0'
    homepage = 'http://lesscss.org/'
    deps = ['npm']

    def install(self):
        self.call('cd "{prefix}" && npm install less@{version}')
        self.call('ln -s "{prefix}/node_modules/less/bin" "{prefix}/bin"')


