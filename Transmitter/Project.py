import math
import time
import _thread
import random

from pathlib import Path
from bitstring import BitArray
from timeit import default_timer as timer


max_length = 0
max_length_log = 0

def calcRedundantBits(m): 

	for i in range(m): 
		if(2**i >= m + i + 1): 
			return i 


def generateCodeWord(arr, r): 
	
	n = len(arr) 
	parity = ""
	for i in range(r): 
		val = 0
		for j in range(1, n + 1): 
			if(j & (2**i) == (2**i)): 
				val = val ^ int(arr[j-1]) 

		parity += str(val)

	return arr + parity


def isascii(s):
	"""Check if the characters in string s are in ASCII, U+0-U+7F."""
	return len(s) == len(s.encode())

def SpecialCharacterFilter(string):

	FilteredList = ""

	for i in string:

		if(isascii(i) == True):
			FilteredList += i 

	return "".join(FilteredList)

rand_list = []
rand_sol_list = []


def correctedInformationWord(arr, nr): 

	n = len(arr)-nr
	res = 0

	for i in range(nr): 
		val = int(arr[i+n])
		for j in range(1, n + 1): 
			if(j & (2**i) == (2**i)): 
				val = val ^ int(arr[j-1])
		res = res + val*pow(2,i)

	arr_list = list(arr)
	detected_error = arr_list.copy()
	if(res > 0):
		arr_list[res-1] = str(int(arr_list[res-1])^1)
		detected_error[res-1] = "_"

	rand_sol_list.append(res-1)

	detected_error = "".join(detected_error)
	corrected = "".join(arr_list.copy())
	arr_list = arr_list[:-nr]
	return ["".join(arr_list), detected_error, corrected]


def compress(uncompressed):
	"""Compress a string to a list of output symbols."""
	
	global max_length, max_length_log

	# Build the dictionary.
	dict_size = 256
	dictionary = dict((chr(i), i) for i in range(dict_size))
	# in Python 3: dictionary = {chr(i): i for i in range(dict_size)}

	w = ""
	result = []
	for c in uncompressed:
		wc = w + c
		if wc in dictionary:
			w = wc
		else:
			result.append(dictionary[w])
			max_length = max(max_length,dictionary[w])
			# Add wc to the dictionary.
			dictionary[wc] = dict_size
			dict_size += 1
			w = c
 
	# Output the code for w.
	if w:
		result.append(dictionary[w])
		max_length = max(max_length,dictionary[w])

	max_length_log = int(math.log(max_length,2))
	if(max_length_log*max_length_log != max_length):
		max_length_log += 1

	return result
 
 
def decompress(compressed):
	"""Decompress a list of output ks to a string."""
	from io import StringIO
 
	# Build the dictionary.
	dict_size = 256
	dictionary = dict((i, chr(i)) for i in range(dict_size))
	# in Python 3: dictionary = {i: chr(i) for i in range(dict_size)}
 
	# use StringIO, otherwise this becomes O(N^2)
	# due to string concatenation in a loop
	result = StringIO()
	w = chr(compressed.pop(0))
	result.write(w)
	for k in compressed:
		if k in dictionary:
			entry = dictionary[k]
		elif k == dict_size:
			entry = w + w[0]
		else:
			raise ValueError('Bad compressed k: %s' % k)
		result.write(entry)
 
		# Add w+entry[0] to the dictionary.
		dictionary[dict_size] = w + entry[0]
		dict_size += 1
 
		w = entry

	return result.getvalue()
 

def convertToBinary(compressed,flag=True):

	result = []

	for num in compressed:
		x = bin(num).replace("0b", "")
		if(flag == True):
			x = "0"*(max_length_log - len(x)) + x
		else:
			x = "0"*(8-len(x)) + x
		result.append(x)

	return result


def convertToDecimal(corrected,flag=True):

	if(flag == True):
		return int(corrected, 2)
	else:
		arr = []
		for data in corrected:
			arr.append(int(data,2))
		return arr


def SaveCompressedFile(s):

	v = int(s, 2) 
	b = bytearray()
	while v:
		b.append(v & 0xff)
		v >>= 8

	f = open('../Reciever/compress.txt', 'wb')
	f.write(bytes(b[::-1]))
	f.close()


def DeCompressFile():

	f = open('../Reciever/compress.txt', 'rb')
	arr = []
	for byte in f.read():
		arr.append(byte)

	arr = convertToBinary(arr,False)
	arr = "".join(arr)

	arr1 = []
	for i in range(len(arr)-1,0,-max_length_log):
		arr1.append(str(arr[i-max_length_log+1:i+1]))

	arr1.reverse()
	arr = []
	for data in arr1:
		if(data == ""):
			continue
		arr.append(convertToDecimal(data))



