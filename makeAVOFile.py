#!/opt/local/bin/python

from osgeo import gdal
from osgeo import osr
import numpy as np
import pyproj
import sys
import os

def read_gdal_file(filehandle,band=1):
    geotransform = filehandle.GetGeoTransform()
    geoproj = filehandle.GetProjection()
    banddata = filehandle.GetRasterBand(band)
    data = banddata.ReadAsArray()
    return filehandle.RasterXSize,filehandle.RasterYSize,geotransform,geoproj,data

# Function to crop the input data to the bounding box as defined by AVO
def cropToAVO(data,dtransform,AVOtransform):
	return 1

# Given a geotransform, calculate the bounding box
def createBBox(xSize,ySize,transform):	
	return transform[0], transform[3], transform[0]+transform[1]*xSize,transform[3]+transform[5]*ySize

def createBlackImage(lines,samples,centerLat,centerLon,pixelH,pixelW):
	bData = np.zeros((lines,samples))
	zone = int((180+centerLon)/6) + 32601
	srs = osr.SpatialReference()
	srs.ImportFromEPSG(zone)
	strZone = "+init=EPSG:"+str(zone)
	UTM = pyproj.Proj(strZone)
	(x,y) = UTM(centerLon,centerLat)
	print x,y
	ulx = x-pixelW*samples/2
	uly = y+pixelH*lines/2
	transform = (ulx,pixelW,0,uly,0,-1*pixelH)
	format = "GTiff"
	driver = gdal.GetDriverByName(format)
	dst_datatype = gdal.GDT_Byte
	dst_ds = driver.Create("black.tif",samples,lines,1,dst_datatype)
	dst_ds.GetRasterBand(1).WriteArray(bData)
	dst_ds.SetGeoTransform(transform)
	dst_ds.SetProjection(srs.ExportToWkt())
	return zone,transform


if __name__ == '__main__':

	if len(sys.argv)==1:
		print "**************************"
		print "Usage:  makeAVOFile.py <input volcano image>"
		print "-> Output are files merged.tif and merged.png which have the input volcano image"
		print "-> merged with a black background made to the AVO specification"
		print "**************************"
		sys.exit()

	# master projection=mercator center_lat=53.42 N center_lon=168.13 W 
	#num_lines=800 num_samples=1000 pixel_width=0.25 pixel_height=0.25 
	#rotate_angle=0 move_center=no   

	# Create a black image based on AVO parameters (converted crazy AVO projection definition to UTM)
	numSamples = 1000
	numLines = 800
	pWidth = 250 
	pHeight = 250 
	cLat = 53.42
	cLon = -168.13

	# Create blank image of AVO dimension.  The function returns the zone number so we can
	# be sure that the blank image and the SAR image are in same projection
	zone,transform = createBlackImage(numLines,numSamples,cLat,cLon,pHeight,pWidth)

	# sys.argv[1] is the input geotiff file
	#gtHandle = gdal.Open(sys.argv[1])

	# Using external gdal programs to do some of the heavier lifting.  This is kludgy to call 
	# out to the system, but so be it.  

	#convert input image to dimensions specified by AVO
	cmd = "gdalwarp -t_srs EPSG:"+str(zone)+" -tr "+str(pWidth)+" "+str(pHeight)+" -cutline Coastal_Land_Area.shp "+sys.argv[1]+" temp.tif"
	print cmd
	os.system(cmd)

	# Merge the black image with the volcano image	
	cmd = "gdal_merge.py -o merge.tif black.tif temp.tif"
	#print cmd
	os.system(cmd)

	cmd = "convert merge.tif merge.png"
	os.system(cmd)


	cmd = "rm temp.tif"
	os.system(cmd)








