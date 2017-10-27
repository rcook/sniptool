#!/usr/bin/env python
##################################################
# Copyright (C) 2017, All rights reserved.
##################################################

from __future__ import print_function
import argparse
import inflection
import jinja2
import jinja2.meta
import os
import pyperclip
import sys

from pyprelude.file_system import make_path

def _set_clipboard_text(s):
    pyperclip.copy(s)

def _has_prefix(s, prefix):
    return s[len(prefix) : ] if s.startswith(prefix) else None

def _has_suffix(s, suffix):
    return s[: -len(suffix)] if s.endswith(suffix) else None

def _read_source(path):
    with open(path, "rt") as f:
        return f.read()

def _read_metadata(source):
    metadata = {}
    defaults = {}
    for line in source.splitlines():
        line = _has_prefix(line, "{#")
        if not line: continue
        line = _has_suffix(line, "#}")
        if not line: continue
        line = line.strip(" -")
        line = _has_prefix(line, ".")
        if not line: continue
        index = line.find(":")
        if not index: continue

        key = line[0 : index].strip()
        value = line[index + 1:].strip()

        t = _has_prefix(key, "default(")
        if t is not None:
            default_key = _has_suffix(t, ")").strip()
            if default_key is not None:
                defaults[default_key] = value
                continue

        metadata[key] = value

    return metadata, defaults

def _prompt(env, source, defaults):
    template = env.parse(source)
    values = {}
    for key in sorted(jinja2.meta.find_undeclared_variables(template)):
        default_value = defaults.get(key, None)
        if default_value is None:
            value = raw_input("Enter value for \"{}\": ".format(key))
            values[key] = value
        else:
            value = raw_input("Enter value for \"{}\" (default: \"{}\"): ".format(key, default_value))
            values[key] = default_value if len(value) == 0 else value

    return values

def _show_metadata(path, metadata, defaults, indent=0):
    prefix = "  " * indent
    print("{}Path: {}".format(prefix, path))
    print("{}Name: {}".format(prefix, metadata.get("name", "(unnamed)")))
    print("{}Description: {}".format(prefix, metadata.get("description", "(no description)")))
    if len(defaults) > 0:
        print("{}Defaults:".format(prefix))
        for key, value in defaults.iteritems():
            print("{}  {}={}".format(prefix, key, value))

def _do_gen(args):
    filters = jinja2.filters.FILTERS.copy()
    filters.update({
        "encode_cpp_literal" : lambda s: "\"" + s.replace("\\", "\\\\") + "\"", # TODO: Implement full set of C++ literal encoding rules
        "pluralize": inflection.pluralize
    })
    env = jinja2.Environment(undefined=jinja2.StrictUndefined)
    env.filters = filters
    path = make_path(args.template_dir, args.template_name)
    source = _read_source(path)
    metadata, defaults = _read_metadata(source)

    print("Template: {}".format(args.template_name))
    _show_metadata(path, metadata, defaults, 1)
    values = _prompt(env, source, defaults)
    output = env.from_string(source, values).render()
    print("==========")
    print(output)
    print("==========")
    _set_clipboard_text(output)
    print("Text sent to clipboard")

def _do_list(args):
    for p in os.listdir(args.template_dir):
        print("Template: {}".format(p))
        path = make_path(args.template_dir, p)
        source = _read_source(path)
        metadata, defaults = _read_metadata(source)
        _show_metadata(path, metadata, defaults, 1)
        print()

def _main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="sniptool")
    parser.add_argument(
        "--template-dir",
        "-t",
        default=make_path(__name__, "..", "_snippets"),
        help="Template directory")
    subparsers = parser.add_subparsers(help="subcommand help")

    gen_parser = subparsers.add_parser("gen", help="Generate code snippet")
    gen_parser.set_defaults(func=_do_gen)
    gen_parser.add_argument(
        "template_name",
        help="Template name")

    list_parser = subparsers.add_parser("list", help="List available templates")
    list_parser.set_defaults(func=_do_list)

    args = parser.parse_args(argv)
    args.func(args)

if __name__ == "__main__":
    _main()