def SimulateError(HammingEncodedList):

	arr_list = []

	for i in range(len(HammingEncodedList)):

		temp = list(HammingEncodedList[i])
		randomNum = random.randint(0, max_length_log-1)
		if(temp[randomNum] == '0'):
			temp[randomNum] = '1'
		else:
			temp[randomNum] = '0'
		rand_list.append(randomNum)

		arr_list.append("".join(temp))

	return arr_list

def HammingEncoding(compressed):

	HammingEncodedList = []

	m = max_length_log # information bits (k)
	r = calcRedundantBits(m) 

	for data in compressed:

		arr = generateCodeWord(data,r)
		HammingEncodedList.append(arr)

	return HammingEncodedList


def HammingDecoding(HammingEncodedList):

	HammingDecodedList = []
	DecodedErrorList = []
	CorrectedErrorList = []

	m = max_length_log
	r = calcRedundantBits(m)
	
	for data in HammingEncodedList:

		[corrected,detected_error,corrected_error_with_parity] = correctedInformationWord(data, r)
		HammingDecodedList.append(corrected)
		DecodedErrorList.append(detected_error)
		CorrectedErrorList.append(corrected_error_with_parity)

	return [HammingDecodedList,DecodedErrorList,CorrectedErrorList]


def SaveDecompressedFile(DecompressedString):

	f = open("../Reciever/Decompressed.txt","w")

	f.write(DecompressedString)

	f.close()


start = end = start_decompress = end_decompress = 0

def Start(fname):

	global start,end,start_decompress,end_decompress

	start = timer()

	f = open(fname,"r")

	FilteredString =  SpecialCharacterFilter(str(f.read()))

	compressed = compress(FilteredString)

	binary_compressed = convertToBinary(compressed)

	compressed_str = "".join(map(str, binary_compressed))

	SaveCompressedFile(compressed_str)

	end = timer()

	HammingEncodedList = HammingEncoding(binary_compressed)
	# 0th element transmitted
	
	RecievedList = SimulateError(HammingEncodedList)
	# RecievedList = HammingEncodedList

	[HammingDecodedList,DecodedErrorList,CorrectedErrorList] = HammingDecoding(RecievedList)
	# 0th element recieved

	start_decompress = timer()

	DecimalList = convertToDecimal(HammingDecodedList,False)

	DecompressedString = decompress(DecimalList)

	SaveDecompressedFile(DecompressedString)

	end_decompress = timer()

	print(DecompressedString)

	return [binary_compressed,HammingEncodedList,RecievedList,DecodedErrorList,CorrectedErrorList]

def test(self,InformationBits,TransmittedBits,RecievedBits,DetectedErrorBits,CorrectedErrorBits,var):

	print("Information Bits per Second = ",str(int(len(InformationBits[0])/var)),"Bits/Sec")
	print("Transmitted Bits per Second = ",str(int(len(TransmittedBits[0])/var)),"Bits/Sec",end="\n\n")

	for i in range(len(InformationBits)):

		print("Information Bits    -", str(InformationBits[i]))
		print("Transmitted Bits    -" ,str(TransmittedBits[i]))
		print("Recieved Bits       -" ,str(RecievedBits[i]))
		print("Detected Error Bits -" ,str(DetectedErrorBits[i]))
		print("Corrected Error Bits-" ,str(CorrectedErrorBits[i]))
		print("\n")			

		time.sleep(var)

# LZW Encoding
# Convert to Binary
	# Information Bits
# Hamming encoding 
	# Transmitted Bits
	# Update Percentage of file transferred
# Simulate Random error 
	# Recieved Bits 
# Hamming decoding 
	# Error Bits or Position
	# Corrected Bits
# Convert to ASCII
# LZW Decoding

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

g1 = []
b1 = []
g2 = []
b2 = []

class Second(QtGui.QMainWindow):
	def __init__(self,parent=None):

		super(Second, self).__init__(parent)
		self.graphWidget = pg.PlotWidget()
		self.setCentralWidget(self.graphWidget)

		pen = pg.mkPen(color=(255, 255, 255))
		self.graphWidget.plot(b1, g1,pen=pen)
		pen = pg.mkPen(color=(255, 255, 0))
		self.graphWidget.plot(b2, g2,pen=pen)

class MainWindow(QtWidgets.QMainWindow):

	def __init__(self, *args, **kwargs):

		super(MainWindow, self).__init__(*args, **kwargs)
		window = Ui_mainWindow()
		window.setupUi(self)


