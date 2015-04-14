<!-- <div> -->
<!-- <img source="C2SM/pyws-BE-15-2-26/slides/intro/pics_template/c2sm_3.png" alt="c2sm logo" /> -->
<!-- </div> -->

![c2sm logo](/slides/intro/pics_template/c2sm_3.png)

# Scientific Programming in Python for Atmospheric Sciences and Climatology

<p align='center'> Harald von Waldow &lt;hvwaldow@env.ethz.ch&gt; | Bas Crezee | Nicolas Piaget</p>

[**How to use it - Instructors**](#instructors)<br>
[**How to use it - Learners**](#learners)<br>
[Format](#format) | [Audience](#audience) | [Duration](#duration) | [Bonus Material](#bonus-material) | [Feedback](#feedback) | [License](#license)

<hr />

## Format

The lectures mostly consist of IPython Notebooks. There is an "Intro"
slide-deck and one related to Exercise 3 in the folder "slides".

## Audience

Python novices who should have programming experience in other
languages. A number of examples and problems are drawn from the field
of Atmospheric Dynamics and Climate Impact Research.

## Duration

An eight hour day. This is enough time to cover Exercises 1
through 4.

## Bonus Material

Exercise 5 is not really an exercise but rather a very explicit walk
through the solution of a real world problem that combines several
powerful packages. This Notebook uses `PIL`, `Cartopy`, `matplotlib`,
`CDO.py`, `requests`, `Pandas` to solve a GIS-like problem. This
Notebook could form the basis of a final exercise in an advanced
workshop that deals with the visualization of geocoded data.

Exercise 6 are some basic (and rather simple) Python coding
exercises. In previous workshops they got not so stellar marks in the
evaluation. They are left so that interested participants can use them on
their own.

## How to use it

### Instructors

In case you have a computer lab at your hands that fulfills some basic
[requirements](https://github.com/C2SM/ipython-workshop-setup#requirements),
we recommend that you have a look at the ready-made, robust, and well tested
setup procedure [here](https://github.com/C2SM/ipython-workshop-setup).

In case you have not, you want to set up the participant's computers
individually (or have them do the setup) as explained in
[the section below](#learners).

We found that the material provided by
[Software Carpentry](http://software-carpentry.org) is an extremely
useful resource, in particular when it comes to workshop organization
and teaching skills.

### Learners

#### 1. Download

**Either**

~~~~bash
git clone https://github.com/C2SM/pyws-BE-15-2-26.git <pyws-directory>
~~~~

in case you are familiar with the command line and have
[git](http://git-scm.com/downloads) installed.

**Otherwise** download the
[zip-archive](https://github.com/C2SM/pyws-BE-15-2-26/archive/master.zip)
and unpack. This will yield a directory `pyws-15-2-26-master`, that
contains everything. Feel free to rename that directory to anything
you want (\<pyws-directory\>) in the following.

#### 2. Installation of Python modules and start IPython Notebook

**These recommendations were changed (2015-04-13).**

Realizing the difficulties that might arise due to interactions of system -
Python and workshop - Python -- even if using a _virtualenvironment_,
**we now recommend for all OS (Windows, OS X, Linux) the _Anaconda_
Python distribution.** Next to a quick setup to work with the tutorial
material, this also provides you with a very comprehensive environment
of the latest Python packages, suited for almost all tasks. (h/t Chris
Barker).

##### Installation with __Anaconda__

1. Download _Anaconda_: http://continuum.io/downloads
    Use Python **2.7** (as opposed to **3.4**)
	
2. Open the "Anaconda Command Prompt" (Windows) or or just a
    terminal window (OS X, Linux).

3. Update conda and anaconda with the latest packages:
    ~~~bash
	conda update conda
	conmda update anaconda
	~~~
	
3. Install some additional packages:

    ~~~bash
	conda install basemap
	conda install netCDF4
	pip install urllib3
	pip install python-magic
	conda install shapely
	pip install pyshp
	pip install cartopy
	pip install cdo
	~~~

4. Launch the "Anaconda Ipython Notebook" (Windows), or simpy type

~~~bash
ipython notebook --pylab=inline
~~~

at the command prompt (OS X, Linux) and navigate to
the exercises.

**Have fun!**

##### Installation for _real programmers_(TM)<br />for UNIXy system such as Linux or OS X

execute the setup script:

~~~bash
cd <pyws-directory>
chmod u+x setup.sh
./setup.sh
~~~

This will create (download, compile, install) a "virtual environment",
that is a python-interpreter and all necessary library packages into
the directory `<pyws-directory>/venv`. It is a neat way to organize
Python projects and makes you independent of the system - Python
installation.  The virtual environment will take up about 350 MB. The
only requirement for this to work is that you already have any (well,
\>=2.6) version of Python installed system-wide that includes the
[`virtualenv`](https://virtualenv.pypa.io/en/latest/) package. Also
building the necessary modules requires your system to have the
build-tool-chain (compilers, etc.) installed. This should be no issue
for all stock Linux distributions.

Activate the virtual environment:

~~~
source venv/bin/activate
~~~

Start the notebook:

~~~bash
ipython notebook --pylab=inline
~~~

**Enjoy!**


## Feedback

I would be very happy to hear from you (mail to <hvwaldow@env.ethz.ch>)
in case you give this course a chance, be it as an instructor (who
maybe mixes parts of this workshop with her own material), as a
learner who attended one of our workshops, or as independent learner
who uses this material for self-study.

Particularly welcome are problem reports, errors, criticism.

# License
<a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc/4.0/88x31.png" /></a><br />The material in this repository is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc/4.0/">Creative Commons Attribution-NonCommercial 4.0 International License</a>.
