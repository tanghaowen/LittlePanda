import MySQLdb
from SiteTools import img
import datetime
from SiteTools import book
import os
import time
import re
from ctypes import *
from SiteTools import file

class sqlDataManager():

    def __init__(self):

        self.sqldb = MySQLdb.connect(host = 'localhost', user="littlepanda",passwd = "shinonomehana" ,charset = "UTF8")
        self.cursor = self.sqldb.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        self.cursor.execute("""
        CREATE DATABASE IF NOT EXISTS littlepanda;
        """)
        self.cursor.execute("""
        USE littlepanda;
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS images(
        image_id INT PRIMARY KEY NOT NULL auto_increment ,
        hash VARCHAR(100) NOT NULL ,
        path TEXT NOT NULL ,
        width SMALLINT NOT NULL ,
        high SMALLINT NOT NULL ,
        `size` VARCHAR(20) NOT NULL ,
        uploader VARCHAR (40) ,
        upload_time DATETIME NOT NULL ,
        remark TEXT
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS books(
        page_index INT PRIMARY KEY NOT NULL auto_increment ,
        book_id INT  NOT NULL ,
        title TEXT NOT NULL ,
        image_id INT NOT NULL ,
        image_type VARCHAR(20) NOT NULL ,
        page SMALLINT NOT NULL,
        ehentai_id INT,
        create_time DATETIME NOT NULL,
        last_edit_time DATETIME NOT NULL);
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags(
        tag_id INT PRIMARY KEY NOT NULL auto_increment , 
        tag_name TEXT NOT NULL,
        tag_catalog TEXT NOT NULL
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tagmap(
        book_id INT NOT NULL, 
        tag_id INT NOT NULL
        );
        """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tagtranslate(
        translate_id INT PRIMARY KEY NOT NULL auto_increment ,
        ori_name TEXT NOT NULL,
        cata TEXT NOT NULL,
        translate_name TEXT
        
        );
        """)

        self.cursor.execute("""
        create table IF NOT EXISTS books_removed select * from books where 0;
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS addfilehash(
        addfileid INT PRIMARY KEY NOT NULL auto_increment ,
        hash VARCHAR(200) NOT NULL,
        INDEX(hash)
        );
        """)
        self.sqldb.commit()

    def addImageToSqlWhithoutCommit(self,image_hash , image_path ,image_width , image_high , size , upload_time ,uploader="anonymous" , remark = ""):
        self.cursor.execute("""
        INSERT INTO images ( hash , path ,width , high , `size` , uploader , upload_time , remark) VALUES 
        ('%s' , '%s' ,%d , %d , %d , '%s','%s' , '%s' )
        """ % ( image_hash, image_path,image_width,image_high,size , uploader , upload_time,remark))

        return self.cursor.lastrowid


    def changeBookInfo(self,book_id , newBookPagesInfosAlreadyExits):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
        select * from books where book_id = %d
        """ % book_id)

        res = self.cursor.fetchall()
        if len(res) == 0: return None
        res =list(res)
        i = 0
        while i<len(res):
            if res[i]['image_type'] == img.IMAGE_TYPE_COVER_THUMBILE or res[i]['image_type'] == img.IMAGE_TYPE_COVER_CONTENT:
                res.remove(res[i])
                i-=1

            i+=1
        i = 0
        lenOfNewPages = len(newBookPagesInfosAlreadyExits)
        lenOfOldPages = len(res)
        print("lenOfPages ",lenOfNewPages)
        for page in newBookPagesInfosAlreadyExits:
            if i >= lenOfOldPages:
                print("insert")
                self.cursor.execute("""
                INSERT INTO books ( book_id , title , image_id ,image_type , page ,create_time,last_edit_time ) VALUES 
                ( %d , '%s' , %d ,'%s' ,%d ,'%s','%s')
                """ % (book_id, page['title'], page['image_id'], page['image_type'], page['page'], page['create_time'], dt))
            else:
                self.cursor.execute("""
                update books set image_id = %d , last_edit_time = '%s' where page_index = %d 
                """ % (page['image_id'] , dt , page["page_index"]))
            print(str(i)+" over")
            i+=1
    def addBookNewPageToSqlNoCommit(self , book_id , book_title , image_id , image_type , page):
        book_title = book_title.replace("'", "\\'")  # type:str
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
        INSERT INTO books_tmp ( book_id , title , image_id ,image_type , page ,create_time,last_edit_time ) VALUES 
        ( %d , '%s' , %d ,'%s' ,%d ,'%s','%s')
        """ % ( book_id , book_title , image_id , image_type , page,dt,dt  ))
        print("Adding new book page success, book id"+str(book_id)+" "+book_title+" page:"+str(page))
        return self.cursor.lastrowid
    def addBookNewPageToSqlNoCommitWithCreateTime(self , book_id , book_title , image_id , image_type , page,create_time):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
        INSERT INTO books ( book_id , title , image_id ,image_type , page ,create_time,last_edit_time ) VALUES 
        ( %d , '%s' , %d ,'%s' ,%d ,'%s','%s')
        """ % ( book_id , book_title , image_id , image_type , page,create_time,dt  ))
        print("Adding new book page success, book id"+str(book_id)+" "+book_title+" page:"+str(page))
        return self.cursor.lastrowid
    def changeTheCover(self , book_id , image_id , image_type ):
        self.cursor.execute("""
        update books set image_id = %d where book_id = %d and image_type = '%s'and page =1
        """ % ( image_id,book_id , image_type))
        print("Change cover success, book id:"+str(book_id))
        self.sqldb.commit()

    def getLargestBookId(self):
        self.cursor.execute("""
        SELECT MAX( book_id) AS max_book_id FROM books
        """)
        results = self.cursor.fetchall()
        self.cursor.execute("""
        SELECT MAX( book_id) AS max_book_id FROM books_removed
        """)
        results_removed = self.cursor.fetchall()

        if len(results) == 0 and len(results_removed) == 0 :return None

        res_max =  res_removed_max = 0
        for res in results:
            res_max = res["max_book_id"]
        for res in results_removed:
            res_removed_max = res["max_book_id"]

        if res_max == None: res_max = 0
        if res_removed_max == None: res_removed_max = 0;
        return max(res_max,res_removed_max)





    def getNextBookId(self):
        return self.getLargestBookId()+1
    def deleteBookFromDatabase(self,book_id , imgLib = "img/"):
        if book_id<1:
            print("Book id smaller than 1!  Error!")
        if book_id>self.getLargestBookId():
            print("Book id larger than max book id! Error!")

        self.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.book_id = %d
        """ % ( book_id))
        books = self.cursor.fetchall()
        if len(books) == 0 :
            print("The book you want to delete is not exists!")
            return None

        for book in books:

            self.cursor.execute("""
            select book_id,image_id,title from books where image_id = %d
            """ % (book["image_id"]))
            imageMap = self.cursor.fetchall()
            if len(imageMap)>1:
                print("page "+str(book["page"]) + " is linked to others books, the image will not delete from image lib.")
            else:
                self.cursor.execute("""
                delete from images where image_id = %d
                """ % (book["image_id"]))
                print("Deleted image id: " + str(book["image_id"]) +" from database")
                try:
                    os.remove(imgLib+book["path"])
                    print("Deleted image file: "+imgLib+book["path"])
                except FileNotFoundError as e:

                    print(e)

        self.cursor.execute("""
        delete from books where book_id = %d
        """ %( book_id))
        print("Delete book: "+str( book_id) + " success!")
        self.sqldb.commit()

    def deleteBookFromDatabaseDirect(self,book_id , imgLib = "img/"):
        if book_id<1:
            print("Book id smaller than 1!  Error!")
        if book_id>self.getLargestBookId():
            print("Book id larger than max book id! Error!")

        self.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.book_id = %d
        """ % ( book_id))
        books = self.cursor.fetchall()
        if len(books) == 0 :
            print("The book you want to delete is not exists!")
            return None


        self.cursor.execute("""
        delete from books where book_id = %d
        """ %( book_id))
        print("Delete book: "+str( book_id) + " success!")

        self.clearAllTagsOfBook( book_id)
        print("And this books tags has been removed!")
        self.sqldb.commit()

    def deleteBookFromDatabaseToTmpTable(self,book_id , imgLib = "img/"):
        if book_id<1:
            print("Book id smaller than 1!  Error!")
        if book_id>self.getLargestBookId():
            print("Book id larger than max book id! Error!")

        self.cursor.execute("""
        select * from books WHERE book_id = %d
        """ % ( book_id))
        books = self.cursor.fetchall()
        if len(books) == 0 :
            print("The book you want to delete is not exists!")
            return None

        self.cursor.execute("""
        insert into books_removed select * from books WHERE book_id = %d
        """% ( book_id))

        self.cursor.execute("""
        delete from books where book_id = %d
        """ %( book_id))
        print("Delete book To tmpTable: "+str( book_id) + " success!")
        self.sqldb.commit()

    def hash2imageId(self,hash:str):
        """
        输入图片的hash值，查找数据库中是否有此图片
        :param hash: 图片的hash值
        :return: 不存在，返回None；存在返回第一个找到的image_id
        """
        image_count = self.cursor.execute("""
        SELECT * FROM images 
        WHERE hash = '%s'
        """ %( hash ))
        results = self.cursor.fetchall()
        if len(results) == 0 : return None
        for res in results:

            return res["image_id"]
    def title2bookId(self,title:str):
        """
        输入书本的title，查找数据库中是否有此书
        :param title: 标题
        :return: 不存在，返回None；存在返回第一个找到的book_id
        """
        title = title.replace("'", "\\'")  # type:str
        image_count = self.cursor.execute("""
        SELECT * FROM books 
        WHERE title = '%s'
        """ %( title ))
        results = self.cursor.fetchall()
        if len(results) == 0 : return None
        for res in results:

            return res["book_id"]
    def title2bookIdInRemoveTable(self,title:str):
        """
        输入书本的title，查找数据库中是否有此书
        :param title: 标题
        :return: 不存在，返回None；存在返回第一个找到的book_id
        """
        title = title.replace("'", "\\'")  # type:str
        image_count = self.cursor.execute("""
        SELECT * FROM books_removed 
        WHERE title = '%s'
        """ %( title ))
        results = self.cursor.fetchall()
        if len(results) == 0 : return None
        for res in results:

            return res["book_id"]
    def addTagsToDatabase(self,book_id , tags_catalogs):
        for catalog , tags in tags_catalogs.items():
            for tag in tags:
                tag_id = 0
                if catalog == "":
                    self.cursor.execute("""
                    select tag_id,tag_catalog from tags where 
                    tag_name = '%s'
                    """ % ( tag ))
                else:
                    self.cursor.execute("""
                    select tag_id from tags where 
                    tag_name = '%s' and tag_catalog = '%s'
                    """ % ( tag , catalog))
                results = self.cursor.fetchall()

                if len(results) == 0:
                    if catalog == '': catalog='unknow'
                    self.cursor.execute("""
                    insert into tags (tag_name , tag_catalog) VALUES ( '%s' , '%s')
                    """ % ( tag , catalog))
                    self.sqldb.commit()
                    tag_id = self.cursor.lastrowid
                else:
                    if catalog == '':catalog = results[0]["tag_catalog"]
                    tag_id = results[0]["tag_id"]

                self.cursor.execute("""
                select * from tagmap inner join tags on tagmap.tag_id = tags.tag_id and tagmap.book_id = %d and tags.tag_name = '%s' and tags.tag_catalog = '%s'
                """ % (int(book_id), tag , catalog))
                results = self.cursor.fetchall()
                if len(results) == 0:
                    self.cursor.execute("""
                    insert into tagmap (book_id , tag_id) VALUES ( %d , %d)
                    """ % ( int(book_id) , tag_id))
                    self.sqldb.commit()

    def changeBookTitle(self , book_id , title,book_url=None):
        self.cursor.execute("""
        select * from books where book_id = %d
        """ % ( int(book_id)))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        if not title==None:
            title = title.replace("'","\\'")# type:str

        if not book_url == None:
            eh_id = re.findall("hentai.org/g/(.*?/.*?)/",book_url)[0]
            self.cursor.execute("""
            update books set title = '%s', ehentai_path = '%s' WHERE book_id = %d
            """ % (title, eh_id,int(book_id) ))
        else:
            self.cursor.execute("""
            update books set title = '%s'WHERE book_id = %d
            """ % (title , int(book_id) ) )
        return True


    def changeBookEhentaiId(self , book_id , ehentaiId):
        self.cursor.execute("""
        select * from books where book_id = %d
        """ % ( int(book_id)))
        res = self.cursor.fetchall()
        if len(res) == 0:
            return None
        self.cursor.execute("""
        update books set title = '%s' WHERE book_id = %d
        """ % (ehentaiId , book_id) )
        return True
    def getTagsFromDatabase(self,book_id ):
        self.cursor.execute("""
        select * from tagmap inner join tags on tagmap.tag_id = tags.tag_id and book_id = %d
        """%( book_id))
        res = self.cursor.fetchall()
        if len(res) == 0:return None
        tags_catalogs={}
        for re in res:
            if tags_catalogs.get( re['tag_catalog' ]) == None:
                tags_catalogs[ re['tag_catalog'] ] = []
            tags_catalogs[re['tag_catalog']].append( re['tag_name'])

        return tags_catalogs

    def changeBookCover(self,book_id,page_number,rectX,rectY,rectW,rectH,imgLib = "img",lpfs_dll = None):


        self.cursor.execute("""
         select * from books inner join images on books.book_id = %d and books.page = %d and books.image_type = '%s' and books.image_id = images.image_id
        """ % ( book_id,page_number,img.IMAGE_TYPE_CONTENT))

        res = self.cursor.fetchall()

        if len(res) == 0:
            return False

        #imgPath = imgLib+"/"+res[0]['path']
        imgPath = file.getFilePathFromLPFS(lpfs_dll,res[0]['image_id'])[0]
        print("Use the page path to the cover: "+imgPath)

        newCoverImgName = img.cropImage(imgPath,rectX,rectY,rectW,rectH)

        print("New Cover Name"+newCoverImgName)
        img.addNewSingleCoverImageFileToDatabaseWithBookId( newCoverImgName,self,book_id,res[0]["title"],res[0]['create_time'],lpfs_dll=lpfs_dll)



    def deleteTagFromDatabase(self,book_id , tag_name , tag_catalog):
        self.cursor.execute("""
        select * from tags where tag_catalog = '%s' and tag_name = '%s'
        """ % ( tag_catalog,tag_name))
        res = self.cursor.fetchall()

        if len(res) == 0:
            print("No this tag")
            return False
        tag_id = res[0]['tag_id']
        print("Try to delete tag:"+tag_name+" "+tag_catalog+" "+str(tag_id)+" from "+str(book_id))

        self.cursor.execute("""
        delete from tagmap where book_id = %d and tag_id = %d
        """%( book_id,tag_id))
        self.sqldb.commit()
        print("Delete tag success")

    def clearAllTagsOfBook(self,book_id):
        self.cursor.execute("""
        delete from tagmap where book_id = %d 
        """%( book_id))
        self.sqldb.commit()

    def fileHashInUploadedArchTable(self, fileHash):
        self.cursor.execute("""
        select * from addfilehash where hash = '%s'
        """ % ( fileHash ))

        res = self.cursor.fetchall()

        if len( res ) == 0:
            return False
        if len( res ) > 0 :
            return True

    def addArchFileHashToTable(self,hash):
        self.cursor.execute("""
        insert into addfilehash (hash) VALUES ('%s')
        """ % ( hash ))
        self.sqldb.commit()

    def getImageIdByImagePath(self,image_path):
        img_hash = img.hashPath2Hash(image_path)
        self.cursor.execute("""select image_id from images where hash = '%s' """%(img_hash))

        res = self.cursor.fetchall()
        if len(res)== 0:
            return false
        else:
            return int(res[0]["image_id"])