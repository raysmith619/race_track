# race_track
2D race track construction / operation game

This program is written entirely in Python 3 and uses tkinter for graphics.

For graphics we make extensive use of 2D homogeneous coordinate transformations with the help of the file src/homocoord.py:

File excerpt.:
   # This file is part of the PyNCulture project, which aims at providing tools to
   # easily generate complex neuronal cultures.  
   # Copyright (C) 2017 SENeC Initiative


Facilitate game player in desiging and operation of two dimentional race track with two dimensional vehicles.
This game is the author's attempt in the development of a layered design of objects.  The botom layer contains objects which can be drawn directly via canvas operations.  Currently lowest level object is a polygon with a set of points.  Each object, except the top, has a container object.  The object is expressed in terms of the container object.  Where appropriate the object's position, rotation, height, width are expressed as a fraction of the containers attributes.  It is hoped that with this generalization, objects can be easily developed.  The general object display process entails the obtaining the objects container tree, and from that, the series of coordinate transformation matices, generating a composite transformation matrix and applying this matrix against each of the object's points.  It is hoped that the efficiency of collapsing the transformations in to a single matrix multiplication per point will save time.

Recursive definition:
It is hoped that the definion scheme will facilitate the object design process.  Some thought has been given to the possibility of recursive object design (an object containing reference to a containing object).  Although no actual programming along these lines was done, one possiblility would be, as the container tree is traveled one could judge the resulting dimensions and prune the results if/when the results would be outside visible bounds.
