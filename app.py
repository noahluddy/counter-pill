# HTMl5 camera capture
from __future__ import print_function
from flask import Flask, request
from PIL import Image, ImageDraw
import os
import sys
import math

app = Flask(__name__)

@app.route('/', methods=['GET'])  # Anytime enter is pressed, it's a get request
def render():
    return '''
    <!doctype html>
    <html>
        <head>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha.5/css/bootstrap.css"/>
            <style>
                #inp {
                    color: blue;
                    border-radius: 20%;
                }
            </style>
        </head>
        <body>
            <form action="/" method="post" enctype="multipart/form-data">
                <input type="file" name="photo" capture="camera" accept="images/*"/>
                <input type="submit" id="inp" value="Upload"/>
            </form>
        </body>
    </html>'''
    # While demoing, change input type="file", take out capture
    # enctype="multipart/form-data"

@app.route('/', methods=['POST'])
def process_img():
    photo = request.files["photo"]
    pil = Image.open(photo)  # JpegImageFile
    print(pil)
    txt = process(pil)
    return '''<html>
        <head>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.0.0-alpha.5/css/bootstrap.css" />
        </head>
        <body>
            <h1>Success {}</h1>
        </body>
    </html>'''.format(txt)

def process(im):
    # im = Image.open(f)

    if im.size[0] >= im.size[1]:
        im = im.resize((1000,750))
    else:
        im = im.resize((750,1000))

    mask = Image.new('RGBA',(im.size[0],im.size[1]),(255,255,255,255))
    mask2 = Image.new('RGBA',(im.size[0],im.size[1]),(255,255,255,255))
    pix = im.load()

    def pixDiff(i,j):
        sum = 0
        for c in range(0,2):
            sum += abs(pix[i-1,j][c] - pix[i,j][c])
            sum += abs(pix[i+1,j][c] - pix[i,j][c])
            sum += abs(pix[i,j-1][c] - pix[i,j][c])
            sum += abs(pix[i,j+1][c] - pix[i,j][c])
            return sum

    # draw = ImageDraw.Draw(mask)
    #
    # for i in range(2,(im.size[0] - 1)):
    #     for j in range(2,(im.size[1] - 1)):
    #         if pixDiff(i,j) <= 100:
    #             draw.point([i,j],fill=(0,0,0,128))
    #
    # del draw

    # im.show()
    # mask.show()

    sample1 = pix[math.floor((im.size[0])/10),math.floor((im.size[1])/10)]
    sample2 = pix[math.floor((im.size[0])/10),math.floor((im.size[1])*9/10)]
    sample3 = pix[math.floor((im.size[0])*9/10),math.floor((im.size[1])/10)]
    sample4 = pix[math.floor((im.size[0])*9/10),math.floor((im.size[1])*9/10)]

    # print(sample1)
    # print(sample2)
    # print(sample3)
    # print(sample4)

    avgsample = ((sample1[0] + sample2[0] + sample3[0] + sample4[0])/4, (sample1[1] + sample2[1] + sample3[1] + sample4[1])/4, (sample1[2] + sample2[2] + sample3[2] + sample4[2])/4)

    # print(avgsample)

    avgdeviation = ((abs(sample1[0] - avgsample[0]) + abs(sample2[0] - avgsample[0]) + abs(sample3[0] - avgsample[0]) + abs(sample4[0] - avgsample[0]))/4, (abs(sample1[1] - avgsample[1]) + abs(sample2[1] - avgsample[1]) + abs(sample3[1] - avgsample[1]) + abs(sample4[1] - avgsample[1]))/4, (abs(sample1[2] - avgsample[2]) + abs(sample2[2] - avgsample[2]) + abs(sample3[2] - avgsample[2]) + abs(sample4[2] - avgsample[2]))/4)

    # print(avgdeviation)

    draw2 = ImageDraw.Draw(mask2)

    RGBpass = [True,True,True]
    itemCount = 0
    RGBsum = [0,0,0]

    for i in range(2,(im.size[0] - 1)):
        for j in range(2,(im.size[1] - 1)):
            for c in range(0,2):
                if pix[i,j][c] <= avgsample[c] + 6 * avgdeviation[c] and pix[i,j][c] >= avgsample[c] - 6 * avgdeviation[c]:
                    draw2.point([i,j],fill=(0,0,0,128))
                    RGBpass[c] = False
            if RGBpass[0] and RGBpass[1] and RGBpass[2]:
                for c in range(0,2):
                    RGBsum[c] += pix[i,j][c]
                itemCount += 1

            for c in range(0,2):
                RGBpass[c] += True

    del draw2

    mask2.show()

    RGBfinal = (RGBsum[0]/itemCount, RGBsum[1]/itemCount, RGBsum[2]/itemCount)

    return(str(RGBfinal))

# Use ajax of some sort to upload a base64 string that represents the image (ajax lib most used is jQuery)
if __name__ == '__main__':
    app.run()