class Ui_mainWindow(object):

	def setupUi(self, mainWindow):
		mainWindow.setObjectName("mainWindow")
		mainWindow.resize(650, 670)

		self.fname = ""
		self.centralwidget = QtWidgets.QWidget(mainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton.setGeometry(QtCore.QRect(100, 60, 171, 51))
		self.pushButton.setObjectName("pushButton")
		self.pushButton.clicked.connect(lambda:self.getfile())
		self.label = QtWidgets.QLabel(self.centralwidget)
		self.label.setGeometry(QtCore.QRect(320, 70, 181, 41))
		font = QtGui.QFont()
		font.setItalic(True)
		self.label.setFont(font)
		self.label.setObjectName("label")
		self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_2.setGeometry(QtCore.QRect(500, 70, 61, 41))
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_2.clicked.connect(lambda:self.start(mainWindow))
		
		self.label_2 = QtWidgets.QLabel(self.centralwidget)
		self.label_2.setGeometry(QtCore.QRect(100, 150, 161, 51))
		self.label_2.setObjectName("label_2")
		self.label_3 = QtWidgets.QLabel(self.centralwidget)
		self.label_3.setGeometry(QtCore.QRect(100, 200, 161, 51))
		self.label_3.setObjectName("label_3")
		self.label_4 = QtWidgets.QLabel(self.centralwidget)
		self.label_4.setGeometry(QtCore.QRect(100, 300, 161, 51))
		self.label_4.setObjectName("label_4")
		self.label_5 = QtWidgets.QLabel(self.centralwidget)
		self.label_5.setGeometry(QtCore.QRect(100, 250, 161, 51))
		self.label_5.setObjectName("label_5")
		self.label_6 = QtWidgets.QLabel(self.centralwidget)
		self.label_6.setGeometry(QtCore.QRect(100, 350, 161, 51))
		self.label_6.setObjectName("label_6")
		self.label_7 = QtWidgets.QLabel(self.centralwidget)
		self.label_7.setGeometry(QtCore.QRect(100, 400, 161, 51))
		self.label_7.setObjectName("label_7")
		self.label_8 = QtWidgets.QLabel(self.centralwidget)
		self.label_8.setGeometry(QtCore.QRect(100, 450, 161, 51))
		self.label_8.setObjectName("label_8")

		font = QtGui.QFont()
		font.setPointSize(12)
		self.label_11 = QtWidgets.QLabel(self.centralwidget)
		self.label_11.setGeometry(QtCore.QRect(100, 530, 281, 41))
		self.label_11.setObjectName("label_11")
		self.label_12 = QtWidgets.QLabel(self.centralwidget)
		self.label_12.setGeometry(QtCore.QRect(100, 580, 281, 41))
		self.label_12.setObjectName("label_12")


		self.label_2_val = QtWidgets.QLabel(self.centralwidget)
		self.label_2_val.setGeometry(QtCore.QRect(300, 150, 261, 51))
		self.label_2_val.setObjectName("label_2_val")
		self.label_3_val = QtWidgets.QLabel(self.centralwidget)
		self.label_3_val.setGeometry(QtCore.QRect(300, 200, 261, 51))
		self.label_3_val.setObjectName("label_3_val")
		self.label_4_val = QtWidgets.QLabel(self.centralwidget)
		self.label_4_val.setGeometry(QtCore.QRect(300, 300, 261, 51))
		self.label_4_val.setObjectName("label_4_val")
		self.label_5_val = QtWidgets.QLabel(self.centralwidget)
		self.label_5_val.setGeometry(QtCore.QRect(300, 250, 261, 51))
		self.label_5_val.setObjectName("label_5_val")
		self.label_6_val = QtWidgets.QLabel(self.centralwidget)
		self.label_6_val.setGeometry(QtCore.QRect(300, 350, 261, 51))
		self.label_6_val.setObjectName("label_6_val")
		self.label_7_val = QtWidgets.QLabel(self.centralwidget)
		self.label_7_val.setGeometry(QtCore.QRect(300, 400, 261, 51))
		self.label_7_val.setObjectName("label_7_val")
		self.label_8_val = QtWidgets.QLabel(self.centralwidget)
		self.label_8_val.setGeometry(QtCore.QRect(300, 450, 261, 51))
		self.label_8_val.setObjectName("label_8_val")
		font = QtGui.QFont()
		font.setPointSize(12)
		self.label_11_val = QtWidgets.QLabel(self.centralwidget)
		self.label_11_val.setGeometry(QtCore.QRect(400, 530, 300, 41))
		self.label_11_val.setObjectName("label_11_val")
		self.label_12_val = QtWidgets.QLabel(self.centralwidget)
		self.label_12_val.setGeometry(QtCore.QRect(400, 580, 300, 41))
		self.label_12_val.setObjectName("label_12_val")

		mainWindow.setCentralWidget(self.centralwidget)
		self.statusbar = QtWidgets.QStatusBar(mainWindow)
		self.statusbar.setObjectName("statusbar")
		mainWindow.setStatusBar(self.statusbar)
		self.dialogs = list()
		self.retranslateUi(mainWindow)
		QtCore.QMetaObject.connectSlotsByName(mainWindow)

	def retranslateUi(self, mainWindow):
		_translate = QtCore.QCoreApplication.translate
		mainWindow.setWindowTitle(_translate("mainWindow", "File Compression"))
		self.pushButton.setText(_translate("mainWindow", "Upload File to Compress"))
		self.label.setText(_translate("mainWindow", "No files selected yet"))
		self.pushButton_2.setText(_translate("mainWindow", "Start"))
		self.label_2.setText(_translate("mainWindow", "Compressed File Size:"))
		self.label_3.setText(_translate("mainWindow", "Compressed File Time:"))
		self.label_4.setText(_translate("mainWindow", "Decompressed File Size:"))
		self.label_5.setText(_translate("mainWindow", "Compression Ratio:"))
		self.label_6.setText(_translate("mainWindow", "Compression Speed:"))
		self.label_7.setText(_translate("mainWindow", "Decompression Speed:"))
		self.label_8.setText(_translate("mainWindow", "Decompression Time:"))
		self.label_11.setText(_translate("mainWindow", "Transmission time without Compression:"))
		self.label_12.setText(_translate("mainWindow", "Transmission time with Compression:"))

	def getfile(self):

		_translate = QtCore.QCoreApplication.translate
		fname = QFileDialog.getOpenFileName(None, 'Open file','.',"Text files (*.txt)")
		fname = fname[0]
		self.fname = fname
		if(fname == ""):
			self.label.setText(_translate("mainWindow", "No files selected yet"))
		else:
			fname = fname.split("/")[-1]
			self.label.setText(_translate("mainWindow", fname))

	def start(self,mainWindow):

		_translate = QtCore.QCoreApplication.translate

		[InformationBits,TransmittedBits,RecievedBits,DetectedErrorBits,CorrectedErrorBits] = Start(self.fname)   

		CompressionFileSize = Path('../Reciever/compress.txt').stat().st_size

		CompressedFileTime = round(end-start,2)

		UncompressedFileSize = Path(self.fname).stat().st_size

		CompressionRatio = round(UncompressedFileSize/CompressionFileSize,2)

		DeCompressedFileSize = Path('../Reciever/Decompressed.txt').stat().st_size

		CompressionSpeed = round(UncompressedFileSize/CompressedFileTime,2)

		DeCompressedFileTime = round(end_decompress - start_decompress,2)

		DecompressionSpeed = round(CompressionFileSize/DeCompressedFileTime,2)

		var = 1

		InformationBitsPerSecond = int(len(InformationBits[0])/var)

		TransmissionTimeWithoutCompression = round((UncompressedFileSize*8)/(InformationBitsPerSecond),2)

		TransmissionTimeWithCompression = round(CompressedFileTime + DeCompressedFileTime + (CompressionFileSize*8)/(InformationBitsPerSecond),2)


		self.label_2_val.setText(_translate("mainWindow", str(CompressionFileSize) + " Bytes"))
		self.label_3_val.setText(_translate("mainWindow", str(CompressedFileTime) + " Seconds"))
		self.label_4_val.setText(_translate("mainWindow", str(DeCompressedFileSize) + " Bytes"))
		self.label_5_val.setText(_translate("mainWindow", str(CompressionRatio)))
		self.label_6_val.setText(_translate("mainWindow", str(CompressionSpeed) + " Bytes/Second"))
		self.label_7_val.setText(_translate("mainWindow", str(DecompressionSpeed) + " Bytes/Second"))
		self.label_8_val.setText(_translate("mainWindow", str(DeCompressedFileTime) + " Seconds"))
		self.label_11_val.setText(_translate("mainWindow", str(TransmissionTimeWithoutCompression) + " Seconds"))
		self.label_12_val.setText(_translate("mainWindow", str(TransmissionTimeWithCompression) + " Seconds"))

		for bandwidth in range(1,100):

			TransmittionTimeWithoutCompression = round((UncompressedFileSize*8)/(bandwidth),2)

			TransmittionTimeWithCompression = round(CompressedFileTime + DeCompressedFileTime + (CompressionFileSize*8)/(bandwidth),2)

			g1.append(TransmittionTimeWithoutCompression)
			b1.append(bandwidth)

			g2.append(TransmittionTimeWithCompression)
			b2.append(bandwidth)

		self.showGraph(mainWindow)

		_thread.start_new_thread( test, (self,InformationBits,TransmittedBits,RecievedBits,DetectedErrorBits,CorrectedErrorBits,var) )

	def showGraph(self,mainWindow):

		dialog = Second(mainWindow)
		self.dialogs.append(dialog)
		dialog.show()

def main():
	app = QtWidgets.QApplication(sys.argv)
	main = MainWindow()
	main.show()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
