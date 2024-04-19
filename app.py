from flask import Flask, send_from_directory, render_template, abort, jsonify, after_this_request, send_file
import os
import shutil
import tempfile
from threading import Lock
from werkzeug.utils import secure_filename, safe_join

app = Flask(__name__)
lock = Lock()
DIRECTORY_PATH = './.git/'

@app.route('/')
@app.route('/<path:subpath>')
def list_folders(subpath=""):
    # 将 subpath 与基目录安全结合
    try:
        relative_path = safe_join(DIRECTORY_PATH, subpath)
    except ValueError:
        abort(404)  # 如果路径不合法，则返回404

    print(relative_path)
    print(subpath)
    # 检查生成的路径是否在目标目录之下
    if not os.path.abspath(relative_path).startswith(os.path.abspath(DIRECTORY_PATH)):
        abort(403)  # 如果尝试访问基目录外的文件，则禁止访问

    if not os.path.isdir(relative_path):
        abort(404)  # 如果目录不存在，返回404
    
    entries = {'files': [], 'directories': []}
    # 遍历目录，添加文件和目录到列表
    for entry in os.listdir(relative_path):
        path = safe_join(relative_path, entry)
        print(path)
        if os.path.isfile(path):
            entries['files'].append(safe_join(subpath, entry))
        elif os.path.isdir(path):
            entries['directories'].append(safe_join(subpath, entry))

    return render_template('folders.html', folders=entries['directories'], files=entries['files'])

@app.route('/package/<path:subpath>', methods=['GET'])
def package_folder(subpath):
    with lock:
        safe_path = safe_join(DIRECTORY_PATH, subpath)
        if not os.path.abspath(safe_path).startswith(os.path.abspath(DIRECTORY_PATH)):
            abort(403)  # 禁止访问
        print(safe_path)
        
        # 检查文件夹是否存在
        if not os.path.isdir(safe_path):
            return "Folder not found.", 404

        with tempfile.TemporaryDirectory() as tmpdirname:
            # 创建 zip 文件的路径
            zip_path = os.path.join(tmpdirname, f"{os.path.basename(subpath)}.zip")
            
            # 打包文件夹
            shutil.make_archive(base_name=os.path.splitext(zip_path)[0], format='zip', base_dir=safe_path)
            
            # 发送文件给客户端
            return send_file(zip_path, as_attachment=True)


@app.route('/download/<path:subpath>')
def download_file(subpath):
    with lock:
        safe_path = safe_join(DIRECTORY_PATH, subpath)
        print(safe_path)
        # print(os.path.abspath(DIRECTORY_PATH))
        if not os.path.abspath(safe_path).startswith(os.path.abspath(DIRECTORY_PATH)):
            abort(403)  # 禁止访问

        if os.path.isfile(safe_path):
            return send_from_directory(directory=os.path.dirname(safe_path), path=os.path.basename(subpath), as_attachment=True)
        abort(404)

if __name__ == '__main__':
    app.run(debug=False)
