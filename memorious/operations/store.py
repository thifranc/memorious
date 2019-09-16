import mimetypes
import os
import json
import shutil
from normality import safe_filename

from memorious import settings


def _get_directory_path(context):
    """Get the storage path fro the output."""
    path = os.path.join(settings.BASE_PATH, 'store')
    path = context.params.get('path', path)
    path = os.path.join(path, context.crawler.name)
    path = os.path.abspath(os.path.expandvars(path))
    try:
        os.makedirs(path)
    except Exception:
        pass
    return path


def directory(context, data):
    """Store the collected files to a given directory."""
    with context.http.rehash(data) as result:
        if not result.ok:
            return

        content_hash = data.get('content_hash')
        if content_hash is None:
            context.emit_warning("No content hash in data.")
            return

        path = _get_directory_path(context)
        file_name = data.get('file_name', result.file_name)
        dft_name = 'raw'
        if file_name is None:
            # try to guess at least the file extension ;
            # if no extension can be guessed, file_name will
            # still be None and dft_name still 'raw'
            mime_type = data['headers']['Content-Type']
            ext_name = mimetypes.guess_extension(mime_type)
            if ext_name is not None:
                dft_name = ext_name
        file_name = safe_filename(file_name, default=dft_name)
        file_name = '%s.%s' % (content_hash, file_name)
        data['_file_name'] = file_name
        file_path = os.path.join(path, file_name)
        if not os.path.exists(file_path):
            shutil.copyfile(result.file_path, file_path)

        context.log.info("Store [directory]: %s", file_name)

        meta_path = os.path.join(path, '%s.json' % content_hash)
        with open(meta_path, 'w') as fh:
            json.dump(data, fh)
