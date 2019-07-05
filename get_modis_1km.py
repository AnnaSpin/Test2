# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 17:56:27 2018

Download MODIS chlorophyll-a data from ftp-like website

@author: chatzopo
"""

import os
import urllib
from urllib.request import Request, urlopen, URLopener,urlretrieve
import datetime as dt
from bs4 import BeautifulSoup
from netCDF4 import Dataset


def get_urllist(url):
    # Download webpage data
    req = Request(url)
    html_page = urlopen(req)
    
    # Load webpage to a BeautifulSoup object
    soup = BeautifulSoup(html_page, "lxml")
    
    # Find and save in list all available links in the webpage
    links = []
    for link in soup.findAll('a'):
        links.append(link.get('href'))
        
    return links

def openurl(url,fname):
    try:
        # Open url that downloads file automatically
        ncurl = url + fname
        nc = urllib.request.URLopener()
        nc.retrieve(ncurl, fname)
    except:
        pass
    
if __name__ == "__main__":
    
    tic = dt.datetime.now()
    # xlims and ylims
    xlim1 = 2.3
    xlim2 = 7.5
    ylim1 = 51
    ylim2 = 56
    
    k = []
#    variables = ['POC_poc'] #"CHL_chl_ocx"] #"CHL_chlor_a","GSM_chl_gsm",
    for year in range(2007,2008):
        print(year)
        for day in range(337,350):
            
            if day<10:
                url = 'https://oceandata.sci.gsfc.nasa.gov/MODIS-Aqua/L2/'+ str(year) + '/00' + str(day)
            elif day<100:
                url = 'https://oceandata.sci.gsfc.nasa.gov/MODIS-Aqua/L2/'+ str(year) + '/0' + str(day)
            else:
                url = 'https://oceandata.sci.gsfc.nasa.gov/MODIS-Aqua/L2/'+ str(year) + '/' + str(day)
                
                
            path = "P:\\1220781-ecopotential-internal\\Intership\\KostasThesis\\07-Data\\MODIS\\1km\\" + str(year) + "\\"
#            path = 'D:\\chatzopo\\Documents\\Kostas\\Thesis\\Data\\MODIS1km\\' + str(year) + '\\'
            os.chdir(path)
            
            links = get_urllist(url)
            ksst = 0
            koc = 0
            for l in links:
                
                try:
                    if l.endswith('.nc') == False:
                        continue
                except:
                    continue
                if l.endswith('SST4.nc') or l.endswith('IOP.nc'):
                    continue
                
                fname = l[48:]
                time = fname[8:14]
                time = dt.datetime.strptime(time,"%H%M%S")
                
                var = fname[-7:-3]
                
                if var.endswith('OC'):
                    if koc>=2:
                        print('Reached 2 OC')
                        continue
                    if (time.hour<11) or (time.hour>13):
                        continue
                    if time.hour == 11 and time.minute<25:
                        continue
                    if time.hour == 13 and time.minute>15:
                        continue
                
                if var.endswith('SST'):
                    if ksst>=2:
                        print('Reached 2 SST')
                        continue
                    if time.hour<1 or time.hour>2:
                        continue
                    if time.hour == 1 and time.minute<15:
                        continue
                    if time.hour == 2 and time.minute>25:
                        continue

                print(fname)
                try:
                    urlretrieve(l,l[48:])
                    print('Retrieved')
                except:
                    print('Failed ' + l)
                    continue
                
                orig = Dataset(path +  l[48:], 'r')
                
                lon = orig.groups['navigation_data'].variables['longitude'][:].data
                lat = orig.groups['navigation_data'].variables['latitude'][:].data
                
                mask = (lon>xlim1) & (lon<xlim2) & (lat>ylim1) & (lat<ylim2)
                check = lon[mask]
                orig.close()
                if check.size<50:
#                    k = l[56:62]
#                    print(fname)
                    try:
                        os.remove(path + l[48:])
                        print('Deleted')
                    except:
                        pass
                elif check.size>200:
                    if var.endswith('SST'):
                        ksst += 1
                        print('+1 SST:' + str(ksst))
                    if var.endswith('OC'):
                        koc += 1
                        print('+1 SST:' + str(koc))
                        

                    
            
        toc = dt.datetime.now()
        print(toc-tic)