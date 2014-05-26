import os
import sys

from opster import command
from benchlib.schema import Schema, PythonSchema
from benchlib.exceptions import BadExitCode

__all__ = ['install', 'uninstall', 'Bench']


class Bench(object):
    def __init__(self, osbench_root=None):
        if osbench_root is None:
            osbench_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.osbench_root = osbench_root

    def load_schema(self, schema_name_or_cls):
        schema_cls = None

        if isinstance(schema_name_or_cls, basestring):
            schema_name = schema_name_or_cls
            schemas_dir = os.path.join(self.osbench_root, 'schemas')

            if sys.path[0] != schemas_dir:
                filename = os.path.join(schemas_dir, schema_name + '.py')
                code = compile(open(filename).read(), filename, 'exec')

                locals = {}
                eval(code, globals(), locals)

                schemas = [schema for schema in locals.values() if isinstance(schema, type) and issubclass(schema, Schema)]
                assert len(schemas) == 1
                schema_cls = schemas[0]
        else:
            schema_cls = schema_name_or_cls
            schema_name = getattr(
                schema_cls,
                'name',
                schema_cls.__name__.lower()
            )
            filename = __import__(schema_cls.__module__).__file__
            schemas_dir = os.path.dirname(filename)

        if schema_cls is not None:
            env = dict(
                osbench_root=self.osbench_root,
                schema=schema_name,
                schema_filename=filename,
                schema_dir=schemas_dir,
            )
            return schema_cls(env)

        raise RuntimeError('Schema {0} not found'.format(schema_name_or_cls))

    def get_schema(self, schema):
        if not isinstance(schema, Schema):
            schema = self.load_schema(schema)
        return schema

    def install(self, schema, interactive=False):
        schema = self.get_schema(schema)
        schema._install(interactive=interactive)
        return schema

    def uninstall(self, schema, interactive=False):
        schema = self.get_schema(schema)
        schema._uninstall()
        return schema


@command()
def install(
        bench,
        schema_name,
        interactive=('i', False, 'drop into the shell when source will be ready'),
    ):
    try:
        bench.install(schema_name, interactive=interactive)
    except BadExitCode:
        return 1


@command()
def uninstall(bench, schema_name):
    try:
        bench.uninstall(schema_name)
    except BadExitCode:
        return 1


@command()
def show(
        bench,
        schema_name,
    ):
    schema = bench.get_schema(schema_name)
    print 'Name:', schema_name
    print 'Installed:', schema.is_installed()

