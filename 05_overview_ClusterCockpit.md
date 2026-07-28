---
title: "Performance Overview"
teaching: 45
exercises: 35
---


::: questions 
- Is job wall-time the only way to study job performance?
- What are commonly used metrics to describe job performance?
- What are common workflows to evaluate performance?
- How can I find the bottlenecks in a given job?
:::

::: objectives
After completing this episode, participants should be able to …

- Create a comprehensive performance overview through dedicated tools.
- Explain the difference between sampling and tracing.
- Measure utilization and the impact of underlying hardware components.
- Determine if their job is affected by a typical performance bottleneck pattern.
:::


::: instructor
## Intention: Introduce third party tools for performance reports

Narrative:

- Scaling study, scheduler tools, project proposal is written and handed in
- Maybe I can squeeze out more from my current system by trying to understand better how it behaves
- Another colleague told us about performance measurement tools
- We are learning more about our application
- Aha, there IS room to optimize! Compile with vectorization


What we're doing here:

- Get a complete picture
- Introduce additional metrics / definitions, and popular representations of data, e.g. Roofline
- Relate to hardware on the same level of detail
:::

::: instructor
## TODO: Discuss requirements in more detail?
Dependent on the cluster config, some of these may have to be addressed?

```
cap_perfmon,cap_sys_ptrace,cap_syslog=ep
kernel.perf_event_paranoid
```
:::

::: instructor
## Prepare a reservation!

We'll have to run a couple of 20 minutes long `--exclusive` jobs here, so make sure enough resources are available for the exercise!
:::

Wall-time measurements with `time` do not tell us why exactly an application is slower than expected.
To learn more about the *why*, we have to measure our applications behavior in more detail and capture the utilization of underlying hardware.

::: instructor
## Know your tool!

We provide alternatives for this episode. Make sure to select the right one in your `config.yaml`.

*ClusterCockpit* is a job monitoring systems that can be configured to capture many performance metrics. It is easy to use, but has to be deployed by the cluster administration team.

Be aware of site-specific setups, e.g. limiting access to performance counters, offering non-standard Slurm options during `sbatch` submission, and how licenses are handled.
Not all metrics discussed in this episode may be configured on every cluster — the set of metrics collected and displayed is chosen by the local administration team, so some panels or plots covered here might simply be unavailable, or show different metrics, on your system.
:::

::: callout
## The performance measurement tool

