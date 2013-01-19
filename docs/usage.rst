================
Getting Started
================

This plugin contains the documentation and component definitions for the OpenMDAO Class was given at the 2013 National Renewable 
Energy Laboratory (NREL) Wind Energy Systems Engineering workshop. The class was given by Justin Gray and Chris Heath 
from the NASA Glenn Research Center. Justin and Chris are members of the OpenMDAO development effort, and built the 
content of this class to demonstrate the basic usage of OpenMDAO with the GUI with some simple wind turbine design 
problems. The class covers: 
* basic usage for creating basic components
* instantiating those components in the GUI to build simple models
* building optimizations around models, working with design of experiments
* recording data from your runs
* building more complex models


You'll need OpenMDAO Version 0.4.2 or later to work with this tutorial. 

Browser Based GUI
========================

The OpenMDAO GUI is written as a browser based application. That means that the entire GUI is written with HTML5 and Javascript. We call it a browser based application,and not a ``web app`` because unlike a web app the OpenMDAO GUI does not require an active internet connection and does not transmit any 
information across the network. Regardless, the GUI functions just like a web app in that you interact with it solely through a web-browser. Also, like many web-apps, the GUI automatically saves your model for you as you build it. There is never any need for you to manually save your 
work. 

Opening the GUI
==================

OpenMDAO ships with a web-browser-based Graphical User Interface. Our GUI is written in Javascript and HTML. 
Even though the GUI is rendered in a web browser, you don't need to be connected to the Internet to use it. OpenMDAO is delivered 
with the GUI built in. So once you've installed OpenMDAO, just open up a command window, 
`activate <http://openmdao.org/docs/getting-started/install.html>` your OpenMDAO environment, and then 
type: 

:: 

  openmdao gui

Two things should happen next. First, you should see a couple of lines output to the console that looks similar to the following: 

:: 
    
  Opening URL in browser: http://localhost:59499 (pid=74061)
  Opened in open
  <<<74061>>> OMG -- Serving on port 59499

The port number after ``http://localhost:`` and the process id after ``pid=`` will be different
every time you open the GUI, so don't worry if your numbers don't match the ones we show here. 

Second, the Chrome web-browser (You did install a recent version of Chrome, right?) will pop up with a page showing a list of 
all your OpenMDAO projects that the GUI knows about. If this is your first time using the GUI, even if you've been 
using OpenMDAO for a while now, there won't be any projects in the list yet. You have to create new GUI projects for any
existing models.

GUI Basics
=============================================================

Start by creating a new project in the OpenMDAO GUI. If you've never used the OpenMDAO GUI before, you'll be greeted by 
an empty projects page like this: 

.. _`empty-project-page`:

.. figure:: empty_project_page.png
   :align: center

   Initial projects page for the GUI

Start by creating a new project. We'll name it ``actuator_disk``. You don't have to specify any description or 
version information if you don't want to. Only the project name field is required. 

.. figure:: new_project_modal.png
    :align: center

    New project creation dialog

When you first open any new project, you'll see a mostly empty setup with an assembly already created for you. 
We always create a default assembly called ``top``, and all assemblies always start out with a RunOnce Driver instance
called "driver". The name ``driver`` is significant to assemblies. When you tell an assembly to run, it always looks for 
"driver" to start the process. 


.. figure:: init_project_view.png
    :align: center

    Initial OpenMDAO project view

With the GUI open, you're ready to start building a model. 









