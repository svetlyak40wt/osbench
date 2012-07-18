class Tmux(Schema):
    url = 'http://downloads.sourceforge.net/project/tmux/tmux/tmux-1.6/tmux-1.6.tar.gz?r=&ts=1342618675&use_mirror=citylan'
    homepage = 'http://tmux.sourceforge.net/'
    deps = ['system.libevent-dev', 'system.libncurses5-dev']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

