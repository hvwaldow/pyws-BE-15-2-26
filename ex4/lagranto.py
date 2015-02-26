#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import print_function
import scipy
import netCDF4
import datetime
import magic
import copy

'''
TODO :

-Make write_netcdf work when usedatetime=False


'''


class Tra(object):
    """
    Class to work with LAGRANTO output

    Read trajectories from a LAGRANTO file and return a structured numpy array

    filename : file containing lagranto trajectories
    return :   structured numpy array traj(ntra,ntime) with variables as tuple.

    Example:
        trajs = Tra(filename)
        trajs['lon'][0,:] : return the longitudes for the first trajectory.

    Author : Nicolas Piaget, ETH Zurich , 2014
             Sebastiaan Crezee, ETH Zurich , 2014
    """

    read_format = {
        'NetCDF Data Format data': 'netcdf',
        'ASCII text': 'ascii',
    }

    def __init__(self, filename, typefile=None, usedatetime=True):
        """
        Read a file based on its type.
        By default typefile is determined automatically,
        but it can also be specified explicitly
        as a string argument:'netcdf' or 'ascii'
        """
        if typefile is None:
            typefile = magic.from_file(filename)
            error = "Unkown fileformat. Known formats are {}".format(
                    ":".join(self.read_format.keys())
            )
            typefile = self.read_format[typefile]
        else:
            error = "Unkown fileformat. Known formats are ascii or netcdf"
        try:
            function = '_read_{}'.format(typefile)
            self._array = globals()[function](filename,
                                              usedatetime=usedatetime)
        except IOError:
            raise IOError(error)

    def __len__(self):
        return len(self._array)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._array, attr)

    def __getitem__(self, key):
        return self._array[key]

    def __setitem__(self, key, item):
        if type(key) is slice:
            self._array = item
        else:
            formats = self._array.dtype.descr + [(key, item.dtype.descr[0][1])]
            formats = [(form[0].encode('ascii', 'ignore'),
                       form[1]) for form in formats]

            newarr = scipy.zeros(self._array.shape, dtype=formats)
            for var in self.variables:
                newarr[var] = self._array[var]
            newarr[key] = item
            self._array = newarr

    def __repr__(self):
        string = " \
        {} trajectories with {} time steps. \n \
        Available fields: {}\n \
        total duration: {} minutes".format(
            self.ntra, self.ntime,
            "/".join(self.variables),
            self.duration
        )
        return string

    @property
    def ntra(self):
        if self.ndim < 2:
            print(" \
                Be careful with the dimensions, \
                you may want to change the shape: \n \
                either shape + (1,) or (1,)+shape \
                ")
            return None
        return self.shape[0]

    @property
    def ntime(self):
        if self.ndim < 2:
            print(" \
                Be careful with the dimensions,\
                you may want to change the shape: \n \
                either shape + (1,) or (1,)+shape \
                ")
            return None
        return self.shape[1]

    @property
    def variables(self):
        return list(self.dtype.names)

    @property
    def duration(self):
        """ time duration in minutes """
        end = self['time'][0, -1]
        end = end.astype(datetime.datetime)
        start = self['time'][0, 0]
        start = start.astype(datetime.datetime)
        delta = end - start
        return delta.total_seconds() / 60.

    @property
    def initial(self):
        """ give the initial time of the trajectories """
        starttime = self['time'][0, 0]
        return starttime

    def set_array(self, array):
        """ To change the trajectories array """
        self._array = array

    def concatenate(self, trajs):
        """ To concatenate trajectories together
            return Tra object
        """
        if type(trajs) is not tuple:
            trajs = (trajs,)
        trajstuple = tuple(tra._array for tra in trajs)
        trajstuple += (self._array,)
        newtrajs = copy.copy(self)
        test = scipy.concatenate(trajstuple)
        newtrajs._array = test
        return newtrajs

    def write(self, filename, fileformat='netcdf'):
        globals()['_write_{}'.format(fileformat)](self, filename)

# -----------------------------------------------------------------------------
# read a netcdf lsl file
# -----------------------------------------------------------------------------


