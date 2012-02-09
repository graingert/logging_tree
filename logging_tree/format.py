"""Routines that pretty-print a hierarchy of logging `Node` objects."""

import logging


def printout(node=None):
    """Print the tree of `Node` tuples whose root is `node`.

    If no `node` is provided, the entire tree of loggers is printed out.

    """
    if node is None:
        from logging_tree.nodes import tree
        node = tree()
    _printout(node)


def _printout(node, prefix='', is_last=True):
    logger = node.logger
    is_placeholder = isinstance(logger, logging.PlaceHolder)
    name = ('[%s]' if is_placeholder else '"%s"') % node.name
    if prefix:
        print prefix + '|'
        arrow = '<--' if (is_placeholder or logger.propagate) else '   '
        print prefix + 'o' + arrow + name
    else:
        print '    ' + name
    prefix += ('    ' if is_last else '|   ')
    if not is_placeholder:
        facts = []
        if logger.level:
            facts.append('Level ' + logging.getLevelName(logger.level))
        if not logger.propagate:
            facts.append('Propagate OFF')

        # getattr() protects us against crazy homemade filters and
        # handlers that might not have the attributes of normal ones:

        for f in getattr(logger, 'filters', ()):
            facts.append('Filter %s' % describe_filter(f))
        for h in getattr(logger, 'handlers', ()):
            facts.append('Handler %s' % describe_handler(h))
            for f in getattr(h, 'filters', ()):
                facts.append('  Filter %s' % describe_filter(f))

        for fact in facts:
            print prefix + fact

    if node.children:
        last_child = node.children[-1]
        for child in node.children:
            _printout(child, prefix, child is last_child)


# It is important that the 'if' statements in the "describe" functions
# below use `type(x) == Y` conditions instead of calling `isinstance()`,
# since a Filter or Handler subclass might implement arbitrary behaviors
# quite different from those of its superclass.

def describe_filter(f):
    """Return text describing the logging filter `f`."""
    if type(f) is logging.Filter:
        return 'name=%r' % f.name
    return repr(f)


def describe_handler(h):
    """Return text describing the logging handler `h`."""
    if type(h) is logging.StreamHandler:
        return 'Stream %r' % h.stream
    if type(h) is logging.FileHandler:
        return 'File %r' % h.baseFilename
    # TODO: add further cases here.
    return repr(h)
