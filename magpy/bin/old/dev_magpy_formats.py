#!/usr/bin/env python
"""
MagPy - WIK analysis
"""


# Non-corrected Variometer and Scalar Data
# ----------------------------------------
from magpy.stream import *
from magpy.absolutes import *
from magpy.transfer import *

# reading WDC data directly from the WDC
# ----------------
stWDC = read(path_or_url='ftp://ftp.nmh.ac.uk/wdc/obsdata/hourval/single_year/2011/fur2011.wdc')
#HDZ: stWDC = read(path_or_url='ftp://ftp.nmh.ac.uk/wdc/obsdata/hourval/single_year/2011/lrv2011.wdc')
stWDC.plot(['x','y','z','f'])

x=1/0


basispath = r'/home/leon/Dropbox/Daten/Magnetism'

#teststream = read(path_or_url=os.path.join(basispath,'WIK-Definite2009','CDF','wik-didd-200901.cdf'))
#print teststream.mean('x')

#print num2date(teststream[-1].time)
#stream.plot(['x','y','z'])
stream = read(path_or_url=os.path.join(basispath,'WIK-Definite2009','WDC','wik2009.wdc'))
year = num2date(stream[0].time).year
stream.plot(['x','y','z','f'],plottitle='Magnetic data for '+str(year),outfile=os.path.join(basispath,'Yearbook',str(year)+'.png'))
monthlst = DataStream()

for i in range(12):
    startmonth = str(i+1)
    stdate = str(year)+'-'+str(i+1)+'-1'
    endmonth = str(i+2)
    if i+2 > 12:
        year = year+1
        endmonth = str(1)
    eddate = str(year)+'-'+endmonth+'-1'
    print stdate, eddate
    stream = read(path_or_url=os.path.join(basispath,'WIK-Definite2009','WDC','wik2009.wdc'),starttime=stdate, endtime=eddate)
    row = LineStruct()
    row.time = np.mean(stream._get_column('time'))
    row.x = stream.mean('x')
    row.y = stream.mean('y')
    row.z = stream.mean('z')
    row.f = stream.mean('f')
    monthlst.add(row)
    stream.header['TEXcaption'] = "Hourly magnetic data for %s" % datetime.strftime(num2date(stream[0].time),"%b %Y")
    stream.header['TEXlabel'] = "tab:"+str(i+1) 
    stream.header['TEXfontsize'] = "\\scriptsize"
    stream.header['TEXrotate'] = True
    stream.write(os.path.join(basispath,'Yearbook'),filenamebegins='latextab-',filenameends='.tex',format_type='LATEX',coverage='month', dateformat='%m',mode='wdc')

monthlst.header['TEXcaption'] = "Monthly magnetic data for %d" % year
monthlst.header['TEXlabel'] = "tab:monthly" 
monthlst.header['TEXfontsize'] = "\\scriptsize"
monthlst.header['TEXrotate'] = False
yeart = monthlst.mean('time')
yearx = monthlst.mean('x')
yeary = monthlst.mean('y')
yearz = monthlst.mean('z')
yearf = monthlst.mean('f')
print yearx, yeary, yearz, yearf
#monthlst.header['TEXrotate'] = True
monthlst = monthlst._convertstream('xyz2hdz')
monthlst.write(os.path.join(basispath,'Yearbook'),filenamebegins='latextab-month',filenameends='.tex',format_type='LATEX',coverage='all')

x=1/0

# Reading data from NOAA (ACE satellite data)
# ----------------

# Job 1: Read data from net and save locally (every 30 min?)
now = datetime.utcnow()
today = datetime.strftime(now,'%Y%m%d')
acedata = today + '_ace_swepam_1m.txt'
ace = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (acedata))
ace.write(os.path.join("/home/leon/Dropbox/Daten/Magnetism","SolarData"),filenamebegins='ace-swepam_',format_type='PYCDF')
ace2data = today + '_ace_sis_5m.txt'
ace2 = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (ace2data))
ace3data = today + '_ace_epam_5m.txt'
ace3 = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (ace3data))
ace5 = mergeStreams(ace3,ace2,keys=['t1','t2'])
ace5.write(os.path.join("/home/leon/Dropbox/Daten/Magnetism","SolarData"),filenamebegins='ace-5min_',coverage='month', dateformat='%Y%m', format_type='PYCDF',mode='replace')

