---
title: 'labjack-controller: Fast Realtime Data Collection with Labjack T-Series DAQs in Python'
tags:
  - Python
  - experimental
  - daq
  - labjack
  - parallel
authors:
  - name: Benjamin A. Montgomery
	orcid: 0000-0002-1240-5385
	affiliation: University of Southern Maine
  - name: Paul A. Nakroshis
	orcid: 0000-0000-0000-0000
	affiliation: University of Southern Maine
date: 5 April 2019
bibliography: paper.bib
---

# Summary

The ability to accurately collect and computationally process data from sensors
in realtime is crucial to many scientific experiments. Common solutions are
tools provided by National Instruments or internally developed tools. This can
lead to cost-ineffective solutions often tied to proprietary analysis software
or languages; in the case of internally developed tools, the onus is placed
upon the developer to ensure these proprietary tools are stable, viable
solutions in the long term. To combat this, hardware has been developed by
multiple manufacturers to capture this market. These solutions tend to have
cost-effective, versatile hardware, but interfaces that are poorly designed or
immature [@Lawson]. Current offerings from Labjack [@Labjack] are one such
example; their hardware is used in major industrial applications, but the
interface is exceedingly nuanced and provides little error recovery.

`labjack-controller` is a Python package which targets T-series DAQs from
LabJack, and is designed to provide a powerful thread-safe facade
representation of these devices. It focuses on providing functions that
abstract and automate data collection, error handling, and configuration
procedures that are normally exceedingly nuanced or complex. Care was given
to writing efficient code for streaming data from and communicating to these
devices, relying heavily on C foreign functions, and interact directly
with Labjack's provided low-level C interface. All functions are thread-safe,
data associated with the facade can be shared between multiple processes with 
live updating.

`labjack-controller` is designed to be used by anyone who has at least an
introductory knowledge of Python and intends to involve a computer in the
process of reading sensor data, from data backup purposes to real-time 
reaction to sensor readings. It is currently used in upper-level undergraduate
physics laboratory courses and a research lab at the University of Southern Maine
for the purposes of reacting to realtime data, most notably with a torsion 
pendulum with dynamic electromagnetic damping.

In order to use this software, the user may choose to connect the LabJack with
an ethernet or USB cable (on the T7-Pro, one can use the wireless capability). 

# Acknowledgements

We acknowledge funding through the University of Southern Maine.


# References
