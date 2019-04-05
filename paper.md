---
title: 'labjack-controller: '
tags:
  - Python
  - experimental
  - dynamics
  - galactic dynamics
  - milky way
authors:
  - name: Benjamin A. Montgomery
    orcid: 0000-0000-0000-0000
    affiliation: University of Southern Maine
  - name: Paul A. Nakroshis
    orcid: 0000-0000-0000-0000
    affiliation: University of Southern Maine
date: 5 April 2019
bibliography: paper.bib
---

# Summary

The ability to accurately collect and computationally process data from sensors
in real time is crucial to many scientific experiments. Common solutions are
tools provided by National Instruments or internally developed tools. This can
lead to cost-ineffective solutions often tied to proprietary analysis software
or languages; in the case of internally developed tools, the onus is placed
upon the developer to ensure these proprietary tools are stable, viable
solutions in the long term. To combat this, hardware has been developed by
multiple manufacturers to capture this market. These solutions tend to have
cost-effective, versatile hardware, but interfaces that are poorly designed or
immature.

``labjack-controller`` is a package which targets T-series DAQs from LabJack,
and is designed to provide a powerful thread-safe facade representation of
these devices. It focuses on providing functions that abstract and automate
data collection, error handling, and configuration proceedures that are
normally exceedingly nuanced or complex. Care was given to writing efficient
code for streaming data from and communicating to these devices, relying
heavily on C foreign functions, and interfacing directly with Labjack's
C interface.
