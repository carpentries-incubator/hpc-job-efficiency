---
title: "Resource Requirements"
teaching: 70
exercises: 30
---

::: questions

- How many resources should I request initially?
- How do I know if they are used well?
- How do I optimise my resource requests?

:::

::: objectives

After completing this episode, participants should be able to …

- Request the proper amount of resources from the scheduler.
- Change the parameters to see how the execution time changes.
- Assess whether the resources are used efficiently.

:::

When you run a program on your local workstation or laptop, you
typically don't plan out the usage of computing resources like memory or
core-hours.
Your applications simply take as much as they need and if your computer
runs out of resources, you can close unneeded applications and wait.

However, unless you are very rich, you probably don't have a dedicated HPC cluster just to yourself.
Instead you have to share one with your colleagues.
In such a scenario, greedily consuming as many resources as possible is very impolite.
It's necessary to carefully request only as many resources as needed for the task at hand.
These resource constraints are then enforced by the clusters scheduling system, such that your
application can't consume more resources than specified by your job.

In the previous section we looked at how the queue waiting time varies with
the job size. The "calculations" we submitted were trivial. Here we will
look at more realistic jobs and consider how efficiently we use the resources
we have requested.

## Benchmarks

In order to improve how we are running our jobs we need two things. First we
need a way to measure how we are doing. Second we need something to compare
this measurement against, so we can decide
whether we are doing better or worse than before.

In computing the term benchmark is often used but in practice this term
can mean one of a few related things:

- it can be a standardized test that is used to assess performance or
  efficiency
- it can a reference result of the standardized test that is used as
  a baseline to compare against
- it can even be a verb to describe the act of benchmarking

Here the term "benchmark" will refer to the first 2 interpretations. We'll
choose a specific test and evaluate how the performance changes when we
vary the job parameters. Commands like `seff` and `sacct` provide useful
information to compare runs.

::::::: spoiler
# `seff` efficiency is not parallel efficiency

In `seff` the CPU efficiency is defined as the sum of the CPU time spend on each
core summed across all cores divided by the elapse time times the number of cores.
That implies that if the some cores finish quickly and others take longer the
efficiency goes down. In other words this definition measures how much of the
cores allocated were actually used. The same definition also applies to
other resources such as memory.

Parallel efficiency is defined as the elapse time running on single core divided
by the elapse time times the number of cores of a parallel run. This definition of
efficiency measures the overheads parallelisation introduces.

For example, if I run the same task $N$ times across $N$ cores then `seff` would report
an efficiency of $100%$ as all cores would start and finish at the same time, and be fully utilized. The parallel
efficiency would instead be $100/N$% as the parallel run would use $N$ times as many resources
as the serial one to get the same result.

So, use `seff`'s efficiency to check whether the allocated resources where actually used.
Check with parallel efficiency whether the resources were used effectively.
:::::::::::::::



## Sizing your jobs

The resources required by your jobs primarily depend on the application you want
to run and are thus very specific to your particular HPC use case.

Generously over-allocating resource requirements as a strategy to ensure job
completion is usually counterproductive.
Not only might you face the wrath of your cluster administrators (and other users!)
for being overly greedy, but you may also be punished by the scheduler itself:
large jobs have to wait longer for the resources to free up, while small jobs can
be "squeezed" into the gaps between larger jobs.
Also, you should remember that you are billed for the amount of resources you
requested from the scheduler and not how much you actually use.
In short, capping resource requests at actual job requirements helps reduce queue
times and conserves your compute budget.

### Sizing your jobs: Time

