class CoffeeScript(Schema):
    version = '1.3.3'
    homepage = 'http://coffeescript.org/'
    deps = ['npm']

    def install(self):
        self.call('cd "{prefix}" && npm install coffee-script@{version}')
        self.call('ln -s "{prefix}/node_modules/coffee-script/bin" "{prefix}/bin"')