if int(datetime.strftime(now,'%H')) < 1: # Repeat for last day to get full coverage
    today = datetime.strftime(now-timedelta(days=1),'%Y%m%d')
    acedata = today + '_ace_swepam_1m.txt'
    ace = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (acedata))
    ace.write(os.path.join("/home/leon/Dropbox/Daten/Magnetism","SolarData"),filenamebegins='ace-swepam_',format_type='PYCDF')
    ace2data = today + '_ace_sis_5m.txt'
    ace2 = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (ace2data))
    ace3data = today + '_ace_epam_5m.txt'
    ace3 = read(path_or_url='http://www.swpc.noaa.gov/ftpdir/lists/ace/%s' % (ace3data))
    ace5 = mergeStreams(ace3,ace2,keys=['t1','t2'])
    ace5.write(os.path.join("/home/leon/Dropbox/Daten/Magnetism","SolarData"),filenamebegins='ace-5min_',coverage='month', dateformat='%Y%m', format_type='PYCDF',mode='replace')



# Job 2: Read data from net and save locally (every 3 hours)

kp = read(path_or_url='http://www-app3.gfz-potsdam.de/kp_index/qlyymm.tab')
# Append that data to the local list (as only one month is published online
kp.write(os.path.join("/home/leon/Dropbox/Daten/Magnetism","SolarData"),filenamebegins='gfzkp',format_type='PYCDF',dateformat='%Y%m',coverage='month')

# Get SOHO image and transfer it to homepage
import urllib
today = datetime.strftime(datetime.utcnow(),"%Y%m%d_%H")

urllib.urlretrieve("http://sohowww.nascom.nasa.gov/data/realtime/eit_304/512/latest.jpg","/home/leon/CronScripts/%s_SOHO_EIT304.jpg" % (today))
urllib.urlretrieve("http://sohowww.nascom.nasa.gov/data/realtime/eit_304/512/latest.jpg","/home/leon/CronScripts/latest_eit304.jpg")
urllib.urlretrieve("http://sohowww.nascom.nasa.gov/data/realtime/hmi_mag/512/latest.jpg","/home/leon/CronScripts/%s_SOHO_HMIMAG.jpg" % (today))
urllib.urlretrieve("http://sohowww.nascom.nasa.gov/data/realtime/hmi_mag/512/latest.jpg","/home/leon/CronScripts/latest_hmimag.jpg")
ftpdatatransfer(localfile=os.path.join('/home/leon/CronScripts','%s_SOHO_EIT304.jpg' % (today)), ftppath='/stories/currentdata/sun/eit304',myproxy='94.136.40.103',login='data@conrad-observatory.at',passwd='data2COBS',logfile='sun.log')
ftpdatatransfer(localfile=os.path.join('/home/leon/CronScripts','%s_SOHO_HMIMAG.jpg' % (today)), ftppath='/stories/currentdata/sun/eit304',myproxy='94.136.40.103',login='data@conrad-observatory.at',passwd='data2COBS',logfile='sun.log')
ftpdatatransfer(localfile=os.path.join('/home/leon/CronScripts','latest_eit304.jpg'), ftppath='/stories/currentdata/sun/latest',myproxy='94.136.40.103',login='data@conrad-observatory.at',passwd='data2COBS',logfile='sun.log')
ftpdatatransfer(localfile=os.path.join('/home/leon/CronScripts','latest_hmimag.jpg'), ftppath='/stories/currentdata/sun/latest',myproxy='94.136.40.103',login='data@conrad-observatory.at',passwd='data2COBS',logfile='sun.log')




# Job 3: Create plots (every 30 min like Job 1 or even 10 min)

stace = read(path_or_url=os.path.join(basispath,'SolarData','ace-swepam*'))
stace.plot(['x','y','z'],labelcolor='0.2',bgcolor='#d5de9c',grid=True,gridcolor='#316931')


