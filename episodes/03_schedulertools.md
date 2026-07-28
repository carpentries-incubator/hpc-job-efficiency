---
title: "Scheduler Tools"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions

- What can the scheduler tell about job performance?
- What's the meaning of collected metrics?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to:

- Explain basic performance metrics.
- Use tools provided by the scheduler to collect basic performance metrics of their jobs.

::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## Intention: Introduce more basic performance metrics

Narrative:

- Okay, so first couple of jobs ran, but were they "quick enough"?
- How many renders could I generate per minute/hour/day according to the current utilization
- Our cluster uses certain hardware, maybe we didn't use it as much as we could have?
- But I couldn't see all metrics (may be cluster dependent) (Energy, Disk I/O, Network I/O?)


What we're doing here:

- What `seff` and `sacct` have to offer
- Introduce simple relation to hardware, what does RSS, CPU, Disk read/write and their utilization mean?
- Point out what's missing from a complete picture

Note:

- `seff` is an optional SLURM tool. It does not come standard with every
  SLURM installation. Therefore, make sure beforehand that this tool is
  available for the students.

:::::::::::::::::::::::::::::::::::::

In the previous episode, we learned how to choose appropriate resources for our jobs and why
requesting them efficiently is important. Once a job has run on an HPC system, an important 
question remains: Did it use the allocated resources efficiently? The scheduler provides tools
that let us inspect completed jobs and answer that question.

## What is a Scheduler?

HPC systems are shared by many users. Every user wants to execute jobs, but
CPUs, GPUs, memory, and compute nodes are limited resources. A **scheduler** is
responsible for deciding when jobs run, where they run, and which resources they
receive. It also monitors running jobs, records accounting information about their
execution, and releases resources after they finish. This accounting information
can later be queried by the job owner to understand the job's performance and
resource utilization.

### Why is a scheduler required?

Imagine fifty researchers all submit jobs to the same HPC cluster at the same time. Some jobs
require only a few CPU cores for a few minutes, while other jobs request hundreds of cores for
several hours. Since the available hardware is limited, not every job can start immediately.
Without a scheduler, users would have to compete for resources manually, leading to conflicts,
idle hardware, and unfair resource allocation.

The scheduler coordinates all submitted jobs so that shared HPC resources are allocated
fairly and efficiently.

### What tools does the scheduler provide?

| Purpose | Example tools |
| ------- | ------------- |
| Submit batch jobs | `sbatch` |
| Run interactive or parallel jobs | `srun`, `salloc` |
| Monitor queued and running jobs | `squeue`, `sstat` |
| View cluster information (nodes and partitions) | `sinfo` |
| Cancel jobs | `scancel` |
| Inspect completed jobs | `sacct`, `seff` |
| ... | ... |

Schedulers provide many tools for submitting, monitoring, and managing jobs. In this episode,
we focus only on the tools for analyzing completed jobs.

These tools use the scheduler's accounting information to help us answer questions such as:

- How long did the job actually run?
- Did I request more time or resources than necessary?
- Did my job use the allocated CPU resources efficiently?
- Did I request enough memory?

Throughout this episode, we will learn how to answer these questions using `sacct` and `seff`.

### Submitting a job: `sbatch`

We'll use `sbatch` once more to submit a job that we can later analyze. It takes
a job script as an argument. The job script contains the resource requests, such
as the amount of time needed for the calculation, the number of nodes, the number
of tasks per node, and so on. It also contains the commands to execute the calculations.

Using your favorite editor, create the job script `render_snowman.sbatch`
with the contents below.

```bash
#!/usr/bin/bash
#SBATCH --job-name=render-snowman
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4

# Only one example, consult your cluster documentation or ask the instructor or your HPC support
module load 2025 GCC/13.2.0 OpenMPI/4.1.6 Boost/1.83.0 CMake/3.27.6 libpng/1.6.40 buildenv/default

mpirun -np 4 ./raytracer -width=800 -height=800 -spp=128 -threads=1 -png=snowman.png
```

Submit the job using `sbatch`. While the job is running, we can monitor its progress
with the scheduler. After it finishes, the scheduler retains accounting information
that we can inspect later.

### Monitoring jobs with `squeue`

