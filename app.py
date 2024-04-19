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
def list_folders(subpath=""):
    # folders = []
    relative_path = safe_join(DIRECTORY_PATH, subpath)
    entries = {'files': [], 'directories': []}
    # 遍历目录，添加文件和目录到列表
    for entry in os.listdir(relative_path):
        path = os.path.join(relative_path, entry)
        if os.path.isfile(path):
            entries['files'].append(os.path.join(DIRECTORY_PATH, subpath, entry))
        elif os.path.isdir(path):
            entries['directories'].append(os.path.join(DIRECTORY_PATH, subpath, entry))
            
    # for name in os.listdir(DIRECTORY_PATH):
    #     if os.path.isdir(os.path.join(DIRECTORY_PATH, name)):
    #         folders.append(name)
    return render_template('folders.html', folders=entries['directories'], files=entries['files'])

@app.route('/<path:subpath>')
def show_subfolder(subpath):
    # 安全性检查
    safe_path = subpath
    print(safe_path)
    if not os.path.abspath(safe_path).startswith(os.path.abspath(DIRECTORY_PATH)):
        abort(403)  # 禁止访问
    if os.path.isdir(safe_path):
        relative_path = subpath
        entries = {'files': [], 'directories': []}
        # 遍历目录，添加文件和目录到列表
        for entry in os.listdir(relative_path):
            path = os.path.join(relative_path, entry)
            if os.path.isfile(path):
                entries['files'].append(os.path.join(relative_path, entry))
            elif os.path.isdir(path):
                entries['directories'].append(os.path.join(relative_path, entry))
        return render_template('folders.html', folders=entries['directories'], files=entries['files'])
    abort(404)  # 目录不存在

@app.route('/files', methods=['GET'])
def list_files_and_directories():
    # 确保只有合法路径被访问
    if not os.path.exists(DIRECTORY_PATH):
        return "Directory not found.", 404

    entries = {'files': [], 'directories': []}
    # 遍历目录，添加文件和目录到列表
    for entry in os.listdir(DIRECTORY_PATH):
        path = os.path.join(DIRECTORY_PATH, entry)
        if os.path.isfile(path):
            entries['files'].append(entry)
        elif os.path.isdir(path):
            entries['directories'].append(entry)

    # 返回文件和目录列表的JSON
    return jsonify(entries)

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
        
        # 创建 zip 文件的路径
        # zip_path = os.path.join(DIRECTORY_PATH, f"{subpath}.zip")
        
        # # 打包文件夹
        # shutil.make_archive(base_name=subpath, format='zip', base_dir=os.path.join(DIRECTORY_PATH, subpath))
        
        # # 确保请求后清理文件
        # @after_this_request
        # def cleanup(response):
        #     try:
        #         os.remove(zip_path)
        #     except Exception as error:
        #         app.logger.error("Error removing or closing downloaded zip file handle", error)
        #     return response
        
        # # 发送文件给客户端
        # return send_file(zip_path)

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
        # print(safe_path)
        # print(os.path.abspath(DIRECTORY_PATH))
        if not os.path.abspath(safe_path).startswith(os.path.abspath(DIRECTORY_PATH)):
            abort(403)  # 禁止访问

        if os.path.isfile(safe_path):
            return send_from_directory(directory=os.path.dirname(safe_path), path=os.path.basename(subpath), as_attachment=True)
        abort(404)

if __name__ == '__main__':
    app.run(debug=True)
