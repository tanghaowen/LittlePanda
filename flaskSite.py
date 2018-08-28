from flask import Flask
from flask import request
from flask import make_response
from flask import render_template
from flask import send_file
from flask import abort
from flask import redirect
import os
import time
from SiteTools import zipClass
from SiteTools import sql
from SiteTools import book
from SiteTools import ehentai
from SiteTools import file
from queue import Queue
from threading import Thread
import img
from SiteTools import img
import json
import copy
from flask import abort
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from ctypes import *

app = Flask(__name__)


@app.route("/img/<path:image_id>")
def get_image(image_id):
    global lpfs_dll
    image_id_low = image_id.lower()

    sqlM = sql.sqlDataManager()
    #img_id =sqlM.getImageIdByImagePath(image_id)
    img_id = sqlM.hash2imageId(image_id);
    sqlM.sqldb.commit()
    sqlM.sqldb.close()
    paths = file.getFilePathFromLPFS(lpfs_dll,img_id)
    if paths == False: return "Error,type of image_id is not list or tuple or int!"
    exacted_image_path = None;
    for i in paths:
        if not i == None:
            exacted_image_path = i;
            break
    print(image_id+exacted_image_path)
    if "ERROR!" in exacted_image_path:
        return "No this image!"
        if ".jpg" in image_id_low:
            return send_file("img/" + image_id, mimetype="image/jpeg")
        elif ".png" in image_id_low:
            return send_file("img/" + image_id, mimetype="image/png")
        elif ".bmp" in image_id_low:
            return send_file("img/" + image_id, mimetype="image/bmp")
    return send_file(exacted_image_path, mimetype="image/bmp")

@app.route("/gallery/<gallery_id>")
def get_gallery(gallery_id:str):

    sqlM = sql.sqlDataManager()
    if not gallery_id.isdigit():
        return "gallery id error"
    gallery_id = int(gallery_id)
    tag_group={"aritsi":["jinjia","nishi"],"para":["clannad","is","is","is","is","is","is","is","is","is","is","is"]}
    bookInfo = book.bookInfo(sqlM)
    book_info_res =  bookInfo.getBookInfoFromDatabaseWithoutCover(gallery_id)

    if book_info_res == None:
        return "No this Gallery"
    book_contentImages = bookInfo.filteOutAllContentImage()
    book_size = 0
    for bk in book_contentImages:
        book_size+=int(bk["size"])
    book_size/=1000000

    tags_groups = sqlM.getTagsFromDatabase(gallery_id)
    if tags_groups == None:tags_groups={}
    sqlM.sqldb.close()
    return render_template("gallery.html",search_title = file.dealWithFileName(bookInfo.bookAllInfo[0]['title']),title = bookInfo.bookAllInfo[0]['title'],tagGroup=tags_groups,books=book_contentImages,book_size = book_size , content_images = json.dumps( bookInfo.getAllContentImageHash()),gallery_id = gallery_id)
@app.route("/editGallery",methods=['GET','POST'])
def editGalery():

    if request.method == 'GET':
        book_id = request.args.get("id")
        book_id = int(book_id)
        sqlM=sql.sqlDataManager()
        bookInfo = book.bookInfo(sqlM)

        bookInfo.getBookInfoFromDatabaseWithoutCover(book_id)
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
        return render_template("editGallery.html",pages = bookInfo.bookAllInfo)
    elif request.method == 'POST':
        jso = request.get_data()
        new_book_order = json.loads(jso)
        sqlM = sql.sqlDataManager()
        bookInfo = book.bookInfo(sqlM)
        book_id = new_book_order['book_id']
        new_book_order = new_book_order['pageOrder']
        bookInfo.getBookInfoFromDatabaseWithoutCover(book_id)
        print(new_book_order)
        pageList=list(bookInfo.bookAllInfo)
        pageList = copy.deepcopy(pageList)
        print(pageList)

        for index in range(0,len(pageList),2):
            page = int(pageList[index]['page'])
            newPage = new_book_order[page-1]
            newPageIndex = (newPage-1)*2


            pageList[index]['image_id'] = bookInfo.bookAllInfo[  newPageIndex ]['image_id']
            pageList[index+1]['image_id'] = bookInfo.bookAllInfo[newPageIndex+1]['image_id']

        sqlM.changeBookInfo(book_id, pageList)
        sqlM.sqldb.commit()
        return redirect("/gallery/"+str(book_id),code = 280)
