"""
MagPy
IAGA02 input filter
Written by Roman Leonhardt June 2012
- contains test, read and write function
"""

from core.magpy_stream import *


def isIAGA(filename):
    """
    Checks whether a file is ASCII IAGA 2002 format.
    """
    try:
        temp = open(filename, 'rt').readline()
    except:
        return False
    if not temp.startswith(' Format'):
        return False
    if not 'IAGA-2002' in temp:
        return False
    return True



def readIAGA(filename, headonly=False, **kwargs):
    """
    Reading IAGA2002 format data.
    """
    starttime = kwargs.get('starttime')
    endtime = kwargs.get('endtime')
    getfile = True

    fh = open(filename, 'rt')
    # read file and split text into channels
    stream = DataStream()
    # Check whether header infromation is already present
    if stream.header is None:
        headers = {}
    else:
        headers = stream.header
    data = []
    key = None

    # get day from filename (platform independent)
    splitpath = os.path.split(filename)
    tmpdaystring = splitpath[1].split('.')[0]
    daystring = re.findall(r'\d+',tmpdaystring)[0]
    if len(daystring) >  8:
        daystring = daystring[:8]
    try:
        day = datetime.strftime(datetime.strptime(daystring, "%Y%m%d"),"%Y-%m-%d")
        # Select only files within eventually defined time range
        if starttime:
            if not datetime.strptime(day,'%Y-%m-%d') >= datetime.strptime(datetime.strftime(stream._testtime(starttime),'%Y-%m-%d'),'%Y-%m-%d'):
                getfile = False
        if endtime:
            if not datetime.strptime(day,'%Y-%m-%d') <= datetime.strptime(datetime.strftime(stream._testtime(endtime),'%Y-%m-%d'),'%Y-%m-%d'):
                getfile = False
    except:
        logging.warning("Could not identify typical IAGA date in %s. Reading all ..." % daystring)
        getfile = True

    if getfile:
        for line in fh:
            if line.isspace():
                # blank line
                continue
            elif line.startswith(' '):
                # data info
                infoline = line[:-4]
                key = infoline[:23].strip()
                val = infoline[23:].strip()
                if key.find('Source') > -1:
                    if not val == '': 
                        headers['Institution'] = val
                if key.find('Station') > -1:
                    if not val == '': 
                        headers['Station'] = val
                if key.find('IAGA') > -1:
                    if not val == '': 
                        headers['IAGAcode'] = val
                if key.find('Latitude') > -1:
                    if not val == '': 
                        headers['Latitude'] = val
                if key.find('Longitude') > -1:
                    if not val == '': 
                        headers['Longitude'] = val
                if key.find('Elevation') > -1:
                    if not val == '': 
                        headers['Elevation'] = val
                if key.find('Format') > -1:
                    if not val == '': 
                        headers['DataFormat'] = val
                if key.find('Reported') > -1:
                    if not val == '': 
                        headers['Reported'] = val
                if key.find('Orientation') > -1:
                    if not val == '': 
                        headers['Orientation'] = val
                if key.find('Digital') > -1:
                    if not val == '': 
                        headers['DigitalSamplingInterval'] = val
                if key.find('Interval') > -1:
                    if not val == '': 
                        headers['DigitalFilter'] = val
                if key.find('Data Type') > -1:
                    if not val == '': 
                        headers['ProvidedType'] = val
            elif line.startswith('DATE'):
                # data header
                colsstr = line.lower().split()
                for it, elem in enumerate(colsstr):
                    if it > 2:
                        colname = "col-%s" % elem[-1]
                        colname = colname.lower()
                        headers[colname] = elem[-1].lower()
                        if elem[-1].lower() in ['x','y','z','f']:
                            headers['unit-'+colname] = 'nT' 
                    else:
                        colname = "col-%s" % elem
                        colname = colname.lower()
                        headers[colname] = elem.lower()
                        if elem.lower() in ['x','y','z','f']:
                            headers['unit-'+colname] = 'nT'
            elif headonly:
                # skip data for option headonly
                continue
            elif line.startswith('%'):
                pass
            else:
                # data entry - may be written in multiple columns
                # row beinhaltet die Werte eine Zeile
                row=[]
                # Verwende das letzte Zeichen von "line" nicht, d.h. line[:-1],
                # da darin der Zeilenumbruch "\n" steht
                for val in string.split(line[:-1]):
                    # nur nicht-leere Spalten hinzufuegen
                    if string.strip(val)!="":
                        row.append(string.strip(val))
                # Baue zweidimensionales Array auf       
                data.append(row)

    fh.close()

    for elem in data:
        # Time conv:
        row = LineStruct()
        row.time=date2num(datetime.strptime(elem[0]+'-'+elem[1],"%Y-%m-%d-%H:%M:%S.%f"))
        xval = float(elem[3])
        yval = float(elem[4])
        zval = float(elem[5])
        if (headers['col-x']=='x'):
            row.x = xval
            row.y = yval
            row.z = zval
        elif (headers['col-h']=='h'):
            row.x, row.y, row.z = hdz2xyz(xval,yval,zval)
        elif (headers['col-i']=='i'):
            row.x, row.y, row.z = idf2xyz(xval,yval,zval)
        else:
            raise ValueError
        if not float(elem[6]) == 88888:
            if headers['col-f']=='f':
                row.f = float(elem[6])
            elif headers['col-g']=='g':
                row.f = np.sqrt(row.x**2+row.y**2+row.z**2) + float(elem[6])
            else:
                raise ValueError
        stream.add(row)

    """
    Speed optimization:
    Change the whole thing to column operations


    col = ColStruct(len(data))
    for idx, elem in enumerate(data):
        # Time conv:
        xxx = col.time
        col.time[idx] = (date2num(datetime.strptime(elem[0]+'-'+elem[1],"%Y-%m-%d-%H:%M:%S.%f")))
        xval = float(elem[3])
        yval = float(elem[4])
        zval = float(elem[5])
        if (headers['col-x']=='x'):
            col.x[idx] = xval
            col.y[idx] = yval
            col.z[idx] = zval
        elif (headers['col-h']=='h'):
            col.x[idx], col.y[idx], col.z[idx] = hdz2xyz(xval,yval,zval)
        elif (headers['col-i']=='i'):
            col.x[idx], col.y[idx], col.z[idx] = idf2xyz(xval,yval,zval)
        else:
            raise ValueError
        if not float(elem[6]) == 88888:
            if headers['col-f']=='f':
                col.f[idx] = float(elem[6])
            elif headers['col-g']=='g':
                col.f[idx] = np.sqrt(row.x**2+row.y**2+row.z**2) + float(elem[6])
            else:
                raise ValueError

    arraystream = np.asarray(col)
    try:
        print len(col.time)
        print "got it"
    except:
        pass
    stream = col
    """

    return DataStream(stream, headers)    


