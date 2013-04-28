class Emacs(Schema):
    url = 'http://ftp.gnu.org/pub/gnu/emacs/emacs-24.2.tar.gz'
    homepage = 'http://www.gnu.org/software/emacs/'
    deps = ['system.libncurses5-dev', 'system.make']

    def install(self):
        self.call('./configure --prefix={prefix} '
                  '--with-xpm=no --with-gif=no --with-tiff=no')
        self.call('make')
        self.call('make install')
