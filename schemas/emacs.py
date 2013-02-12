class Git(Schema):
    url = 'http://ftp.gnu.org/pub/gnu/emacs/emacs-24.2.tar.gz'
    homepage = 'http://www.gnu.org/software/emacs/'
    deps = ['system.libncurses5-dev']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')