@app.route("/downfromEx",methods=["POST"])
def downloadFromExhentai():
    if request.method =='POST':
        json_string = request.get_data()
        json_data = json.loads(json_string)


        download_eh_queue.put(json_data["exurl"])
        download_eh_list[json_data["exurl"]] = "wait"

        return ""
@app.route("/editGalleryCover",methods=['GET','POST'])
def editGalleryCover():
    if request.method == 'POST':
        jso = request.get_data()
        newCoverJson = json.loads( jso )
        book_id = newCoverJson['book_id']
        cover_page_number = newCoverJson['page']
        recX,recY,recW,recH = newCoverJson['rectInfo']
    elif request.method == 'GET':
        book_id= request.args.get("book_id")
        page = request.args.get("page")
        sqlM=sql.sqlDataManager()
        bookInfo = book.bookInfo(sqlM)

        if (bookInfo.getPageWithBookId(book_id,page)) == None:
            return "No this Page In gallery"
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
        return render_template("cropCover.html",pageInfo = bookInfo.bookAllInfo[0],book_id=book_id,page=page)
@app.route("/cropGalleryCover",methods=['POST'])
def cropGalleryCover():
    global lpfs_dll
    if request.method == 'POST':
        jso = request.get_data()
        newCoverInfoJson = json.loads( jso)
        book_id = newCoverInfoJson['book_id']
        page = newCoverInfoJson['page']
        startX,startY,endX,endY = newCoverInfoJson['rect']

        print(startX)
        print(startY)
        print(endX )
        print(endY)
        sqlM = sql.sqlDataManager()
        sqlM.changeBookCover(book_id,page,startX,startY,endX,endY,lpfs_dll=lpfs_dll)
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
        return redirect("/gallery/"+str(book_id),code = 280)
@app.route("/downloadarch/<gallery_id>",methods=['GET','POST'])
def download_gallery(gallery_id:str):
    if not gallery_id.isdigit():
        return "gallery id error"
    gallery_id = int(gallery_id)
    tag_group={"aritsi":["jinjia","nishi"],"para":["clannad","is","is","is","is","is","is","is","is","is","is","is"]}
    bookInfo = book.bookInfo(sqlManager)
    book_info_res =  bookInfo.getBookInfoFromDatabase(gallery_id)

    if book_info_res == None:
        return "No this Gallery"
    book_contentImages = bookInfo.filteOutAllContentImage()
    zipClass.createZipArch(bookInfo.bookAllInfo[0]["title"],book_contentImages)
    return ""
@app.route("/test/")
@app.route("/test/<test_name>",methods=['GET','POST'])
def test(test_name=None):
    if request.method == 'POST':
        return 'post'
    elif request.method == 'GET':
        return  render_template("index.html",keyword=test_name)
@app.route("/delete",methods=['GET','POST'])
def delete():
    if request.method == 'POST':
        delete_type = request.form['type']
        delete_target = request.form['target']
        end_page = request.form['page']

        if delete_type  == 'gallery':
            sqlM = sql.sqlDataManager()
            sqlM.deleteBookFromDatabaseToTmpTable( int(delete_target))
            sqlM.sqldb.commit()
            sqlM.sqldb.close()
            return redirect("/")
        if delete_type  == 'gallery_direct':
            sqlM = sql.sqlDataManager()
            sqlM.deleteBookFromDatabaseDirect( int(delete_target))
            sqlM.sqldb.commit()
            sqlM.sqldb.close()
            return redirect("/")
