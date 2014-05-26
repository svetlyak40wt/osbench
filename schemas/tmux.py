class Tmux(Schema):
    url = 'http://downloads.sourceforge.net/project/tmux/tmux/tmux-1.9/tmux-1.9a.tar.gz?use_mirror=citylan'
    homepage = 'http://tmux.sourceforge.net/'
    deps = ['system.libevent-dev', 'system.libncurses5-dev', 'system.make']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

