import numpy as np
import matplotlib.pyplot as plt

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def create_sounding_url(date,time,stnm):
    '''
    usage:  
         create_sounding_url('30122010','00','06610')

    input: 
         date (str) - the date as ddmmyyyy
         time (str) - the time as hh   ('00' or '12')
         stnm (str) - the station number, e.g.: 
                    10410 Essen (D)
                    10618 Idar-Oberstein (D)
                    07145 Trappes (F)
                    06260 De Bilt (NL)
                    10238 Bergen (D)
                    06610 Payerne (CH)   

    output: 
         url (str) 
    '''
    soundingurl = 'http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%%3ALIST&YEAR=%s&MONTH=%s&FROM=%s%s&TO=%s%s&STNM=%s' \
    % (date[4:8],date[2:4],date[:2],time[:2],date[:2],time[:2], stnm)
    return soundingurl

def get_sounding(file_or_url):
    '''
    input: 
         file_or_url (string)  -  the name of the sounding file or the URL of the sounding file
    output: 
         sounding (dictionary) - a dictionary containing the sounding data
    '''
    import urllib2
    # load the data from a sounding, using the university of wyoming website
    if file_or_url[:7]=='http://':
        soundingfile = urllib2.urlopen(file_or_url).read()
        filelines = soundingfile.splitlines()
    else:
        soundingfile = open(file_or_url,'r').read()
        filelines = soundingfile.splitlines()
    # The first line is found by detecting the first line where all entries are numbers
    i_firstrow = None
    for n,line in enumerate(filelines):
        if line.split():
            if line.split()[0]=='PRES':
                i_colnames = n
            if False not in [is_number(element) for element in line.split()] and i_firstrow is None:
                i_firstrow = n
            if '</PRE><H3>' in line:
                i_lastrow = n
    
    indices = range(7,11*8,7)
    indices.insert(0,0)
                
    splitindices = [(a,a+7) for a in indices]
    columndict = dict((key,ncol) for ncol,key in zip(splitindices,filelines[i_colnames].split()))

    variables = filelines[i_colnames].split()
    datadict = dict((key,[]) for key in filelines[i_colnames].split() if key in variables)

    
    for l in filelines[i_firstrow:i_lastrow]:
        for key in datadict:
            colstart,colend = columndict[key]
            data = l[colstart:colend]
            if data.isspace():
                data = 'nan'
            datadict[key].append(data)
    for key in datadict:
        datadict[key]=np.array(datadict[key],dtype=float)
        
    #convert wind from polar to carthesian coordinates
    if 'DRCT' in datadict:  
        datadict['DRCT'] = datadict['DRCT']*np.pi/180
    if 'SKNT' in datadict and 'DRCT' in datadict:  
        datadict['U'],datadict['V'] = datadict['SKNT']*np.sin(-datadict['DRCT']),-datadict['SKNT']*np.cos(datadict['DRCT'])
    return datadict

def plot_skewT_ax(ax=None,xlims=(-35,45),ylims=(105000.,20000.),figsize=(12,12),dp=100):
    from matplotlib.ticker import FormatStrFormatter,MultipleLocator
    # Get values from kwargs
    Tmin,Tmax = xlims
    P_b,P_t = ylims
    if ax is None:
        fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
    # set some constants
    T_zero = 273.15
    cp = 1005.
    cv = 718.
    kappa = (cp-cv)/cp
    P_top = 10000.
    P_bot = 100000.#P_b # see if this works, was 100000.
    plevs  = np.arange(P_b,P_t-1,-dp)
    ax.axis([Tmin,Tmax,P_b,P_t])
    ax.set_xlabel('Temperature ($^{\circ}\! C$)')
    xticks = np.arange(Tmin,Tmax+1,5)
    ax.set_xticks(xticks,['' if tick%10!=0 else str(tick) for tick in xticks])
    ax.set_ylabel('Pressure (Pa)')
    yticks = np.arange(P_bot,P_t-1,-10**4)#,-50e3)#,-10**4)
    ax.set_yscale('log')
    
    ax.yaxis.set_major_formatter(FormatStrFormatter('%1.0f'))
    ax.yaxis.set_minor_formatter(FormatStrFormatter('%1.0f'))
    
    # plot isotherms
    for temp in np.arange(-150,50,10):
        ax.plot(temp + skewnessTerm(plevs,P_bot), plevs, color = ('blue'), linestyle=('solid'), linewidth = .5)
    
    # plot isobars
    for n in yticks:
        ax.plot([Tmin,Tmax], [n,n], color = 'black', linewidth = .5)
    ax.plot([Tmin,Tmax],[85000,85000], color = 'black', linewidth = .5)   
    
    # plot dry adiabats
    for tk in T_zero+np.arange(-30,210,10):
        dry_adiabat = tk * (plevs/P_bot)**kappa - T_zero + skewnessTerm(plevs,P_bot)
        ax.plot(dry_adiabat, plevs, color = 'brown', linestyle='dashed', linewidth = .5)
     
    # plot moist adiabats  
    ps = [p for p in plevs if p<=P_bot]
    for temp in np.concatenate((np.arange(Tmin,10.1,5.),np.arange(12.5,Tmax+.1,2.5))):
        moist_adiabat = []
        for p in ps:
            temp -= dp*gamma_s(temp,p)
            moist_adiabat.append(temp  + skewnessTerm(p,P_bot))
        ax.plot(moist_adiabat, ps, color = 'green',linestyle = 'dashed', linewidth = .5)
        
    # plot mixing ratios
    for mixr in [0.1,0.2,0.5,1,2,3,4,6,8,12,16,24,32,48,64]:
        Tdew = dewpt(mixr*0.001,0.01*plevs)
        ax.plot(Tdew + skewnessTerm(plevs,P_bot),plevs, color = ('red'), linestyle=('dashed'), linewidth = .5)
    return ax