```bash
# monitor for the user
squeue --me
# or squeue -u $USER
```

```output
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          21271983     short render-s     user  R       0:04      1 wn21249
```

Periodically check the job status using `squeue --me`. Once the job is no longer listed,
continue to the next section.

| SLURM Status (ST) | Meaning |
| ----------------- | ------- |
| CA | Cancelled |
| CD | Completed |
| CF | Configuring |
| CG | Completing |
| F | Failed |
| OOM | Out of Memory |
| PD | Pending |
| R | Running |
| ST | Stopped |
| S | Suspended |
| TO | Timeout |
| ... | ... |

Once the job is completed, the `squeue --me` no longer lists the job:

```output
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
```

Once the job has completed, we can view the application's output:

```bash
cat slurm-21271983.out
```

```output
Image rendered in CPU

==============================================
     Computational Performance Metrics
==============================================
Image Size:                 800 x 800
Number of Snowmen:          3
MPI Processes:              4
Threads per Process:        1
----------------------------------------------
Performance (rays/sec):     2.766e+06
----------------------------------------------
Max Local Computation Time (s):              29.617
Min Local Computation Time (s):              29.532
Avg Local Computation Time (s):              29.574
==============================================
```

The `render-snowman` job takes approximately 30 seconds to render the snowmen scene.

The application reports its own computational performance in the output file. The
scheduler also records information about the job itself, such as resource usage and
execution time. Next, we'll inspect those scheduler records using `sacct`.

## Inspect the completed jobs using accounting `sacct` tool

:::::::::::::::: instructor
Note that the information `sacct` can provide depends on the information
that SLURM stores on a given machine. By default this includes Billing, CPU,
Energy, Memory, Node, FS/Disk, Pages and VMem. Additional information is
available only when SLURM is configured to collect it. These additional
trackable resources are listed in `AccountingStorageTRES`. For I/O
`fs/lustre` is commonly useful, and for the interconnect communication
`ic/ofed` is required. The setting `AccountingStorageTRES` is found in
`slurm.conf`. Unfortunately there doesn't seem to be a way to get `sacct`
to print the optional trackable resources.
::::::::::::::::::::::::::

The `sacct` command shows data stored in the job accounting database. You can query
the accounting information for any of your previously completed jobs. Rather than
keeping track of job IDs yourself, `sacct` can also provide an overview of your
recent jobs.

```bash
sacct
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode 
------------ ---------- ---------- ---------- ---------- ---------- -------- 
21271983     render-sn+      short       whep          4  COMPLETED      0:0 
21271983.ba+      batch                  whep          4  COMPLETED      0:0 
21271983.ex+     extern                  whep          4  COMPLETED      0:0
```

Each submitted job appears as one primary job entry followed by one or more
job steps. For this episode, we will focus on the primary job entry, since
it summarizes the entire job.

::: spoiler

In the output every job is shown three times here. This is because `sacct`
lists one line for the primary job entry, followed by a line for every job
step. A job step corresponds to an `mpirun` or `srun` command. The `extern`
line corresponds to all work that is done outside of SLURM's control,
for example an `ssh` command that runs something somewhere else.

:::

Note that by default `sacct` only lists the jobs that have been run today. You
can use the `--starttime` option to list all jobs that have been run since
the given start date. For example, try running

```bash
sacct --starttime=<YYYY-MM-DD>
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
21271983     render-sn+      short       whep          4  COMPLETED      0:0 
21271983.ba+      batch                  whep          4  COMPLETED      0:0 
21271983.ex+     extern                  whep          4  COMPLETED      0:0
21283742     render-sn+      short       whep         16  COMPLETED      0:0 
21283742.ba+      batch                  whep         16  COMPLETED      0:0 
21283742.ex+     extern                  whep         16  COMPLETED      0:0 
```

You may want to change the date of `YYYY-MM-DD` to something more sensible
when you work through this tutorial.
Note that some HPC systems may limit the range of such a request to a maximum of,
for example, 30 days to avoid overloading the slurm database with too large requests.

With the job ID you can ask `sacct` for information about a specific job
as in

```bash
sacct --jobs=21271983
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
21271983     render-sn+      short       whep          4  COMPLETED      0:0 
21271983.ba+      batch                  whep          4  COMPLETED      0:0 
21271983.ex+     extern                  whep          4  COMPLETED      0:0
```

