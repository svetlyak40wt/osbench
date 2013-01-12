import os.path
import tempfile
import shutil

from benchlib.schema import Schema
from unittest import TestCase

TEMP_DIR = None


class Test(Schema):
    url = None
    homepage = 'http://example.com/'

    def install(self):
        self.makedirs('bin')
        self.create_file_with_content(
            'bin/hello-world.sh',
            'echo "Hello World!"'
        )


class TestSchemaWithPython(Schema):
    name = 'test-python'
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


# TESTS

class TestInstallationProcess(TestCase):
    def setUp(self):
        self.TEMP_DIR = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.TEMP_DIR)
        del self.TEMP_DIR

    def create_bench(self):
        from benchlib.commands import Bench
        return Bench(osbench_root=self.TEMP_DIR)

    def test_install(self):
        bench = self.create_bench()

        bench.install(Test)

        filename = os.path.join(bench.osbench_root, 'bin', 'hello-world.sh')
        assert os.path.exists(filename)
        assert open(filename).read() == 'echo "Hello World!"'


    def test_uninstall(self):
        bench = self.create_bench()

        bench.install(Test)
        schema = bench.uninstall(Test)

        linkname = os.path.join(bench.osbench_root, 'bin', 'hello-world.sh')
        filename = os.path.join(schema.env['prefix'], 'bin', 'hello-world.sh')

        assert not os.path.exists(linkname)
        assert not os.path.exists(filename)


    def test_unlink_does_not_destory_files_which_are_not_link_back_to_workbench(self):
        bench = self.create_bench()

        # there is already python in the bin directory
        os.makedirs(os.path.join(bench.osbench_root, 'bin'))
        with open(os.path.join(bench.osbench_root, 'bin', 'python'), 'w') as f:
            f.write('System python')

        schema = bench.load_schema(TestSchemaWithPython)
        bench.install(schema)

        files = schema.get_files_to_unlink()
        for ftype, name in files:
            assert 'python' not in name, 'There is "python" in ' + name