def plot_skew_T(sounding,T_surf=None,qv_surf=None,ax=None,options='lc'):
    '''
    # This script plots a Skew-T ln(P) diagram. 
    # 
    # usage: 
    #     plot_skew_T(mysounding)  OR   plot_skew_T(mysounding, T_surf=22, qv_surf=12) etc. 
    # 
    # input:  
    #     sounding  (dict) -  should contain the sounding data
    # 
    # optional input: 
    #     T_surf (float)   - the temperature (C) of a parcel at the surface level
    #     qv_surf (float)  - the specific humidity (g/kg) of a parcel at the surface level
    # 
    #     options (string)  - the characters indicate what should be plotted, by default 'l' (LCL) and 'c' (CAPE)
    '''
    P,T,qv,u,v = sounding['PRES'][1:],sounding['TEMP'][1:],sounding['MIXR'][1:],sounding['U'][1:],sounding['V'][1:]
    T_zero = 273.15
    P_top = 10000.
    P_bot = 100000.
    cp = 1005.
    cv = 718.
    kappa = (cp-cv)/cp
    g = 9.81
    Rs = cp-cv
    if ax is None:
        ax = plot_skewT_ax()
    if T_surf is None:
        T_surf = T[0]
    if qv_surf is None:
        qv_surf = qv[0]
    pnew = 100*P
    Td = dewpt(qv*0.001,P)
  
    Tmin,Tmax = ax.get_xlim()
    P_b,P_t = ax.get_ylim()
    # start reading a row later if the first row is empty
    sbi = 0
    for i in T:
        if np.isnan(i) == True:
            sbi += 1
    #################################################### plot parcel trajectories
    # surface pressure levels instead of pressure levels
    
    # calculate the dry trajectories for Temp and Td
    #mixedlayer_r = sum(rnew[:4])/len(rnew[:4])
    #mixedlayer_temp = sum(Tempnew[:4])/len(Tempnew[:4])
    #mixedlayer_pres = sum(Presnew[:4])/len(Presnew[:4])
    
    
    # use mixed layer values
    #dryTd = dewpt(mixedlayer_r,0.01*splevs)
    #dryT = (T_zero+mixedlayer_temp) * (splevs/mixedlayer_pres)**kappa - T_zero
    
    
    #+splevs = np.arange(pres,P_t-1,-dp)
    #use surface values
    #dryTd = dewpt(rv2m,0.01*splevs)
    
    # calulate trajectory
    dp = 100.
    splevs = np.arange(pnew[1],pnew[-1]-1,-dp)                  
    dryTd = dewpt(qv_surf*0.001,splevs*0.01)
    dryT = (T_zero+T_surf) * (splevs/pnew[0])**kappa - T_zero # was: pnew[sbi] 

    if 'l' in options: # calculate LCL     
        # calculate the index number of the LCL
        TminTd = abs(dryT-dryTd)
        lcli = np.nonzero(TminTd == TminTd.min())[0].squeeze()
        
        moistT = []
        temp = dryT[lcli]
        for ps in splevs[lcli:]:
            temp -= dp*gamma_s(temp,ps)
            moistT.append(temp)

        # calculate the trajectories arrays
        plotTd = dryTd[:lcli]
        plotp = splevs[:lcli]
        trajT = np.concatenate([dryT[:lcli],moistT])
    
        # plot the trajectories
        ax.plot(plotTd + skewnessTerm(plotp,P_bot),plotp, color = 'purple', linestyle='solid', linewidth = 1.5)
        ax.plot(trajT  + skewnessTerm(splevs,P_bot),splevs, color = 'purple', linestyle='solid', linewidth = 1.5)
        
        # plot LCL
        lcl = splevs[lcli]
        ax.plot([Tmin,Tmax],[lcl,lcl], color = 'purple', linestyle = 'solid', linewidth = 1.0)
        ax.text(Tmin+.5,lcl,'LCL',color='purple',ha='left',va='center',fontsize=14,\
                bbox=dict(edgecolor='black',facecolor='white', alpha=0.8))    
    
    ################################################ plot temperature and dewpoint temperature
        
        
    # plot the actual graph
    ax.plot(T + skewnessTerm(pnew,P_bot),pnew, color=('red'),linestyle=('solid'),linewidth= 1.5)
    ax.plot(Td + skewnessTerm(pnew,P_bot),pnew, color=('blue'),linestyle=('solid'),linewidth= 1.5)
    if u is not None and v is not None:
        ax.plot([40]*2,[P_b,P_t],color='black',linewidth=.5)
        ax.barbs([40]*len(pnew),pnew,1.94384449*u,1.94384449*v,length=8)  # convert from m/s to knots
    ax.scatter(T + skewnessTerm(pnew,P_bot),pnew,color='red',s=5)
    ax.scatter(Td + skewnessTerm(pnew,P_bot),pnew,color='blue',s=5)
    if 'c' in options:
        #calculate cape
        interpT = np.interp(splevs[::-1],pnew[1:][::-1],T[1:][::-1])[::-1]
        
        Tdiff = Rs/splevs[lcli:] * (trajT[lcli:]-interpT[lcli:])
        Tdiffzero = []
        presresp = []
        for tempele,presele in zip(Tdiff,splevs[lcli:]):
            if tempele > 0:
                Tdiffzero.append(tempele)
                presresp.append(presele)
        cape = sum(Tdiffzero)*dp
        
        ax.fill_betweenx(splevs[lcli:],trajT[lcli:] + skewnessTerm(splevs[lcli:],P_bot),interpT[lcli:]+ skewnessTerm(splevs[lcli:],P_bot),\
                         where=trajT[lcli:]>interpT[lcli:],color='red',alpha=.3)
        
        #show variables
        textstr = 'CAPE = %1.0f J/Kg'%cape
        
        
        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round',facecolor='white', alpha=0.8)
        
        # place a text box in upper left in axes coords
        ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=16,
                verticalalignment='top', bbox=props)
    return ax


