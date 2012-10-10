"""
MagPy
GSM 19 input filter
Written by Roman Leonhardt June 2012
- contains test and read function, toDo: write function
"""

from core.magpy_stream import *

def int_to_roman(input):
   """
   Convert an integer to Roman numerals.

   taken from:
   http://code.activestate.com/recipes/81611-roman-numerals/

   Examples:
   >>> int_to_roman(0)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(-1)
   Traceback (most recent call last):
   ValueError: Argument must be between 1 and 3999

   >>> int_to_roman(1.5)
   Traceback (most recent call last):
   TypeError: expected integer, got <type 'float'>

   >>> for i in range(1, 21): print int_to_roman(i)
   ...
   I
   II
   III
   IV
   V
   VI
   VII
   VIII
   IX
   X
   XI
   XII
   XIII
   XIV
   XV
   XVI
   XVII
   XVIII
   XIX
   XX
   >>> print int_to_roman(2000)
   MM
   >>> print int_to_roman(1999)
   MCMXCIX
   """
   if type(input) != type(1):
      raise TypeError, "expected integer, got %s" % type(input)
   if not 0 < input < 4000:
      raise ValueError, "Argument must be between 1 and 3999"   
   ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
   nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
   result = ""
   for i in range(len(ints)):
      count = int(input / ints[i])
      result += nums[i] * count
      input -= ints[i] * count
   return result


def roman_to_int(input):
   """
   Convert a roman numeral to an integer.

   http://code.activestate.com/recipes/81611-roman-numerals/   

   >>> r = range(1, 4000)
   >>> nums = [int_to_roman(i) for i in r]
   >>> ints = [roman_to_int(n) for n in nums]
   >>> print r == ints
   1

   >>> roman_to_int('VVVIV')
   Traceback (most recent call last):
    ...
   ValueError: input is not a valid roman numeral: VVVIV
   >>> roman_to_int(1)
   Traceback (most recent call last):
    ...
   TypeError: expected string, got <type 'int'>
   >>> roman_to_int('a')
   Traceback (most recent call last):
    ...
   ValueError: input is not a valid roman numeral: A
   >>> roman_to_int('IL')
   Traceback (most recent call last):
    ...
   ValueError: input is not a valid roman numeral: IL
   """
   if type(input) != type(""):
      raise TypeError, "expected string, got %s" % type(input)
   input = input.upper()
   nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
   ints = [1000, 500, 100, 50,  10,  5,   1]
   places = []
   for c in input:
      if not c in nums:
         raise ValueError, "input is not a valid roman numeral: %s" % input
   for i in range(len(input)):
      c = input[i]
      value = ints[nums.index(c)]
      # If the next place holds a larger number, this value is negative.
      try:
         nextvalue = ints[nums.index(input[i +1])]
         if nextvalue > value:
            value *= -1
      except IndexError:
         # there is no next place.
         pass
      places.append(value)
   sum = 0
   for n in places: sum += n
   # Easiest test for validity...
   if int_to_roman(sum) == input:
      return sum
   else:
      raise ValueError, 'input is not a valid roman numeral: %s' % input

    
def isGSM19(filename):
    """
    Checks whether a file is GSM19 format.
    """
    try:
        temp = open(filename, 'rt')
    except:
        return False
    li = temp.readline()
    while li.isspace():
        li = temp.readline()
    if not li.startswith('Gem Systems GSM-19'):
        if not li.startswith('/Gem Systems GSM-19'):
            return False
    return True