def writeIAGA(datastream, filename, **kwargs):
    """
    Writing IAGA2002 format data.
    """
    
    mode = kwargs.get('mode')

    if os.path.isfile(filename):
        if mode == 'skip': # skip existing inputs
            exst = pmRead(path_or_url=filename)
            datastream = mergeStreams(exst,datastream,extend=True)
            myFile= open( filename, "wb" )
        elif mode == 'replace': # replace existing inputs
            exst = pmRead(path_or_url=filename)
            datastream = mergeStreams(datastream,exst,extend=True)
            myFile= open( filename, "wb" )
        elif mode == 'append':
            myFile= open( filename, "ab" )
        else: # overwrite mode
            #os.remove(filename)  ?? necessary ??
            myFile= open( filename, "wb" )
    else:
        myFile= open( filename, "wb" )

    header = datastream.header
    line = []
    if not mode == 'append':
        if header.get('Elevation') > 0:
            print header
        line.append(' Format %-15s IAGA-2002 %-34s |\n' % (' ',' '))
        line.append(' Source of Data %-7s %-44s |\n' % (' ',header.get('Institution'," ")[:44]))
        line.append(' Station Name %-9s %-44s |\n' % (' ', header.get('Station'," ")[:44]))
        line.append(' IAGA Code %-12s %-44s |\n' % (' ',header.get('IAGAcode'," ")[:44]))
        line.append(' Geodetic Latitude %-4s %-44s |\n' % (' ',header.get('Latitude (WGS84)'," ")[:44]))
        line.append(' Geodetic Longitude %-3s %-44s |\n' % (' ',header.get('Longitude (WGS84)'," ")[:44]))
        line.append(' Elevation %-12s %-44s |\n' % (' ',header.get('Elevation (NN)'," ")[:44]))
        line.append(' Reported %-13s %-44s |\n' % (' ',header.get('ProvidedComp'," ")))
        line.append(' Sensor Orientation %-3s %-44s |\n' % (' ',header.get('InstrumentOrientation'," ")[:44]))
        line.append(' Digital Sampling %-5s %-44s |\n' % (' ',header.get('DigitalSamplingInterval'," ")[:44]))
        line.append(' Data Interval Type %-3s %-44s |\n' % (' ',(header.get('ProvidedInterval'," ")+' ('+header.get('DigitalFilter'," ")+')')[:44]))
        line.append(' Data Type %-12s %-44s |\n' % (' ',header.get('ProvidedType'," ")[:44]))
        line.append('DATE       TIME         DOI %5s %9s %9s %9s      |\n' % (header.get('col-x'," ").upper(),header.get('col-y'," ").upper(),header.get('col-z'," ").upper(),header.get('col-f'," ").upper()))
    try:
        myFile.writelines(line) # Write header sequence of strings to a file
    except IOError:
        pass

    try:
        line = []
        for elem in datastream:
            row = ''
            for key in KEYLIST:
                if key == 'time':
                    try:
                        row = datetime.strftime(num2date(eval('elem.'+key)).replace(tzinfo=None), "%Y-%m-%d %H:%M:%S.%f")
                        row = row[:-3]
                        doi = datetime.strftime(num2date(eval('elem.'+key)).replace(tzinfo=None), "%j")
                        row += ' %s' % str(doi)
                    except:
                        row = ''
                        pass
                elif key == 'x':
                    row += '%13.2f' % elem.x
                elif key == 'y':
                    row += '%10.2f' % elem.y
                elif key == 'z':
                    row += '%10.2f' % elem.z
                elif key == 'f':
                    row += '  %.2f' % elem.f
            line.append(row + '\n')
        try:
            myFile.writelines( line )
            pass
        finally:
            myFile.close()
    except IOError:
        pass


