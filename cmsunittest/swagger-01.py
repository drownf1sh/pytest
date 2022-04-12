import re
import os
import sys

from requests import Session

template ="""
args:
  - {method}
  - {api}
kwargs:
  -
    caseName: {caseName}
    {data_or_params}:
        {data}
validator:
  -
    json:
      successed: True
"""


def auto_gen_cases(swagger_url, project_name):
    """
    根据swagger返回的json数据自动生成yml测试用例模板
    :param swagger_url:
    :param project_name:
    :return:
    """
    res = Session().request('get', swagger_url).json()
    data = res.get('paths')

    # workspace = os.getcwd()
    workspace = r'C:\wqw\Git\cmsunittest\yaml'

    project_ = os.path.join(workspace, project_name)

    if not os.path.exists(project_):
        os.mkdir(project_)

    for k, v in data.items():
        pa_res = re.split(r'[/]+', k)
        dir, *file = pa_res[1:]

        if file:
            file = ''.join([x.title() for x in file])
        else:
            file = dir

        file += '.yaml'

        dirs = os.path.join(project_, dir)

        if not os.path.exists(dirs):
            os.mkdir(dirs)

        os.chdir(dirs)

        if len(v) > 1:
            v = {'post': v.get('post')}
        for _k, _v in v.items():
            method = _k
            api = k
            caseName = _v.get('description')
            data_or_params = 'params' if method == 'get' else 'data'
            parameters = _v.get('parameters')

            data_s = ''
            try:
                for each in parameters:
                    data_s += each.get('name')
                    data_s += ': \n'
                    data_s += ' ' * 8
            except TypeError:
                data_s += '{}'

        file_ = os.path.join(dirs, file)

        with open(file_, 'w', encoding='utf-8') as fw:
            fw.write(template.format(
                method=method,
                api=api,
                caseName=caseName,
                data_or_params=data_or_params,
                data=data_s
            ))

        os.chdir(project_)

# swagger_url = "https://mik.qa.platform.michaels.com/api/cms/v3/api-docs/ContentApi"
# project_name = "ContentApi"
# auto_gen_cases(swagger_url,project_name)