[*ClusterCockpit*](https://clustercockpit.org/): A job monitoring service available on many clusters in NRW. Sampled measurements of the application are stored and visualized in a timeline for each job. It needs to be centrally provided by your HPC administration team and may not be available to you!

This tool may require access to performance counters, sometimes granted by requesting `--exclusive`, but it really depends on the system.
If something covered in this episode isn't available or looks different on your cluster, check your cluster documentation or ask your HPC support staff.
:::

Let us set up our performance measurement tool by running an example job with 8 cores.
To give the job enough work to be worth measuring, let's go with $2263 \times 2263$ pixels and `-spp=512`, we repeat this experiment twice back to back.

A single run finishes quickly and would give ClusterCockpit only a handful of samples to plot, making the timelines look sparse and hard to read.
Running it twice stretches the job out to a longer time, giving the sampling-based collectors enough time to gather a richer set of data points,  which makes for much clearer plots when we look at the metrics.
Additionally, we limit the execution time to 20 minutes to not wait too long, before getting the results.
It does not hurt us, if the job gets cut off by the Slurm `TIMEOUT`, since the measurements will still represent the applications behavior up to that point.

Submit a job that runs for at least $5$ minutes, so it is picked up by cluster cockpit.
The job could look like this:

```bash
#!/usr/bin/bash
#SBATCH --time=00:20:00
#SBATCH --partition=intelsr_devel
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --exclusive

module purge
module load GCC/13.2.0 OpenMPI/4.1.6-GCC-13.2.0 CMake/3.27.6-GCCcore-13.2.0 Boost/1.83.0-GCC-13.2.0 libpng/1.6.40-GCCcore-13.2.0

for i in {1..3}; do
    mpirun -- ./build/raytracer -width=2263 -height=2263 -spp=512 -threads=1 -png "img_${SLURM_JOB_ID}_$(date +%Y-%m-%d_%H%M%S).png"
done
```

We will call this job 1.
Note the use of `--exclusive` here, which books a whole node for the job.
This is important to make sure the performance measurements are not disturbed by concurrent jobs.
Additionally, ClusteCockpit collects some metrics only on a per-node basis, so concurrent jobs would make these measurements less usable

:::: challenge
## Exercise: Run a second job with `raytracer_float4`

Submit a second job using the `raytracer_float4` executable instead of `raytracer` — keep the resolution, `-spp`, core count, repeat count, and `--exclusive` request all the same as the original job.

We will call this job 2.
::::
::: solution

There are other binaries next to the `raytracer` example, called `raytracer_float4`, `_float8`, `_float16`.
We can start one of those in our job script instead:

```bash
#!/usr/bin/bash
#SBATCH --time=00:20:00
#SBATCH --partition=intelsr_devel
#SBATCH --ntasks=4
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --exclusive

module purge
module load GCC/13.2.0 OpenMPI/4.1.6-GCC-13.2.0 CMake/3.27.6-GCCcore-13.2.0 Boost/1.83.0-GCC-13.2.0 libpng/1.6.40-GCCcore-13.2.0

for i in {1..3}; do
    mpirun -- ./build/raytracer_float4 -width=2263 -height=2263 -spp=512 -threads=1 -png "$(date +%Y-%m-%d_%H%M%S).png"
done
```
:::

While the test jobs are running, let's look into the relationship between computer hardware architecture and performance.



## Hardware Architecture & Counters
Broadly categorized, a jobs performance is mostly dependent on

- **CPU utilization**, e.g. how quickly instructions can be send to the processor, how quickly and how much data can be read from memory, and the raw calculation capabilities of the CPU.
- **Memory utilization** may vary in terms of how much data is stored in memory, how often data in memory is written or read, and how quickly the data can be read and written to.
- **Disk input and output** affects jobs that work with amounts of data that exceed available memory capacities.
- **Network input and output** affects applications that rely on remote data, e.g. MPI applications that regularly share results between processes on multiple worker nodes.


![The underlying hardware frames any performance analysis.
Calculations are performed in multiple cores, potentially multiple threads per core, and even in vectorized instructions where a single operation is applied to multiple sets of data in a single instruction.
Data moves through the data hierarchy to CPU cores, where each level "closer" to the CPU has a smaller storage capacity, but larger bandwidth and smaller latencies, improving access performance.](fig/JobEfficiency.drawio.png){alt='Diagram to visualize the data hierarchy of CPU architectures. Network, local disks, memory, and CPU caches have decreasing amounts of storage capacity, but increasing bandwidths and shorter latencies. Calculations occur in CPUs, possibly in multiple CPU cores, which may have multiple threads each, and even apply vectorized instructions.'}

::: discussion
# Want to share an example?

Every job is limited by a contention point in the hardware.
Resolving one issue, e.g. too slow reading of data from disk, just shifts the contention point to a different location, e.g. waiting for calculations to finish in the CPU cores.
The absolute performance of the application is improved, but it will be always "slowed down" somewhere.

Did you experience a situation, where an application was clearly slowed down in some way?

What performance bottleneck scenarios can you imagine in the given hardware architecture sketch?
:::


### Measurement Workflows
To learn how applications utilize the computers hardware, we employ third party tools that read usage metrics from *performance counters*, often implemented either in the operating system kernels (software) or in hardware.

Dedicated performance measurement tools often employ similar methods and rely on the same sources of information, but they my focus on different issues and use different data processing and visualization methods.

In general there are two approaches to performance measurements:

1. **Sampling**: Read out performance counters and the application state at regular intervals during execution
1. **Tracing**: Record every event and operation that occurs

*Tracing* is exact and allows for a very detailed analysis.
On the other hand, it results in very large amounts of measurement data that even affects the applications performance during data collection.
It may be impractical in some situations.

*Sampling* on the other hand is less exact and results in a statistical description of the applications behavior.
Sampling has a smaller *measurement overhead*, but may suffer from, for example, slight mis-attributions of measurements to wrong sections of the code and fluctuating results between repeated measurements.

Measurement results are either stored and analysed in a *timeline*, or aggregated into a final measurement, often called a *profile*.

## General Report
Going back to our Cluster Cockpit results, log in to the ClusterCockpit web interface of your HPC system, as explained in your cluster documentation. Go to `My Jobs` and click on the job 1 with the same Slurm job id, once it is available

![ClusterCockpits main menu. Select "My Jobs" to see a list of the jobs associated to your account.](fig/cc/cc_bar.png){alt='"My Jobs" tab in the ClusterCockpit web UI'}



As a first step, to go beyond a wall-time analysis, we employ the measurement tool to produce a general overview of our applications behavior.
Here, we typically try to answer questions like:

- Are available CPU, memory, disk, and network capabilities utilized well?
- Dose the jobs performance depend on a particular hardware component?
- Is there an obvious contention point that could be eliminated?

### First Overview

The job view of a particular job in ClusterCockpit begins with three summary panels for the job.

![](fig/cc-new/job-metrics.png){alt='ClusterCockpit Job Info panel'}

The *Job Info* panel summarizes Slurm metadata about the job, e.g. job ID, accounts, start time, duration, etc.

![](fig/cc-new/footprint.png){alt='Cluster Cockpit Footprint panel summarizing central job characteristics'}

The *Footprint* panel summarizes a preconfigured set of performance characteristics for the job.
It categorizes values in a traffic-light system, so yellow and red indicators motivates further investigation.
The exact list and type of metrics depends on the ClusterCockpit configuration, which is prepared by the administrator of the service.

Here, all four values are not in acceptable range. We see why:

- `cpu_load (avg)` is shown in red. Since we requested the node with `--exclusive`, we were given all $96$ cores of the node, but our job only uses $8$ of them. The footprint compares load against the full $96$ cores that are requested by us, so it correctly flags that most of the requested resources are sitting idle. This is underutilization of requested resources.
- `flops_any (avg)` is Floating Point Operations per second. In this case, it is calculated as $22.38 GF/s$, which is far below what the node can theoretically achieve. It can point to anything from not utilizing the hardware features to simply not needing many floating point operations at all.
- `mem_used (avg)` shows the memory utilization of the job. This, together with the bandwidth metric below, is exactly why we requested an exclusive node in the first place: memory- and energy-related hardware counters are not available at a per-core granularity. They are measured at socket level or node level rather than per core, so running exclusively is what keeps them meaningful for our job alone.
- `mem_bw (avg)` is the memory bandwidth, i.e. how much data is transferred to and from memory per second.

::::::::: callout

### Granularity of Metrics

Not every metric ClusterCockpit shows describes your job. Some describe the whole CPU socket, or even the whole node, regardless of how many cores your job actually occupies. The underlying collectors read hardware performance counters that are simply wired up at a particular level of the machine, and they have no notion of which Slurm job is currently running. This is true regardless of which monitoring tool you use, but it is essential to understand for reading ClusterCockpit correctly.

Metrics come in three granularities:

- **Core-level**: measured separately for each individual CPU core, e.g. `cpu_user`, `ipc`, `flops_any`. These are meaningful for your job even if other jobs share the same node, since each core is attributed to exactly one job.
- **Socket-level**: measured once for an entire CPU socket (which may host several cores of several different jobs), e.g. `mem_bw` and the package power reading behind the Energy panel (`pkg_pwr`). If another job shares your socket, its memory traffic or power draw is mixed into your measurement.
- **Node-level**: measured once for the whole compute node, e.g. `cpu_load`, `mem_used` and network or filesystem metrics. These are effected by every job on the node, not just yours.

Each metric plot in ClusterCockpit has a small drop-down menu as shown in image below, typically labelled core, socket, or node. This label tells you directly at which granularity that particular chart was measured — a core selection means one line per core of your job, while socket or node means the value is shared with (and possibly polluted by) other jobs. If the drop-down only offers socket or node, treat the value with more caution unless you know the node was exclusively yours

![](fig/cc-new/dropdown-menu.png){alt='Drop down menu'}

This is precisely why we requested `--exclusive` when submitting our job earlier in this episode: on a node reserved exclusively for our job, socket- and node-level metrics describe our job alone, since there is nothing else running to mix into the measurement. If you cannot use `--exclusive`, for example because your allocation only ever needs a fraction of a node, keep an eye on which granularity a given metric is measured at, and treat socket- or node-level values as an upper bound that may include other jobs' activity rather than a precise reading of your own.
:::::::::


![](fig/cc/job_select_metrics.png){alt='Select Metrics button in the ClusterCockpit job view'}

More detailed plots for each individual metric are available and can be configured through the *Select Metrics* button.

In general, the footprint panel gives the most information on what issues our job may have and where to start the investigation. In our case:

- We can utilize all $96$ cores instead of just $8$ to make use of the full exclusive allocation.
- We can try to improve either `flops_any` or `mem_bw`. To know which one actually makes sense to target, we need to look at the next panel, the *Roofline plot*.

### How to read a Roofline Plot

Before looking at our job's result, here's what to expect on Roofline plot and how to understand the plot. Here is the example Roofline Plot:

![](fig/roofline-example.png){alt='Example Roofline plot with labels'}

In jobs performing floating point operations on data read from memory, i.e. any numeric operation, which are very common in HPC, a Roofline plot is a common visualization of the jobs performance.

- The x-axis is operational intensity: how many floating point operations are performed per byte loaded from memory. The y-axis is achieved performance: floating point operations per second.
- A diagonal line marks the maximum performance possible. $$P_{peak} = \min(\text{Memory Bandwidth} \times \text{Operational Intensity},\ \text{Flop/s}_{peak})$$
- A job with low intensity i.e. high memory transfers is pinned close to diagonal line: memory is the bottleneck, no matter how fast the CPU could otherwise compute.
- The two horizontal lines mark the maximum performance possible if CPU computation itself is the limit: lower line for scalar operations, a higher one once vectorized instructions are used.
- Where the diagonal and horizontal lines meet is the knee. Left of the knee = memory bound (data movement is the bottleneck). Right of the knee = compute bound (calculation capability is the bottleneck).
- The colored dots show measurements taken at different points in time during the job's run, following a blue-to-red gradient: blue marks the start of the application, red marks the end. Their position relative to the rooflines shows how close each phase of execution came to the physical performance limits, and how that changed over the runtime.

:::::: discussion

Below is the Roofline plot for our application.
![](fig/cc-new/roofline.png){alt='Cluster Cockpit Roofline plot of a job'}

Take a moment to look at where our raytracer's dot(s) land on the plot.

- Is the job **compute bound or memory bound**? Which side of the knee do the measurements fall on?
- Do the dots sit close to the scalar roofline, or closer to the vectorized roofline? What does that tell you about whether the application is actually using vectorized instructions?
- Given where the job sits, which metric is more interesting for our next investigation — `flops_any`, or `mem_bw`? Which one, if improved, would actually move the dot closer to a roofline?
- Does the dot's position stay roughly constant over the blue-to-red timeline, or does it drift? What might cause a job to move further from (or closer to) the roofline as it runs?

::::::

### CPU Metrics

CPU performance can be categorized in

1. *Front-end* utilization: preparation and scheduling of instructions of program code provided through the cache hierarchy
2. *Computation*: Arithmetic and logical operations with various data types, including the utilization of vectorized instructions, etc.
3. *Back-end* utilization: loading and storing of data in the cache hierarchy

The front- and backend hardware of a physical CPU core is often duplicated to implement *simultaneous multithreading* (SMT, also called hyperthreading).
Here, the arithmetic logical unit receives data and instructions from two independent threads to achieve a sufficient amount, which is a common limiting factor in everyday calculations.
On HPC systems, the benefit of SMT is very much application-dependent.
It is often disabled on HPC systems, since code is optimized to maximize computational intensity.

ClusterCockpit captures many dedicated CPU metrics and provides a timeline visualization for each.

![](fig/cc-new/cpu-user.png){alt='ClusterCockpit cpu_user metric'}

`cpu_user` shows, per core, the share of CPU time spent executing our application's own instructions, as opposed to time spent in kernel/system activity or sitting idle.
A high `cpu_user` near $1$ is a good sign: the core is busy, and busy doing *our* work rather than system overhead.
A core sitting noticeably below $1$ is worth a closer look. Some of its time is going to something other than our application's own instructions, whether that's kernel activity, waiting, or other overhead.
A `cpu_user` of $0$ means the core was idle for that interval and not running our application at all.

![](fig/cc-new/flops-any.png){alt='ClusterCockpit flops_any metric'}

`flops_any` captures any floating point operation on Intel CPUs, at core-level granularity, with single- and double-precision operations accumulated into the same value.
Recall from the Footprint panel that our job's `flops_any (avg)` sat at only $22.38$ GF/s, while the node's theoretical peak is $8532$ GF/s.

That gap looks enormous, but it isn't a fair comparison yet: the $8532$ GF/s peak is for all $96$ cores of the exclusive node, while our job only ever uses $8$ of them. Scaled down to $8$ cores, the theoretical peak is roughly $711$ GF/s, so $22.38$ GF/s is still well below what our $8$ cores could theoretically achieve, but nowhere near the dramatic 96-core gap the raw numbers first suggest.
This isn't a contradiction of the Roofline plot classifying the job as compute bound either way: compute bound only means the CPU's calculation capability is the limiting factor relative to how little data is moved, not that the job is issuing many *floating point* operations specifically.

:::: challenge
## Exercise: Compare `flops_any` between job 1 and job 2

We now have two jobs to compare: our job1 (`raytracer`) and a job2 run with the `raytracer_float4` executable.

Look at the `flops_any` metric for both jobs. What's different between them, and why?

::: solution

![](fig/cc-new/vec-flops-any.png){alt='ClusterCockpit flops_any metric for job2'}

In our measurements, `flops_any (avg)` per core is close to $3$ GF/s for job 1, and close to $6$ GF/s for job 2, roughly a $2\times$ increase.

`raytracer_float4` uses SIMD: `float4` corresponds to SSE2 vectorized instructions, where a single instruction operates on $4$ float operands at once, instead of one operand at a time as in the original scalar `raytracer`.

`flops_any` counts floating point operations regardless of whether they were issued as scalar or vectorized instructions, each vectorized instruction in job 2 is counted as $4$ floating point operations rather than $1$. As a result, `flops_any (avg)` for job 2 is noticeably higher than for job 1. For the same amount of *work* done, the vectorized version issues far fewer instructions to do it, and each one accomplishes $4\times$ as much.

:::::: instructor
## Demonstrating the Job 1 vs. Job 2 comparison

Open Job 1 and Job 2 side by side in two browser tabs, and navigate both to the Roofline plot panel, to demonstrate the comparison live rather than just describing it.

Hovering the cursor over a dot draws guide lines out to the x- and y-axes, letting you read off its operational intensity and achieved performance directly from the axes rather than judging position by eye alone. Hover over a dot in Job 1's plot, note where its guide lines land, then do the same for a dot at a similar point in the run in Job 2. Comparing the two readings this way gives learners a much clearer feel for exactly how much higher and how much further right Job 2's dots sit compared to Job 1's, rather than relying on "it looks a bit higher."
:::::: 

This is also a good moment to connect back to the Roofline plot: job 2's dots sit slightly higher on the plot than job 1's, and also shift further right along the x-axis — since computing more FLOPs per byte loaded raises the operational intensity too. They don't touch the upper, vectorized roofline yet — that would become more visible if we used the full node instead of just $8$ of its $96$ cores.

:::
::::

Our raytracer performs plenty of integer, branching, and memory-addressing work per byte loaded, which does not count towards `flops_any`. This is why a low `flops_any` is not necessarily a red flag here. 
On top of that, our original raytracer is not vectorized. It issues one scalar floating point operation at a time rather than operating on multiple values per instruction, which further caps how high `flops_any` can climb regardless of how well the rest of the code performs.

### Memory Metrics

Memory utilization is characterized in terms of used capacity, bandwidth and access latencies.


![](fig/cc-new/mem-used.png){alt='ClusterCockpit mem_used metric'}

`mem_used` sits at approximately $5$ GB for our job, shown as an almost flat, straight line across the runtime, which is a good sign. A flat line means memory consumption is stable once the application has allocated what it needs.
A slanted, steadily increasing line instead would be a warning sign of a **memory leak**: memory that is allocated but never freed, growing continuously over the job's runtime instead of leveling off.


![](fig/cc-new/mem-bw.png){alt='ClusterCockpit mem_bw metric'}

`mem_bw` is a **socket-level** metric. It measures how much memory is transferred to and from a given CPU socket per second, not per individual core.
Since our node has multiple sockets, you'll typically see a different `mem_bw` value reported for each socket. This difference depends entirely on which cores on each socket are actually active and running part of the application: a socket with more of our job's cores running on it will show higher memory traffic than a socket with fewer (or none) of them active.


### Energy

![](fig/cc-new/energy.png){alt=''}

Depending on the ClusterCockpit configuration, an energy demand is displayed below the job info panels.
This measurement is highly dependent on hardware configurations of your HPC systems, so the estimates may vary.
They are often based on CPU package power measurements, which are unlikely to cover the whole energy demand of the node, e.g. omitting disks, fans, etc.
In other cases, the energy may be estimated from power supply measurements and scaled to CPU activity to get a more accurate estimate.

These estimates often still not include network, parallel filesystem components and cooling of the clusters.
Nevertheless, the estimate is a great tool to identify the scale of the jobs energy demand.


### Miscellaneous
Typically, many more measurements and perspectives on the data are available for each tool.

![](fig/cc-new/stats.png){alt=''}

ClusterCockpit provides a detailed statistics table covering all measurements involved with a job. Alongside this table, you can also see your job script and Slurm info, which tells you how much of each resource was actually allocated to your job. 
The statistics table itself shows the max, min, and avg values for whichever metrics have been configured for your ClusterCockpit deployment.


## How to identify a bottleneck?

:::::::::::::::::::::::::: instructor
## Intention: Uncover one or two issues in the application

What we're doing here:

- Where does our system choke?
- What's a bottleneck?
- How can we identify a bottleneck?
- "Online" and "after the fact" workflows of performance measurements (trace, accumulated results, attached to the process (live), or after it ran)
- Point to additional resources of common performance/bottleneck issues, e.g. on hpc-wiki

Maybe something like this already occurred before in 4. Scaling Study, or 5. Performance Overview

Summary could be:
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

:::::::::::::::::::::::::::::::::::::

:::: challenge
## Exercise: Match application behavior to hardware

Which parts of the computer hardware may become a point of contention for these application patterns:

1. Calculating matrix multiplications
2. Reading data from processes on other computers
3. Calling many different functions from many equally likely if/else branches
4. Writing very large files (TB)
5. Comparing strings for matches
6. Constructing a large simulation model
7. Reading thousands of small files for each iteration

Maybe not the best questions, also missing something for accelerators.

::: solution
1. CPU (FLOPS), maybe the cache hierarchy if matrix elements do not align well to cache sizes
2. I/O (network)
3. CPU (Front-End), difficult to prepare instructions in time
4. I/O (disk), bandwidth limited
5. CPU (Back-End), getting strings through the caches
6. Memory (capacity)
7. I/O (disk)
:::
::::


## Summary
Dedicated performance measurement tools are helpful to create reports of the general job behavior.
These tools either trace every event, or sample the application and hardware state at regular intervals.
Many tools are available, but some may have to be set up by the HPC system administrators, or rely on valid licenses.

The relationship between a job and the execution on physical hardware can become a very deep topic.
One of these topics is the correct mapping of job processes to the requested number of CPU cores, addressed in the next episode.

::: keypoints
- Performance tools measure data as regular samples or by tracing every event
- The data is either processed and visualized in a timeline or aggregated in a final profile
- Job performance relates closely to contention points in physical hardware
  - CPU utilization (front-end, ALU, back-end), multithreading, vectorization
  - Memory utilization (capacity, bandwidth, latency)
  - Disk I/O
  - Network I/O

:::