Finding the right amount of resources is often a matter of trial and error as many
applications do not have precisely predictable resource requirements.
Let's try this for our snowman renderer. Put the following in a file named `snowman.job`:
```bash
#!/bin/bash
#SBATCH --job-name=snowman
#SBATCH --nodes=1
#SBATCH --partition=<put your partition here>
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:01:00
#SBATCH --output=snowman-stdout-%j.log

# Always a good idea to purge modules first to start with a clean module environment
module purge
# <put the module load commands for your cluster here>

# Start the raytracer
mpirun -n 4 ./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=1 -alloc_mode=3 -png=snowman.png
```
<!-- mpirun -n 4 ./SnowmanRaytracer/build/raytracer -width=1024 -height=1024 -spp=256 -threads=1 -alloc_mode=3 -png=snowman.png -->

Most of the resource requirements we have seen before in the previous
episode. New is the last directive, `--output`, which
redirects the job's output to the file `snowman-stdout-<job id>.log`.

To test if our estimate works, you have to submit the job to the scheduler:

```bash
sbatch snowman.job
```

This command will also print the ID of the job, so we can observe what is happening with it.
Wait a bit and have a look at how your job is doing. We use `sacct` to see what accounting
information the scheduler is collecting about your job:

```bash
sacct -X -j <jobid of your job>
```

We use the flag `-X` to only show a single summarising line per job.

::::::: challenge
# Find out how your job did

Is your job successful? If it isn't, what information do you get from the
scheduler or the log-file?

:::::::::::::::::
:::::::: solution
After a while, you will see that `sacct` gives the status of your job as `TIMEOUT`.

When you check the file `snowman-stdout.log` as well, you will see a line like this near the bottom:

```output
slurmstepd: error: *** JOB 1234567 ON somenode CANCELLED AT 2025-04-01T13:37:00 DUE TO TIME LIMIT ***
```

Evidently, our job was aborted because it did not finish within the time limit of one minute that we set above.
::::::::::::::::::

Let's try giving our job a time limit of 10 minutes instead.
```bash
#SBATCH --time=00:10:00
```

This time the job should succeed and show a status of "COMPLETED" in `sacct`.
We can check the resources actually needed by our job with the help of `seff`:

```bash
seff <jobid of your job>
```

The output of `seff` contains many useful bits of information for sizing our job. In particular, let's look at these lines:

```output
[...]
CPU Utilized: 00:21:34
CPU Efficiency: 98.93% of 00:21:48 core-walltime
Job Wall-clock time: 00:05:27
Memory Utilized: 367.28 MB
Memory Efficiency: 35.87% of 1.00 GB
```

::: spoiler

# Measurements are hardware dependent!

The exact numbers here depend a lot on the hardware and software of your local cluster.
Differences between two HPC systems or even different partitions on the same HPC system may be caused by different CPU generations, larger or smaller memory bandwidths, file system and network technologies, etc.

:::

The `Job Wall-clock time` is the time our job took. As we can see, our job takes much longer than one minute to complete which is why our first attempt with a time limit of one minute has failed.

The `CPU Utilized` line shows us how much CPU time our job has used. This is calculated by determining the busy time for each core and then summing these times for all cores. In an ideal world, the CPU cores should be busy for the entire time of our job, so the CPU time should be equal to the time the job took times the number of CPU cores. The ratio between the real CPU time and the ideal CPU time is shown in the `CPU Efficiency` line.

Finally, `Memory utilized` line shows the peak memory consumption that your job had at any point during its runtime, while `Memory Efficiency` is the ratio between this peak value and the requested amount of memory for the allocation. As we will see later, this value has to be taken with a grain of salt.

Starting from the set of parameters that successfully run our program, we can now try to reduce the amount of requested resources. As is good scientific practice, we should only vary one parameter at a time and observe the result. Let's start by reducing the time limit. There is often a bit of variation in the time needed to run a job since not all nodes are perfectly identical, so you should add an arbitrarily chosen safety margin of maybe 10 percent. According to the time reported by `seff`, seven minutes should therefore be a good time limit. If your cluster is faster, you might reduce this even further.

```bash
#SBATCH --time=00:07:00
```

As you can see, your job will still complete successfully.

:::::::::: challenge
# Choose a reliable time limit for the cluster you're on

