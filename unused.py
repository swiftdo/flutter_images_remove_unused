import json, os, re


def get_file_paths(root_dir: str, exclude_types: list[str],
                   exclude_dirs: list[str]) -> list[str]:
    '''
    rootDir: 项目路径
    excludeTypes: 忽略的文件类型
    excludeDirs: 忽略的目录
    '''

    filepath_result: list[str] = []

    for dirpath, _, file_names in os.walk(root_dir):

        can_find = True

        for exclude_dir in exclude_dirs:
            if dirpath.startswith(exclude_dir):
                can_find = False
                break
        if not can_find:
            continue

        for file_name in file_names:
            apath = os.path.join(dirpath, file_name)
            (_, ext) = os.path.splitext(apath)  # 文件类型
            if len(ext) > 0 and ext not in exclude_types:
                filepath_result.append(apath)

    return filepath_result


def check_in_file(file_path: str, find_key: str) -> list[str]:
    '''判断文件是否存在字符串'''
    with open(file_path) as f:
        datafile = f.readlines()
    result: list[str] = []
    for line in datafile:
        if find_key in line:
            result.append(line.strip())
    return result


def check_in_files(file_paths: list[str], find_key: str) -> list:
    all_exist_result: list = []
    for file_path in file_paths:
        result: list[str] = check_in_file(file_path=file_path,
                                          find_key=find_key)
        if len(result) > 0:
            all_exist_result.append({"file_path": file_path, "lines": result})

    return all_exist_result


def name_convert_to_camel(name: str) -> str:
    """下划线转驼峰(小驼峰)"""
    return re.sub(r'(_[a-z])', lambda x: x.group(1)[1].upper(), name)


def get_all_images_names(root_dir: str) -> list[str]:
    '''获取全部的图片名字'''
    name_result = set([])
    for dirpath, dir_names, file_names in os.walk(root_dir):
        for file_name in file_names:
            (name, _) = os.path.splitext(file_name)
            name_result.add(name)

    return list(name_result)


def images_find_used(image_names: list[str], file_paths: list[str]) -> dict:
    '''找到所有图片的代码引入情况'''

    result: dict = {}

    for image_name in image_names:
        res = check_in_files(file_paths=file_paths,
                             find_key=f"Assets.images.{image_name}")
        result[image_name] = res

    return result


if __name__ == '__main__':

    # 可以外部传入
    root_dir = "../umall/lib"
    img_dir = "../umall/assets/images"
    exclude_types = [".DS_Store"]
    exclude_dirs = ["l10n", "generated"]

    # 最终传值
    exclude_dirs_f = list(map(lambda x: root_dir + '/' + x, exclude_dirs))

    # 获取到需要匹配的目录
    file_paths = get_file_paths(root_dir=root_dir,
                                exclude_types=exclude_types,
                                exclude_dirs=exclude_dirs_f)

    print(json.dumps(file_paths, indent=4))

    # 获取全部的图片名
    file_images_names = get_all_images_names(root_dir=img_dir)
    print(json.dumps(file_images_names, indent=4))

    # 将全局文件名转化为我们要的格式
    search_names = list(
        map(lambda x: name_convert_to_camel(x), file_images_names))
    print(json.dumps(search_names, indent=4))

    # 找到图片对应使用的代码情况
    all_result = images_find_used(image_names=search_names,
                                  file_paths=file_paths)
    print(json.dumps(all_result, indent=2))

    #打印那些未使用的图片
    all_unused_result = {
        key: value
        for key, value in all_result.items() if len(value) == 0
    }

    print("未使用的图片：")
    print(json.dumps(all_unused_result, indent=2))
