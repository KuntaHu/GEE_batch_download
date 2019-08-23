import os
import urllib.request as request
import logging
import sys


def url_download(url, savePath, saveName):

    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(message)s',
        level=logging.INFO,
        stream=sys.stdout)
    
    # file_path = os.path.join(os.getcwd(),'dir_name/file_name')
    filePath = savePath + saveName

    if os.path.isfile(filePath):
        os.system("rm " + filePath)
        logging.info("Existed file deleted: " + saveName)
    else:
        logging.info("File doesn't exist.")
    # replace with url you need

    # if dir 'dir_name/' doesn't exist
    file_dir = savePath
    if not os.path.exists(file_dir):
        logging.info("Make direction: " + savePath)
        os.mkdir(file_dir)

    def down(_save_path, _url):
        try:
            request.urlretrieve(_url, _save_path)
            return True
        except:
            print('\nError when retrieving the URL:\n{}'.format(_url))
            return False

    # logging.info("Downloading file.")
    #
    # flag = False
    # while(~flag):
    #     flag = down(filePath, url)

    flag = down(filePath, url)
    if flag:
        print("------- Download Finished! ---------")
    else:
        print("------- Download Fail --------")


if __name__ == "__main__":
    url = 'https://earthengine.googleapis.com/api/download?docid=655e05e76c7ff994204447f78c2db921&token=f5efa820f5526f0743a9b5ad74be9dab'
    savePath = r"/home/jovyan/work/workspace/ee_download/download_results/"
    saveName = "test1.zip"

    url_download(url, savePath, saveName)
