import os
import sys
import logging

from opster import command
from benchlib.schema import Schema

__all__ = ['install', 'uninstall', 'Bench']

class Bench(object):
    def __init__(self, osbench_root=None, loglevel='info'):
        if osbench_root is None:
            osbench_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.osbench_root = osbench_root

        logging.basicConfig(
            format='%(message)s',
            level=getattr(logging, loglevel.upper()),
        )

    def _load_schema(self, schema_name):
        schema = None

        schemas = os.path.join(self.osbench_root, 'schemas')

        if sys.path[0] != schemas:
            filename = os.path.join(schemas, schema_name + '.py')
            code = compile(open(filename).read(), filename, 'exec')

            locals = {}
            eval(code, globals(), locals)

            schemas = [schema for schema in locals.values() if isinstance(schema, type) and issubclass(schema, Schema)]
            assert len(schemas) == 1

            env = dict(
                osbench_root=self.osbench_root,
                schema=schema_name,
                schema_filename=filename,
            )
            schema = schemas[0](env)

        return schema

    def install(self, schema_name, interactive=False):
        schema = self._load_schema(schema_name)
        schema._install(interactive=interactive)
        return schema

    def uninstall(self, schema_name, interactive=False):
        schema = self._load_schema(schema_name)
        schema._uninstall()
        return schema


@command()
def install(
        bench,
        schema_name,
        interactive=('i', False, 'drop into the shell when source will be ready'),
    ):
    bench.install(schema_name, interactive=interactive)


@command()
def uninstall(bench, schema_name):
    bench.uninstall(schema_name)


