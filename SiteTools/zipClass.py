import zipfile
import rarfile
import os
import datetime
def exactZipToTmp(zipfileName , tmpPath="tmp/"):
    print("Start to exact arch file: "+zipfileName)
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S/")
    zipExactPath = tmpPath+dt
    print(zipExactPath)
    try:
        os.makedirs(zipExactPath)
    except FileExistsError as e:
        print(e)

    zip = zipfile.ZipFile(tmpPath+"uploadedArch/"+zipfileName,mode='r')
    for f in zip.namelist():
        print("exacting:"+zipExactPath+f)
        zip.extract(f , zipExactPath)
    print("exact '"+zipfileName+"' over.")
    return zipExactPath


def exactRarToTmp(rarFilename , tmpPath = "tmp/"):
    print("Start to exact arch file: "+rarFilename)
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S/")
    rarExactPath = tmpPath+dt
    print(rarExactPath)
    try:
        os.makedirs(rarExactPath)
    except FileExistsError as e:
        print(e)

    rar = rarfile.RarFile(tmpPath+"uploadedArch/"+rarFilename,mode='r')
    for f in rar.infolist():
        print("exacting:"+rarExactPath+f.filename)
        rar.extract(f.filename , rarExactPath)
    print("exact '"+rarFilename+"' over.")
    return rarExactPath

def exactArchToTmp(archFilename , tmpPath = "tmp/"):
    fil_spli = os.path.splitext(archFilename)
    if fil_spli[1] == '.zip':
        return exactZipToTmp( archFilename,tmpPath)
    elif fil_spli[1] == '.rar':
        return exactRarToTmp( archFilename,tmpPath)

    else:
        print("Unsupport Arch File! Error!")
        return None



def createZipArch(archFilename , imgPaths , imgLib="/img/"):
    z = zipfile.ZipFile(archFilename+".zip",mode='w' , compression=zipfile.ZIP_STORED)
    i =1
    for imgPath in imgPaths:

        path = imgLib+imgPath
        z.write( path ,"%04d.jpg" % i )

    z.close()


