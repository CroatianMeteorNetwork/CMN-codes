FireballFitter
=========

FireballFitter software is used during fireball analysis to approximate raw fireball data (time vs. flight path, time vs. height) with an exponential curve.
Fireball velocity is derived from the flight path and stored to a file and calculated data points are shown on a graph.

Input file format (input.txt):

Station Time Flight_path Height Optional_uncertanty

e.g.

VIB 004.000 066.384 28.820  185.27182

VIB 004.020 066.555 28.662  185.27182

VIB 004.040 066.728 28.502  185.27182

APO 000.181 003.283 86.549   64.24059

APO 000.341 006.137 83.936   64.24059

APO 000.381 006.906 83.229   64.24059

...


The software has an option to aproximate the flight path with a 6-parameter exponential curve: 

`y = a + b*x + c* exp(d*x) + e* exp(f*x)`

This has shown to be a major improvement from the standard 4-parameter exponential curve:

`y = a + b*x + c* exp(d*x)`

especially during the final moments of the fireball's flight. But the 6-parameter curve's velocity often exhibits a tendency to rise during the pre-decelaration phase, which is certainly not the case in the real world scenario. Thus, the part until the inflection point is approximated with the 4-parameter curve and the part after with the 6-parameter curve. This gives a better velocity approximation.
This option can be turned off in the code by toggling the "extended_ending" variable to False.