# -*- coding: utf-8 -*-
# Created on 2018/3/22

import os, time

import requests

import threadpool
import glob

"""
下载M3U8文件里的所有片段
"""

c_fule_name=r'阿丽塔.ts'

suffix="*.ts"

def downTs(url, destFile):
    if os.path.exists(destFile):
        return
    print("downts",destFile)
    res = requests.get(url, verify=False)
    #c_fule_name = str(file_line[index + 1])
    with open(destFile, 'ab') as f:
        f.write(res.content)
        f.flush()
        
def download(url):

    if os.path.exists(c_fule_name):
        print()
        conti = input("%s已经存在,继续下载？(Y|N)" % c_fule_name)
        if conti.lower() != "y":
            return
        
    download_path = os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    all_content = requests.get(url, verify=False).text  # 获取M3U8的文件内容
    file_line = all_content.split("\n")  # 读取文件里的每一行
    #print(file_line)
    m3u8TsList=[]
    start_time = time.time()
    # 通过判断文件头来确定是否是M3U8文件
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True  # 用来判断是否找到了下载的地址
        task_pool=threadpool.ThreadPool(12)#12是线程池中线程的个数
        urldestList=[]#存放任务列表
        
        for index, line in enumerate(file_line):
            if "EXTINF" in line:
                unknow = False
                # 拼出ts片段的URL
                tsFile=file_line[index + 1]
                pd_url = url.rsplit("/", 1)[0] + "/" + tsFile
                destFile= os.path.sep.join([download_path, tsFile])
                m3u8TsList.append(destFile)
                func_var = [pd_url, destFile]
                
                #print(func_var)
                urldestList.append(func_var)
        #print(urldestList)
        if unknow:
            raise BaseException("未找到对应的下载链接")
        else:
            request_list=[ (urldest, None) for urldest in urldestList ]
            reqs = threadpool.makeRequests(downTs, request_list) 
            [task_pool.putRequest(req) for req in reqs]
            #将每个任务放到线程池中，等待线程池中线程各自读取任务，然后进行处理，使用了map函数，不了解的可以去了解一下。  
            #map(task_pool.putRequest,request_list)
            #等待所有任务处理完成，则返回，如果没有处理完，则一直阻塞  
            task_pool.wait() 
            print("下载完成 %d second" % (time.time()-start_time))
    saved=False
    with open(c_fule_name ,'ab') as f:
        print("存储为%s" % c_fule_name)
        for ts in m3u8TsList:
            with open(ts,'rb') as fs:
                f.write(fs.read())
                f.flush()
        saved=True
        print("保存%s完毕" % c_fule_name)
        
    if saved:  
        for ts in glob.glob(os.path.sep.join([download_path,suffix])):
            print(ts)
            os.remove(ts)

if __name__ == '__main__':
    #download("https://youku.cdn2-youku.com/20180710/12991_efbabf56/index.m3u8")
    #download("http://boba.52kuyun.com/20180820/9z5t36SE/index.m3u8?v2")
    download("http://zy.kubozy-youku-163-aiqi.com/20190225/260_880207f2/1000k/hls/index.m3u8")