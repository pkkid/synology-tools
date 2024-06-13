#!/usr/bin/env python
import argparse, hashlib, json, os
import supernotelib
from supernotelib.converter import PdfConverter

SOURCE = '/volume1/Synology/Supernote/Note'
DEST = '/volume1/homes/pkkid/Sync/Notes/Supernote'
CACHE = __file__.replace('.py', '.cache')


def md5hash(filepath):
    """ Return md5 hash of the file. """
    with open(filepath, 'rb') as handle:
        return hashlib.md5(handle.read()).hexdigest()

def read_cache(filepath):
    """ Read the cache file. """
    print(f'Reaching cache {filepath}')
    if not os.path.exists(filepath):
        return {}
    with open(filepath, 'r') as handle:
        return json.load(handle)

def save_cache(filepath, cache):
    """ Read the cache file. """
    print(f'Saving cache {filepath}')
    with open(filepath, 'w') as handle:
        json.dump(cache, handle, indent=2)

def iter_notes(source):
    """ Recursively find all .note files. """
    for root, dirs, files in os.walk(source):
        for file in files:
            if file.endswith('.note'):
                yield os.path.join(root, file)

def convert_note(notepath, source, dest):
    """ Convert a .note file to a PDF. """
    print(f'Reading note {notepath}')
    note = supernotelib.load_notebook(notepath, policy='strict')
    converter = PdfConverter(note, palette=None)
    data = converter.convert(-1, vectorize=False, enable_link=True)
    if data is None:
        print(f'No data for note {notepath}')
        return None
    pdfpath = notepath.replace(source, dest).replace('.note', '.pdf')
    print(f'Saving pdf {pdfpath}')
    os.makedirs(os.path.dirname(pdfpath), exist_ok=True)
    with open(pdfpath, 'wb') as handle:
        handle.write(data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create PDFs from Supernotes')
    parser.add_argument('--source', type=str, default=SOURCE, help='Source directory')
    parser.add_argument('--dest', type=str, default=DEST, help='Destination directory')
    parser.add_argument('--cachepath', type=str, default=CACHE, help='Filepath to save md5 hashes')
    opts = parser.parse_args()
    cache = read_cache(opts.cachepath)
    for notepath in iter_notes(opts.source):
        notehash = md5hash(notepath)
        if notehash != cache.get(notepath):
            convert_note(notepath, opts.source, opts.dest)
            cache[notepath] = notehash
            save_cache(opts.cachepath, cache)
