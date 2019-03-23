import zipfile
import rarfile
import os
import datetime
import subprocess
def exactZipToTmp(zipfileName , uploadedArchDirPath ,tmpPath = "tmp/",status = None,index = None):


    print("Start to exact arch file: "+zipfileName)

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S/")
    dt2 = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    tmpExactPath = tmpPath+dt
    zipExactPath = uploadedArchDirPath+dt
    print(zipExactPath)
    print(tmpExactPath)
    try:
        os.makedirs(tmpExactPath)
    except FileExistsError as e:
        print(e)



    subprocess.call([r".\7z.exe" , 'e',uploadedArchDirPath+zipfileName,"-oE:\\Project\\LittlePanda\\tmp\\"+dt2] )

    return tmpExactPath
    zip = zipfile.ZipFile(uploadedArchDirPath+zipfileName,mode='r')

    indexpage = 1
    allPagesNumber = len( zip.namelist())



    for f in zip.namelist():
        #fn = f.encode('cp437').decode("shift_jis")
        print("exacting:"+tmpExactPath+f)
        zip.extract(f , tmpExactPath)
        if not status == None:
            status[index] = "Now exacting: %d/%d" % ( indexpage,allPagesNumber)
        indexpage+=1
    print("exact '"+zipfileName+"' over.")
    return tmpExactPath
def exact7zToTmp(zipfileName , uploadedArchDirPath ,tmpPath = "tmp/",status = None,index = None):


    print("Start to exact arch file: "+zipfileName)

    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S/")
    dt2 = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    tmpExactPath = tmpPath+dt
    zipExactPath = uploadedArchDirPath+dt
    print(zipExactPath)
    print(tmpExactPath)
    try:
        os.makedirs(tmpExactPath)
    except FileExistsError as e:
        print(e)



    subprocess.call(["E:\\Program Files\\7-Zip\\7z.exe" , 'e',uploadedArchDirPath+zipfileName,"-oE:\\Project\\flaskSite\\tmp\\"+dt2] )

    return tmpExactPath
    zip = zipfile.ZipFile(uploadedArchDirPath+zipfileName,mode='r')

    indexpage = 1
    allPagesNumber = len( zip.namelist())



    for f in zip.namelist():
        #fn = f.encode('cp437').decode("shift_jis")
        print("exacting:"+tmpExactPath+f)
        zip.extract(f , tmpExactPath)
        if not status == None:
            status[index] = "Now exacting: %d/%d" % ( indexpage,allPagesNumber)
        indexpage+=1
    print("exact '"+zipfileName+"' over.")
    return tmpExactPath


def exactRarToTmp(rarFilename , uploadedArchDirPath ,tmpPath = "tmp/",status = None,index = None):
    print("Start to exact arch file: "+rarFilename)
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S/")
    rarExactPath = uploadedArchDirPath+dt
    tmpExactPath = tmpPath+dt
    print(rarExactPath)
    print(tmpExactPath)
    try:
        os.makedirs(tmpExactPath)
    except FileExistsError as e:
        print(e)

    rar = rarfile.RarFile(uploadedArchDirPath+rarFilename,mode='r')
    indexpage = 1
    allPagesNumber = len( rar.infolist())
    for f in rar.infolist():
        print("exacting:"+tmpExactPath+f.filename)
        rar.extract(f.filename , tmpExactPath)
        if not status == None:
            status[index] = "Now exacting: %d/%d" %( indexpage,allPagesNumber)
        indexpage += 1
    print("exact '"+rarFilename+"' over.")
    return tmpExactPath


def exactArchToTmp(archFilename , uploadedArchDirpath,status=None,index=None):
    fil_spli = os.path.splitext(archFilename)
    if fil_spli[1] == '.zip':
        return exactZipToTmp( archFilename,uploadedArchDirpath ,status=status,index=index)
    elif fil_spli[1] == '.rar':
        return exactRarToTmp( archFilename,uploadedArchDirpath ,status=status,index=index)
    if fil_spli[1] == '.7z':
        return exact7zToTmp( archFilename,uploadedArchDirpath ,status=status,index=index)
    else:
        print("Unsupport Arch File! Error!")
        return None



def createZipArch(archFilename , imgPaths , imgLib="img/"):
    z = zipfile.ZipFile("tmp/"+archFilename,mode='w' , compression=zipfile.ZIP_STORED)
    i =1
    for imgPath in imgPaths:

        path = imgLib+imgPath
        z.write( path ,"%04d.jpg" % i )

    z.close()


