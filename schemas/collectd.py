class Collectd(Schema):
    url = 'http://collectd.org/files/collectd-5.0.2.tar.bz2'
    homepage = 'http://collectd.org/'

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')