Play a bit the time limits and check whether you job still runs successfully.
::::::::::::::::::::
::::::::::: solution
You could run the job with a long time limit multiple times (say 5).
Look at what `seff` reports for the wallclock time of each run.
This gives you a basic idea of how much that time fluctuates.
Based on this information you can make a choice as to what time limits
make sense here. Note that any choice can still be wrong in
extreme cases (massive congestion on the switch, or another
process running on the node interfering, filesystem problems, etc.).
But a reasonable choice should work in the vast majority of cases.
::::::::::::::::::::

::: instructor

For the next section, the exact memory requirements depend on the cluster configuration (e.g., the MPI backends used). You might have to adapt these numbers for your local cluster to see the out-of-memory behavior.

:::

### Sizing your jobs: Memory

Next, we can optimize our memory allocation. According to Slurm, we used 367.28 MB of memory in our last run, so let's set the memory limit to 500 MB.

```bash
#SBATCH --mem=500M
```

:::::::::: challenge
# Establish the fate of your job

Use `sacct` to see if your job was successful. Can you suggest why you got
the result you got?
::::::::::::::::::::
::::::::::: solution
Most likely the job failed with the job status `OUT_OF_MEMORY`. That means
that the scheduler terminated the job because it was trying to use more
memory than you requested.

If not, you could
try and see how close to the memory usage reported by `seff` you can set the memory request.
The job will start failing well before you get to the value reported by `seff`.

The reason is that Slurm measures memory usage by polling.
::::::::::::::::::::

This behavior seems contradictory at first: Slurm reported previously
that our job only used around 367 MB of memory at most, which is well
below the 500 MB limit we set. The explanation for this discrepancy lies
in the fact that Slurm measures the peak memory consumption of jobs by
*polling*, i.e., by periodically sampling how much memory the job currently
uses. Unfortunately, if the program has spikes in memory consumption that are
short enough to fit between two samples, Slurm will miss them and report an
incorrect peak memory value. Spikes in memory usage are quite common, for
example if your application uses short-lived subprocesses. Most annoyingly,
many programs allocate a large chunk of memory right at the end of the computation
to write out the results. In the case of the snowman raytracer, we encode the raw
pixel data into a PNG at the end, which means we temporarily keep both the raw image
and the PNG data in memory.

![](fig/slurm-memory-sampling.svg){alt="A graph plotting memory consumption of a job over time. The curve has an upwards trend with intermittent spikes. The periodic sampling of Slurm are shown as vertical lines intersecting the graph in regular intervals. While one of the memory spikes coincides with a sampling point, two others do not. One of them is near the start of the execution time and falls between two sample points. The other is at the very end of the execution time and occurs after the last sample point."}

So how big is the peak memory consumption of our process *really*? Luckily, the Linux kernel keeps track of this for us, if Slurm is configured to use the so-called "cgroups v2" mechanism to enforce resource limits (which many HPC systems are). Let's use this system to find out how much memory the raytracer actually needs. First, we set the memory limit back to 1 GB, i.e., to a configuration that is known to work.

```bash
#SBATCH --mem=1G
```

Next, add these lines at the end of your job script:

```bash
echo -n "Total amount of memory used (in bytes): "
CGROUPPATH="$(cat /proc/self/cgroup | awk -F ':' '{print $3}')"
cat /sys/fs/cgroup/${CGROUPPATH}/memory.peak
```

Let's break down what each line does:

- The first line prints out a nice label for our peak memory output. We use `-n` to omit the usual newline that `echo` adds at the end of its output.
- For the next part we need the so-called "cgroup path" of our job. To find out this path, we can use the `/proc/self/cgroup` file, which contains this path as the third entry of a colon-separated list. Therefore, we read the contents of this file (`cat`) and extract the third entry of the colon-separated list (`awk -F ':' '{print $3}'`). Since we do this in `$(...)`, Bash will place the output of these commands (i.e., the cgroup path) in the variable `CGROUPPATH`.
- The third line outputs the contents of a file (`cat`). The path of this file starts with `/sys/fs/cgroup`, which is a location where the Linux kernel exports all the cgroups v2 information as files, followed by the cgroup path of our job in the `CGROUPPATH` variable.
- The final part of the path is the information we actually want from the cgroup. In our case, we are interested in `memory.peak`, which contains the peak memory consumption of the cgroup.

