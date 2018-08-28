import os
import shutil
import SiteTools.sql
import datetime
from PIL import Image
from SiteTools import file
from SiteTools import img
from SiteTools import zip
from SiteTools import sql
from PIL import Image
import time
from subprocess import call
def time_me(fn):
    def _wrapper(*args, **kwargs):
        start = time.clock()
        fn(*args, **kwargs)
        print("%s cost %s second"%(fn.__name__, time.clock() - start))
    return _wrapper
IMAGE_TYPE_COVER_CONTENT = "cover_content"
IMAGE_TYPE_COVER_THUMBILE = "cover_thumb"
IMAGE_TYPE_CONTENT_THUMBILE = "content_thumb"
IMAGE_TYPE_CONTENT = "content_image"


def mvImageToLib(imagePath , fileHash:str , sqlManager ,image_width ,image_heigh,imgLibPath = "img/" , uploader = "" , remark="" ):
    starttime = time.time()
    if fileHash == False:return False
    image_id = sqlManager.hash2imageId( fileHash )
    if image_id != None:
        print("The same image already exists in the image database, skip adding image to database!, image id:"+str(image_id)+", Image Hash :" + fileHash)
        return image_id
    print("---------:1.检测数据库内是否存在hash的图片部分%0.10f"%(time.time()-starttime))
    starttime=time.time()
    has1path = imgLibPath + fileHash[0:2]
    has2path = imgLibPath + fileHash[0:2] + "/" + fileHash[2:4]
    hashImagePath = has2path+"/"+fileHash[4:]+imagePath[-4:]
    imagePathNoLibPath = fileHash[0:2] + "/" + fileHash[2:4]+"/"+fileHash[4:]+imagePath[-4:]

    print("---------:文件名处理部分%0.10f"%(time.time()-starttime))
    starttime=time.time()
    file_size = os.path.getsize( imagePath)
    if not os.path.exists( has2path ):
        print("Hash Path Not exists, create direct and move imag file into it")
        os.makedirs(has2path)
        shutil.move(imagePath, hashImagePath)
    else:
        print("Hash Path exists")

        if os.path.exists(hashImagePath):
            print("Image exists in lib ,skip move image!")
        else:
            print("Image no exists in lib ,move file")
            shutil.move(imagePath, hashImagePath)
    print("---------:图片目录存在检测移动部分%0.10f"%(time.time()-starttime))
    starttime=time.time()
    print(imagePath)
    print(hashImagePath)
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")



    starttime=time.time()
    if uploader == "":
        image_id = sqlManager.addImageToSqlWhithoutCommit(fileHash, imagePathNoLibPath , image_width, image_heigh, file_size, dt , remark=remark)
    else:
        image_id = sqlManager.addImageToSqlWhithoutCommit(fileHash, imagePathNoLibPath,image_width, image_heigh, file_size, dt , uploader=uploader ,remark = remark)
    print("---------:编入数据库部分%0.10f"%(time.time()-starttime))
    return image_id

def hash2HashPath( hash ,format ):
    """
        输入图片hash值和格式，返回path，如：
    ad343fddf343 -> ad/34/3fddf343.jpg
    :param hash: 
    :param format: 图片格式扩展名 
    :return: 
    """
    return hash[0:2] + "/" + hash[2:4]+"/"+hash[4:]+"."+format

def hashPath2Hash( hashPath  ):
    """
        输入图片hash值和格式，返回path，如：
    ad343fddf343 -> ad/34/3fddf343.jpg
    :param hash:
    :param format: 图片格式扩展名
    :return:
    """
    return hashPath[0:2]+hashPath[3:5]+hashPath[6:-4]