stace5 = read(path_or_url=os.path.join(basispath,'SolarData','ace-5min*'))
stace5.plot(['f','df','dx','dy','dz','var3','var4','t1','t2'])

# Reading data from the GFZ (Kp)
# ----------------
stream = read(path_or_url=os.path.join(basispath,'SolarData','gfzkp*'))
stream.plot(['var1'],bartrange=0.06,symbollist=['z'],specialdict = {'var1': [0,9]})

# Extract last 30 min mean values of solar wind speed, proton density and proton flux 75-100, and last Kp
# Solar wind (max 1000), proton dens, proton flux > 500 warning, > 1000 approaching (maximum reached about 20 min before magnetic storm)
print "Values"
#print stace[-1].x
i = 1
while isnan(stace[-i].x):
    i=i+1
pd = stace[-i].x
i = 1
while isnan(stace[-i].y):
    i=i+1
sw = stace[-i].y
i = 1
while isnan(stace5[-1].dy):
    i=i+1
pf = stace5[-1].dy

vals = [sw,pd,pf,stream[-1].var1,stream[-1].var1]
valsmax = [1000,40,500,9,9]

names = [r'$V_{Sol}$',r'$\rho_{p^+}$',r'$\Phi_{p^+}$',r'$K_p$',r'$K_{Cobs}$'] 
fig = plt.figure(figsize=(5,5))
im = plt.imread('/home/leon/CronScripts/image3156.png')
implot = plt.imshow(im, aspect='auto')
ax1 = fig.add_subplot(111)
plt.subplots_adjust(left=0.115, right=0.88)
fig.canvas.set_window_title('Space Weather condition chart')
ax1.get_xaxis().set_visible(False)

pos = np.arange(5)+0.5 #Center bars on the Y-axis ticks
nm = Normalize(0, 1) 

for i in range(len(vals)):
    if float(vals[i])/valsmax[i] < 0.3334:
        col = 'g'
    elif float(vals[i])/valsmax[i] < 0.6667:
        col = 'y'
    else:
        col = 'r'
    if vals[i] > valsmax[i]:
        vals[i] = valsmax[i]
    rects = ax1.barh(pos[i]*100, float(vals[i])/valsmax[i]*500, align='center', height=50, color=col)

ax1.axis([0,500,0,500])
yticks(pos*100, names)
for tick in ax1.yaxis.get_major_ticks():
    tick.set_pad(-50)
ax1.set_title('Current Space Weather')

plt.show()
#savefig()
#ftpdatatransfer(localfile=os.path.join('/home/leon/CronScripts','latest_hmimag.jpg'), ftppath='/stories/currentdata/sun/latest',myproxy='94.136.40.103',login='data@conrad-observatory.at',passwd='data2COBS',logfile='sun.log')


x = 1/0

# Annotation of plots
# ----------------
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','data','*'),starttime='2009-12-01', endtime='2009-12-2')
stDIDD.plot(['x','y','z','f'],annotate=True)
stDIDD = stDIDD.remove_flagged()
stDIDD.plot(['x','y','z','f'])
# Check for storm onsets
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','data','*'),starttime='2011-9-9', endtime='2011-9-14')
stDIDD = stDIDD._convertstream('xyz2hdz')
stDIDD = stDIDD.aic_calc('x',timerange=timedelta(hours=2))
stDIDD = stDIDD.differentiate(keys=['var2'],put2keys=['var3'])
stDIDD = stDIDD.eventlogger('var3',[20,30,50],'>',None,True)
stfilt = stDIDD.filtered(filter_type='linear',filter_width=timedelta(minutes=60),filter_offset=timedelta(minutes=30))
stfilt = stfilt._get_k(key='var2',put2key='var4',scale=[0,70,140,210,280,350,420,490,560])
stfilt.header['col-var4'] = 'Cobs k_-index'
stDIDD = mergeStreams(stDIDD,stfilt,key=['var4'])
stDIDD.plot(['x','var2','var3','var4'],bartrange=0.02,symbollist = ['-','-','-','z'],plottitle = "Storm onsets and local variation index", annotate=True)

x=1/0


