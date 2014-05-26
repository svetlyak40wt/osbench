class Collectd(Schema):
    url = 'http://collectd.org/files/collectd-5.4.1.tar.bz2'
    homepage = 'http://collectd.org/'
    deps = ['system.wget', 'system.bzip2', 'system.librrd-dev']

    patch_which_adds_initscript = 'patches/collectd-add-init-script.diff'

    def install(self):
        self.call('./configure --prefix={prefix} --localstatedir={osbench_root}/var')
        self.call('make')
        self.call('make install')

