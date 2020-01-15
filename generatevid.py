import glob, os
from PIL import Image, ImageDraw, ImageFont
import json
import copy
import textwrap
import cv2 as cv
import yaml

dta = {}

def main(pth):
    imgs = []
    with open(pth, 'r') as f:
        dta = json.load(f)
    with open('style.yaml') as f:
        style = yaml.load(f, Loader=yaml.FullLoader)
        print(style)
    src = dta["source"].splitlines()
    curr = -1
    strtln = dta["lines"]["1"]["report"][0]
    allvars = {}
    TRANSPARENCY = .75
    OPACITY = int(255 * TRANSPARENCY)
    variablevalues = {}
    length = len(dta["lines"])
    for j in range(1, len(dta["lines"])+1):
        img = Image.new('RGB', (1920, 1080), color = (0, 0, 0))
        fnt = ImageFont.truetype('fonts/hack.ttf', 20)
        d = ImageDraw.Draw(img)
        d.line((940,0, 940,1080), fill=(255,255,255), width=5)
        curr = dta["lines"][str(j)]["report"][0]-strtln+1
        for i in range(len(src)):
            if(i == curr):
                d.rectangle(((0,(i*20)), (940,(i*20)+20)), fill=(58, 61, 72))
                d.text((0,(i*20)),src[i], fill=(255,255,255), font = fnt)
            else:
                d.text((0,(i*20)),src[i], fill=(255,255,255), font = fnt)
        fnt = ImageFont.truetype('fonts/hack.ttf', 20)
        if dta["lines"][str(min(j+1, length))]["report"][2] == 1:
            ln = "This line has been executed %s time and the time spent till" % (1)
        else:
            ln = "This line has been executed %s times and the time spent till" % (dta["lines"][str(min(j+1, length))]["report"][2])
        ln2 = "now on this line is {:f} seconds".format(dta["lines"][str(min(j+1, length))]["report"][3])
        d.text((960, 20),ln, fill=(255,255,255), font = fnt)
        d.text((960, 20+20),ln2, fill=(255,255,255), font = fnt)
        d.line((940, 80, 1920,80), fill=(255,255,255), width=5)
        didmodify = {}
        for i in dta["lines"][str(min(j+1, length))]["report"][7]:
            allvars[i[0]] = [i[0], None, i[1]]
            variablevalues[i[0]] = i[1]
            didmodify[i[0]] = True

        for i in dta["lines"][str(min(j+1, length))]["report"][9]:
            allvars[i[0]] = [i[0], None, i[1]]
            didmodify[i[0]] = True

        for i in dta["lines"][str(min(j+1, length))]["report"][8]:
            allvars[i[0]] = [i[0], i[1], i[2]]
            didmodify[i[0]] = True

        for i in dta["lines"][str(min(j+1, length))]["report"][6]:
            temp = variablevalues[i[0]].copy()
            temp[i[1]] = i[3]
            allvars[i[0]] = [i[0], variablevalues[i[0]], temp]
            variablevalues[i[0]] = temp.copy()
            didmodify[i[0]] = True

        for i in dta["lines"][str(min(j+1, length))]["report"][5]:
            temp = variablevalues[i[0]].copy()
            temp[i[0]].append(i[1])
            allvars[i[0]] = [i[0], variablevalues[i[0]], temp]
            variablevalues[i[0]] = temp.copy()
            didmodify[i[0]] = True
        stp = 0
        for i in allvars:
            if i in didmodify:
                if(didmodify[i] == True):
                    st = "The variable " + allvars[i][0] + " previous value " +  str(allvars[i][1]) + " and current value " + str(allvars[i][2])
                    lines = textwrap.wrap(st, width=60)
                    for k in lines:
                        d.text((960, 90 + (stp*20)),k, fill=(0,200,0), font = fnt)
                        stp+=1
            else:
                st = "The variable " + allvars[i][0] + " previous value " +  str(allvars[i][1]) + " and current value " + str(allvars[i][2])
                lines = textwrap.wrap(st, width=60)
                for k in lines:
                    d.text((960, 90 + (stp*20)),k, fill=(255,255,255), font = fnt)
                    stp+=1
        imgnm = 'img' + str(j+1) + ".png"
        img.save(imgnm)
        img2 = cv.imread(imgnm)
        height, width, layers = img2.shape
        size = (width,height)
        imgs.append(img2)
    out = cv.VideoWriter('DebuggerVideo.avi',cv.VideoWriter_fourcc(*'DIVX'), 1, size)
    imglast = imgs[len(imgs)-1]
    for i in range(5):
        imgs.append(imglast)
    for i in range(len(imgs)):
        out.write(imgs[i])
    out.release()
    for file in glob.glob("*.png"):
        os.remove(file)
    
    print("Video Saved in this folder with name DebuggerVideo.avi")
# main("data.json")