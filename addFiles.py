
from SiteTools import img
from SiteTools import sql
from SiteTools import file
import SiteTools.book

from SiteTools import ehentai
tmpPath = "tmp/"
uploadedArchPath=tmpPath+"uploadedArch/"
uploadedArchPath = "D:\\tmp\\"
sqlManager = sql.sqlDataManager()

archNames , archPaths =  file.getAllArchFilesInfo(uploadedArchPath)

for index , archname in enumerate( archNames):
    print("Progress:"+ str(index+1)+" / "+ str(len(archNames)))
    img.addNewArchFileToImgLib(archname, sqlManager,
                               archname[0:-4],
                               uploadedArchPath)