# Read Radon data
# ----------------
stRADON = read(path_or_url='ftp://trmsoe:mgt.trms!@www.zamg.ac.at/data/radon/')
stRADON.plot(['x','t1','var1'],padding=0.2)
stRADON.powerspectrum('x')

x = 1/0


# reading Lemis binary data from the memory card
# ----------------
stLemibin = read(path_or_url='/home/leon/CronScripts/LemiBinary/L025_065.B01')
stLemibin.plot(['x','y','z','t1','t2'])
stLemibin.spectrogram(['x'],wlen=10,dbscale=True,title='LEMI at GMO(Conrad) - HF-spectra')
stLemibin.powerspectrum('x')

x=1/0


# reading WDC data directly from the WDC
# ----------------
stWDC = read(path_or_url='ftp://ftp.nmh.ac.uk/wdc/obsdata/hourval/single_year/2011/fur2011.wdc')
#HDZ: stWDC = read(path_or_url='ftp://ftp.nmh.ac.uk/wdc/obsdata/hourval/single_year/2011/lrv2011.wdc')
stWDC.plot(['x','y','z','f'])

x=1/0

# write WDC Format
# ----------------
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','preliminary','*'),starttime='2012-09-01', endtime='2012-10-01')
stDIDD = stDIDD.flag_stream('x',3,"Water income",datetime(2012,9,28,15,35,0,0),datetime(2012,9,28,17,21,0,0))
stDIDD = stDIDD.remove_flagged()
stDIDD = stDIDD.filtered(filter_type='linear',filter_width=timedelta(minutes=60),filter_offset=timedelta(minutes=30))
stDIDD.write(os.path.join(basispath),filenamebegins='wik',format_type='WDC',coverage='month',dateformat='%Y%m')
# ToDo: WDC minute filter

x=1/0

# write IAGA2002 Format
# ----------------
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','preliminary','*'),starttime='2012-09-01', endtime='2012-09-02')
stDIDD.write(os.path.join(basispath),filenamebegins='IAGA_',format_type='IAGA')

x=1/0

# write monthly files
# ----------------
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','preliminary','*'),starttime='2012-09-01', endtime='2012-10-2')
stDIDD.write(os.path.join(basispath),filenamebegins='Mon_',format_type='PYCDF',dateformat="%Y-%m",coverage='month')
# Works for DIDD when read again: Test this function for all other file formats as well
stDIDD = read(path_or_url=os.path.join(basispath,'Mon_*'),starttime='2012-09-01', endtime='2012-10-2')
stDIDD.plot(['x','y','z','f'])

x=1/0

stLEMI = read(path_or_url=os.path.join(basispath,'LEMI-WIK','data','*'),starttime='2011-01-01', endtime='2011-03-31')
stLEMI = stLEMI.remove_flagged()
absLEMI = read(path_or_url=os.path.join(basispath,'ABSOLUTE-RAW','data','absolutes_lemi.txt'))
stLEMI = stLEMI.rotation(alpha=3.3)
stLEMI = stLEMI.baseline(absLEMI,knotstep=0.05,plotbaseline=True)
stLEMI = stLEMI.filtered(filter_type='linear',filter_width=timedelta(minutes=60),filter_offset=timedelta(minutes=30))
stDIDD = read(path_or_url=os.path.join(basispath,'DIDD-WIK','data','*'),starttime='2011-01-01', endtime='2011-03-31')
stDIDD = stDIDD.remove_flagged()
absDIDD = read(path_or_url=os.path.join(basispath,'ABSOLUTE-RAW','data','absolutes_didd.txt'))
stDIDD = stDIDD.baseline(absDIDD,knotstep=0.05,plotbaseline=True)
stDIDD = stDIDD.filtered(filter_type='linear',filter_width=timedelta(minutes=60),filter_offset=timedelta(minutes=30))
stLEMI.plot(['x','y','z','f'])
stDIDD.plot(['x','y','z','f'])
stdiff = subtractStreams(stDIDD,stLEMI,keys=['x','y','z','f']) # Stream_a gets modified - stdiff = st1mod...
stdiff.plot(['x','y','z','f'])

x=1/0

