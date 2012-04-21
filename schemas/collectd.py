class Collectd(Schema):
    url = 'http://collectd.org/files/collectd-5.0.2.tar.bz2'
    homepage = 'http://collectd.org/'
    deps = ['wget', 'bzip2']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

    patch_which_adds_initscript = 'patches/collectd-add-init-script.diff'