@app.route("/search",methods=['GET','POST'])
def search():
    sqlM = sql.sqlDataManager()
    if request.method == 'POST':
        search_keyword = request.form['keyword'] # type: str
        search_keywords = search_keyword.split(" ")
        search_books = book.bookInfo(sqlM)
        search_books.SearchBooksInfoFromDatabaseOrderByCreateTime( search_keywords)
        sqlM.sqldb.close()
        return render_template("searchpage.html", books=search_books.bookAllInfo, nowPage=1)
    if request.method == 'GET':
        search_tag = request.args.get("tag")
        bookInfo = book.bookInfo(sqlM)
        bookInfo.SearchBooksInfoFromDatabaseOrderByCreateTimeWithTag( search_tag)
        sqlM.sqldb.close()
        return render_template("searchpage.html" , books = bookInfo.bookAllInfo,nowPage = 1)
@app.route("/random",methods=['GET','POST'])
def randomGallery():
    sqlM = sql.sqlDataManager()
    if request.method == 'GET':
        bookInfo = book.bookInfo(sqlM)
        bookInfo.getRandom20Book()
        return render_template("searchpage.html" , books = bookInfo.bookAllInfo,nowPage = 1)
@app.route("/searcheh",methods=['GET','POST'])
def searchEh():
    global tmp_book_title
    global tmp_book_tags_groups
    global tmp_book_catalog
    global tmp_book_url
    global tmp_book_infos
    if request.method == 'GET':
        search_keyword = request.args.get("keyword")
        target_book_id = request.args.get("bookid")
        if "e-hentai.org" in search_keyword or "exhentai.org" in search_keyword:

            book_url = search_keyword
            book_id = target_book_id
            tmp_book_infos[book_id+" - "+book_url] = {}
            tmp_book_infos[book_id + " - " + book_url]["url"] = book_url
            title, tags_catalogs, book_catalog, comments = exhentaiRequest.getBookInfoFromEhentai( book_url)
            tmp_book_infos[book_id + " - " + book_url]["title"] = title
            tmp_book_infos[book_id + " - " + book_url]["tags"] = tags_catalogs
            tags_catalogs['catalog'] = [book_catalog]
            tmp_book_infos[book_id + " - " + book_url]["cata"] = book_catalog
            return render_template("ehentaiBookInfo.html" ,book_id = book_id, title = title , tagGroup = tags_catalogs ,book_catalog = book_catalog, book_url = book_url)


        res_li = exhentaiRequest.search(search_keyword)
        if len(res_li) == 0:return "No Search Resault"
        return render_template("searchEhentaiRes.html", res_list=res_li ,book_id = target_book_id)
    if request.method == 'POST':

        data = request.get_data()
        json_data = json.loads(data)

        book_url = json_data.get("url","") # type: str
        type = json_data['type']
        book_id = json_data["book_id"]

        if type == 'get_book_info':


            return redirect("/fuckyoujavascript?book_url="+book_url+"&book_id="+str(book_id) , code=280)

        elif type=="settags":
            bookin = tmp_book_infos[str(book_id) + " - " + book_url]
            sqlM = sql.sqlDataManager()
            sqlM.changeBookTitle( book_id,bookin["title"],bookin["url"]);
            sqlM.addTagsToDatabase(book_id,bookin["tags"])
            sqlM.sqldb.commit()
            sqlM.sqldb.close()
            return redirect("/gallery/"+str(book_id))
@app.route("/fuckyoujavascript")
def fuckyouJs():
    global tmp_book_title
    global tmp_book_tags_groups
    global tmp_book_catalog
    global tmp_book_url
    global tmp_book_infos
    book_id = request.args.get("book_id")
    book_url = request.args.get("book_url")

    title, tags_catalogs, book_catalog, comments = exhentaiRequest.getBookInfoFromEhentai(book_url)
    tags_catalogs["catalog"] = [book_catalog]
    tmp_book_infos[book_id + " - " + book_url] = {}
    tmp_book_infos[book_id + " - " + book_url]["title"] = title
    tmp_book_infos[book_id + " - " + book_url]["tags"] = tags_catalogs
    tmp_book_infos[book_id + " - " + book_url]["url"] = book_url
    tmp_book_infos[book_id + " - " + book_url]["cata"] = book_catalog
    tmp_book_catalog = book_catalog
    return render_template("ehentaiBookInfo.html", book_id=book_id, title=title, tagGroup=tags_catalogs,
                           book_catalog=book_catalog , book_url = book_url)
