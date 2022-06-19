import os
import threading
import sqlite3
from operator import itemgetter

#Arduino 연결
import serial
arduino = serial.Serial(
    port = '/dev/ttyACM0',
    baudrate = 115200,
    timeout = .1,
    bytesize = serial.EIGHTBITS,
    parity = serial.PARITY_NONE,
)

recent_car=[]
max_count=0

#연결
conn = sqlite3.connect("apart.db", check_same_thread=False)

#커서 생성(파일 읽고 쓰려고 사용)
curs = conn.cursor()

#번호판 클래스
plate_list=[0,1,2,3,4,5,6,7,8,9,'가','나','다','라','마','거','너','더','러','머',
            '버','서','어','저','고','노','도','로','모','보','소','오','조','구',
            '누','두','루','무','부','수','우','주','바','사','아','자','허','하',
            '호','배']

#초기화 
def init():
    global firezone_count
    global max_count
    firezone_count=0
    max_count=0

#xywh를 xxyy로
def convert_xywh_to_xxyy(old_list=[]):
    new_list=[]
    new_list.append(old_list[0])
    new_list.append(round(float(old_list[1])-0.5*float(old_list[3]),7))
    new_list.append(round(float(old_list[1])+0.5*float(old_list[3]),7))
    new_list.append(round(float(old_list[2])-0.5*float(old_list[4]),7))
    new_list.append(round(float(old_list[2])+0.5*float(old_list[4]),7))
    return new_list

#범위 안이면(겹치면?) 
def is_in_range(target=[],zone={}):
    return target[2]>float(zone['xmin']) and target[4]>float(zone['ymin']) \
        and target[1]<float(zone['xmax']) and target[3]<float(zone['ymax'])

#차량 위치 읽어오는거 
def save_video1_bbox(save_list=[],to_list=[],is_firezone=True,firezone_num=None):
    global firezone_count

    new_dict = {}
    new_dict['xmin']=save_list[1]
    new_dict['xmax']=save_list[2]
    new_dict['ymin']=save_list[3]
    new_dict['ymax']=save_list[4]
    
    if is_firezone:
        firezone_count += 1
        new_dict['firezone']=firezone_count
    else:
        new_dict['firezone']=firezone_num
        new_dict['count']=0

    to_list.append(new_dict)

#번호판 위치 읽어오는거
def save_video2_bbox(save_list=[],to_list=[]):
    global firezone_count

    new_dict = {}
    new_dict['class']=save_list[0]
    new_dict['letter']=plate_list[int(save_list[0])]
    new_dict['x']=save_list[1]
    new_dict['y']=save_list[2]
    new_dict['w']=save_list[3]
    new_dict['h']=save_list[4]

    to_list.append(new_dict)

#겹치는 정도 확인 
def overlapped_rate(recent={},present={}):
    if float(recent['xmax'])<=float(present['xmin']) or float(recent['xmin'])>=float(present['xmax']) \
        or float(recent['ymax'])<=float(present['ymin']) or float(recent['ymin'])>=float(present['ymax']) \
        or int(recent['firezone'])!=int(present['firezone']):
        return 0
    else:
        x_loc=[recent['xmin'],recent['xmax'],present['xmin'],present['xmax']]
        y_loc=[recent['ymin'],recent['ymax'],present['ymin'],present['ymax']]
        recent_area=(x_loc[1]-x_loc[0])*(y_loc[1]-y_loc[0])
        x_loc.sort()
        y_loc.sort()
        present_area=(x_loc[2]-x_loc[1])*(y_loc[2]-y_loc[1])
        return present_area/recent_area

#파일 읽어서 정렬 후 가장 앞(최근)파일 recent_file
def read_file(path,video_num):
    os.chdir(path)
    files_Path = path
    file_name_and_time_lst = []
    # 해당 경로에 있는 파일들의 생성시간을 함께 리스트로 넣어줌. 
    for f_name in os.listdir(f"{files_Path}"):
        written_time = os.path.getctime(f"{files_Path}{f_name}")
        file_name_and_time_lst.append((f_name, written_time))
    # 생성시간 역순으로 정렬하고, 
    sorted_file_lst = sorted(file_name_and_time_lst, key=lambda x: x[1], reverse=True)
    # 가장 앞에 있는 파일을 넣어준다.
    recent_file=''
    video_name_list=['video0_','video1_']
    while not recent_file:
        for i in range(len(sorted_file_lst)):
            if video_name_list[video_num-1] in sorted_file_lst[i][0]:
                recent_file = sorted_file_lst[i]
                break
    return recent_file


