"""
Generate site from static pages, loosely inspired by Jekyll.
Usage: ./generate.py [-v] source_path output_path
Options:
    -v, --verbose: enable verbose mode
"""

import os
import logging
import json

from optparse import OptionParser
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
# clint is a module filled with a set of tools for developing commandline applications.
from clint.textui.colored import red, yellow

logging.basicConfig()
log = logging.getLogger(__file__)

"""
Return a generator with .rst files from a folder path.
"""
def list_files(folder_path):
    for name in os.listdir(folder_path):
        base, ext = os.path.splitext(name)
        if ext != '.rst':
            continue
        yield os.path.join(folder_path, name)

"""
Read file and return metadata and file content.
"""
def read_file(file_path):
    with open(file_path, "rb") as f:
        # read metadata and content
        raw_metadata = ""
        for line in f:
            if line.strip() == '---':
                break
            raw_metadata += line
        content = ""
        for line in f:
            content += line

        # make sure metadata can be decoded
        try:
            metadata = json.loads(raw_metadata)
        except ValueError:
            log.warn(yellow("Metadata for %r is not json valid" % file_path))
            metadata = {}

    return metadata, content

"""
Write generated template to file.
"""
def write_output(path, html):
    with open(path, "w") as f:
        f.write(html)
"""
Get the template and reder it.
"""
def render_template(jinja_env, template_name, metadata, content):
   # get the template and render it
    template = jinja_env.get_template(template_name)
    # create context data for template
    data = dict(metadata, content=content)
    return template.render(**data)

"""
Return file name with new path and .html extension.
"""
def get_output_filename(file_path, output_path):
    filename = os.path.splitext(os.path.basename(file_path))[0]
    return os.path.join(output_path, "%s.html" % filename)

"""
Generate static files from .rst templates
"""
def generate_site(source_path, output_path):
    log.info("Generating site from %r", source_path)
    # set enviroment for jinja
    jinja_template_path = os.path.join(source_path, "layout")
    jinja_env = Environment(loader=FileSystemLoader(jinja_template_path))

    for file_path in list_files(source_path):
        metadata, content = read_file(file_path)
        template_name = metadata.get("layout", "")

        try:
            html = render_template(jinja_env, template_name, metadata, content)
        except TemplateNotFound:
            log.error(red("Template %r not found" % template_name))
            continue

        output_filename = get_output_filename(file_path, output_path)
        write_output(output_filename, html)
        log.info("Writing %r with template %r", output_filename, template_name)

    log.info("Finished generating site")

def main():
    # parse list of command line arguments.
    parser = OptionParser(usage="usage: %prog [-v] source_path outpup_path", version="%prog 2.0")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose")
    (options, args) = parser.parse_args()

    # validate command line options and arguments
    not_valid_dir_message = "%r is not a valid directory."

    if len(args) != 2:
        parser.error(red("Incorrect number of arguments"))
    if not os.path.isdir(args[0]):
        parser.error(red(not_valid_dir_message % args[0]))
    if not os.path.isdir(args[1]):
        parser.error(red(not_valid_dir_message % args[1]))

    # enable log.info
    if options.verbose:
        log.setLevel(logging.DEBUG)

    generate_site(source_path=args[0], output_path=args[1])

if __name__ == "__main__":
    main()