Using `sacct` with the `--jobs` flag is just another way to select which jobs
we want more information about. In itself it does not provide any additional
information.

So far we've identified the completed job we want to inspect. The default `sacct`
output only provides a summary of each job. To answer questions about resource
usage–such as how long the job ran, how much memory the job used, or how efficiently
it used the allocated CPUs–we need to ask `sacct` to display additional accounting
fields.

The `--format` option lets us choose exactly which accounting fields to display.
We'll start with one simple example before requesting several metrics together.

### How long did my job run?

```bash
sacct --jobs=21271983 --format=Elapsed
```

```output
   Elapsed
----------
  00:00:36 
  00:00:36 
  00:00:36
```

::: instructor

# Give more insight in the collected `sacct` metrics

- `AllocCPUS`: number of CPU cores we requested for the job
- `MaxRSS` = `AveRSS`: low fluctuation in memory, data is held throughout the whole job
- `MaxPages` & `AvePages`: number of pages loaded into memory
- `MaxDiskRead`: Data read from disk by the application, but also to start the application.

For the challenge, ask the learners and answer after the exercise:

- Did I use the CPUs effectively?
    - AllocCPUS
    - TotalCPU
    - CPU frequency
- Did I have enough memory?
    - RSS
    - Page faults
- Was I waiting on storage?
    - Disk read
    - Disk write
- Additional Information
    - Energy

:::

::::::::::::::::::: challenge

# What does the accounting `sacct` tool inspect?

Use `sacct --format` to display the metrics discussed above, including `JobID`.
Note that the `--format` flag takes a comma separated list. Also note that
the result shows that more data is read than written, even though
the program generates and writes an image, and reads no data at all.
Why would that be?

For all the available options use the command:

```bash
sacct --helpformat
```

```output
Account             AdminComment        AllocCPUS           AllocNodes         
AllocTRES           AssocID             AveCPU              AveCPUFreq         
AveDiskRead         AveDiskWrite        AvePages            AveRSS             
AveVMSize           BlockID             Cluster             Comment            
Constraints         ConsumedEnergy      ConsumedEnergyRaw   Container          
CPUTime             CPUTimeRAW          DBIndex             DerivedExitCode    
Elapsed             ElapsedRaw          Eligible            End                
ExitCode            Extra               FailedNode          Flags              
GID                 Group               JobID               JobIDRaw           
JobName             Layout              Licenses            MaxDiskRead        
MaxDiskReadNode     MaxDiskReadTask     MaxDiskWrite        MaxDiskWriteNode   
MaxDiskWriteTask    MaxPages            MaxPagesNode        MaxPagesTask       
MaxRSS              MaxRSSNode          MaxRSSTask          MaxVMSize          
MaxVMSizeNode       MaxVMSizeTask       McsLabel            MinCPU             
MinCPUNode          MinCPUTask          NCPUS               NNodes             
NodeList            NTasks              Partition           Planned            
PlannedCPU          PlannedCPURAW       Priority            QOS                
QOSRAW              Reason              ReqCPUFreq          ReqCPUFreqGov      
ReqCPUFreqMax       ReqCPUFreqMin       ReqCPUS             ReqMem             
ReqNodes            ReqTRES             Reservation         ReservationId      
Start               State               Submit              SubmitLine         
Suspended           SystemComment       SystemCPU           Timelimit          
TimelimitRaw        TotalCPU            TRESUsageInAve      TRESUsageInMax     
TRESUsageInMaxNode  TRESUsageInMaxTask  TRESUsageInMin      TRESUsageInMinNode 
TRESUsageInMinTask  TRESUsageInTot      TRESUsageOutAve     TRESUsageOutMax    
TRESUsageOutMaxNode TRESUsageOutMaxTask TRESUsageOutMin     TRESUsageOutMinNode
TRESUsageOutMinTask TRESUsageOutTot     UID                 User               
UserCPU             WCKey               WCKeyID             WorkDir
```

Address the learners to concentrate on RSS, Pages, CPUS, Disk Read and Write, Energy and Frequency.

::::::::: solution

To query all of the above variable run

