import requests
import bs4
from SiteTools import sql
import re
tag_trans_catalog = {
        "artist":"https://github.com/Mapaler/EhTagTranslator/wiki/artist",
        "female": "https://github.com/Mapaler/EhTagTranslator/wiki/female",
         "male":"https://github.com/Mapaler/EhTagTranslator/wiki/male",
        "parody": "https://github.com/Mapaler/EhTagTranslator/wiki/parody",
        "character":"https://github.com/Mapaler/EhTagTranslator/wiki/character",
        "group":"https://github.com/Mapaler/EhTagTranslator/wiki/group",
        "language":"https://github.com/Mapaler/EhTagTranslator/wiki/language",
        "reclass":"https://github.com/Mapaler/EhTagTranslator/wiki/reclass",
        "misc":"https://github.com/Mapaler/EhTagTranslator/wiki/misc"}

def getBookInfoFromEhentai(ehentai_url):
    tags_catalogs = {}

    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    proxies = {
      "http": "http://127.0.0.1:1080",
      "https": "http://127.0.0.1:1080",
    }

    r = requests.get(ehentai_url , headers = headers ,proxies = proxies)
    content = r.content.decode("utf-8")
    soup = bs4.BeautifulSoup( content )

    tag_catalogs = soup.select("div#taglist > table > tr")
    for catalog in tag_catalogs:

        cata_str =  catalog.select("td.tc")[0].string # type:str
        cata_str = cata_str.replace(":","")

        tags_catalogs[cata_str]=[]
        print(cata_str)

        tags = catalog.select("a")
        for tag in tags:
            print("\t"+tag.string)
            tags_catalogs[cata_str].append(tag.string)

    book_catalog = soup.select("div#gdc > a")[0]['href']
    if 'doujin' in book_catalog:
        book_catalog = 'doujin'
    elif 'manga' in book_catalog:
        book_catalog = 'manga'
    elif 'cosplay' in book_catalog:
        book_catalog = 'cosplay'
    elif 'gamecg' in book_catalog:
        book_catalog = 'gamecg'
    else:
        book_catalog = 'other'
    print(book_catalog)
    print()

    comments_div = soup.select("div#cdiv")[0].select(".c6")
    comments = []
    for comm in comments_div:
        comments.append(comm.find_all_next(string=True))
    print(comments)

    title = soup.select("#gj")[0].string
    print( title )

    return [title , tags_catalogs , book_catalog , comments]
def searchInEhentai(keyword):
    searchUrl = "https://e-hentai.org/?f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=1&f_non-h=1&f_imageset=1&f_cosplay=1&f_asianporn=1&f_misc=1&f_search="+keyword+"&f_apply=Apply+Filter"
    # searchUrl = "https://exhentai.org/?f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=1&f_asianporn=0&f_misc=0&f_search="+keyword+"&f_apply=Apply+Filter&advsearch=1&f_sname=on&f_stags=on&f_sdesc=on&f_storr=on&f_sdt1=on&f_sdt2=on&f_sh=on&f_sr=on&f_srdd=2"
 
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
    proxies = {
      "http": "http://127.0.0.1:1080",
      "https": "http://127.0.0.1:1080",
    }
    r = requests.get(searchUrl , headers = headers ,proxies = proxies)
    search_content = r.content.decode("utf-8")
    soup = bs4.BeautifulSoup( search_content )

    searchList = soup.select("table.itg > tr")

    list = []
    for li in searchList:

        if li.get("class") == None:
            continue
        if "gtr" in li.get("class")[0]:
            list.append( li )


    res_list = []
    for li in list:
        url = li.select("div.it5 > a")[0]["href"]
        title = li.select("div.it5 > a")[0].string
        res = li.select("div.it2 > img")
        if len(li.select("div.it2 > img"))>0:
            img_url = li.select("div.it2 > img")[0]["src"]
        else:
            text =  li.select("div.it2")[0].string

            domain = re.findall("inits~(.*?)~t" , text)[0]
            path = re.findall("~(t.*?)~",text)[0]
            img_url = "https://"+domain+"/"+path
            print(res)
        print( url , title)
        res_list.append( {"url":url,"title":title , "img_url":img_url})

    return res_list