@app.route("/edittag",methods=["POST"])
def editTage():
    if request.method == "POST":
        post_data = request.get_data()
        data_json = json.loads(post_data)

        command = data_json['command']
        data = data_json['data']
        book_id = data_json['book_id']


        if command == 'delete':
            tag_catalog = data['catalog']
            tag_name = data['name']
            sqlM=sql.sqlDataManager()
            sqlM.deleteTagFromDatabase(book_id,tag_name,tag_catalog)
            sqlM.sqldb.commit()
            sqlM.sqldb.close()
            return "Mid"
        elif command == 'add':
            sqlM = sql.sqlDataManager()
            sqlM.addTagsToDatabase(book_id,data)
            sqlM.sqldb.commit()
            sqlM.sqldb.close()
            return redirect("/gallery/"+str(book_id),code=280)
@app.route("/editTitle",methods=["POST"])
def editTitle():
    if request.method == 'POST':
        post_data = request.get_data()
        data_json = json.loads(post_data)

        book_id = data_json['book_id']
        title = data_json['title']
        sqlM = sql.sqlDataManager()
        sqlM.changeBookTitle(book_id,title)
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
        return redirect("/gallery/"+str(book_id), code=280)
@app.route("/manage",methods=['GET','POST'])
def manageLittlePanda():
    global lpfs_dll
    global adding_to_sys_status
    if request.method == 'GET':
        sqlM = sql.sqlDataManager()
        book_removed = book.bookInfo(sqlM)
        book_removed.getRemovedBooks()
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
        return render_template("managePage.html",removed_books = book_removed.bookAllInfo,archpath = uploadedArchPath )
    if request.method == 'POST':
        jso = request.get_data()
        data = json.loads( jso )
        actionType = data.get('type')
        actionData = data.get('data')
        sqlManager2 = sql.sqlDataManager()
        archPath = actionData
        print("actionYpe: "+actionType)
        print("actionData: "+actionData)
        adding_to_sys_status = {}
        file.importArchFileFromTmp(sqlManager2,archPath,status=adding_to_sys_status,lpfs_dll=lpfs_dll)
        return actionType
@app.route("/")
def homepage():



    page = int(request.args.get("page",1))
    items = int(request.args.get("items",20))
    gid_mode = int(request.args.get("gid",1))
    mode = request.args.get("mode","normal")

    if page < 1:
        page =1
    sqlM = sql.sqlDataManager()
    home_page_books = book.bookInfo(sqlM)


    if gid_mode == 1:
        items = 40
        if mode == "findnoehpath":
            home_page_books.getBooksCoverThumbInfoNotHaveCatalogInfoFromDatabaseOrderByCreateTimeWithPage(page,items)
            return render_template("homepage_gid_findnoehpath.html", books=home_page_books.bookAllInfo, nowPage=page)

        else:
            if(home_page_books.getBooksCoverThumbInfoFromDatabaseOrderByCreateTimeWithPage(page, items)) == None:
                return "Gallery no book"
        return render_template("homepage_gid.html",books=home_page_books.bookAllInfo , nowPage = page)
    else:
        items = 40
        if home_page_books.getBooksCoverThumbInfoFromDatabaseOrderByCreateTimeWithPage(page, items) == None:
            return "Gallery no book"

        return render_template("homepage_gid.html",books=home_page_books.bookAllInfo , nowPage = page)
@app.route("/task")
def taskProcess():
    global adding_to_sys_status
    if not request.method == "GET":
        return abort(404)
    taskType = request.args.get("type")
    taskID = request.args.get("taskID")
    if taskType == 'downloadeh':
        status_list = []
        for url , status in download_eh_list.items():
            status_list.append( [ url, status])

        download_json_statuts = json.dumps( status_list )
        return download_json_statuts
    if taskType == 'addingtosys':
        status_list_string = json.dumps( adding_to_sys_status )
        return status_list_string









