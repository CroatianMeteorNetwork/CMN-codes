CMN-codes
=========

A small preview of codes I use for working with Croatian Meteor Network.

  * ## FF_bin_suite 
  
  Required for using [CMN_bin_viewer](http://cmn.rgn.hr/binviewer/binviewer.html) software: 
  It is a collection of functions and examples how to work with CAMS standard *.bin files (rading the format and building individual frames).
  It also contains optimized functions for image processing such as levels adjustment, dark frame subtraction, flat fielding, image stacking, etc.

 * ## HMM_radio2txt
  
  Converting WAV files to *.txt format
  Header of the output file tells you the amount of samples per second and the number of chunks it has been reduced to.
  Other lines are in the following format:
  <sample_no> <level>
  e.g.
  1 1422
  2 1899
  3 267
  4 964
  5 244
  6 -2223
  ...

  * ## antialiasing 
    
  A test project I used to introduce myself to image processing with python. It is a slow and non-optimized brute-force approach and uses loops. A very bad code indeed.
  I don't have any intention to improve it, as it was just a quick introductory exercise. Use at your own risk.
