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

    # there is already python in the bin directory
    python_filename = os.path.join(bench.osbench_root, 'bin', 'python')
    # with open(python_filename, 'w') as f:
    #     f.write('OSBench\'s python')

    bench.install('test')

    schema = bench.uninstall('test')

    linkname = os.path.join(bench.osbench_root, 'bin', 'hello-world.sh')
    filename = os.path.join(schema.env['prefix'], 'bin', 'hello-world.sh')

    assert not os.path.exists(linkname)
    assert not os.path.exists(filename)
    assert os.path.exists(python_filename)

    with open(python_filename, 'w') as f:
        assert f.readline() == 'OSBench\'s python'