```bash
sacct --jobs=21271983 --format=MaxRSS,AveRSS,MaxPages,AvePages,AllocCPUS,Elapsed,MaxDiskRead,MaxDiskWrite,ConsumedEnergy,AveCPUFreq
```

```output
    MaxRSS     AveRSS MaxPages   AvePages  AllocCPUS    Elapsed  MaxDiskRead MaxDiskWrite ConsumedEnergy AveCPUFreq 
---------- ---------- -------- ---------- ---------- ---------- ------------ ------------ -------------- ---------- 
                                                   4   00:00:36                                        0            
   616644K    616644K      787        787          4   00:00:36       95.11M       16.53M              0     33.38M 
         0          0        0          0          4   00:00:36        0.01M        0.00M              0      2.35G
```

Although the program we have run generates an image and writes that
to a file, there is also a non-zero amount of data read. The writing part
is associated with the image file the program writes. The reading part is
not associated with anything that the program does, as it doesn't read
anything from disk. It is instead associated with the fact that the operating
system has to read the program itself and its dependencies to execute it.

:::::::::

:::::::::::::::::::

::: spoiler

### More about accounting `sacct` metrics:

### How long did my job actually run?

- `Elapsed` is the wall-clock time between the start and the completion of the job.
  It tells you how long the job occupied the allocated resources. Comparing this
  value with the requested wall time helps determine whether the requested time
  limit was appropriate.

### How many CPU cores did the scheduler allocate?

- `AllocCPUS` reports the number of CPUs allocated for the job. This is the amount
  of CPU resources the scheduler reserved based on the resource request in the job
  script. It does not indicate how effectively those CPUs were used.

### How much memory did my application use?

- `MaxRSS` and `AveRSS` report the maximum and average Resident Size Set (RSS), which
  is the amount of memory actively resident in physical RAM. Comparing these values
  with the memory requested for the job helps determine whether the memory request
  is appropriate.

### Was the application limited by memory?

- `MaxPages` and `AvePages` report the number of page faults that occurred during the
  job. Page faults occur when data required by the application is not currently resident
  in the physical memory and must be retrieved. Large numbers of page faults can
  significantly reduce performance because the application spends more time waiting
  for memory instead of performing computations.

### How much data moved to and from storage?

- `MaxDiskRead` and `MaxDiskWrite` report the amount of data read from and written to
  storage during the job. Disk activity may include not only application input and
  output files but also reading the executable and shared libraries required to start
  the program.

### How much energy did the job consume?

- `ConsumedEnergy` reports the energy used by the job if the HPC system is configured
  to collect this information. On systems where energy accounting is not enabled, this
  value is typically reported as zero.

### At what frequency did the CPU run?

- `AveCPUFreq` reports the average CPU frequency during the job. Some processors
  automatically adjust their operating frequency depending on workload, temperature, and
  power-management policies. This metric is mainly useful when investigating performance
  on systems that support dynamic frequency scaling.

:::

::::::::::::::::::::::: challenge

# This challenge needs correction

So far we have considered our initial calculation using 4 cores.
To run the calculation faster we could consider using more cores.
Run the same calculation on 8, 16, and 32 cores as well. Collect
and compare the results from `sacct` and see how the job performance
changes.

::::::: solution

The machine these calculations have been run on has 112 core
per node. So we can double the number of cores from 4 until
64 and stay within one node. If we go to two nodes then some
of the communication between tasks will have to go across the
interconnect. At that point the performance characteristics
might change in a discontinuous manner. Hence we try to
avoid doing that.

Alternatively you might scale the calculation across multiple
nodes, for example 2, 4, 8, 16 nodes. With 112 cores per node
you would have to make sure that the calculation is large enough
for such a large number of cores to make sense.

Create `running_snowmen.sh` with

```input
#!/usr/bin/bash
for nn in 4 8 16 32; do
    id=`sbatch --parsable --time=00:12:00 --nodes=1 --tasks-per-node=$nn --ntasks-per-core=1 render_snowman.sh`
    echo "ntasks $nn jobid $id"
done
```

Create `render_snowman.sh` with