When you submit your job and look at the output once it finishes, you will find a line like this:

```output
[...]
Total amount of memory used (in bytes): 579346432
[...]
```

So even though Slurm reported our job to only use 367.28 MB of memory, we actually used nearly 600 MB! With this measurement we can make an informed decision on how to set the memory limit for our job:

```bash
#SBATCH --mem=700M
```

Run your job again with this limit to verify that it completes successfully.

::: instructor

# Todo: Can we demonstrate the callout below?

How can too tight memory limits in Slurm + cgroupsv2 cause cache thrashing?

:::

::: callout
# Too tight memory limits can reduce performance!

Slurm enforces memory limits for all processes in a job.
Besides the applications memory demand (RSS - resident set size), this also includes caching mechanism of the Linux Kernel, e.g. for file I/O.

Too tight memory limits can cause too small caches next to the applications memory demand.
This in turn can severely reduce the jobs performance in some cases.

:::

::: instructor

At this point you might want to point out to your audience that for certain applications it can be disastrous for performance to set the memory constraint too tightly. The reason is that the memory limit enforced by Slurm does not only affect the resident set size of all the processes in the job allocation, but also the memory used for caching (e.g., file pages). If the allocation runs out of memory for the cache, it will have to evict memory pages to disk, which can cause I/O operations and new memory allocations to block for longer than usual. If the application makes heavy use of this cache (e.g., repeated read and/or write operations on the same file) and the memory pressure in the allocation is high, you can even run into a *cache thrashing* situation, where the job spends the majority of its time swapping data in and out of system memory and thus slows down to a crawl.

:::

### Sizing your jobs: CPU Cores

So far we have tuned the time and memory limits of our job. Now let us have a look at the CPU core limit.

This limit works slightly differently than the ones we looked at so far in the sense that your job is not getting terminated if you try to use more cores than you have allocated. Instead, the scheduler exploits the fact that multitasking operating systems can switch out the process a given CPU core is working on. If you have more active processes in your job than you have CPU cores (i.e., *CPU oversubscription*), the operating system will simply switch processes in and out while trying to ensure that each process gets an equal amount of CPU time. This happens very fast, so you can't see the switching directly, but tools like `top` will show your processes running at less than 100% CPU utilization.

Below you can see a situation of four processes running on three CPU cores, which results in each process running only 75% of the time.

![](fig/cpu-oversubscription.svg){alt="Depicted is a situation of four processes running on three CPU cores, which results in each process running only 75% of the time."}

::: caution

CPU oversubscription can be harmful to performance as switching between processes by the operating system can cost a significant amount of CPU time itself.

:::

Let's try reducing the number of cores we allocate by reducing the number of MPI tasks we request in our job script:

```bash
#SBATCH --ntasks=2
```

Now we have a mismatch between the number of tasks we request and the number of tasks we use in `mpirun`. However, MPI catches our folly and prevents us from accidentally oversubscribing our CPU cores. In the output file you see the full explanation

```output
There are not enough slots available in the system to satisfy the 4
slots that were requested by the application:

  ./SnowmanRaytracer/build/raytracer

Either request fewer procs for your application, or make more slots
available for use.

A "slot" is the PRRTE term for an allocatable unit where we can
launch a process.  The number of slots available are defined by the
environment in which PRRTE processes are run:

  1. Hostfile, via "slots=N" clauses (N defaults to number of
     processor cores if not provided)
  2. The --host command line parameter, via a ":N" suffix on the
     hostname (N defaults to 1 if not provided)
  3. Resource manager (e.g., Slurm, PBS/Torque, LSF, etc.)
  4. If none of a hostfile, the --host command line parameter, or an
     RM is present, PRRTE defaults to the number of processor cores

In all the above cases, if you want PRRTE to default to the number
of hardware threads instead of the number of processor cores, use the
--use-hwthread-cpus option.

Alternatively, you can use the --map-by :OVERSUBSCRIBE option to ignore the
number of available slots when deciding the number of processes to
launch.
```