def getTagChineseTranslate( catalog , tag ,sqlManager:sql.sqlDataManager):

    if catalog == "artist":
        url = tag_trans_catalog["artist"]
    elif catalog == "female":
        tag_trans_catalog["female"]
    elif catalog == "male":
        tag_trans_catalog["male"]
    elif catalog == "parody":
        tag_trans_catalog["parody"]
    elif catalog == "character":
        tag_trans_catalog["character"]
    elif catalog == "group":
        tag_trans_catalog["group"]
    elif catalog == "language":
        tag_trans_catalog["language"]
    elif catalog == "reclass":
        tag_trans_catalog["reclass"]
    elif catalog == "misc":
        tag_trans_catalog["misc"]

    r = requests.get(url=url)
    content = r.content.decode("utf-8")

    soup = bs4.BeautifulSoup(content)

    list = soup.select("table > tbody > tr")
    tags_trans = []
    for li in list:
        tds = li.select("td")
        tags_trans.append([ tds[0].string , tds[1].string])
    print(tags_trans)

    sqlManager.cursor.execute("""
    select * from tagtranslate WHERE ori_name = `%s`
    """ % ( tag ))
    results = sqlManager.cursor.fetchall()
    if len(results) == 0:
        return tag
    return results[0]
def updateTranslate( sqlManager:sql.sqlDataManager):
    for cata,url in tag_trans_catalog.items():
        r = requests.get(url=url)
        content = r.content.decode("utf-8")

        soup = bs4.BeautifulSoup(content)
        list = soup.select("table > tbody > tr")

        for li in list:
            tds = li.select("td")
            if tds[0].string == None:continue
            updateTranslateToDatabase( tds[0].string ,cata, tds[1].string ,sqlManager)
def updateTranslateToDatabase(tag_ori,tag_trans,catalog,sqlManager:sql.sqlDataManager):
    sqlManager.cursor.execute("""
    select translate_id from tagtranslate 
    where ori_name = '%s'
    """ %( tag_ori))

    resault = sqlManager.cursor.fetchall()
    if len(resault) == 0:

        print("Insert new tag translate... Catalog:"+catalog,tag_trans)

        sqlManager.cursor.execute("""
        insert into tagtranslate (ori_name,cata,translate_name) VALUES ( '%s' , '%s', '%s')
        """ %( tag_ori ,catalog, tag_trans))
    else:
        sqlManager.cursor.execute("""
        insert into tagtranslate (ori_name,translate_name) VALUES ( `%s` , `%s`)
        """ %( tag_ori , tag_trans))



