"""
这个工具可以用来下载gitlab上面的代码。
使用说明：
1. 要求本机可以能够从gitlab git clone代码
2. 有些git clone需要认证一次指纹，本程序没有实现，如果是第一次下载代码，请先用命令行git clone任意一个仓库，确认指纹。
3. 在gitlab添加自己的PRIVATE TOKEN，并付给PRIVATE_TOKEN参数
4. 修改输入路径BASE_PATH
"""

import requests
import os
import collections

groups = []
projects = []

BASE_URL = 'http://gitlab.os.adc.com/'
API_VERSION = 'api/v4/'
PRIVATE_TOKEN = 'xxxxxxxxxxx'
BASE_PATH = 'e:\\code\\'
PER_PAGE = '?per_page=100'


def get_groups():
    global groups
    queue = collections.deque()
    count = 0
    headers = {
        'PRIVATE-TOKEN': PRIVATE_TOKEN
    }
    temp_groups = requests.get(BASE_URL + API_VERSION + 'groups' + PER_PAGE, headers=headers).json()
    count = count + temp_groups.__len__();
    print(f'get groups: {count} ....')
    queue.extend(temp_groups)
    while len(queue) != 0:
        g = queue.popleft()
        groups.append(g)
        sub_groups = requests.get(BASE_URL + API_VERSION + f'groups/{g["id"]}/subgroups' + PER_PAGE,
                                  headers=headers).json()
        if sub_groups.__len__() > 0:
            queue.extend(sub_groups)
            count = count + sub_groups.__len__();
            print(f'get groups: {count} ....')


def get_projects():
    global groups
    global projects
    headers = {
        'PRIVATE-TOKEN': PRIVATE_TOKEN
    }
    count = 0

    for g in groups:
        tmp = requests.get(BASE_URL + API_VERSION + f"groups/{g['id']}", headers=headers, ).json()
        tmp_projects = tmp['projects']
        if tmp_projects.__len__() > 0:
            projects.extend(tmp_projects)
            count = count + tmp_projects.__len__()
            print(f'get projects: {count} ....')


def clone_projects():
    global projects
    i = 1
    projects_total_len = projects.__len__();
    for p in projects:
        path = BASE_PATH + p['path_with_namespace']
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path + '/.git'):
            print(f"{i}-{projects_total_len}: start update {p['path_with_namespace']}...")
            print(os.popen(f"git -C {path} pull --progress").read())
            print(f"{i}-{projects_total_len}: end update {p['path_with_namespace']}...")
        else:
            print(f"{i}-{projects_total_len}: start clone {p['path_with_namespace']}...")
            print(os.popen(f"git clone --progress {p['ssh_url_to_repo']} {path}").read())
            print(f"{i}-{projects_total_len}: end clone {p['path_with_namespace']}...")
        i = i + 1


print("start to get groups...")
get_groups()
for g in groups:
    print(g)
print(f"end get groups: {groups.__len__()}")
print("start to get projects...")
get_projects()
print(f"end get projects: {projects.__len__()}")
clone_projects()
print(f"end")
