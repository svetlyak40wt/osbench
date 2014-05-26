class GitExtras(Schema):
    url = 'git://github.com/visionmedia/git-extras.git'
    homepage = 'https://github.com/visionmedia/git-extras'
    deps = ['git']
    patch_which_fixes_paths = 'patches/git-extras-fix-bashcompletion-path.diff'

    def install(self):
        self.call('make install PREFIX={prefix}')
