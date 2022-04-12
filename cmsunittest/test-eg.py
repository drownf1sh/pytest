import shutil
# filepath = r'C:\Users\Willy Wang\Desktop\img\iamge01.jpg'
filepath = r'C:\Users\Willy Wang\Desktop\img20M\test 1.jpg'
DOCUMENT = ["txt","pdf"]
PHOTO = ["jpg","jpeg","png","gif","jpe","jif","jfif","jfi"]
VIDEO = ["webm","mpg","mp2","mpeg","mpe","mpv","ogg","mp4","m4p","m4v","avi","wmv","asf","mov","qt","flv","swf","avchd","m3u8","ts","3gp","x-matroska"]


for i in range(0,8):
    # 复制单个文件
    name = 'img'+ str(i+1)+ '.' +PHOTO[i]
    # name = 'cp00'+str(i) + '.mp4'
    cfilepath = r'C:\Users\Willy Wang\Desktop\img20M' + '\\' +name
    shutil.copy(filepath, cfilepath)


