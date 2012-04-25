from logbook import StringFormatter, Processor


class IndentFormatter(StringFormatter):
    def format_record(self, record, handler):
        result = super(IndentFormatter, self).format_record(record, handler)
        indent = record.extra.get('indent', 0)
        return u'  ' * indent + result


def higher_log_indent():
    def inject_indent(record):
        record.extra['indent'] = record.extra.get('indent', 0) + 1
    return Processor(inject_indent)

