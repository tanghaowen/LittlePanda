import hashlib
import os
import re
from SiteTools import img

from ctypes import *

def calFileMd5(file_name):
    print("start to calcate the md5 of: %s" % file_name)
    try:
        f = open(file_name,"rb")

        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        f.close()
        hash = md5_obj.hexdigest()
        return hash
    except FileNotFoundError as e:
        print(e)
        return False



def getAllFiles(rootDir):
    filePaths=[]
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            filePaths.append(os.path.join(root,f))

    return filePaths


def getAllArchFilesInfo(rootDir):
    """
    获取指定目录下，所有压缩包
    返回[ [文件名列表],[完整路径列表] ]
    :param rootDir: 
    :return: 
    """
    filePaths=[]
    fileNames=[]
    list_dirs = os.walk(rootDir)
    print(rootDir)
    print(list_dirs)
    for root, dirs, files in list_dirs:
        for f in files:
            if '.zip' in f or '.rar' in f or '.7z' in f:
                filePaths.append(os.path.join(root,f))
                fileNames.append(f)

    return [fileNames,filePaths]
def getAllImageFiles(rootDir):
    filePaths=[]
    list_dirs = os.walk(rootDir)
    for root, dirs, files in list_dirs:
        for f in files:
            f_low = f.lower()
            if '.jpg' in f_low or '.png' in f_low or '.bmp' in f_low:
                filePaths.append(os.path.join(root,f))

    return filePaths


def dealWithFileName( title ):
    r = re.compile("\(.*?\)")
    title2 = title

    title = r.sub('',title)

    r2 = re.compile("\[(.*?)\]")
    ress = r2.findall(title);
    if len(ress) == 0:
        return title2
    artist =  ress[0]

    title = r2.sub('',title)
    sd = title.split(" ")
    title = ""
    for s in sd:
        if s == " " or s == "　" or s == "":
            continue
        title = s
        break
    return artist + " " + title


def getFilePathFromLPFS(lpfs_dll,image_ids):
    if isinstance(image_ids,str):
        image_ids = int(image_ids)
    if isinstance(image_ids,int):
        image_ids = [image_ids]
    if isinstance(image_ids,(list,tuple)):
        attr = (c_int * len(image_ids))(*image_ids)
        s = (c_wchar_p * 1000)()
        lpfs_dll.exactImages(attr, len(image_ids), s)
        return s
    else:
        return False


def importArchFileFromTmp(sqlManager,uploadedArchPathRoot,tmpPath="tmp/", status = None,lpfs_dll=None):

    """
    status 结构
    {
        "allFiles":     file数量,
        "doneFiles":    完成数量,
        "doingIndex":   正在处理的进度位置
        "files":"
                [   [fileName1, fileName2 , fileName3 , ...],
                    [filePath1, filePath2 , filePath3 , ... ],
                    [status1 ,  status2 ,   status3,    ...]
                ]
        “
    }

    :param sqlManager:
    :param uploadedArchPathRoot:
    :param tmpPath:
    :param status: 传入空的字典：{}
    :return:
    """
    print("The uploaded arch path is :"+uploadedArchPathRoot)
    archNames, archPaths = getAllArchFilesInfo(uploadedArchPathRoot)
    if status == None:
        status = {}

    status["allFiles"] = len( archNames )
    status["doneFiles"] = 0
    status["doingIndex"] = -1
    status["files"] = [archNames,
                       archPaths,
                       ["Waiting"] * len( archNames )
                       ]

    print( archNames)
    print( archPaths)

    rootdir = os.getcwd()
    for index, archname in enumerate(archNames):
        status["doingIndex"] = index
        print("Progress:" + str(index + 1) + " / " + str(len(archNames)))
        status["files"][2][index] = "doing"
        img.addNewArchFileToImgLibWithProgress(archname, sqlManager,
                                   archname[0:-4],
                                   uploadedArchPathRoot,
                                               status["files"][2],index,lpfs_dll=lpfs_dll)

        status["doneFiles"] += 1