def _read_netcdf(filename, usedatetime):
    """ Read a netcdf lsl file """

    # read the netcdf, the formats and the variables names

    ncfile = netCDF4.Dataset(filename)
    if usedatetime:
        formats = [var[1].dtype if var[0] != 'time' else 'datetime64[s]'
                   for var in list(ncfile.variables.items())]
    else:
        formats = [var[1].dtype for var in list(ncfile.variables.items())]

    variables = list(ncfile.variables.keys())

    # set the numbers of trajectories and time step
    try:
        ntra = len(ncfile.dimensions['dimx_lon'])
    except:
        try:
            ntra = len(ncfile.dimensions['id'])
        except:
            try:
                ntra = len(ncfile.dimensions['ntra'])
            except:
                raise Exception('Cannot read the number of trajectories,\
                                not one of dimx_lon, id or ntra')

    try:
        ntime = len(ncfile.dimensions['time'])
    except:
        ntime = len(ncfile.dimensions['ntim'])

    # change names of the coordinates if necessary

    nvariables = list(variables)

    if "longitude" in variables:
        nvariables[variables.index("longitude")] = "lon"

    if "latitude" in variables:
        nvariables[variables.index("latitude")] = "lat"

    # create a structured array using numpy

    array = scipy.zeros((ntra, ntime),
                        dtype={'names': nvariables, 'formats': formats})

    for variable in variables:
        if variable == 'BASEDATE':
            continue
        nvariable = variable
        if variable == 'longitude':
            nvariable = 'lon'
        if variable == 'latitude':
            nvariable = 'lat'
        if len(ncfile.variables[variable].shape) == 4:
            array[nvariable] = ncfile.variables[variable][:, 0, 0, :][:].T
        else:
            array[nvariable] = ncfile.variables[variable][:].T

    # read the starting date and duration

    try:
        date = [int(i) for i in ncfile.variables['BASEDATE'][0, 0, 0, :]]
        starttime = datetime.datetime(date[0], date[1],
                                      date[2], date[3], date[4])
    except:
        starttime = datetime.datetime(ncfile.ref_year,
                                      ncfile.ref_month,
                                      ncfile.ref_day,
                                      ncfile.ref_hour,
                                      ncfile.ref_min)

    # find characteristic of trajectories
    timestep = ncfile.variables['time'][1] - ncfile.variables['time'][0]
    period = ncfile.variables['time'][-1] - ncfile.variables['time'][0]

    # True if time = hh.mm
    cond1 = 0.00 < (ncfile.variables['time'][:] % 1).max() <= 0.60

    if cond1:
        timestep = scipy.floor(timestep) + ((timestep % 1) / .60)
        timestep = scipy.around(timestep, 6)
        period = scipy.floor(period) + ((period % 1) / .60)
        period = scipy.around(period, 6)

    # transform the times into datetime object
    # special treatment for online trajectories (time given in minutes)
    if usedatetime:
        try:
            time = scipy.array(
                [scipy.datetime64(starttime + datetime.timedelta(hours=t))
                 for t in scipy.arange(0, period + timestep, timestep)]
            )
        except AttributeError:
            time = scipy.array(
                [scipy.datetime64(starttime + datetime.timedelta(seconds=t))
                 for t in scipy.arange(0, period + timestep, timestep)]
            )
        time.shape = (1,) + time.shape
        time = time.repeat(array.shape[0], axis=0)
        array['time'] = time

    ncfile.close()
    return array


# ------------------------------------------------------------------------------
# read an ASCII lsl file
# -----------------------------------------------------------------------------

def _read_ascii(filename, usedatetime, nhead=5):
    """ Read a lsl file from ASCII """
    # open the file
    open_file = open(filename, 'r')

    # get the header
    file_lines = open_file.readlines()
    nvariables = file_lines[2].strip().split()
    head = file_lines[0].split()

    # read starting time new and old formats
    try:
        starttime = datetime.datetime.strptime(head[2], '%Y%m%d_%H%M')
    except ValueError:
        try:
            starttime = datetime.datetime.strptime(
                head[2] + '_' + head[3], '%Y%m%d_%H'
            )
        except:
            print("Warning: could not retrieve starttime from header,\
                  setting to default value ")
            starttime = datetime.datetime(1970, 1, 1)
    if usedatetime:
        dtypes = ['f8' if var != 'time' else datetime.datetime
                  for var in nvariables]
    else:
        dtypes = ['f8' for var in nvariables]

    # read the content as numpy array
    array = scipy.genfromtxt(filename,
                             dtype=dtypes,
                             names=nvariables,
                             skip_header=nhead,
                             missing_values=-999.99)

    # find characteristic of trajectories
    timestep = float(array[1][0]) - float(array[0][0])
    period = float(array[-1][0]) - float(array[0][0])

    # Convert minutes to decimal hours
    if max((array['time'].astype(float)) % 1) <= 0.60:
        timestep = scipy.floor(timestep) + ((timestep % 1) / .60)
        period = scipy.floor(period) + ((period % 1) / .60)

    # period/timestep gives strange offset (related to precision??)
    # so use scipy.around
    ntime = int(1 + scipy.around(period / timestep))
    ntra = int(array.size / ntime)

    # reshape traj file
    array = scipy.reshape(array, (ntra, ntime))

    if usedatetime:
        # change time into datetime object
        time = scipy.array(
            [scipy.datetime64(starttime + datetime.timedelta(hours=t))
             for t in scipy.arange(0, period + timestep, timestep)]
        )

        time.shape = (1,) + time.shape
        time = time.repeat(array.shape[0], axis=0)
        array['time'] = 0
        newdtypes = [descr if descr[0] != 'time' else ('time', 'datetime64[s]')
                     for descr in array.dtype.descr]
        array = array.astype(newdtypes)
        array['time'] = time

    return array

# ------------------------------------------------------------------------------
# write trajectories to a netcdf file
# ------------------------------------------------------------------------------


def _write_netcdf(Tra, filename):

    ncfile = netCDF4.Dataset(filename, 'w', format='NETCDF3_CLASSIC')
    ncfile.createDimension('ntra', Tra.ntra)
    ncfile.createDimension('ntim', Tra.ntime)
    ncfile.ref_year, ncfile.ref_month, ncfile.ref_day, ncfile.ref_hour,\
        ncfile.ref_min = Tra.initial.astype(datetime.datetime).timetuple()[0:5]

    vararray = ncfile.createVariable('time', 'f4', ('ntim', ))
    delta = Tra['time'][0, :] - Tra.initial
    time = [int(a.astype(datetime.datetime).total_seconds() / 3600) +
            (a.astype(datetime.datetime).total_seconds() -
             int(a.astype(datetime.datetime).total_seconds() / 3600) * 3600)
            / 60 * 0.01 for a in delta]
    vararray[:] = time

    # add variables
    for var in Tra.variables:
        if var == 'time':
            continue
        vararray = ncfile.createVariable(var, Tra[var].dtype, ('ntim', 'ntra'))
        vararray[:] = Tra[var].T

    ncfile.close()