def readGSM19(filename, headonly=False, **kwargs):
    """
    Reading GSM19 format.
    Basis looks like:

    Gem Systems GSM-19W 3101329 v6.0 24 X 2003 
    ID 1 file 23c-ost .b   09 VII10
    datum  48000.00


    115014.0  48484.12 99
    115015.0  48487.04 99
    115016.0  48489.92 99
    115017.0  48488.16 99
    115018.0  48486.06 99
    115019.0  48487.17 99
    115020.0  48487.44 99

    Others look like
    """
    timestamp = os.path.getmtime(filename)
    creationdate = datetime.fromtimestamp(timestamp)
    daytmp = datetime.strftime(creationdate,"%Y-%m-%d")
    YeT = daytmp[:2]
    
    fh = open(filename, 'rt')
    # read file and split text into channels
    stream = DataStream()
    # Check whether header infromation is already present
    if stream.header == None:
        headers = {}
    else:
        headers = stream.header
    data = []
    key = None

    for line in fh:
        if line.isspace():
            # blank line
            pass
        elif line.startswith('Gem Systems GSM-19') or line.startswith('/Gem Systems GSM-19'):
            head = line.split()
            headers['SerialNumber'] =  head[3]
            headers['Instrument'] = head[2]+head[4]
            # data header
            pass
        elif line.startswith('ID') or line.startswith('/ID'):
            tester = line.split('.')
            typus = tester[1].split()
            print typus[0]
            # typus[0] can be b, m, g, wg, ...
            if len(typus) == 2:
                da = typus[1][:2]
                yecnt = len(typus[1])-2
                ye = typus[1][yecnt:]
                inp = typus[1][2:yecnt]
                mo = roman_to_int(inp)
                day = str(YeT)+str(ye)+'-'+str(mo)+'-'+str(da)
            else:
                da = typus[1]
                yecnt = len(typus[2])-2
                ye = typus[2][yecnt:]
                inp = typus[2][:yecnt]
                mo = roman_to_int(inp)
                day = str(YeT)+str(ye)+'-'+str(mo)+'-'+str(da)
            # data header
            pass
        elif line.startswith('datum'):
            # data header
            pass
        elif headonly:
            # skip data for option headonly
            continue
        else:
            elem = line.split()
            if len(elem) == 3 and typus[0]=='b': # a Baseline file
                try:
                    row = LineStruct()
                    hour = elem[0][:2]
                    minute = elem[0][2:4]
                    second = elem[0][4:]
                    # add day
                    strtime = datetime.strptime(day+"T"+str(hour)+":"+str(minute)+":"+str(second),"%Y-%m-%dT%H:%M:%S.%f")
                    row.time=date2num(strtime)
                    row.f = float(elem[1])
                    row.var5 = float(elem[2])
                    stream.add(row)
                except:
                    logging.warning("Error in input data: %s - skipping bad value" % filename)
                    pass
            elif typus[0] == 'g':
                try:
                    row = LineStruct()
                    hour = elem[6][:2]
                    minute = elem[6][2:4]
                    second = elem[6][4:]
                    # add day
                    strtime = datetime.strptime(day+"T"+str(hour)+":"+str(minute)+":"+str(second),"%Y-%m-%dT%H:%M:%S.%f")
                    row.time=date2num(strtime)
                    row.f = float(elem[2])
                    row.df = float(elem[3])
                    row.var5 = float(elem[4])
                    row.var1 = float(elem[0])
                    row.var2 = float(elem[1])
                    stream.add(row)
                except:
                    logging.warning("Error in input data: %s - skipping bad value" % filename)
                    pass                
            elif typus[0] == 'wg':
                headers['col-var4'] = 'N satelites'
                headers['col-var1'] = 'Latitude'
                headers['col-var2'] = 'Longitude'
                headers['col-var3'] = 'Elevation'
                try:
                    row = LineStruct()
                    hour = elem[8][:2]
                    minute = elem[8][2:4]
                    second = elem[8][4:]
                    # add day
                    try:
                        strtime = datetime.strptime(day+"T"+str(hour)+":"+str(minute)+":"+str(second),"%Y-%m-%dT%H:%M:%S.%f")
                    except:
                         strtime = datetime.strptime(day+"T"+str(hour)+":"+str(minute)+":"+str(second),"%Y-%m-%dT%H:%M:%S")
                    row.time=date2num(strtime)
                    row.f = float(elem[3])
                    row.df = float(elem[4])
                    row.var5 = float(elem[5])
                    row.var1 = float(elem[0])
                    row.var2 = float(elem[1])
                    row.var3 = float(elem[2])
                    row.var4 = float(elem[7])
                    stream.add(row)
                except:
                    logging.warning("Error in input data: %s - skipping bad value" % filename)
                    pass
            else:
                if not len(elem) == 3: 
                    logging.error("GSM 19 file - %s - type %s not yet supported" % (filename, typus[0]))


    if len(stream) > 0:
        headers['col-f'] = 'f'
        headers['unit-col-f'] = 'nT'

    logging.info("Loaded GSM19 file of type %s, using creationdate of file (%s), %d values" % (typus[0],day,len(stream)))
    fh.close()

    return DataStream(stream, headers)    