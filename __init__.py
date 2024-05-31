#!/usr/bin/env python3

import os
import shutil
import subprocess
import paramiko
import hashlib


def get_file_hash(file_path):
    """计算文件的哈希值"""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def sync_files(obsidian_folder, jekyll_posts_folder):
    obsidian_files = {
        f: os.path.join(obsidian_folder, f)
        for f in os.listdir(obsidian_folder)
        if os.path.isfile(os.path.join(obsidian_folder, f))
    }
    jekyll_files = {
        f: os.path.join(jekyll_posts_folder, f)
        for f in os.listdir(jekyll_posts_folder)
        if os.path.isfile(os.path.join(jekyll_posts_folder, f))
    }

    for file_name, obsidian_file_path in obsidian_files.items():
        jekyll_file_path = jekyll_files.get(file_name)

        if jekyll_file_path:
            # 文件已存在于jekyll_posts_folder中，检查是否需要更新
            if get_file_hash(obsidian_file_path) != get_file_hash(jekyll_file_path):
                shutil.copy2(obsidian_file_path, jekyll_file_path)
                print(f"Updated: {file_name}")
        else:
            # 文件不存在于jekyll_posts_folder中，直接复制
            shutil.copy2(obsidian_file_path, jekyll_posts_folder)
            print(f"Copied: {file_name}")


def build_jekyll_site(jekyll_folder):
    try:
        subprocess.run(["jekyll", "build"], cwd=jekyll_folder, check=True)
        print("Jekyll site built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Jekyll build: {e}")

def upload_site_to_server(local_site_folder, remote_folder, server_ip, username, password):
    transport = paramiko.Transport((server_ip, 22))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    
    for root, dirs, files in os.walk(local_site_folder):
        for dir in dirs:
            local_dir_path = os.path.join(root, dir)
            relative_dir_path = os.path.relpath(local_dir_path, local_site_folder)
            remote_dir_path = os.path.join(remote_folder, relative_dir_path).replace('\\', '/')
            
            try:
                sftp.stat(remote_dir_path)
            except FileNotFoundError:
                sftp.mkdir(remote_dir_path)
        
        for file in files:
            local_file_path = os.path.join(root, file)
            relative_file_path = os.path.relpath(local_file_path, local_site_folder)
            remote_file_path = os.path.join(remote_folder, relative_file_path).replace('\\', '/')
            
            sftp.put(local_file_path, remote_file_path)
            print(f'Uploaded: {local_file_path} to {remote_file_path}')
    
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
    upload_site_to_server(local_site_folder, remote_folder, server_ip, username, password)
