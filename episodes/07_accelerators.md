---
title: "Performance of Accelerators"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions 

- What are accelerators? 
- How do they affect my jobs performance?
- How can I measure accelerator utilization?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to …

- Understand difference of performance measurements on accelerators (GPUs, FPGAs) to CPUs.
- Understand how batch systems and performance measurements tools treat accelerators.

::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## Intention: Jump onto accelerator with the example application

Narrative:

- The deadline is creeping up, only few ways to go!
- Hey, we have a GPU partition! Maybe this will help us speed up the process!


What we're doing here:

- What changes?
- New metrics
- Transfer to/from accelerator
- Different options/requirements to scheduler & performance measurement tools

:::::::::::::::::::::::::::::::::::::


## Introduction
Run the same example workload on GPU and compare.


:::::::::::::::::::::::::: instructor
## ToDo
Don't mention FPGAs too much, maybe just a node what accelerators could be, besides GPU.
Goal is to keep it simple and accessible, focus on what's common in most HPC systems these days
:::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## ToDo
Explain how to decide where to run something. CPU vs. small GPU vs. high-end GPUs.
Touches on transfer overhead etc.
:::::::::::::::::::::::::::::::::::::

<!-- EPISODE CONTENT HERE -->

## Summary

:::::::::::::::::::::::::: challenge
## Exercise:
::::::::::::::::::::::::::::::::::::

Leading question: Performance optimization is a deep topic and we are not done learning. How could I continue exploring the topic?

:::::::::::::::::::::::::::::::::::::: keypoints
- Tools to measure GPU/FPGA performance of a job
- Common symptoms of GPU/FPGA problems
::::::::::::::::::::::::::::::::::::::::::::::::