::: instructor

This error message was generated with OpenMPI. Other MPI implementations might produce different messages.

:::

If we actually want to see oversubscription in action, we need to switch from MPI to multithreading. First, let us try without oversubscribing the CPU cores:

```bash
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

# [...]

./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=4 -alloc_mode=3 -png=snowman.png
```

We use the output of `seff` as a baseline for our multithreaded job:

```output
[...]
CPU Utilized: 00:21:32
CPU Efficiency: 99.08% of 00:21:44 core-walltime
Job Wall-clock time: 00:05:26
Memory Utilized: 90.85 MB
Memory Efficiency: 12.11% of 750.00 MB
```

::: challenge

Compare our measurements for 4 threads here to the measurements we made for doing the computation with 4 MPI tasks earlier.
What metrics are similar and which ones are different? Do you have an explanation for this?

:::

::: solution

We can see that the CPU utilization time and the walltime are virtually identical to the MPI version of our job, while the memory utilization is much lower.
The exact reasons for this will be discussed in the following episodes, but here is the gist of it:

- Our job is strongly *compute-bound*, i.e., the time our job takes is mostly determined by how fast the CPU can do its calculations.
  This is why it does not matter much for CPU utilization whether we use MPI or threads as long as both can keep the same number of CPU cores busy.
- MPI typically incurs an overhead in CPU usage and memory due to the need to communicate between the tasks (in comparison, threads can share a block of memory without communication).
  In our raytracer, this overhead for CPU usage is negligible (hence the same CPU utilization time metrics), but there is a significant memory overhead.

:::

Now let's see what happens when we oversubscribe our CPU by doubling the number of threads without increasing the number of allocated cores in our job script:

```bash
./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=8 -alloc_mode=3 -png=snowman.png
```

::: challenge

If your cluster allows direct access to the compute nodes, try logging into the node your job is running on and watch the CPU utilization live using

```bash
top -u <your username>
```

If your cluster does not allow logging into the compute node directly you may still be able to get an
interactive shell on a compute node where your job is running using `srun`

```bash
srun --overlap --jobid <jobid of your job> --pty bash
```

or in case of a multinode job

```bash
srun --overlap --jobid <jobid of your job> --nodelist=<nodeid> --pty bash
```

Once you have a shell on the compute node you can use `top` as shown above.

Compare the CPU utilization of the `raytracter` threads with different total numbers of threads.

In the top right of `top` you can also see a metric called *load average*. Simplified, this is the number of processes / threads that are currently either running or could run if a CPU core was free. Compare the amount of load you generate with your job depending on the number of threads.

:::

::: solution

You can see that the CPU utilization of each `raytracer` thread goes down as the number of threads increases. This means, each process is only active for a fraction of the total compute time as the operating system switches between threads.

For the load metric, you can see that the load increases linearly with the number of threads **regardless if they are actually running or waiting for a CPU core**.
Load is a fairly common metric to be monitored by cluster administrators, so if you cause excessive load by CPU oversubscription you will probably hear from your local admin.

:::

Despite using twice the amount of threads, we barely see any difference in the output of `seff`:

```output
CPU Utilized: 00:21:29
CPU Efficiency: 98.85% of 00:21:44 core-walltime
Job Wall-clock time: 00:05:26
Memory Utilized: 93.32 MB
Memory Efficiency: 12.44% of 750.00 MB
```

This shows that despite having more threads, the CPU cores are not performing more work. Instead, the operating system periodically rotates the threads running on each allocated core, making sure every thread gets a time slice to make progress.