# Read optical data files
# ----------------
basispath = r'/home/leon/Dropbox/Daten/Magnetism/OPT-WIK'
stD = read(path_or_url=os.path.join(basispath,'D_2009_0*'))
stH = read(path_or_url=os.path.join(basispath,'H_2009_0*'))
stZ = read(path_or_url=os.path.join(basispath,'Z_2009_0*'))
stF = read(path_or_url=os.path.join(basispath,'F_2009_0*'))
stHZ = mergeStreams(stH,stZ)
stHDZ = mergeStreams(stHZ,stD)
stOPT = mergeStreams(stHDZ,stF)
stOPT = stOPT._convertstream('hdz2xyz')
stOPT.plot(['x','y','z','f'])


# Read binary data from the GDAS logger
# ----------------

basispath = r'/home/leon/Dropbox/Daten/Magnetism/DataFormats'
infile = os.path.join(basispath,'WIC-GDAS','WIC_v1_20120906.sec')
st = read(path_or_url=infile)
st.plot(['x','y','z'],outfile="test.png")

ftpdatatransfer(localpath='',filestr="test.png", ftppath='/data', myproxy='www.zamg.ac.at',port=21, login='trmsoe', passwd='mgt.trms!',logfile = 'ltest.txt')

st2 = read(path_or_url='ftp://trmsoe:mgt.trms!@www.zamg.ac.at/data/WIC_v1_min_20120906.bin')
st2.plot(['x','y','z','f'])


x=1/0


# Read data from field surveys
# ----------------

basispath = r'/home/leon/Dropbox/Projects/SpaceWeather/Conrad Observatorium/Basismessungen'

st = read(path_or_url=os.path.join(path,'outdoorsurvey_2012-08-*.csv'))
st = st.remove_outlier()
st = st.remove_flagged()
st.plot(['f'],plottitle = "Ex 1 - Plot")
bas = read(path_or_url=os.path.join(basispath,'*'))
bas = bas.remove_outlier()
bas = bas.remove_flagged()
bas.plot(['f'],plottitle = "Basis")
newst = subtractStreams(st,bas,keys='f')
newst.plot(['f'],plottitle = "Sub")
newst.write(path,coverage='all',filenamebegins='outdoorsurvey_red_2012-08-02')


x = 1/0

# Example for the analysis of WIK data

# 
# 1)   Absolute Values
#
# Analyze Absolute measurments
logging.info("----- Analyzing Absolute measurements -----")
#absanapath = os.path.normpath('f:\\Absolute-Cobenzl\\Analysis')
#absarchpath = os.path.normpath('f:\\Absolute-Cobenzl\\Archive')
#absdidd = read(path_or_url=os.path.normpath('..\\dat\\output\\absolutes\\absolutes_didd.txt'))
#absdidd = analyzeAbsFiles(path_or_url=absanapath, alpha=0.0, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), archivepath=absarchpath)
#absdidd.write('..\\dat\\output\\absolutes\\',coverage='all',mode='replace',filenamebegins='absolutes_didd')
#absdidd.plot(['x','y','z'],plottitle = "Analysis of absolute values")
#abslemi = analyzeAbsFiles(path_or_url=absanapath, alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), archivepath=absarchpath)
#abslemi.write('..\\dat\\output\\absolutes\\',coverage='all',mode='replace',filenamebegins='absolutes_lemi')
#abslemi.plot(['x','y','z'],plottitle = "Analysis of absolute values")


#absdidd = read(path_or_url=os.path.join('..','dat','output','absolutes','absolutes_didd.txt'))
#abslemi = read(path_or_url=os.path.join('..','dat','output','absolutes','absolutes_lemi.txt'))
#absdidd.plot(['x','y','z'],plottitle = "Analysis of absolute values - DIDD")
#abslemi.plot(['x','y','z'],plottitle = "Analysis of absolute values - LEMI")

#absdiff = subtractStreams(absdidd,abslemi,keys=['x','y','z','f']) # Stream_a gets modified - stdiff = st1mod...
#absdiff.plot(['x','y','z','f'],plottitle = "Differences of absolute values")

