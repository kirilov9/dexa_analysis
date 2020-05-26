# модули tkinter
from tkinter import * 
from tkinter import ttk
from tkinter import messagebox
from tkinter.filedialog import askopenfile
#модули PIL
from PIL import Image, ImageTk
#модули pydicom, cv2 и numpy
import pydicom, cv2
import numpy as np
from operator import itemgetter 
from scipy.spatial import distance as dist
#създаване на tkinter интерфейс прозорец
root = Tk()
root.title("DEXA ANALYSIS TOOL")
root.minsize(800, 800) # width, height
root.geometry("300x300+50+50")
#създаване на интерфейс тип ноутбуук
nb = ttk.Notebook(root)
nb.pack() 
#първи таб
f1 = Frame(nb)
nb.add(f1, text="File")
#втори таб
f2 = Frame(nb)
nb.add(f2, text="DICOM")
#трети таб
f3 = Frame(nb)
nb.add(f3, text="Analysis")
#четвърти таб
f4 = Frame(nb)
nb.add(f4, text="Settings")
nb.select(f1)
nb.enable_traversal()
#глобални стойности
canny_t1=200
canny_t2=300
hough_ro=1
hough_theta=180
hough_t = 90
#основни методи
def open_file(): 
    file = askopenfile(mode ='r', filetypes =[('DICOM images', '*.dcm')]) 
    if file is not None: 
        read_dicom(file)
def read_dicom(file):
    ds = pydicom.dcmread(file.name)
    ds2 = pydicom.dcmread(file.name)
    image = ds.pixel_array
    image = Image.fromarray(image)
    #image = image.resize((250, 250), Image.ANTIALIAS)
    if ds[0x8,0x1030].value == "Lumbar Spine" and ds[0x20,0x13].value == 1:
        analyze_angle(ds)
        analyze_roi(ds2)
    else:
        messagebox.showinfo("Error", "Please, choose a file containg DEXA measurement of the spine!")
        Label(f1, text="Please, choose a file containg DEXA measurement of the spine!",justify=CENTER).pack(fill=BOTH)
    photo = ImageTk.PhotoImage(image)
    img = Label(f1, image=photo)
    img.image = photo
    img.pack(side=LEFT)
    Label(f2, text=ds,justify=LEFT).pack(fill=BOTH)
def analyze_angle(ds):
    #ds = pydicom.dcmread("dicom/41_BONEVA_Rumyana.dcm")
    #image = Image.open("spine2.jpg")
    imagess = ds.pixel_array[200:554, 50:346]
    hsv = cv2.cvtColor(imagess, cv2.COLOR_RGB2HSV)
    lower_red = np.array([10,20,20])
    upper_red = np.array([50,255,255])  
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(imagess,imagess, mask= mask)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, canny_t1, canny_t2)
    lines = cv2.HoughLines(edged,hough_ro,np.pi/hough_theta,hough_t)
    points="LINES:"
    allpoints=[]
    angles=[]
    for line in lines:
        for rho,theta in line:
            a = np.cos(theta)
            b = np.sin(theta)
            x0 = a*rho
            y0 = b*rho
            x1 = int(x0 + 1000*(-b))
            y1 = int(y0 + 1000*(a))
            x2 = int(x0 - 1000*(-b))
            y2 = int(y0 - 1000*(a))
            angle = np.arctan2(y2 - y1, x2 - x1) * 180. / np.pi
            if angle<40 and angle>-40:
                cv2.line(imagess,(x1,y1),(x2,y2),(255,0,0),2)
                points+="\nx0={},y0={},x1={},y1={},x2={},y2={},ъгъл={}\n".format(x0,y0,x1,y1,x2,y2,angle)
                angles.append(angle)
    image = Image.fromarray(imagess)
    #imager = image.resize((250, 250), Image.ANTIALIAS)
    #image2 = image.crop((53,193,346, 554)) 
    photo = ImageTk.PhotoImage(image)
    img = Label(f3, image=photo)
    img.image = photo
    img.pack(side=TOP,anchor=N)
    #Label(f3, text=points,justify=LEFT).pack()
    scoliosisangle = "SCOLIOSIS ANGLE:\n {} °".format(round(calculate_angle(angles),2))
    Label(f3, text=scoliosisangle,fg="red",font=("HELVETICA",20)).pack()
