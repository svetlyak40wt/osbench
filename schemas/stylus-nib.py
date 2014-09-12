class StylusNib(Schema):
    version = '0.8.1'
    homepage = 'https://github.com/visionmedia/nib'
    deps = ['npm']

    def install(self):
        self.call('cd "{prefix}" && npm install nib@{version}')
        self.call('ln -s "{prefix}/node_modules/nib/bin" "{prefix}/bin"')