```input
#!/usr/bin/bash

# Possibly a "module load ..." command to load required libraries
# Depends on your particular HPC system

export START=`pwd`
# Create a sub-directory for this job if it doesn't exist already
mkdir -p $START/test.$SLURM_NTASKS
cd $START/test.$SLURM_NTASKS
# The -spp flag ensures we have enough samples per ray such that the job
# on 32 cores takes longer than 30s. Slurm by default is configured such
# that job data is collected every 30s. If the job finishes in less than
# that Slurm might fail to collect some of the data about the job.
mpirun -np $SLURM_NTASKS raytracer -width=800 -height=800 -spp 1024 -threads=1 -alloc_mode=3 -png=rendered_snowman.png
```

Next we submit this whole set of calculations

```bash
./running_snowmen.sh
```

producing

```output
ntasks 4 jobid 349291
ntasks 8 jobid 349292
ntasks 16 jobid 349293
ntasks 32 jobid 349294
```

After the jobs are completed we can run

```bash
sacct --jobs=349291,349292,349293,349294 \
      --format=MaxRSS,AveRSS,MaxPages,AvePages,AllocCPUS,Elapsed,MaxDiskRead,MaxDiskWrite,ConsumedEnergy,AveCPUFreq
```

to produce

```output
    MaxRSS     AveRSS MaxPages   AvePages  AllocCPUS    Elapsed  MaxDiskRead MaxDiskWrite ConsumedEnergy AveCPUFreq
---------- ---------- -------- ---------- ---------- ---------- ------------ ------------ -------------- ----------
                                                   4   00:09:35                                        0
   142676K    142676K        1          1          4   00:09:35        7.75M        0.72M              0       743K
         0          0        0          0          4   00:09:35        0.01M        0.00M              0      2.61M
                                                   8   00:05:01                                        0
   289024K    289024K        0          0          8   00:05:01       10.15M        1.45M              0       960K
         0          0        0          0          8   00:05:02        0.01M        0.00M              0      2.42M
                                                  16   00:02:21                                        0
   563972K    563972K       93         93         16   00:02:21       15.00M        2.94M              0      1.03M
         0          0        0          0         16   00:02:21        0.01M        0.00M              0      2.99M
                                                  32   00:01:14                                        0
  1082540K   1082540K      260        260         32   00:01:14       24.83M        6.07M              0      1.08M
         0          0        0          0         32   00:01:14        0.01M        0.00M              0         3M
```

Note that the elapse time goes down as the number of cores increases, which is reasonable as more cores
normally can get the job done quicker. The amount of data read also increases as every MPI rank has to
read the executable and all associated shared libraries. The volume of data written is harder to understand.
Every run produces an image file `rendered_snowman.png` that is about 100KB in size. This file is written
just by the root MPI rank. This cannot explain the increase in data written with increasing numbers of cores.
The increasing number of page faults with increasing numbers of cores suggests that paging memory to disk
is responsible for the majority of data written.

:::::::

:::::::::::::::::::::::

So far, we have used `sacct` to inspect the accounting information collected for completed
jobs. While `sacct` lets us examine individual accounting fields, interpreting all of these
metrics can take some effort. Rather than displaying those accounting fields individually,
`seff` summarizes the same accounting information into a concise report highlighting CPU
utilization, memory usage, wall-clock time, and other key efficiency metrics.
Like `sacct`, it uses a completed job's ID to retrieve its accounting summary.

## Interpret the efficiency of the submitted jobs using `seff` tool

::: instructor

# Todo: extend the following list and examples to include CPU

To reconstruct the CPU utilization reported by `seff`:
- `TotalCPU`/`CPUTime` should give the percentage
- Could also mention `UserCPU` and `SystemCPU` and discuss the difference? Both result in `TotalCPU`

Maybe remove `AveCPUFreq` instead, or do we try to teach something specific about it?

Don't forget to change the example output of all `sacct`s in the following examples/challenges!

:::

::: callout

# `seff` may not be available

`seff` is an optional SLURM tool for more convenient access to `sacct`. It does not come
standard with every SLURM installation. Your particular HPC system may or may not provide
it. Check for its availability on your login nodes, or consult your cluster documentation
or support staff.

