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

After completing this episode, participants should be able to …

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


## Scheduler Tools

A scheduler performs important tasks such as accepting and scheduling jobs,
monitoring job status, starting user applications, cleaning up jobs that
have finished or exceeded their allocated time. The scheduler also keeps
a history of jobs that have been run and how they behaved. The information
that is collected can be queried by the job owner to learn about how
the job utilized the resources it was given.

### The `seff` tool

The `seff` command can be used to learn about how efficiently your job
has run. The `seff` command takes the job identifier as an argument
to select which job it displays information about. That means we need
to run a job first to get a job identifier we can query SLURM about.
Then we can ask about the efficiency of the job.

::: callout

# `seff` may not be available

`seff` is an optional SLURM tool for more convenient access to `saact`. It does not come standard with every SLURM installation.
Your particular HPC system may or may not provide it. Check for it's availability on your login nodes, or consult your cluster documentation or support staff.

Other third party alternatives, e.g. [reportseff](https://github.com/troycomi/reportseff/), can be installed with default user permissions.

:::::::::::

The `sbatch` command is used to submit a job. It takes a job script as
an argument. The job script contains the resource requests, such as the
amount of time needed for the calculation, the number of nodes, the
number of tasks per node, and so on. It also contains the commands to
execute the calculations.

Using your favorite editor, create the job script `render_snowman.sbatch`
with the contents below.
```input
#!/usr/bin/bash
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4

# Possibly a "module load ..." command to load required libraries
# Depends on your particular HPC system

mpirun -np 4 raytracer -width=800 -height=800 -spp=128 -alloc_mode=3
```
Next submit the job with `sbatch`, and see what `seff` says about
the job with the following commands.

```bash
jobid=$(sbatch --parsable render_snowman.sbatch)
seff $jobid
```

```output
Job ID: 309489
Cluster: bigiron
User/Group: usr123/grp123
State: COMPLETED (exit code 0)
Nodes: 1
Cores per node: 4
CPU Utilized: 00:07:43
CPU Efficiency: 98.93% of 00:07:48 core-walltime
Job Wall-clock time: 00:01:57
Memory Utilized: 35.75 MB
Memory Efficiency: 0.20% of 17.58 GB (4.39 GB/core)
```

The job script we created asks for 4 CPUs for an hour. After submitting
the job script we need to wait until the job has finished as `seff` can
only report sensible statistics after the job is completed. The report
from `seff` shows basic statistics about the job, such as

- The resources the job was given
  * the number of nodes
  * the number of cores per node
  * the amount of memory per core
- The amount of resources used
  * `CPU Utilized` the aggregate CPU time (the time the job took times the number of CPUs allocated)
  * `CPU Efficiency` the actual CPU usage as a percentage of the total available CPU capacity
  * `Job Wall-clock time` the time the job took from start to finish
  * `Memory Utilized` the aggregate memory usage
  * `Memory Efficiency` the actual memory usage as a percentage of the total avaialable memory


::: instructor

# Todo: give clear recommendation of what to aim for?
Maybe 80% of job time?

::::::::::::::

Looking at the `Job Wall-clock time` it shows that the job took just under 2
minutes. Therefore this job took a lot less time
than the one hour we asked for. This can be problematic as the scheduler looks
for time windows when it can fit a job in. Long running jobs cannot be squeezed
in as easily as short running jobs. As a result, jobs that request a long time
to complete typically have to wait longer before they can be started. Therefore
asking for more than 10 times as much time as the job really needs, simply
means that you will have to wait longer for the job to start. On the other hand
you do not want to ask for too little time. Few things are more annoying than
waiting for a long running calculation to finish, just to see the job being
killed right before the end because it would have needed a couple of minutes more
than you asked for. So the best approach is to ask for more time than
the job needs, but not go overboard here. As the job elapse time depends on
many machine conditions, including congestion in the data communication, disk
access, operating system jitter, and so on, you might want to ask for a
substantial buffer. Nevertheless, asking for more than twice as much time as
job is expected to need, usually doesn't make sense.

Another thing is that SLURM by default reserves a certain amount of memory per
core. In this case the actual memory usage is just a fraction of that amount.
We could reduce the memory allocation by explicitly asking for less
by modifying the `render_snowman.sbatch` job script.

::: instructor

# Todo: potential issue?

Running this on our cluster and adding a module load command resulted in 600MB of memory required.
My guess is, this is due to cgroups_v2 and Page caches being counted towards the job as well, so loading the modules might spike the resource requirements as well?

Maybe we should play it safe and use a larger value in the following exercise.
But we also want to teach not overdoing it, so it'd be good if we can find a useful but generic compromise here

::::::::::::::

:::::::::::::::::::: challenge

Edit the batch file to reduce the amount of memory requested for the
job. Note that the amount of memory per node can be requested with the
`--mem=` argument. The amount of memory is specified by a number followed by
a unit. The units can represent kilobtytes (KB), megabytes (MB),
gigabytes (GB). For the calculations we are doing here 100 megabytes per
node is more than sufficient. Submit the job, and inspect the efficiency
with `seff`. What is the memory usage efficiency you get?

:::::::: solution

The batch file after adding the memory request becomes.

```input
#!/usr/bin/bash
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4
#SBATCH --mem=100MB

# Possibly a "module load ..." command to load required libraries
# Depends on your particular HPC system

mpirun -np 4 raytracer -width=800 -height=800 -spp=128 -alloc_mode=3
```

Submit this jobscript, as before, with the following command.

```bash
jobid=$(sbatch --parsable render_snowman.sbatch)
seff $jobid
```

```output
Job ID: 310002
Cluster: bigiron
User/Group: usr123/grp123
State: COMPLETED (exit code 0)
Nodes: 1
Cores per node: 4
CPU Utilized: 00:07:43
CPU Efficiency: 98.09% of 00:07:52 core-walltime
Job Wall-clock time: 00:01:58
Memory Utilized: 50.35 MB
Memory Efficiency: 50.35% of 100.00 MB (100.00 MB/node)
```

The output of `seff` shows that about 50% of requested memory
was used.

::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::

Now we see that a much larger fraction of the allocated memory has been
used. Normally you would not worry too much about the memory request. Lately
HPC clusters are used more for machine learning work loads which tend to require
a lot of memory. Their memory requirements per core might actually be so large
that they cannot use all the cores in a node. So there may be spare cores
available for jobs that need little memory. In such a scenario tightening the
memory allocation up could allow the scheduler to start your job early. How
much milage you might get from this depends on the job mix at the HPC site where
you run your calculations.

Note that the CPU utilization is reported as almost 100%, but this just means
that the CPU was busy with your job 100% of the time. It does not mean that this
time was well spent. For example, every parallel program has some serial parts
to the code.
Typically those parts are executed redundantly on all cores, which is wasteful
but not reflected in the CPU efficiency. Also, this number does not reflect
how well the capabilities of the CPU are used. If your CPU offers vector
instructions, for example, but your code does not use them then your code will
just run slow. The CPU efficiency will still show that the CPU was busy 100% of
the time even though the program is just running at a fraction of the speed
it could achieve if it fully exploited the hardware capabilities. It is worth
keeping these limitations of `seff` in mind.

::: callout

# Good utilization does not imply efficiency
Measuring close to 100% CPU utilization does not say anything about how useful the calculations are.
It's merely stating, that the CPU was mostly busy with calculations, instead of waiting for data or running idle, waiting for other conditions to occur.

Good CPU utilization is only efficient, if it runs only "useful" calculations that contribute with new results towards an intended goal.

:::::::::::

The `seff` command cannot give you any information about the I/O performance of
your job. You have to use other approaches for that, and `sacct` may be one of them.

### The `sacct` tool

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

The `sacct` command shows data stored in the job accounting database. You can
query the data of any of your previously run jobs. Just like with `seff` you
will need to provide the job ID to query the accounting database. Rather than
keeping track of all your jobs yourself you can ask `sacct` to provide you
with an overview of the jobs you have run.

```bash
sacct
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
309902       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
309902.batch      batch             project_a          4  COMPLETED      0:0
309902.exte+     extern             project_a          4  COMPLETED      0:0
309903       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
309903.batch      batch             project_a          4  COMPLETED      0:0
309903.exte+     extern             project_a          4  COMPLETED      0:0
310002       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
310002.batch      batch             project_a          4  COMPLETED      0:0
310002.exte+     extern             project_a          4  COMPLETED      0:0
```

In the output every job is shown three times here. This is because `sacct`
lists one line for the primary job entry, followed by a line for every job
step. A job step corresponds to an `mpirun` or `srun` command. The `extern`
line corresponds to all work that is done outside of SLURM's control,
for example an `ssh` command that runs something somewhere else.

Note that by default `sacct` only lists the jobs that have been run today. You
can use the `--starttime` option to list all jobs that have been run since
the given start date. For example, try running

```bash
sacct --starttime=2025-09-25
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
308755       snowman.s+  STD-s-96h  project_a         16  COMPLETED      0:0
308755.batch      batch             project_a         16  COMPLETED      0:0
308755.exte+     extern             project_a         16  COMPLETED      0:0
308756       snowman.s+  STD-s-96h  project_a          4  COMPLETED      0:0
308756.batch      batch             project_a          4  COMPLETED      0:0
308756.exte+     extern             project_a          4  COMPLETED      0:0
309486       interacti+  STD-s-96h  project_a          4     FAILED      1:0
309486.exte+     extern             project_a          4  COMPLETED      0:0
309486.0          prted             project_a          4  COMPLETED      0:0
309489       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
309489.batch      batch             project_a          4  COMPLETED      0:0
309489.exte+     extern             project_a          4  COMPLETED      0:0
309902       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
309902.batch      batch             project_a          4  COMPLETED      0:0
309902.exte+     extern             project_a          4  COMPLETED      0:0
309903       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
309903.batch      batch             project_a          4  COMPLETED      0:0
309903.exte+     extern             project_a          4  COMPLETED      0:0
310002       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
310002.batch      batch             project_a          4  COMPLETED      0:0
310002.exte+     extern             project_a          4  COMPLETED      0:0
```

You may want to change the date of `2025-09-25` to something more sensible
when you work through this tutorial.
Note that some HPC systems may limit the range of such a request to a maximum of, for example, 30 days to avoid overloading the slurm database with too large requests.

With the job ID you can ask `sacct` for information about a specific job
as in

```bash
sacct --jobs=310002
```

```output
JobID           JobName  Partition    Account  AllocCPUS      State ExitCode
------------ ---------- ---------- ---------- ---------- ---------- --------
310002       render_sn+  STD-s-96h  project_a          4  COMPLETED      0:0
310002.batch      batch             project_a          4  COMPLETED      0:0
310002.exte+     extern             project_a          4  COMPLETED      0:0
```

Using `sacct` with the `--jobs` flag is just another way to select which jobs
we want more information about. In itself it does not provide any additional
information.
To get more specific data we need to explicitly ask for the information
we want. As SLURM collects a broad range of data about every job it is worth
to evaluate what the most relevant items are.

::: instructor

# Todo: extend the following list and examples to include CPU

To reconstruct the CPU utilization reported by `seff`:
- `TotalCPU`/`CPUTime` should give the percentage
- Could also mention `UserCPU` and `SystemCPU` and discuss the difference? Both result in `TotalCPU`

Maybe remove `AveCPUFreq` instead, or do we try to teach something specific about it?

Don't forget to change the example output of all `sacct`s in the following examples/challenges!

::::::::::::::

- `MaxRSS`, `AveRSS`, or the Maximum or Average Resident Size Set (RSS). The
  RSS is the memory allocated by a program that is actually resident in the
  main memory of the computer. If the computer gets low on memory then the
  virtual memory manager can extend the apparently available memory by moving
  some of the data from memory to disk. This is done entirely transparently to the
  application, but the data that has been moved to disk is no longer resident
  in main memory. As a result accessing it will be slower because it needs to
  retrieved from disk first. Therefore if the RSS is small compared to the
  total amount of memory the program uses this might affect the performance
  of the program.
- `MaxPages`, `AvePages`, or the Maximum or Average number of Page Faults.
  These quantities are related to the Resident Size Sets. When the program
  tries to access data that is not resident in main memory this triggers a
  page fault.
  The virtual memory manager responds to a page fault by retrieving the accessed
  data from disk (and potentially migrating other data to disk to make
  space). These operations are typically costly. Therefore high numbers of
  page faults typically correspond to a significant reduction in the program's
  performance. For example, the CPU utilization might drop from as high as 98%
  to as low as 2% due to page faults. For that reason some HPC machines are
  configured to kill your job if the application generates a high rate of
  page faults.
- `AllocCPUS` is the number of CPUs allocated for the job.
- `Elapsed` is the amount of wall clock time it took to complete the job. I.e.
  the amount of time that passed between the start and finish of the job.
- `MaxDiskRead`, the Maximum amount of data read from disk.
- `MaxDiskWrite`, the Maximum amount of data written to disk.
- `ConsumedEnergy`, the amount of energy consumed by the job if that information  was collected. The data may not be collected on your particular HPC system and is reported as 0.
- `AveCPUFreq`, the average CPU frequency of all tasks in a job, given in kHz. In general the
  higher the clock frequency of the processor the faster the calculation runs.
  The exception is if the application is memory bandwidth limited and the data
  cannot be moved to processor fast enough to keep it busy. In that case
  modern hardware might throttle the frequency. This saves energy as the power
  consumption scales linearly with the clock frequency, but doesn't slow
  the calculation down as the processor was having to wait for data anyway.

We can explicitly select the data elements that we are interested in. To
see how long the job took to complete run

```bash
sacct --jobs=310002 --format=Elapsed
```

```output
   Elapsed
----------
  00:01:58
  00:01:58
  00:01:58
```

::::::::::::::::::: challenge

Request information regarding all of the above variables from `sacct`, including `JobID`.
Note that the `--format` flag takes a comma separated list. Also note that
the result shows that more data is read than written, even though
the program generates and write an image, and reads no data at all.
Why would that be?

::::::::: solution

To query all of the above variable run

```bash
sacct --jobs=310002 --format=MaxRSS,AveRSS,MaxPages,AvePages,AllocCPUS,Elapsed,MaxDiskRead,MaxDiskWrite,ConsumedEnergy,AveCPUFreq
```

```output
    MaxRSS     AveRSS MaxPages   AvePages  AllocCPUS    Elapsed  MaxDiskRead MaxDiskWrite ConsumedEnergy AveCPUFreq
---------- ---------- -------- ---------- ---------- ---------- ------------ ------------ -------------- ----------
                                                   4   00:01:58                                        0
    51556K     51556K      132        132          4   00:01:58        6.91M        0.72M              0         3M
         0          0        0          0          4   00:01:58        0.01M        0.00M              0         3M
```

Although the program we have run generates an image and writes that
to a file, there is also a none zero amount of data read. The writing part
is associated with the image file the program writes. The reading part is
not associated with anything that the program does, as it doesn't read
anything from disk. It is instead associated with the fact that the operating
system has to read the program itself and it's dependencies to execute it.

:::::::::

:::::::::::::


::: instructor

# Give more insight in the collected `sacct` metrics

- `AllocCPUS`: number of CPU cores we requested for the job
- `MaxRSS` = `AveRSS`: low fluctuation in memory, data is held throughout the whole job
- `MaxPages` & `AvePages`: number of pages loaded into memory
- `MaxDiskRead`: Data read from disk by the application, but also to start the application.

::::::::::::::

## Shortcomings

While `seff` and `sacct` provide a lot of information it is still incomplete. For
example, the information is accumulated for the entire calculation. Variations in the
metrics as a function of time throughout the job are not available.
Communication between different MPI processes is not recorded. The collection
of the energy consumption depends on the hardware and system configuration
at the HPC center and might not be available. We are also often missing reliable measurements
for I/O via the interconnect between nodes and the parallel file system.

So while we might be able to
glean some indications for different types of performance problems, for a
proper analysis more detailed information is needed.

## Summary

This episode introduced the SLURM tools `seff` and `sacct` to get a high
level perspective on a job's performance. As these tools just use the statistics
that SLURM collected on a job as it ran, they can always be used without
any special preparation.

::::::::::::::::::::::: challenge

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

:::::::::::::::::::::::::::::::::::::: keypoints

- Schedulers provide tools for a high level view on our jobs, e.g. `sacct` and `seff`
- Important basic performance metrics we can gather this way are:
  - **CPU Utilization**, often as fraction of `time where CPU was active`/`elapsed time of the job`
  - **Memory utilization**, often measured as *Resident Set Size* (RSS) and number of *Pages*
- `sacct` can also provide metrics about disk I/O and energy consumption 
- Metrics through `sacct` are accumulated for the whole job runtime and may be too broad for more specific insight

::::::::::::::::::::::::::::::::::::::::::::::::
