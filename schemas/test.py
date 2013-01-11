class Test(Schema):
    url = None
    homepage = 'http://example.com/'

    def install(self):
        self.makedirs('bin')
        self.create_file_with_content(
            'bin/python',
            'Test project python interpreter'
        )
        self.create_file_with_content(
            'bin/hello-world.sh',
            'echo "Hello World!"'
        )