Let's see what happens when we increase the thread count to extreme levels:

```bash
./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=1024 -alloc_mode=3 -png=snowman.png
```

With this setting, `seff` yields

```output
CPU Utilized: 00:26:45
CPU Efficiency: 99.07% of 00:27:00 core-walltime
Job Wall-clock time: 00:06:45
Memory Utilized: 113.29 MB
Memory Efficiency: 15.11% of 750.00 MB
```

As we can see, our job is actually getting slowed down from all the switching between threads. This means, that for our raytracer application CPU oversubscription is either pointless or actively harmful regarding performance.

::: discussion

Can you imagine a situation where CPU oversubscription might be sensible (perhaps also outside the HPC context)?

:::

::: solution

On HPC we often have a *CPU bound* application, i.e., the work done by the CPU is the limiting factor and thus dividing this work into smaller chunks does not help with performance.

However, there are also applications bound by other resources. For these applications it makes sense to assign the CPU core elsewhere while the process is waiting, e.g., on a storage medium.

Also, on many systems it is desirable to have more programs running than your computer has CPU cores since often only a few of them are active at the same time.
One common example is your everyday computer with multiple programs running at the same time.

:::

## Multi-node jobs

So far, we have only used a single node for our job. The big advantage of MPI as a parallelism scheme is the fact that not all MPI tasks need to run on the same node.
Let's try this with our Snowman raytracer example:

```bash
#!/bin/bash
#SBATCH --nodes=2
#SBATCH --partition=<put your partition here>
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=700M
#SBATCH --time=00:07:00
#SBATCH --output=snowman-stdout.log
#SBATCH --job-name=snowman

# Always a good idea to purge modules first to start with a clean module environment
module purge
# <put the module load commands for your cluster here>

mpirun -- ./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=1 -alloc_mode=3 -png=snowman.png

echo -n "Total amount of memory used (in bytes): "
CGROUPPATH="$(cat /proc/self/cgroup | awk -F ':' '{print $3}')"
cat /sys/fs/cgroup/${CGROUPPATH}/memory.peak
```

The important change here compared to the MPI jobs before is the `--nodes=2` directive, which instructs Slurm to distribute the 4 tasks across exactly two nodes.

::: callout

# Slurm accepts ranges

You can also leave the decision of how many nodes to use up to Slurm by specifying a minimum and a maximum number of nodes, e.g.,

```
--nodes=1-3
```

would mean that Slurm can assign your job either one, two or three nodes. It gives you the maximum
number of nodes that match the range and become available first. For example, if five nodes become available
you'll get three, if two nodes become available you'll get two, if one node becomes available you'll get one.

:::


Let's look at the `seff` report of our job once again:

```output
[...]
Nodes: 2
Cores per node: 2
CPU Utilized: 00:21:32
CPU Efficiency: 98.78% of 00:21:48 core-walltime
Job Wall-clock time: 00:05:27
Memory Utilized: 280.80 MB
Memory Efficiency: 20.06% of 1.37 GB
```

We can see that Slurm did indeed split up the job such that each of the two nodes is running two tasks. We can also see that the walltime and CPU time of our job are basically the same as before.
Considering the fact that communication between nodes is usually much slower than communication within a node, this result is surprising at first.
However, we can find an explanation in the way our raytracer works. Most of the compute time is spent on tracing light rays through the scene for each pixel.
Since these light rays are independent from one another, there is no need to communicate between the MPI tasks.
Only at the very end, when the final image is assembled from the samples calculated by each task, there is some MPI communication happening. The overall communication overhead is therefore vanishingly small.

::: callout

How well your program makes use of a larger number of nodes depends strongly on the amount of communication in your program.

:::

We can also look at the memory consumption:

```output
[...]
Total amount of memory used (in bytes): 464834560
[...]
```

