#!/usr/bin/python3
# Author: Eduardo Marossi

import os
import subprocess
import argparse

VERSION = '1.0.0'

def create_dir(root_nextcloud_url, username, password, folder):
    if folder.strip() == '':
        return None
    p = subprocess.run('curl -u "{}:{}" -X MKCOL "{}/remote.php/dav/files/{}/{}"'.format(username, password, root_nextcloud_url, username, folder),
                       shell=True, stdout=subprocess.PIPE)
    return p.stdout.decode('utf-8')


def upload_file(root_nextcloud_url, username, password, local_file_path, remote_file_path):
    p = subprocess.run('curl -u "{}:{}" -T "{}" "{}/remote.php/dav/files/{}/{}"'
                       .format(username, password, local_file_path, root_nextcloud_url, username, remote_file_path), shell=True, stdout=subprocess.PIPE)
    return p.stdout.decode('utf-8')


def mirror_recursively(root_nextcloud_url, username, password, local_file_path, delete_after_upload):
    dirs_created = []
    start_path = local_file_path
    for p, d, f in os.walk(local_file_path):
        for dir in d:
            full_path = os.path.join(p, dir)
            full_path = full_path.replace(start_path, '')
            if full_path not in dirs_created:
                print('Creating remote folder: {}'.format(full_path))
                create_dir(root_nextcloud_url, username, password, full_path)
                dirs_created.append(full_path)

        for file in f:
            if '.DS_Store' in file or file.startswith('Thumbs.db'):
                continue

            full_path = os.path.join(p, file)
            remote_folder = p.replace(start_path, '')
            if remote_folder not in dirs_created:
                print('Creating remote folder: {}'.format(remote_folder))
                create_dir(root_nextcloud_url, username, password, remote_folder)
                dirs_created.append(remote_folder)

            remote_path = full_path.replace(start_path, '')
            if remote_path[0] == os.sep:
                remote_path = remote_path[1:]

            print('Uploading file: {}'.format(remote_path))
            upload_file(root_nextcloud_url, username, password, full_path, remote_path)
            if delete_after_upload:
                print('Deleting file: {}'.format(full_path))
                os.unlink(full_path)
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replicate Nextcloud {} by Eduardo Marossi'.format(VERSION))
    parser.add_argument('-o', '--host', type=str, required=True)
    parser.add_argument('-u', '--username', type=str, required=True)
    parser.add_argument('-p', '--password', type=str, required=True)
    parser.add_argument('-l', '--local-path', type=str, required=True)
    parser.add_argument('-d', '--delete-after-upload', default=False, action='store_true')
    args = parser.parse_args()

    mirror_recursively(args.host, args.username, args.password, args.local_path, args.delete_after_upload)