def calculate_angle(angles):
    cobbangle=[]
    for angle in angles:
                        for angle2 in angles:
                                cobbangle.append(abs((angle2-angle)))
    return max(cobbangle)
def set_canny(t1,t2):
    global canny_t1,canny_t2
    canny_t1=int(t1)
    canny_t2=int(t2)
    messagebox.showinfo("OK", "Hough transform Rho, Theta and Threshold: {}, {}!".format(canny_t1,canny_t2))
def set_hough(ro,theta,t):
    global hough_ro,hough_theta,hough_t
    hough_ro=int(ro)
    hough_theta=int(theta)
    hough_t=int(t)
    messagebox.showinfo("OK", "Hough transform Rho, Theta and Threshold: {}, {}, {}!".format(ro,theta,t))
def analyze_roi(ds):
    image = ds.pixel_array[200:554, 50:346]
    # Grayscale 
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # ([25, 146, 190], [62, 174, 250]), ([0,50,40]), ([245,245,220])     
    lower_red = np.array([15,100,20])
    upper_red = np.array([40,255,255])   
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(image,image, mask= mask)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY) 
    edged=gray
    contours, hierarchy = cv2.findContours(edged,  
    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    c = max(contours, key=cv2.contourArea)
    extLeft = tuple(c[c[:, :, 0].argmin()][0])
    extRight = tuple(c[c[:, :, 0].argmax()][0])
    extTop = tuple(c[c[:, :, 1].argmin()][0])
    extBot = tuple(c[c[:, :, 1].argmax()][0])
    M=cv2.moments(c)
    cX=int(M["m10"]/M["m00"])
    cY=int(M["m01"]/M["m00"])
    print(extTop)
    print(extBot)
    print("{},{}".format(cX,cY))
    get_spine(ds,extTop[1],extBot[1],extLeft[0],extRight[0])
def get_spine(ds,top,bot,roi_extL,roi_extR):
    topn=200+top
    botn=200+bot
    image = ds.pixel_array[topn:botn, 50:346]
    hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    # ([25, 146, 190], [62, 174, 250]), ([0,50,40]), ([245,245,220])     
    lower_red = np.array([0,50,50])
    upper_red = np.array([19,255,255])   
    mask = cv2.inRange(hsv, lower_red, upper_red)
    res = cv2.bitwise_and(image,image, mask= mask)
    gray = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY) 
    gray = cv2.fastNlMeansDenoising(gray,None,30,7,21) 
    res=image
    # Find Canny edges 
    #edged = cv2.Canny(gray, 30, 200) 
    edged=gray
    contours, hierarchy = cv2.findContours(edged,  
    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    blank_image = np.zeros(shape=[700, 512, 3], dtype=np.uint8)
    centroids=[]
    for contour in contours:
        M=cv2.moments(contour)
        cX=int(M["m10"]/M["m00"])
        cY=int(M["m01"]/M["m00"])
        centroids.append((cX,cY))
        #cv2.circle(res, (roi_extL, cY), 7, (255, 255, 255), -1)
        #cv2.circle(res, (cX, cY), 7, (255, 255, 255), -1)
        print(cv2.contourArea(contour))
        x,y,w,h = cv2.boundingRect(contour)
        cv2.rectangle(blank_image,(x,y),(x+w,y+h),(0,255,0),2)
    rightcenter = max(centroids,key = itemgetter(0))
    leftcenter = min(centroids,key = itemgetter(0))
    #draw left bound and left spine contour centroid
    cv2.circle(res, (roi_extL, leftcenter[1]), 2, (255, 255, 255), -1)
    cv2.circle(res, (leftcenter[0], leftcenter[1]), 2, (255, 255, 255), -1)
    DL = dist.euclidean((roi_extL, leftcenter[1]), (leftcenter[0], leftcenter[1]))
    cv2.line(res,(roi_extL,leftcenter[1]),(leftcenter[0],leftcenter[1]),(255,0,0),4)
    cv2.putText(res, "{:.1f}px".format(DL), (int(roi_extL), int(leftcenter[1] - 10)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,0,0), 2)
    print(DL)
     #draw right bound and right spine contour centroid
    cv2.circle(res, (roi_extR, rightcenter[1]), 2, (255, 255, 255), -1)
    cv2.circle(res, (rightcenter[0], rightcenter[1]), 2, (255, 255, 255), -1)
    DR = dist.euclidean((roi_extR, rightcenter[1]), (rightcenter[0], rightcenter[1]))
    cv2.line(res,(roi_extR,rightcenter[1]),(rightcenter[0],rightcenter[1]),(255,0,0),4)
    cv2.putText(res, "{:.1f}px".format(DR), (int(rightcenter[0]), int(rightcenter[1] - 10)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255,0,0), 2)
    print(DR)
    print(leftcenter)
    print(rightcenter)
    #cv2.circle(res, (roi_cX, roi_cY-top), 7, (255, 255, 255), -1)
    cv2.drawContours(blank_image, contours, -1, (255, 255, 255), 1) 
    #res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(res)
    #imager = image.resize((250, 250), Image.ANTIALIAS)
    #image2 = image.crop((53,193,346, 554)) 
    photo = ImageTk.PhotoImage(image)
    img = Label(f3, image=photo)
    img.image = photo
    img.pack(side=TOP,anchor=N)
    scoliosisangle = "DEVIATION FROM CENTER:\n {} px".format(abs(DL-DR))
    Label(f3, text=scoliosisangle,fg="red",font=("HELVETICA",20)).pack()
    
menu = Menu(root)
root.config(menu=menu)

menufile = Menu(menu)
menufile.add_command(label="Open", command=lambda:open_file())
menufile.add_command(label="Exit", command=root.destroy)

menuhelp = Menu(menu)
menuhelp.add_command(label="Help", command=lambda:{messagebox.showinfo("Help","Please, read readme.txt!")})
menuhelp.add_command(label="About", command=lambda:{messagebox.showinfo("About this software","Developed by: Dr Nikola Kirilov \n 2019 г.")})

menu.add_cascade(label="File", menu=menufile)
menu.add_cascade(label="Help", menu=menuhelp)

#Настройки Кени
Label(f4, text="Canny's edge detector").grid(row=0,column=1,columnspan=2)
Label(f4, text="Threshold 1").grid(row=1)
Label(f4, text="Threshold 2").grid(row=2)
e1 = Entry(f4)
e2 = Entry(f4)
Button(f4,text='Set', command=lambda:set_canny(e1.get(),e2.get())).grid(row=3,column=1,columnspan=2)
e1.insert(0,canny_t1)
e2.insert(0,canny_t2)
e1.grid(row=1, column=1)
e2.grid(row=2, column=1)
#Настройки Хаф
Label(f4, text="Hough's transform").grid(row=4,column=1,columnspan=2)
Label(f4, text="Rho").grid(row=5)
Label(f4, text="Theta π/").grid(row=6)
Label(f4, text="Threshold").grid(row=7)
e3 = Entry(f4)
e4 = Entry(f4)
e5 = Entry(f4)
Button(f4,text='Set', command=lambda:set_hough(e3.get(),e4.get(),e5.get())).grid(row=8,column=1,columnspan=2)
e3.grid(row=5, column=1)
e4.grid(row=6, column=1)
e5.grid(row=7, column=1)
e3.insert(0,hough_ro)
e4.insert(0,hough_theta)
e5.insert(0,hough_t)
root.mainloop()