As we can see, there was indeed less memory consumed on the node running our submit script compared to before (470 MB vs 580 MB).
However, our method of measuring peak memory consumption does not account for the second node. So let’s reach deeper into the toolbox to find out how much memory we actually use.

:::::::::: challenge
# Adapt a job script so it will work well with a node range

If we want to give SLURM some flexibility to schedule jobs on different numbers of nodes
we can do that specifying, for example, `--nodes=1-4`. But now we don't know how many
nodes we are going to get. It can be any number of between 1 and 4. What changes do
you need to make to your job script to make this work?

Assume that the initial job script was
```bash
#!/bin/bash
#SBATCH --nodes=2
#SBATCH --partition=<put your partition here>
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=700M
#SBATCH --time=00:07:00
#SBATCH --output=snowman-stdout.log
#SBATCH --job-name=snowman

# Always a good idea to purge modules first to start with a clean module environment
module purge
# <put the module load commands for your cluster here>

mpirun -- ./SnowmanRaytracer/build/raytracer -width=768 -height=768 -spp=256 -threads=1 -alloc_mode=3 -png=snowman.png

echo -n "Total amount of memory used (in bytes): "
CGROUPPATH="$(cat /proc/self/cgroup | awk -F ':' '{print $3}')"
cat /sys/fs/cgroup/${CGROUPPATH}/memory.peak
```
::::::::::::::::::::
:::::::::: solution
As we don't know how many nodes we'll get but we could run 4 tasks on a node
in prior jobs, it would be rather restrictive to fix the number of tasks at 4.
Instead we could request 4 tasks per node using `--tasks-per-node=4` instead
of `--ntasks=4`. So that the number of tasks adapts to the number of nodes we
are given.

The memory requirement would likely also change with the number of nodes, but here
we only have two options. We can use either `--mem` to request the amount of memory
per node, or `--mem-per-core`. Which one is best depends on the implementation of
the code. In a distributed data code every task only has part of the data and the
size of that part would decrease with the number of tasks. Using `--mem` would be
best in that case even though it would not adapt to the number of tasks.

In a replicated data code every task has a full copy of the data, and only the compute
is shared between the tasks. In that case `--mem-per-core` is the best to use.
::::::::::::::::::::


## Tips for job submission

To end this lesson, we discuss some tips for choosing resource allocations such that your jobs get scheduled more quickly.

- Many clusters have activated the so-called *backfill scheduler* option in Slurm. This mechanism tries to squeeze low priority jobs in the gaps between jobs of higher priority (as long as the larger jobs are not delayed by this). In this case, smaller jobs are generally advantageous as they can "skip ahead" in the queue and start early.
- Using `sinfo -t idle` you can specifically search for partitions that have idle nodes. Consider using these partitions for your job if possible as an idle node will typically start your job immediately.
- Different partitions might have different *billing weights*, i.e., they might use different factors to determine the "cost" of your calculation, which is subtracted from your compute budget or fairshare score. You can check these weights using `scontrol show partition <partitionname> | grep TRESBillingWeights`. The idea behind different billing weights is to even out the cost of the different resources (i.e., how many hours of memory use correspond to one hour of CPU use) and to ensure that using more expensive hardware carries an appropriate cost for the users.
- Typically, it takes longer for a large slot to free up than it takes for several small slots to open. Splitting your job across multiple nodes might not be the most computationally efficient way to run it due to the possible communication overhead, but it can be more efficient in terms of scheduling.

::: keypoints

- Your cluster might seem to have an enormous amout of computing resources, but these resources are a shared good. You should only use as much as you need.
- Resource requests are a promise to the scheduler to not use more than a specific amount of resources. If you break your promise to the scheduler and try to use more resources, terrible things will happen.
  - Overstepping memory or time allocations will result in your job being terminated.
  - Oversubscribing CPU cores will at best do nothing and at worst diminish performance.
- Finding the minimal resource requirements takes a bit of trial and error. Slurm collects a lot of useful metrics to aid you in this.

:::