class exHentaiRequest():
    heads = {"Host":"exhentai.org",
             "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0",
             "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
             "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
             "Accept-Encoding":"deflate, br",
             "Content-Type":"application/x-www-form-urlencoded",
             "Referer":"https://e-hentai.org/bounce_login.php?b=d&bt=1-2"}
    proxies = {
        "http": "http://127.0.0.1:1080",
        "https": "http://127.0.0.1:1080",
    }
    def __init__(self,cookie_str):
        self.session = requests.Session()
        self.heads["Cookie"]=cookie_str
        self.session.headers.update(self.heads)

    def getPage(self):
        res = self.session.get("https://exhentai.org")
        print(res.text)

    def search(self,keyword):
        # searchUrl = "https://exhentai.org/?f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=1&f_non-h=1&f_imageset=1&f_cosplay=1&f_asianporn=1&f_misc=1&f_search="+keyword+"&f_apply=Apply+Filter"
        searchUrl = "https://exhentai.org/?f_doujinshi=1&f_manga=1&f_artistcg=1&f_gamecg=1&f_western=0&f_non-h=1&f_imageset=0&f_cosplay=1&f_asianporn=0&f_misc=0&f_search="+keyword+"&f_apply=Apply+Filter&advsearch=1&f_sname=on&f_stags=on&f_sdesc=on&f_storr=on&f_sdt1=on&f_sdt2=on&f_sh=on&f_sr=on&f_srdd=2"

        print(searchUrl)
        r = self.session.get(searchUrl,proxies = self.proxies )
        search_content = r.content.decode("utf-8")
        soup = bs4.BeautifulSoup( search_content )

        searchList = soup.select("table.itg > tr")

        list = []
        for li in searchList:

            if li.get("class") == None:
                continue
            if "gtr" in li.get("class")[0]:
                list.append( li )


        res_list = []
        for li in list:
            url = li.select("div.it5 > a")[0]["href"]
            title = li.select("div.it5 > a")[0].string
            res = li.select("div.it2 > img")
            if len(li.select("div.it2 > img"))>0:
                img_url = li.select("div.it2 > img")[0]["src"]
                print(img_url)
            else:
                text =  li.select("div.it2")[0].string

                domain = re.findall("inits~(.*?)~t" , text)[0]
                path = re.findall("~(t.*?)~",text)[0]
                img_url = "https://"+domain+"/"+path
                print(img_url)
                print(res)
            print( url , title)
            res_list.append( {"url":url,"title":title , "img_url":img_url})

        return res_list

    def getBookInfoFromEhentai(self,ehentai_url):
        tags_catalogs = {}

        r = self.session.get(ehentai_url ,proxies = self.proxies )
        content = r.content.decode("utf-8")
        if 'This gallery has been removed or is unavailable' in content:
            print("This gallery in ehentai are removed.")
            return ["Gallery removed", {}, "manga", ""]
        soup = bs4.BeautifulSoup( content )

        tag_catalogs = soup.select("div#taglist > table > tr")
        for catalog in tag_catalogs:

            cata_str =  catalog.select("td.tc")[0].string # type:str
            cata_str = cata_str.replace(":","")

            tags_catalogs[cata_str]=[]
            print(cata_str)

            tags = catalog.select("a")
            for tag in tags:
                print("\t"+tag.string)
                tags_catalogs[cata_str].append(tag.string)

        book_catalog = soup.select("div#gdc > a")[0]['href']
        if 'doujin' in book_catalog:
            book_catalog = 'doujin'
        elif 'manga' in book_catalog:
            book_catalog = 'manga'
        elif 'cosplay' in book_catalog:
            book_catalog = 'cosplay'
        elif 'gamecg' in book_catalog:
            book_catalog = 'gamecg'
        else:
            book_catalog = 'other'
        print(book_catalog)
        print()

        comments = []
        if len(soup.select("div#cdiv")) > 0 :
            comments_div = soup.select("div#cdiv")[0].select(".c6")

            for comm in comments_div:
                comments.append(comm.find_all_next(string=True))
            print(comments)

        title = soup.select("#gj")[0].string
        if title == None:
            title = soup.select("#gn")[0].string
        print( title )

        return [title , tags_catalogs , book_catalog , comments]

    def downloadArch(self,gallery_url,status):
        r = self.session.get(gallery_url,proxies = self.proxies )
        gallery_content = r.content.decode("utf-8")
        soup = bs4.BeautifulSoup( gallery_content )
        down_a = soup.select("#gright")[0].select("a[href='#']")[0]
        download_page_url = re.findall("'(http.*?)'",down_a["onclick"])[0]
        print(download_page_url)

        r = self.session.get(download_page_url,proxies = self.proxies )
        download_page_content = r.content.decode("utf-8")
        soup = bs4.BeautifulSoup( download_page_content)

        post_download_url = soup.select("form")[0]["action"]

        print(post_download_url)


        r = self.session.post(post_download_url,proxies = self.proxies ,data={"dltype":"org","dlcheck":"Download Original Archive"} )
        waiting_download_url_page = r.content.decode("utf-8")
        soup = bs4.BeautifulSoup( waiting_download_url_page)

        final_got_url = soup.select("#continue > a")[0]['href']

        print(final_got_url)
        r = self.session.get(final_got_url,proxies = self.proxies )
        final_got_url_page = r.content.decode("utf-8")
        soup = bs4.BeautifulSoup( final_got_url_page)
        print(soup.select("div#db")[0].select("a")[0]["href"])
        final_download_url = final_got_url+"?start=1"
        print(final_download_url)

        file_name = soup.select("strong")[0].string



        print("start to download...")
        r = requests.get(final_download_url, stream=True)
        content_size = int(r.headers['content-length'])
        f = open("tmp/downloadedFile/"+file_name, "wb+")

        count_size = 0
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                f.flush()
                count_size += len(chunk)
                print("%d / %d -- %d%%"%( count_size,content_size,count_size/content_size*100) ,end='\r')
                status[gallery_url] = "Downloading: %d%%" %(count_size/content_size*100)

        print("Over")
        return file_name
