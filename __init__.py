#!/usr/bin/env python3

import os
import shutil
import subprocess
import paramiko


def sync_files(obsidian_folder, jekyll_posts_folder):
    # 清空jekyll的posts文件夹
    for filename in os.listdir(jekyll_posts_folder):
        file_path = os.path.join(jekyll_posts_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    # 将obsidian文件夹中的内容同步到jekyll的posts文件夹
    for item in os.listdir(obsidian_folder):
        s = os.path.join(obsidian_folder, item)
        d = os.path.join(jekyll_posts_folder, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, False, None)
        else:
            shutil.copy2(s, d)


def build_jekyll_site(jekyll_folder):
    try:
        # 使用指定的环境变量和命令构建 Jekyll 站点
        result = subprocess.run(
            ['bundle', 'exec', 'jekyll', 'build'],
            cwd=jekyll_folder,
            env={**os.environ, 'JEKYLL_ENV': 'production'},
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Jekyll site built successfully.")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error during Jekyll build: {e}")
        print(e.stdout)
        print(e.stderr)


def upload_site_to_server(
    local_site_folder, remote_folder, server_ip, username, password
):
    transport = paramiko.Transport((server_ip, 22))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)

    for root, dirs, files in os.walk(local_site_folder):
        for dir in dirs:
            local_dir_path = os.path.join(root, dir)
            relative_dir_path = os.path.relpath(local_dir_path, local_site_folder)
            remote_dir_path = os.path.join(remote_folder, relative_dir_path).replace(
                "\\", "/"
            )

            try:
                sftp.stat(remote_dir_path)
            except FileNotFoundError:
                sftp.mkdir(remote_dir_path)

        for file in files:
            local_file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(local_file_path, local_site_folder)
            remote_file_path = os.path.join(remote_folder, relative_file_path).replace(
                "\\", "/"
            )

            sftp.put(local_file_path, remote_file_path)
            print(f"Uploaded: {local_file_path} to {remote_file_path}")

    sftp.close()
    transport.close()
    print("Site uploaded successfully.")


if __name__ == "__main__":
    obsidian_folder = "/Users/mmagicker/document/ObsidianLib/06-blog/"
    jekyll_posts_folder = "/Users/mmagicker/code/mMagicker/project/myblog/_posts"
    jekyll_folder = "/Users/mmagicker/code/mMagicker/project/myblog"
    local_site_folder = os.path.join(jekyll_folder, "_site")
    remote_folder = "/home/_site"
    server_ip = "**"
    username = "root"
    password = "**"

    sync_files(obsidian_folder, jekyll_posts_folder)
    build_jekyll_site(jekyll_folder)
    upload_site_to_server(
        local_site_folder, remote_folder, server_ip, username, password
    )
