class Collectd(Schema):
    url = 'http://collectd.org/files/collectd-5.0.2.tar.bz2'
    homepage = 'http://collectd.org/'
    deps = ['wget', 'bzip2']

    def install(self):
        self.call('./configure --prefix={prefix}')
        self.call('make')
        self.call('make install')

    patch_which_adds_a_blah = """
diff --git a/Makefile.am b/Makefile.am
index 9e3feac..a046a31 100644
--- a/Makefile.am
+++ b/Makefile.am
@@ -1,6 +1,7 @@
 ACLOCAL_AMFLAGS = -I libltdl/m4
 
 SUBDIRS = libltdl src bindings
+# BLAH
 
 INCLUDES = $(LTDLINCL)
"""

