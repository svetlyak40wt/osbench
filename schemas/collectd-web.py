class Collectd(Schema):
    url = 'https://github.com/downloads/httpdss/collectd-web/collectd-web_0.4.0.tar.gz'
    homepage = 'http://collectdweb.appspot.com/'
    deps = ['system.libhtml-parser-perl', 'system.libjson-perl', 'system.librrds-perl']

    patch_which_fixes_paths = 'patches/collectd-web-paths.diff'

    def install(self):
        self.call('mkdir bin')
        self.call('mv runserver.py bin/collectd-web')
        self.call('cp -r * "{prefix}"')

        self.makedirs(
            'etc/collectd',
        )

        self.copy_file('{schema_dir}/configs/etc/collectd/collection.conf', 'etc/collectd/collection.conf')
