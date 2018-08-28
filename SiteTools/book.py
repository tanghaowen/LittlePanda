import SiteTools.sql
from SiteTools import img
class bookInfo():
    def __init__(self,sqlManager,imgLibPath="img/"):
        self.content_page = []
        self.title = self.id = None
        self.sqlManager = sqlManager
        self.bookAllInfo = []
        self.imgLibPath = imgLibPath

    def getBookInfoFromDatabase(self,book_id):
        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.book_id = %d
        """ % ( book_id))
        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0 :return None
        self.bookAllInfo = results
        return True
    def getBookInfoFromDatabaseWithoutCover(self,book_id):
        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.book_id = %d
        """ % ( book_id))
        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0 :return None
        res =list(results)
        i = 0
        while i<len(res):
            if res[i]['image_type'] == img.IMAGE_TYPE_COVER_THUMBILE or res[i]['image_type'] == img.IMAGE_TYPE_COVER_CONTENT:
                res.remove(res[i])
                i-=1

            i+=1
        self.bookAllInfo = tuple(res)
        return True
    def getBookInfoFromDatabaseTempInFirstpage(self,book_id):
        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.book_id = %d and books.page = 1
        """ % ( book_id))
        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0 :return None

        return results[0]
    def SearchBooksInfoFromDatabaseOrderByCreateTime(self , keywords):
        search_str = """select * from books inner join images on books.image_id = images.image_id and books.image_type = '%s'and (""" % (img.IMAGE_TYPE_COVER_THUMBILE)
        i = 0
        for keyword in keywords:
            if i == 0:
                search_str+="books.title like '%"+keyword+"%' "
            else:
                 search_str+="and books.title like '%" + keyword + "%' "
            i+=1

        search_str+=""" )order by books.create_time DESC"""
        print(search_str)
        self.sqlManager.cursor.execute(search_str )
        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0: return None
        self.bookAllInfo = results
        return True
    def SearchBooksInfoFromDatabaseOrderByCreateTimeWithTag(self,tag):
        search_str="""
        select * from books , images, tagmap , tags 
        where tags.tag_name = '%s' 
        and tags.tag_id = tagmap.tag_id 
        and tagmap.book_id = books.book_id 
        and books.image_type = 'cover_thumb' 
        and books.image_id = images.image_id
        ORDER BY books.create_time DESC ;
        """ % (tag)




        self.sqlManager.cursor.execute(search_str)
        res = self.sqlManager.cursor.fetchall()

        if len(res) == 0:
            return None
        self.bookAllInfo = res
        return True

    def getBooksCoverThumbInfoFromDatabaseOrderByCreateTimeWithPage(self , page = 1 , items = 10):

        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.page = 1 and books.image_type = '%s' order by books.create_time DESC limit %d,%d;

        """ % ( img.IMAGE_TYPE_COVER_THUMBILE,(page-1)*items , items))

        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0: return None

        self.bookAllInfo = results
        return True
    def getBooksCoverThumbInfoNotHaveEhentaiPathFromDatabaseOrderByCreateTimeWithPage(self , page = 1 , items = 10):

        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.image_type = '%s' and books.page = 1 and ehentai_path is null order by books.create_time DESC limit %d,%d;

        """ % ( img.IMAGE_TYPE_COVER_THUMBILE,(page-1)*items , items))

        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0: return None

        self.bookAllInfo = results
        return True
    def getBooksCoverThumbInfoNotHaveCatalogInfoFromDatabaseOrderByCreateTimeWithPage(self , page = 1 , items = 10):

        self.sqlManager.cursor.execute("""
        SELECT * FROM tagmap;
        """)
        tagMap = {}
        all_books = []
        books_have_catalog = []
        books_not_have_catalog = []
        res = self.sqlManager.cursor.fetchall()

        for i in res:
            item = tagMap.get(i['book_id'], None)
            if item == None: tagMap[i['book_id']] = []

            tagMap[i['book_id']].append(i['tag_id'])

        for book_id, tags in tagMap.items():
            all_books.append(book_id)
            for tag in tags:
                if tag in [1213, 1446, 2049, 3683,3684]:
                    books_have_catalog.append(book_id)
                    break

        for book_id in all_books:
            if not book_id in books_have_catalog:
                books_not_have_catalog.append(book_id)

        format_strings = ','.join(['%s'] * len(books_not_have_catalog))
        self.sqlManager.cursor.execute("""
        select * from books,images where books.page=1 and books.image_type = 'cover_thumb' and books.book_id in (%s) AND 
        books.image_id = images.image_id
        order by books.create_time DESC limit %d,%d;

        """ % (format_strings,(page-1)*items , items), tuple(books_not_have_catalog))


        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0: return None

        self.bookAllInfo = results
        return True
    def getBooksInfoFromDatabaseOrderByCreateTimeWithPage(self , page = 1 , items = 10):
        self.sqlManager.cursor.execute("""
        select * from books inner join images on books.image_id = images.image_id and books.image_type = '%s' and books.page = 1 order by books.create_time DESC limit %d,%d;

        """ % (img.IMAGE_TYPE_CONTENT_THUMBILE , (page-1)*items , items))
        results = self.sqlManager.cursor.fetchall()
        if len(results) == 0: return None
        self.bookAllInfo = results
        return True
    def getAllContentImagePath(self):
        content_images_path = []
        for hon in self.bookAllInfo:
            if hon["image_type"] == img.IMAGE_TYPE_CONTENT:
                content_images_path.append(hon["path"])

        return content_images_path
    def getAllContentImageHash(self):
        content_images_path = []
        for hon in self.bookAllInfo:
            if hon["image_type"] == img.IMAGE_TYPE_CONTENT:
                content_images_path.append(hon["hash"])

        return content_images_path

    def filteOutAllContentImage(self):
        books = []
        for book in self.bookAllInfo:
            if book["image_type"] == img.IMAGE_TYPE_CONTENT:
                books.append( book )
        return books
    def getAllContentThumbImagePath(self):
        content_images_path = []
        for hon in self.bookAllInfo:
            if hon["image_type"] == img.IMAGE_TYPE_CONTENT_THUMBILE:
                content_images_path.append(self.imgLibPath+hon["path"])

        return content_images_path

    def getCoverImageThumb(self):

        for hon in self.bookAllInfo:
            if hon["image_type"] == img.IMAGE_TYPE_CONTENT_THUMBILE and hon["page"] == 1:
                return  self.imgLibPath+hon["path"]

    def getRemovedBooks(self):
        self.sqlManager.cursor.execute("""
        select * from books_removed where page = 1 and image_type = '%s'
        """ % img.IMAGE_TYPE_COVER_THUMBILE)

        res = self.sqlManager.cursor.fetchall()
        if len(res) == 0:
            return None
        self.bookAllInfo = res

    def getPageWithBookId(self,book_id,page):
        que = """
         select * from books inner join images on books.image_id = images.image_id and books.book_id = %d and books.page = %d and image_type = '%s'
        """ %(int(book_id),int(page),img.IMAGE_TYPE_CONTENT)
        self.sqlManager.cursor.execute(que)
        res = self.sqlManager.cursor.fetchall()
        if len(res) == 0:
            return None
        self.bookAllInfo = res
        return True

    def getRandom20Book(self):
        self.sqlManager.cursor.execute("""
                select * from books inner join images on books.image_id = images.image_id and books.image_type = '%s' and books.page = 1 order by RAND() limit 20"""
                                       %(img.IMAGE_TYPE_COVER_THUMBILE))

        self.bookAllInfo = self.sqlManager.cursor.fetchall()