def skewnessTerm(P,P_bot):
    skewness = 37.5
    return skewness * np.log(P_bot/P)

def dewpt(r,p):
    """Returns dewpoint temperature (Celcius) for given mixing ratio (kg/kg)
    and pressure (hectopascal)"""
    R = 287.04  # gas constant air
    Rv = 461.5  # gas constant vapor
    eps = R/Rv
    return 243.5/(17.67/(np.log((r*p/(r+eps))/6.112))-1)

def es(T):
    """Returns saturation vapor pressure (Pascal) at temperature T (Celsius)
    Formula 2.17 in Rogers&Yau"""
    return 611.2*np.exp(17.67*T/(T+243.5))

def gamma_s(T,p):
    """Calculates moist adiabatic lapse rate for T (Celsius) and p (Pa)
    Note: We calculate dT/dp, not dT/dz
    See formula 3.16 in Rogers&Yau for dT/dz, but this must be combined with 
    the dry adiabatic lapse rate (gamma = g/cp) and the
    inverse of the hydrostatic equation (dz/dp = -RT/pg)"""
    # constants used to calculate moist adiabatic lapse rate
    # See formula 3.16 in Rogers&Yau
    T_zero = 273.15
    L = 2.501e6 # latent heat of vaporization
    R = 287.04  # gas constant air
    Rv = 461.5  # gas constant vapor
    eps = R/Rv
    cp = 1005.
    cv = 718.
    kappa = (cp-cv)/cp
    g = 9.81
    Rs = cp-cv
    a = 2./7.
    b = eps*L*L/(R*cp)
    c = a*L/R
    esat = es(T)
    wsat = eps*esat/(p-esat) # Rogers&Yau 2.18
    numer = a*(T+T_zero) + c*wsat
    denom = p * (1 + b*wsat/((T+T_zero)**2))
    return numer/denom # Rogers&Yau 3.16