def checkQueue(que, ehentai):
    while True:
        next_job_url = que.get()

        download_eh_list[next_job_url] = "downloading"
        arch_fileName = ehentai.downloadArch(next_job_url,download_eh_list)
        download_eh_list[next_job_url] = "adding"
        sqlM = sql.sqlDataManager()
        book_id = img.addNewArchFileToImgLibWithProgress(arch_fileName, sqlM,
                                   arch_fileName[0:-4],
                                   "tmp/downloadedFile/",[download_eh_list[next_job_url]],0,lpfs_dll=lpfs_dll)
        title, tags_catalogs, book_catalog, comments = ehentai.getBookInfoFromEhentai(next_job_url)
        tags_catalogs['catalog'] = [book_catalog]
        print("Changing Title")

        sqlM.changeBookTitle(book_id, title,next_job_url);
        print("Adding Tags")
        sqlM.addTagsToDatabase(book_id, tags_catalogs)
        print("Over")
        download_eh_list[next_job_url] = "over"
        sqlM.sqldb.commit()
        sqlM.sqldb.close()
def uploadedFileDirMoniter( dirPath):
    global adding_to_sys_status
    global now_adding_arch_file
    while True:

        print("Start scan uploaded directory:"+ dirPath)
        adding_to_sys_status = {}
        sqlM = sql.sqlDataManager()
        now_adding_arch_file = True
        file.importArchFileFromTmp(sqlM,dirPath,status=adding_to_sys_status)
        now_adding_arch_file = False
        print("Auto scan and adding over, wait for 120s.")
        time.sleep( 120)
if __name__ == '__main__':
    sqlManager = sql.sqlDataManager()
    tmp_book_title = tmp_book_tags_groups = tmp_book_catalog = tmp_book_url =""
    tmp_book_infos = {}
    exhentaiRequest = ehentai.exHentaiRequest("ipb_member_id=1895088; ipb_pass_hash=b179347632dbd0f9145ba7cb2ffd8fc8; igneous=77ce340a6; lv=1526364287-1526578611; s=9ce4959a5; sk=poju5lt5udz7dqen43zo7qjd1uk9")
    imgLib = 'img/'
    tmpLib = 'tmp/'
    uploadedArchPath = 'F:\\LPFS_LIB\\tmp\\'

    autoscanArchPath = 'F:\\LPFS_LIB\\tmp\\'



    download_eh_queue = Queue()
    download_eh_list = {}
    adding_to_sys_status = {}
    thread_check_queue = Thread(target=checkQueue, args=[download_eh_queue, exhentaiRequest])
    thread_check_queue.start()

    add_arch_to_system_queue = Queue()
    now_adding_arch_file = False
    #thread_auto_scan_path = Thread(target=uploadedFileDirMoniter, args=[autoscanArchPath])
    #thread_auto_scan_path.start()


    """event_handler = file.MyHandler()
    observer = Observer()
    observer.schedule(event_handler, uploadedArchPath, recursive=True)
    observer.start()"""
    LPFS_LIB_PATH = c_wchar_p("F:/LPFS_LIB")
    image_lib_path = c_wchar_p("E:\\Project\\flaskSite\\img")
    exact_path = c_wchar_p("F:\\LPFS_LIB\\cache")
    tmp_path = c_wchar_p("E:\\Project\\flaskSite")
    lpfs_dll = windll.LoadLibrary("E:\\Project\\LittlePandaFS\\LittlePandaFileSystem\\x64\\Debug\\LPFS_DLL.dll")
    lpfs_dll.init(LPFS_LIB_PATH, image_lib_path, exact_path,tmp_path, 1024)






    app.run(host='0.0.0.0', debug=True,threaded = True)

    #app.run(host='0.0.0.0', debug=True)
