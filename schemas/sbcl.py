class Emacs(Schema):
    url = 'http://downloads.sourceforge.net/project/sbcl/sbcl/1.1.5/sbcl-1.1.5-source.tar.bz2'
    homepage = 'http://sbcl.org'
    deps = ['system.clisp', 'system.make']

    def install(self):
        self.call('sh make.sh "clisp"')
        self.call('INSTALL_ROOT={prefix} sh install.sh')
