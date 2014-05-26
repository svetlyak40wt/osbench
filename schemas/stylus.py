class Stylus(Schema):
    version = '0.29.0'
    homepage = 'http://learnboost.github.com/stylus/'
    deps = ['npm']

    def install(self):
        self.call('cd "{prefix}" && npm install stylus@{version}')
        self.call('ln -s "{prefix}/node_modules/stylus/bin" "{prefix}/bin"')