Other third party alternatives, e.g. [reportseff](https://github.com/troycomi/reportseff/),
can be installed with default user permissions.

:::::::::::

Let's summarize the same job we inspected with `sacct` using its job ID (`21271983`).

```bash
seff 21271983
```

```output
Job ID: 21271983
Cluster: pleiades
User/Group: <user>/<usrgrp>
State: COMPLETED (exit code 0)
Nodes: 1
Cores per node: 4
CPU Utilized: 00:02:02
CPU Efficiency: 84.72% of 00:02:24 core-walltime
Job Wall-clock time: 00:00:36
Memory Utilized: 602.19 MB
Memory Efficiency: 3.96% of 14.84 GB
```

The report combines several accounting fields into a concise overview of the resources
allocated to the job and how effectively they were used. Rather than inspecting
individual accounting fields, we can quickly identify whether the requested wall-clock
time and memory were appropriate.

The report summarizes three types of information:

- Resources allocated
    - Number of nodes
    - Cores per node
    - Allocated memory

- Resources used
    - CPU utilized
    - Job wall-clock time
    - Memory utilized

- Efficiency
    - CPU Efficiency
    - Memory Efficiency

The allocated resources describe what the scheduler reserved for the job. The resource
usage describes what the application actually consumed. The efficiency metrics
compare the allocated resources with the resources that were actually used.

We can use the summary reported by `seff` for the job ID `21271983` to evaluate
whether the requested resources were appropriate and identify opportunities to improve
future job submissions. Looking at the `Job Wall-clock time`, we see that the job
completed in approximately 36 seconds, even though we requested one hour. Requesting
substantially more time than a job actually needs can increase the time it spends
waiting in the queue because the scheduler must find a sufficiently large time window in
which to run it. Shorter jobs are often easier for the scheduler to fit into the
schedule than longer ones.

On the other hand, requesting too little risks the job being terminated before it
finishes. The goal is therefore to request enough time for the job to complete reliably
while avoiding an unnecessarily large safety margin. Because a job's running time depends
on many machine factors–including network communication, disk access, operating system
jitter, and system load–it is sensible to include a modest buffer once you have a good
estimate of the expected wall-clock time. Nevertheless, requesting more than twice the
expected running time rarely makes sense.

The memory utilization reported by `seff` shows that the job used only a small fraction
of the allocated memory. By default, SLURM reserves a certain amount of memory per CPU
core, so in this case the default allocation was much larger than the application
required, resulting in a memory efficiency of only about 4%. We could reduce the requested
memory by explicitly specifying a smaller memory allocation in the `render_snowman.sbatch`
job script.

::: instructor

# Todo: potential issue?

Running this on our cluster and adding a module load command resulted in 600MB of memory
required. My guess is, this is due to `cgroups_v2` and Page caches being counted towards
the job as well, so loading the modules might spike the resource requirements as well?

Maybe we should play it safe and use a larger value in the following exercise.
But we also want to teach not overdoing it, so it'd be good if we can find a useful but
generic compromise here

::::::::::::::

:::::::::::::::::::: challenge

# Does the memory usage efficiency improve?

Edit the batch file to reduce the amount of memory requested for the
job. Note that the amount of memory requested per CPU core can be specified with the
`--mem-per-cpu=` option.

Memory amounts may be specified using the following suffixes:

- `K` or `k` for kilobytes
- `M` or `m` for megabytes
- `G` or `g` for gigabytes
- `T` or `t` for terabytes

For this example, requesting 160 MB per CPU core is more than sufficient. Submit the job,
and inspect the efficiency with `seff`. How does the memory efficiency compare with the
previous submission?

:::::::: solution

The modified batch script becomes:

```bash
#!/usr/bin/bash
#SBATCH --job-name=render-snowman
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4
#SBATCH --mem-per-cpu=160MB

# Only one example, consult your cluster documentation or ask the instructor or your HPC support
module load 2025 GCC/13.2.0 OpenMPI/4.1.6 Boost/1.83.0 CMake/3.27.6 libpng/1.6.40 buildenv/default

mpirun -np 4 ./raytracer -width=800 -height=800 -spp=128 -threads=1 -png=snowman.png
```

Submit the modified jobscript as shown before with the following command:

```bash
sbatch render_snowman.sbatch
```

Check the status of the job using `squeue --me`.

```output
             JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
          21295177     short render-s     user  R       0:15      1 wn21231
```

Once the job is completed, execute the following command:

```bash
seff 21295177
```

```output
Job ID: 21295177
Cluster: pleiades
User/Group: <user>/<usrgrp>
State: COMPLETED (exit code 0)
Nodes: 1
Cores per node: 4
CPU Utilized: 00:02:11
CPU Efficiency: 86.18% of 00:02:32 core-walltime
Job Wall-clock time: 00:00:38
Memory Utilized: 602.53 MB
Memory Efficiency: 94.14% of 640.00 MB
```

The output of `seff` shows that approximately 94% of the requested memory was used.

::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::

Now we see that a much larger fraction of the allocated memory has been used. This means
that the requested memory is now much closer to what the application actually requires.
In practice, modestly overestimating memory is often not a major concern. However, requesting
only the memory your application needs gives the scheduler more flexibility when placing
jobs on the available compute nodes, which may reduce the time your job spends waiting
in the queue.

This can be particularly beneficial on systems running many memory-intensive workloads,
such as machine learning applications. These jobs may require so much memory per CPU core
that they cannot use every core on a node, leaving some cores idle. Jobs with smaller
memory requirements can sometimes make use of these otherwise unavailable resources
and therefore start sooner. How much benefit this provides depends on the workload
mix and scheduling policies of the HPC system where you run your calculations.

The CPU efficiency reported by `seff` is close to 100%, indicating that the allocated
CPU cores spent almost all of their time executing your job rather than sitting idle.
However, this does not necessarily mean that the application is making efficient use of
the available hardware or running as fast as possible.

For example, every parallel application contains some serial sections that cannot be
parallelized. During these periods, CPU cores may remain busy even though the application
is not making the most effective use of the available CPU resources. Likewise,
CPU efficiency does not indicate how well an application exploits the capabilities of
the CPU. If a processor supports vector instructions but the application does not use
them, the CPUs may still appear fully utilized even though the application is running
significantly slower than it could.

`seff` therefore provides a useful summary of how busy the allocated CPU resources were,
but it cannot determine whether the application is making efficient use of the underlying
hardware. It is therefore important to keep these limitations in mind when interpreting
the CPU efficiency reported by `seff`.

::: callout

# High CPU utilization does not imply efficient execution

High CPU utilization indicates that the CPU spent most of its time performing computations
rather than sitting idle. It does not necessarily mean that the application used the
hardware efficiently or that it produced useful work as efficiently as possible.

:::::::::::

The `seff` command cannot give you any information about the I/O performance of
your job. You have to use other approaches for that, and `sacct` may be one of them.


## Shortcomings

The accounting information provided by `sacct` and `seff` gives a useful summary
of how a job used the resources allocated by the scheduler. However, it is intended
to provide a high-level overview rather than a detailed performance analysis.

For example, the reported metrics summarize the entire execution of a job. They do not
show how resource usage changes over time, making it difficult to identify different
execution phases or short-lived performance problems.

Likewise, scheduler accounting does not record communication between MPI processes. Reliable
measurements of I/O between the compute nodes and the parallel file system are also
often unavailable. Some hardware-specific metrics, such as energy consumption, depend
on the capabilities and configuration of the HPC system and may not be collected.

The information reported by `sacct` and `seff` can therefore help identify potential
performance issues and improve future resource requests. However, a detailed performance
analysis requires more specialized profiling and performance analysis tools.

## Summary

In this episode, we used SLURM tools `sacct` and `seff` to inspect completed jobs and
interpret the accounting information collected by the scheduler. We learned how to use
this information to evaluate wall-clock time, memory usage, and CPU utilization,
helping us determine whether the requested resources were appropriate and identify
opportunities to improve future job submissions.

Because these tools use accounting information collected automatically while a job runs,
they can be used to analyze any completed job without requiring special preparation or
instrumentation.

:::::::::::::::::::::::::::::::::::::: keypoints

- `sacct` provides detailed accounting information for completed jobs, while `seff` summarizes it.
- Scheduler accounting helps evaluate wall-clock time, memory usage, and CPU utilization.
- Scheduler accounting can be used to improve future resource requests.
- Scheduler accounting provides a high-level summary; detailed performance analysis requires specialized profiling tools.

::::::::::::::::::::::::::::::::::::::::::::::::
