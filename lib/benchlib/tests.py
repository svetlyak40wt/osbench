import os.path

from benchlib.commands import Bench


def test_install():
    bench = Bench()

    bench.install('test')

    filename = os.path.join(bench.osbench_root, 'bin', 'hello-world.sh')
    assert os.path.exists(filename)
    assert open(filename).read() == 'echo "Hello World!"'


def test_uninstall():
    bench = Bench()

    bench.install('test')
    schema = bench.uninstall('test')

    linkname = os.path.join(bench.osbench_root, 'bin', 'hello-world.sh')
    filename = os.path.join(schema.env['prefix'], 'bin', 'hello-world.sh')

    assert not os.path.exists(linkname)
    assert not os.path.exists(filename)