def read_video1_file(recent_file=[]):
    recent_file_name = recent_file[0]

    arr=[]
    firezone=[]
    present_car=[]
    global recent_car
    global max_count

    recent_file=open(recent_file_name,'r')
    while True:
        line=recent_file.readline()
        if not line:
            break
        line_split=[x.strip() for x in line.split(' ')]
        arr.append(line_split)
    recent_file.close()

    arr_new=sorted(arr, key=lambda x : x[0])

    sortfile=open('sorted_video1.txt','w')
    for a in arr_new:
        sortfile.write(a[0]+' '+a[1]+' '+a[2]+' '+a[3]+' '+a[4]+"\n")
    sortfile.close()

    f = open('sorted_video1.txt', 'r')
    while True: 
        line = f.readline()
        if not line:
            if present_car:
                for a in present_car:
                    if not recent_car:
                        a['count']=1
                    else:
                        for b in recent_car:
                            if overlapped_rate(a,b)>=0.85:
                                a['count']=b['count']+1
                    max_count=max(max_count,a['count'])
            else:
                max_count=0
                arduino.write("0|".encode())
            recent_car=present_car
            if max_count>=3:
                arduino.write("1|".encode())
            break
        
        line_split=[x.strip() for x in line.split(' ')]
        converted_list=convert_xywh_to_xxyy(line_split)
        if converted_list[0]=='50':
            save_video1_bbox(converted_list,firezone)
        elif converted_list[0]=='51':
            for i in firezone:
                if is_in_range(converted_list,i):
                    save_video1_bbox(converted_list,present_car,False,i['firezone'])
    f.close()

def read_video2_file(file):
    recent_file_name = file[0]

    arr=[]
    plate=[]
    line1=[]
    line2=[]
    letter_y=0
    letter_h=0

    recent_file=open(recent_file_name,'r',encoding='UTF-8')
    while True:
        line=recent_file.readline()
        if not line:
            break
        line_split=[x.strip() for x in line.split(' ')]
        arr.append(line_split)
    recent_file.close()

    arr_new=sorted(arr, key=lambda x : x[0], reverse=True)

    sortfile=open('sorted_video2.txt','w')
    for a in arr_new:
        sortfile.write(a[0]+' '+a[1]+' '+a[2]+' '+a[3]+' '+a[4]+"\n")
    sortfile.close()

    f = open('sorted_video2.txt', 'r')
    while True: 
        line = f.readline()
        if not line:
            for a in plate:
                if int(a['class'])<10:
                    if abs(float(a['y'])-letter_y)<float(a['h'])/2:
                        line1.append(a)
                    else:
                        line2.append(a)
                else:
                    line1.append(a)
            
            sorted_line1=sorted(line1,key=itemgetter('x'))
            sorted_line2=sorted(line2,key=itemgetter('x'))
            number_for_database=""
            if not sorted_line1:
                break
            elif not sorted_line2:
                for a in sorted_line1:
                    number_for_database=number_for_database+str(a['letter'])
            elif float(sorted_line1[0]['y'])<float(sorted_line2[0]['y']):
                for i in sorted_line1:
                    number_for_database=number_for_database+str(i['letter'])
                for j in sorted_line2:
                    number_for_database=number_for_database+str(j['letter'])
            else:
                for i in sorted_line2:
                    number_for_database=number_for_database+str(i['letter'])
                for j in sorted_line1:
                    number_for_database=number_for_database+str(j['letter'])
            find_plate = (number_for_database,)
            curs.execute("SELECT * FROM apartment WHERE car_plate =?", find_plate)
            print('find_plate',curs.fetchone())
            conn.commit()
            number_for_database=""
            break
            
        line_split=[x.strip() for x in line.split(' ')]
        if int(line_split[0])<50:
            if int(line_split[0])>=10:
                letter_y=float(line_split[2])
                letter_h=float(line_split[4])
            save_video2_bbox(line_split,plate)
            

def my_timer():
    timer = threading.Timer(3, my_timer)
    init()
    video1_path="/home/sdmax/yolov5/runs/detect/exp/labels/"
    read_video1_file(read_file(video1_path,1))
    if max_count>=5:
        video2_path="/home/sdmax/yolov5/runs/detect/exp/labels/"
        read_video2_file(read_file(video2_path,2))
    timer.start()

my_timer()
print('')