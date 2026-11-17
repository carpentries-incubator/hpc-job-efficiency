---
site: sandpaper::sandpaper_site
---

:::::: callout
🚧 Under Construction 🚧

This course is still being constructed---please be patient.

::::::::::::::::::

Outlining the course

- Targeted audience (see learner profiles: New HPC users, Research Software Engineers with users on HPC systems, researchers in HPC.NRW)
- Estimated length and recommended formats (e.g. X full days, X * 2 half days, in-person/online, live-coding)
- Course intentions (focus on learners perspective!):
   - Speed up research (efficient computations, more per time, shorter iteration times, "less in the way")
   - Convey intuition about job-sizes. What is considered large, what small?
   - Improve batch utilization through matching application requirements to requested hardware (minimal resource requirements, maximum resource utilization)
   - Sharpen awareness for importance to avoid wasting time/energy on a shared system
   - Teach common concepts and terms of performance on a beginner level
   - First steps into performance optimizations (cluster-, node-, and application level)
- Course context for learners:
   - Working on HPC Systems (Batch system, shared file systems, software modules, ...)
   - Performance of scheduled batch jobs
   - Application performance is only addressed briefly (related to job efficiency), but in-depth is outside of the scope. Episode "Next Steps" should point towards deeper performance analyses, e.g. with tracers and profilers, and how to get started there

::: instructor

# Select and prepare a toolset!

This course requires certain software to be in place, so make sure to:

1. Update all Slurm job script examples with
   - The correct partitions
   - Correct module load commands (OpenMPI, GCC, etc.)
2. Select either GNU `time`, your clusters shell built-in `time`, or third party tools like `hyperfine`
3. Update `config.yaml` with the correct version of episode 05, i.e. ClusterCockpit ord LinaroForge perf reports. More alternatives are TBD.

:::
