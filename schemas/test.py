class Test(Schema):
    url = None
    homepage = 'http://example.com/'

    def install(self):
        self.make_dirs('bin')
        self.create_file(
            'bin/hello-world.sh',
            'echo "Hello World!"'
        )