abslemi = analyzeAbsFiles(path_or_url="ftp://data@conrad-observatory.at:data2COBS@94.136.40.103/cobenzlabs/2011-11-21_13-51-42_AbsoluteMeas.txt", alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'))


#abslemi = analyzeAbsFiles(path_or_url="ftp://94.136.40.103:21",alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'))
#abslemi = analyzeAbsFiles(path_or_url="ftp://data@conrad-observatory.at:data2COBS@94.136.40.103/cobenzlabs/", alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'))

# Do it for the Lemi
abslemi = analyzeAbsFiles(path_or_url="ftp://data@conrad-observatory.at:data2COBS@94.136.40.103/cobenzlabs/", alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'))
# write the data
abslemi.write(os.path.join('..','dat','absolutes'),coverage='all',mode='replace',filenamebegins='absolutes_lemi')
# make plot covering one year back from now
start = datetime.utcnow()-timedelta(days=365)
abslemi = read(path_or_url=os.path.join('..','dat','absolutes','absolutes_lemi.txt'),starttime=start)
abslemi.plot(['x','y','z'],plottitle = "Analysis of absolute values - LEMI", outfile="AutoAnalysisLemi")

# Repeat for DIDD but write new logfile
absdidd = analyzeAbsFiles(path_or_url="ftp://data@conrad-observatory.at:data2COBS@94.136.40.103/cobenzlabs/", alpha=0.0, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), archivepath=os.path.normpath('f:\\Absolute-Cobenzl\\Archive'))
absdidd.write(os.path.join('..','dat','absolutes'),coverage='all',mode='replace',filenamebegins='absolutes_didd')
absdidd = read(path_or_url=os.path.join('..','dat','absolutes','absolutes_lemi.txt'),starttime=start)
absdidd.plot(['x','y','z'],plottitle = "Analysis of absolute values - DIDD", outfile="AutoAnalysisDIDD")
# Use new mail function to send log and plot
msg = 'Successfully analyzed files were transferred to archive directory\n\nControl the graph - still erroneous data is usually related to wrong azimuth marks\nThis data has to be uploaded manually again for correction\nPlease check the remaining files on the server for errors -> see attached logfile for hints\n\nCheers, Your Analysis-Robot'
send_mail('roman_leonhardt@web.de', ['roman.leonhardt@zamg.ac.at'], text=msg, files=['magpy.log','AutoAnalysisDIDD.png','AutoAnalysisLemi.png'], smtpserver='smtp.web.de',user="roman_leonhardt",pwd="2kippen")

plt.show()

test = 1/0


# Script for automatic procedure using cron job
logging.info("----- Analyzing Absolute measurements -----")
# - a) Download all files to analysis folder using transfer package (or access database)

# - b) Analyse data for lemi , keep data in analysis folder 
absanapath = os.path.normpath('f:\\Absolute-Cobenzl\\Analysis') # try to use ftp path 
abslemi = analyzeAbsFiles(path_or_url=absanapath, alpha=3.3, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\LEMI\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'))
# - c) Analyse data for didd , move data to archive folder
absarchpath = os.path.normpath('f:\\Absolute-Cobenzl\\Archive')
absdidd = analyzeAbsFiles(path_or_url=absanapath, alpha=0.0, beta=0.0, variopath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), scalarpath=os.path.normpath('f:\\Vario-Cobenzl\\dIdD-System\\*'), archivepath=absarchpath)
# - d) Eventually upload AbsPlots to status page of homepage (or send by mail with (f))

# - e) Upload erroneous files to server again (requires a correction possibility

# - f) Send logging info to observer





# 2) Analyze data





pmagpath = 'f:\\Vario-Cobenzl\\dIdD-System\\pmag\\2011\\01\\*'
# see magpy_gsm19
st = read(path_or_url=os.path.normpath(pmagpath))
st.plot(['f'],plottitle = "Ex 1 - Plot")

st = st.remove_outlier()
st = st.remove_flagged()

st.plot(['f'],plottitle = "Ex 1 - Plot")


# write
st2 = read(path_or_url=os.path.normpath(diddpath))
st2.plot(['f'],plottitle = "Ex 1 - Plot")

st2 = st2.remove_outlier()

stdiff = subtractStreams(st,st2,keys=['f']) # Stream_a gets modified - stdiff = st1mod...
#plot

# flag