def addNewArchFileToImgLib( archFilename , sqlManager ,title,uploadedArchPath, tmpLibPath = "tmp/", imgLibPath = "img/" , uploader = "" , remark = "" , coverPage = 1):
    same_title_book_id = sqlManager.title2bookId( title)
    if same_title_book_id != None:
        print("The same book title already exists! Error!!")
        return False

    same_title_book_id_in_removedtable = sqlManager.title2bookIdInRemoveTable( title)
    if same_title_book_id_in_removedtable != None:
        print("The same book title already exists in removed lib! Error!!")
        return False

    exactStartTime = time.time()
    exactPath = zip.exactArchToTmp(archFilename,uploadedArchPath)
    print("压缩包解压耗时%0.10f"% (time.time()-exactStartTime))
    if exactPath == None:
        return


    filesInTmp = file.getAllImageFiles(exactPath)
    book_id = sqlManager.getNextBookId()


    page = 1

    forInTmpStartTime = time.time()
    for f in filesInTmp:
        startTiem=time.time()
        imageFileMd5 = file.calFileMd5(f)

        image = Image.open(f) # type: Image
        image_width, image_heigh = image.size
        image.thumbnail([250,350])
        thumbImageName= str(page) + "-thumb"
        thumImagePath = exactPath+"/"+thumbImageName+".jpg"
        thumb_image_width , thumb_image_heigh = image.size
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(thumImagePath, "JPEG")

        image.close()


        thumbImageFileMd5 = file.calFileMd5(thumImagePath)

        print("图片获取尺寸，生成缩略图部分耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()


        image_id = img.mvImageToLib(f, imageFileMd5, sqlManager ,image_width,image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)

        print("mvImageToLib耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        sqlManager.addBookNewPageToSqlNoCommit(book_id, title , image_id,
                                       img.IMAGE_TYPE_CONTENT, page)
        print("Page编入数据库耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        thumImage_id = img.mvImageToLib(thumImagePath, thumbImageFileMd5, sqlManager ,thumb_image_width,thumb_image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)

        print("缩略图mvImageToLib耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        sqlManager.addBookNewPageToSqlNoCommit(book_id, title , thumImage_id,
                                       img.IMAGE_TYPE_CONTENT_THUMBILE, page)
        print("缩略图Page编入数据库耗时%0.10f" % (time.time() - startTiem))


        if page == 1:
            image_id = img.mvImageToLib(f, imageFileMd5, sqlManager, image_width, image_heigh, imgLibPath=imgLibPath,
                                        uploader=uploader, remark=remark)
            sqlManager.addBookNewPageToSqlNoCommit(book_id, title, image_id,
                                                   img.IMAGE_TYPE_COVER_CONTENT, page)

            thumImage_id = img.mvImageToLib(thumImagePath, thumbImageFileMd5, sqlManager, thumb_image_width,
                                            thumb_image_heigh, imgLibPath=imgLibPath, uploader=uploader, remark=remark)
            sqlManager.addBookNewPageToSqlNoCommit(book_id, title, thumImage_id,
                                                   img.IMAGE_TYPE_COVER_THUMBILE, page)
        page += 1
        sqlManager.sqldb.commit()
    print("forInTmpStartTime耗时%0.10f"% (time.time()-forInTmpStartTime))
    shutil.rmtree(exactPath)
    return book_id


def addNewArchFileToImgLibWithProgress( archFilename , sqlManager ,title,uploadedArchPath, status,index , tmpLibPath = "tmp/", imgLibPath = "img/" , uploader = "" , remark = "" , coverPage = 1):
    same_title_book_id = sqlManager.title2bookId( title)
    if same_title_book_id != None:
        print("The same book title already exists! Error!!")
        status[index] = "Skip: same book title exists"
        return False

    archfileHash =  file.calFileMd5(uploadedArchPath+archFilename)
    status[index] = "Hash calcute error!May be file not exists"
    if archfileHash == False:
        return False
    print("Arch File Hash: "+ archfileHash)
    hashInTable =  sqlManager.fileHashInUploadedArchTable( archfileHash )
    if hashInTable:
        print("The same hash file has already uploaded.skip this file ")
        status[index] = "Skip! - same hash file has uploaded already!"
        return False
    else:
        sqlManager.addArchFileHashToTable(archfileHash)



    same_title_book_id_in_removedtable = sqlManager.title2bookIdInRemoveTable( title)
    """if same_title_book_id_in_removedtable != None:
        print("The same book title already exists in removed lib! Error!!")
        status[index] = "Skip: same book title exists in removed lib"
        return False"""

    exactStartTime = time.time()
    status[index] = "Now exacting..."
    exactPath = zip.exactArchToTmp(archFilename,uploadedArchPath,status,index)
    status[index] = "Exacting done."
    print("压缩包解压耗时%0.10f"% (time.time()-exactStartTime))
    if exactPath == None:
        return


    filesInTmp = file.getAllImageFiles(exactPath)
    book_id = sqlManager.getNextBookId()


    page = 1

    forInTmpStartTime = time.time()
    status[index] = "Now adding pages to system..."
    sqlManager.cursor.execute("""
    CREATE TEMPORARY TABLE IF NOT EXISTS books_tmp AS (SELECT * FROM books where 0);
    """)

    for f in filesInTmp:
        startTiem=time.time()
        imageFileMd5 = file.calFileMd5(f)

        image = Image.open(f) # type: Image
        image_width, image_heigh = image.size
        image.thumbnail([250,350])
        thumbImageName= str(page) + "-thumb"
        thumImagePath = exactPath+"/"+thumbImageName+".jpg"
        thumb_image_width , thumb_image_heigh = image.size
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(thumImagePath, "JPEG")

        image.close()


        thumbImageFileMd5 = file.calFileMd5(thumImagePath)

        print("图片获取尺寸，生成缩略图部分耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()


        image_id = img.mvImageToLib(f, imageFileMd5, sqlManager ,image_width,image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)

        print("mvImageToLib耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        sqlManager.addBookNewPageToSqlNoCommit(book_id, title , image_id,
                                       img.IMAGE_TYPE_CONTENT, page)
        print("Page编入数据库耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        thumImage_id = img.mvImageToLib(thumImagePath, thumbImageFileMd5, sqlManager ,thumb_image_width,thumb_image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)

        print("缩略图mvImageToLib耗时%0.10f" % (time.time() - startTiem))
        startTiem = time.time()

        sqlManager.addBookNewPageToSqlNoCommit(book_id, title , thumImage_id,
                                       img.IMAGE_TYPE_CONTENT_THUMBILE, page)
        print("缩略图Page编入数据库耗时%0.10f" % (time.time() - startTiem))


        if page == 1:
            image_id = img.mvImageToLib(f, imageFileMd5, sqlManager, image_width, image_heigh, imgLibPath=imgLibPath,
                                        uploader=uploader, remark=remark)
            sqlManager.addBookNewPageToSqlNoCommit(book_id, title, image_id,
                                                   img.IMAGE_TYPE_COVER_CONTENT, page)

            thumImage_id = img.mvImageToLib(thumImagePath, thumbImageFileMd5, sqlManager, thumb_image_width,
                                            thumb_image_heigh, imgLibPath=imgLibPath, uploader=uploader, remark=remark)
            sqlManager.addBookNewPageToSqlNoCommit(book_id, title, thumImage_id,
                                                   img.IMAGE_TYPE_COVER_THUMBILE, page)
        page += 1
        status[index] = "Adding pages to system(%d/%d)" % ( page , len(filesInTmp))
        sqlManager.sqldb.commit()
    print("forInTmpStartTime耗时%0.10f"% (time.time()-forInTmpStartTime))
    shutil.rmtree(exactPath)
    sqlManager.cursor.execute("""
    insert into books select * from books_tmp WHERE book_id = %d
    """ % (book_id))
    sqlManager.sqldb.commit()
    status[index] = "Complete!"
    return book_id


def addNewSingleCoverImageFileToDatabaseWithBookId( imageFilename , sqlManager,book_id ,title, createTime,tmpLibPath = "tmp/", imgLibPath = "img/" , uploader = "" , remark = "" , coverPage = 1 ,):
    imageFullPath = tmpLibPath+imageFilename
    image = Image.open(imageFullPath) # type: Image
    image_width, image_heigh = image.size
    image.thumbnail([250,350])
    thumbImageName= imageFilename+ "-thumb"
    thumImagePath = tmpLibPath+thumbImageName+".jpg"
    thumb_image_width , thumb_image_heigh = image.size
    if image.mode != "RGB":
        image = image.convert("RGB")
    image.save(thumImagePath, "JPEG")

    image.close()

    imageFileMd5 = file.calFileMd5(imageFullPath)
    thumbImageFileMd5 = file.calFileMd5(thumImagePath)

    image_id = img.mvImageToLib(imageFullPath, imageFileMd5, sqlManager ,image_width,image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)
    sqlManager.changeTheCover( book_id,image_id,img.IMAGE_TYPE_COVER_CONTENT)



    thumImage_id = img.mvImageToLib(thumImagePath, thumbImageFileMd5, sqlManager ,thumb_image_width,thumb_image_heigh,imgLibPath=imgLibPath, uploader = uploader , remark = remark)
    sqlManager.changeTheCover( book_id,thumImage_id,img.IMAGE_TYPE_COVER_THUMBILE)


    sqlManager.sqldb.commit()


def cropImage( imageFullPath , rectX,rectY,rectW,rectH):
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    coverImage = Image.open(imageFullPath,'r')

    newCoverImg =  coverImage.crop(( rectX,rectY,rectW,rectH))


    if newCoverImg.mode != "RGB":
        newCoverImg = newCoverImg.convert("RGB")

    newCoverImgName = dt+".jpg"
    newCoverImgFullPath = "tmp/"+dt+".jpg"
    newCoverImg.save(newCoverImgFullPath, "JPEG")
    newCoverImg.close()
    coverImage.close()

    return newCoverImgName