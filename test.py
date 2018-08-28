from SiteTools import img
from SiteTools import sql
from SiteTools import file
import SiteTools.book
from SiteTools import ehentai
from SiteTools import book
import queue
from queue import Queue
import time
import flaskSite
import threading
from ctypes import *
"""
tmpPath = "tmp/"
uploadedArchPath = tmpPath + "uploadedArch/"
sqlManager = sql.sqlDataManager()

bookInfo = book.bookInfo(sqlManager)

bookInfo.getBookInfoFromDatabase(300)
l=list(bookInfo.bookAllInfo)
tmp = l[0]["image_id"]
l[0]["image_id"] = l[10]["image_id"]
l[10]["image_id"] = tmp
l.append(l[0])
l.append(l[1])
l.append(l[2])
l.append(l[2])
l.append(l[2])
l.append(l[2])
l.append(l[2])
l.append(l[2])
l.append(l[2])
sqlManager.changeBookInfo(300,l)
sqlManager.sqldb.commit()

archNames , archPaths =  file.getAllArchFilesInfo(uploadedArchPath)

for index , archname in enumerate( archNames):
    print("Progress:"+ str(index+1)+" / "+ str(len(archNames)))
    img.addNewArchFileToImgLib(archname, sqlManager,
                               archname[0:-4],
                               )



title , tags_catalogs , book_catalog , comments = ehentai.getBookInfoFromEhentai("https://e-hentai.org/g/1119061/7e9d4d4b85/")
# ehentai.searchInEhentai("clannad")
sqlManager.getTagsFromDatabase(2)


print(file.dealWithFileName("(成年コミック) [丸居まる] 貼ったらヤレちゃう！？ えろシール～ワガママJKのアソコをたった1枚で奴隷に～ 1-9 [DL版] "))



exhentai = ehentai.exHentaiRequest()
url = exhentai.search("clannad")[0]["url"]
print(url)
exhentai.getBookInfoFromEhentai(url)
sqlManager.changeBookCover(432,1,0,0,1000,1000)


sqlManager.deleteTagFromDatabase(472,"shotacon","male")
sqlManager.sqldb.commit()

sqlManager.addTagsToDatabase(472,{"mangazin":["kairakuten"]})





def checkQueue(que:queue.Queue,ehentai:SiteTools.ehentai.exHentaiRequest):
    while True:
        next_job_url = que.get()
        arch_fileName = ehentai.downloadArch( next_job_url)
        img.addNewArchFileToImgLib(arch_fileName, sqlM,
                                   arch_fileName[0:-4],
                                   "tmp/downloadedFile/")
q = queue.Queue()
thread_check_queue = Thread(target=checkQueue,args=[q,ehentai])
thread_check_queue.start()


time.sleep(4)
q.put("https://exhentai.org/g/1128522/098894ab3d/")


sqlM = sql.sqlDataManager()


sqlM.deleteBookFromDatabase(1317)
sqlM.sqldb.commit()
sqlM.sqldb.close()



l = file.getAllFiles("tmp/")
print(l)
"""
sqlM = sql.sqlDataManager()

sqlM.cursor.execute("""
SELECT * FROM tagmap;
""")
tagMap = {}
all_books =[]
books_have_catalog = []
books_not_have_catalog = []
res = sqlM.cursor.fetchall()

for i in res:
    item = tagMap.get(i['book_id'],None)
    if item == None: tagMap[i['book_id']] = []

    tagMap[i['book_id']].append(i['tag_id'])


for book_id, tags in tagMap.items():
    all_books.append(book_id)
    for tag in tags:
        if tag in [1213,1446,2049,3683]:
            books_have_catalog.append( book_id)
            break


for book_id in all_books:
    if not book_id in books_have_catalog:
        books_not_have_catalog.append(book_id)


format_strings = ','.join(['%s'] * len(books_not_have_catalog))

sqlM.cursor.execute("""
select * from books where books.page=1 and books.image_type = 'content_image' and books.book_id in (%s)

""" % format_strings,tuple(books_not_have_catalog))
res = sqlM.cursor.fetchall()

exhentaiRequest = ehentai.exHentaiRequest(
    "ipb_member_id=1895088; ipb_pass_hash=b179347632dbd0f9145ba7cb2ffd8fc8; yay=louder; igneous=77ce340a6; lv=1507097240-1507097540")

sqlM.cursor.execute("""
select * from books where books.page=1 and books.image_type = 'content_image' and books.ehentai_path is not null;
""")
res = sqlM.cursor.fetchall()

for book in res:
    if book["book_id"] in books_not_have_catalog:
        print("Start to deal with the book id:"+str(book["book_id"]) +"  http://127.0.0.1:5000/gallery/"+str(book["book_id"]))

        book_url = "https://exhentai.org/g/"+book['ehentai_path']
        title, tags_catalogs, book_catalog, comments = exhentaiRequest.getBookInfoFromEhentai(book_url)

        sqlM.addTagsToDatabase(book["book_id"], {"catalog":[book_catalog]})
