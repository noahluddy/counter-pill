from __future__ import print_function
from flask import Flask, request
from PIL import Image, ImageDraw
import os
import sys
import math

app = Flask(__name__)

@app.route('/', methods=['GET'])
def render():
    return '''
    <!doctype html>
    <html lang="en">
        <head>
            <title>💊 Counter Pill</title>
            <style>
                body {
                    background-color: rgb(225, 218, 245);
                    font-family: 'Calibri', sans-serif;
                    margin: auto;
                    text-align: center;
                }

                #top-bar {
                    background: rgb(51, 0, 51);
                    background: rgba(51, 0, 51, 0.75);
                    height: 75px;
                }

                img {
                    border-radius: 2%;
                }

                .image-upload > input {
                    display: none;
                }

            </style>
        </head>

        <body>
            <div id="top-bar">
                <a href="https://counter-pill.herokuapp.com"><img src="http://i.imgur.com/ANrnFJv.png" alt="Counter" height="75px"></a>
            </div>
            <h2>Validate Your Medicine!</h2>
            <form action="/" method="post" enctype="multipart/form-data" id="formy">
                <div>
                    <select id="drug" name="drug">
                        <option>Please select your medicine</option>
                        <option>Ibuprofen</option>
                        <option>Claritin</option>
                        <option>Mint Vitamin</option>
                        <option>TicTac</option>
                    </select>
                </div>
                <br/>
                <div class="image-upload">
                    <label for="file-input">
                        <img src="http://i.imgur.com/etdpVMW.png" alt="Camera" width="330px">
                    </label>
                    <input id="file-input" type="file" name="photo" capture="camera" accept="images/*"/>
                </div>
                <br/>
                <div class="image-upload">
                    <label for="submit">
                        <img id="done" src="http://i.imgur.com/rsHeWYq.png" alt="Submit" width="200px">
                    </label>
                    <input id="submit" type="submit"/>
                </div>
            </form>
            <div id="words">
                <p>Please take the picture slighty under a foot away and against a contrasting and uniform background.</p>
            </div>
        </body>
    </html>'''

@app.route('/', methods=['POST'])
def process_img():
    drug = request.form.get('drug')
    pil = Image.open(request.files["photo"])  # JpegImageFile
    data = imageAnalysis(pil, drug)
    if data[2] == (0, 0, 0):
        return '<h1 style="font-family: sans-serif">Please refresh the page and take another picture.</h1>'
    urls = ['http://i.imgur.com/T07jZsx.png', 'http://i.imgur.com/Ydf2zHb.png']  # 0 - genuine, 1 - counterfeit
    if data[0] == True:
        url = urls[0]
        realfake = 'real'
    else:
        url = urls[1]
        realfake = 'fake'
    return '''
    <!doctype html>
    <html lang="en">
        <head>
            <style>
                body {
                    background-color: rgb(225, 218, 245);
                    font-family: 'Calibri', sans-serif;
                    margin: auto;
                    text-align: center;
                }

                #top-bar {
                    background: rgb(51, 0, 51);
                    background: rgba(51, 0, 51, 0.75);
                    height: 75px;
                }

                img {
                    border-radius: 2%;
                }

                #info {
                    width:200px;
                }

            </style>
        </head>

        <body>
            <div id="top-bar">
                <a href="https://counter-pill.herokuapp.com"><img src="http://i.imgur.com/ANrnFJv.png" alt="Counter" height="75px"></a>
            </div>
            <br/>
            <img id="info" src=''' + url + '''/>
            <p>Your pill is ''' + realfake + ''' and we're ''' + str(data[1]) + '''% sure of it.
        </body>
    </html>'''

drugDict = {'Ibuprofen':(100,50,45), 'Claritin':(250,250,250), 'Mint Vitamin':(80,90,100), 'TicTac':(60,120,100), 'data':(0,0,0)}

def imageAnalysis(im, drug):
	if im.size[0] >= im.size[1]:
		im = im.resize((1000,750))
	else:
		im = im.resize((750,1000))

	pix = im.load()

	def pixDiff(i,j):
		sum = 0
		for c in range(0,3):
			sum += abs(pix[i-1,j][c] - pix[i,j][c])
			sum += abs(pix[i+1,j][c] - pix[i,j][c])
			sum += abs(pix[i,j-1][c] - pix[i,j][c])
			sum += abs(pix[i,j+1][c] - pix[i,j][c])
		return sum

	drugThreshold = 15

	sample1 = pix[math.floor((im.size[0])/10),math.floor((im.size[1])/10)]
	sample2 = pix[math.floor((im.size[0])/10),math.floor((im.size[1])*9/10)]
	sample3 = pix[math.floor((im.size[0])*9/10),math.floor((im.size[1])/10)]
	sample4 = pix[math.floor((im.size[0])*9/10),math.floor((im.size[1])*9/10)]

	avgsample = ((sample1[0] + sample2[0] + sample3[0] + sample4[0])/4, (sample1[1] + sample2[1] + sample3[1] + sample4[1])/4, (sample1[2] + sample2[2] + sample3[2] + sample4[2])/4)

	avgdeviation = ((abs(sample1[0] - avgsample[0]) + abs(sample2[0] - avgsample[0]) + abs(sample3[0] - avgsample[0]) + abs(sample4[0] - avgsample[0]))/4, (abs(sample1[1] - avgsample[1]) + abs(sample2[1] - avgsample[1]) + abs(sample3[1] - avgsample[1]) + abs(sample4[1] - avgsample[1]))/4, (abs(sample1[2] - avgsample[2]) + abs(sample2[2] - avgsample[2]) + abs(sample3[2] - avgsample[2]) + abs(sample4[2] - avgsample[2]))/4)

	def drugPixDiff(i,j):
		sum = 0
		for c in range(0,3):
			sum += abs(pix[i,j][c] - avgsample[c]) / avgdeviation[c]
		return sum

	itemCount = 1
	RGBsum = [0,0,0]

	for i in range(1,(im.size[0])):
		for j in range(1,(im.size[1])):
			if not drugPixDiff(i,j) <= drugThreshold:
				for c in range(0,3):
					RGBsum[c] += pix[i,j][c]
				itemCount += 1

	RGBfinal = (RGBsum[0]/itemCount, RGBsum[1]/itemCount, RGBsum[2]/itemCount)
	print(RGBfinal)
	def certainty(drug):
		cert = float(abs(RGBfinal[0] - drugDict[drug][0]) + abs(RGBfinal[1] - drugDict[drug][1]) + abs(RGBfinal[2] - drugDict[drug][2])) / (3 * float(drugThreshold))
		if cert <= 0.5:
			if cert < 0.1:
				return [True, 90, RGBfinal]
			else:
				return [True, int(100 * (1 - cert)), RGBfinal]
		else:
			if cert >= 1:
				return [False, 100, RGBfinal]
			else:
				return [False, int(100 * cert), RGBfinal]

	return certainty(drug)

if __name__ == '__main__':
    app.run()
