---
title: "How to identify a bottleneck?"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions 

- How can I find the bottlenecks in a given job?
- What are common workflows to evaluate performance?
- What are some common types of bottlenecks?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to …

- Choose between multiple workflows to evaluate job performance.
- Name typical performance issues.
- Determine if their job is affected by one of these issues.

::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## Intention: Uncover one or two issues in the application

Narrative:

- Okay, what's slowest with creating snowman pictures?
- Where does our system choke?


What we're doing here:

- What's a bottleneck?
- How can we identify a bottleneck?
- "Online" and "after the fact" workflows of performance measurements (trace, accumulated results, attached to the process (live), or after it ran)
- Point to additional resources of common performance/bottleneck issues, e.g. on hpc-wiki

Maybe something like this already occurred before in 4. Scaling Study, or 5. Performance Overview

:::::::::::::::::::::::::::::::::::::

## How to identify a bottleneck?

<!-- EPISODE CONTENT HERE -->


## Summary

:::::::::::::::::::::::::: challenge
## Exercise:
::::::::::::::::::::::::::::::::::::

Leading question: We were looking at a standard configuration with CPU, Memory, Disks, Network, so far. What about GPU applications, which are very common these days?

:::::::::::::::::::::::::::::::::::::: keypoints
- General advice on the workflow 
- Performance reports may provide an automated summary with recommendations
- Performance metrics can be categorized by the underlying hardware, e.g. CPU, memory, I/O, accelerators.
- Bottlenecks can appear by metrics being saturated at the physical limits of the hardware or indirectly by other metrics being far from what the physical limits are.
- Interpreting bottlenecks is closely related to what the application is supposed to do.
- Relative measurements (baseline vs. change)
   - system is quiescent, fixed CPU freq + affinity, warmups, ...
   - Reproducibility -> link to git course?
- Scanning results for smoking guns
- Any best practices etc.
::::::::::::::::::::::::::::::::::::::::::::::::
