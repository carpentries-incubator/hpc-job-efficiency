---
title: "Introduction"
teaching: 60
exercises: 60
---

:::::::::::::::::::::::::::::::::::::: questions

- What exactly is job efficiency in the computing world?
- Why would I care about job efficiency and what are potential pitfalls?
- If I want to work efficiently how much can I ask for?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to:

- Explain what job efficiency is.
- Use `sinfo` and `sreport` to characterise the cluster being used.
- Identify how implementation choices affect runtime, resource usage, and numerical results.
- Explain how inefficient jobs affect resource consumption and energy usage.

::::::::::::::::::::::::::::::::::::::::::::::::

<!--
Prerequisite: Bash https://swcarpentry.github.io/shell-novice/05-loop.html
-->

:::::::::::::::::::::::::: instructor
## Intention: Step into the narrative

Set up narrative:

- Important upcoming conference presentation
- Time is ticking, the deadline is approaching way too fast
- The talk is almost done, but, critically, we're missing a picture for the title slide
- It should contain three snowmen, and we've exhausted our credits for all generative AI models in previous chats with colleagues
- => Ray tracing a scene to the rescue!
- Issue: we need to try many different iterations of the scene to find the exact right picture. How can we maximise the number of raytraced snowman images before our conference deadline?
- Ray tracing is expensive, but luckily we have access to an HPC system
- We could get this done but we have to work efficiently.

Ask learners: "What is efficiency and why should you care about efficiency?"

After the answers, address the learners with efficient jobs, they can attain/achieve:
- shorter turnaround time
- lower resource consumption
- lower allocation usage
- more scientific iterations
- lower energy consumption

::::::::::::::


:::::::::::::::::::: instructor

**This needs to go somewhere further down.**

What we're doing here:

- Find out what we can expect from the HPC system
- How big is the system in numbers of nodes?
- How full is the system with waiting jobs?
- How much memory does the system have?
- What partitions are there and how large are they?

:::::::::::::::::::::::::::::::::::::


<!---the ratio of the useful work performed by a machine or in a process to the total energy expended or heat taken in
     (note this definition was developed for steam engines, which is a historically interesting footnote but quite
      the departure from the subject matter of this course).
-->

## Background

According to Oxford English Dictionary, *[efficiency](https://doi.org/10.1093/OED/5627316442)*
is "*[t]he ratio of the useful work performed by a machine  [...] to the total energy input [...].*"

<!---Oxford English Dictionary, “efficiency (n.), sense 3.b,” September 2026,
     https://doi.org/10.1093/OED/5627316442.
-->

In a *High-Performance Computing* (*HPC*) context, **the useful work** corresponds
to the scientific computations performed by an application. Efficient execution
therefore means making effective use of allocated computational resources such
as CPU cores, memory, GPUs, storage systems, and interconnect bandwidth, while
also minimizing runtime and energy consumption. Or, phrased more bluntly, we
want to avoid running large HPC systems for *nothing but hot air*.

::::::::: spoiler
### Historical note on efficiency
The full definition of *efficiency* from the Oxford English Dictionary is:
*The ratio of the useful work performed by a machine or device to the total energy input or heat consumed*.
The "heat consumed" part of the
definition is a bit curious when thinking about computing, as computers
produce waste heat rather than consuming any heat. This phrase becomes understandable
when realizing that the term *efficiency* was first defined in 1855 in the context of
developing steam engines. Previously, the term *[duty](https://doi.org/10.4236/ahs.2023.122004)*
was used instead by James Watt starting as early as 1763.
:::::::::::::::::

At first glance, a single inefficient job may seem to have little impact
on overall power consumption of an HPC system, since such systems operate
continuously anyway. Nevertheless, an HPC system is a shared resource and
inefficient usage has knock on effects for all users.
In HPC systems, users influence overall system efficiency through
the way they configure, execute, and optimize their workloads.
Throughout this lesson, we will build intuition about resource
utilization and start to approach performance optimization.

## Efficiency as in not wasting your time waiting

As stated above an HPC system is a resource that you share with other users.
How you setup your jobs has an impact on how long you have to wait for your
turn to run them. The system might be able to slot a small job in very quickly,
but a really big calculation will have to wait until a significant portion of
the machine becomes available. But what is *small* and what is *big*? The answer
is: It depends...

- on the scale of the machine,
- on the number of users you are sharing it with,
- on the kind of jobs that users typically run.

To get an idea of the scale of the resource we are using we can use the `sinfo`
command.

```bash
sinfo -O PartitionName,Nodes,CPUs,Memory,Gres,Time
```

```output
PARTITION           NODES               CPUS                MEMORY              GRES                TIMELIMIT
normal              223                 36                  95000+              (null)              1-00:00:00
long                90                  36                  192000              (null)              7-00:00:00
express             6                   36                  95000+              (null)              2:00:00
zen4                46                  192                 763758+             (null)              2-00:00:00
gpuexpress          1                   32                  240000              gpu:rtx2080:7       12:00:00
gpu4090             8                   32                  360448              gpu:rtx4090:6       7-00:00:00
gpuh200             4                   128                 1547843             gpu:h200:8          7-00:00:00
```

:::::::: spoiler
### `sinfo` is part of SLURM
The `sinfo` command is a component of the [SLURM](https://link.springer.com/chapter/10.1007/10968987_3) scheduler.
The scheduler is a tool that lets you submit jobs, maintains a list of waiting jobs, and allocates resources to
run jobs. In addition the scheduler keeps a database of jobs that have been submitted or run, what resources
they have used, and whether they were successful or not. Other useful SLURM commands include `salloc`, `sacct`,
`sbatch`, `seff`, and `srun`. These commands will be introduced later. As SLURM was specifically designed for
Linux clusters (the "L" in SLURM stands for "Linux") and distributed under the GNU General Public License
it is often used on HPC systems in the academic community.
::::::::::::::::

In the output, we see the name of each partition, the number of nodes in this partition,
the number of CPU cores per node, the amount of memory per node in Mebibytes, the number
of *generic resources* (typically GPUs) per node and finally the maximum amount of time
any job is allowed to take.

::::::: callout
### Available partitions depend on the HPC system
Partitions often represent usage policies and you should read your clusters documentation
about their names, underlying hardware, potential access restrictions, and so on. Even if
the cluster documentation does not explicitly state what kind of jobs a particular
partition is for you can make an educated guess based on the partition name and the
node characteristics.

Some examples:

- A partition with the name `long` is typically intended for long running jobs,
  whereas `express` is intended for short jobs you want to get through quickly.
- A partition with a high number of cores and large amounts of memory per node
  is ideally suited for shared memory jobs.
- A partition with lots of nodes that each have a (relatively) small number of
  cores and memory is more suited for distributed memory jobs (typically using
  MPI).
- A partition with powerful GPUs, but only a small amount of CPU cores is
  suitable for jobs where the majority of the work is offloaded to the GPUs.
- A partition with GPUs, many CPU cores and substantial amounts of memory
  is suited for hybrid jobs.

Note that on some clusters you have to state which partition of the machine
you want your job to run on. On other machines the scheduler might select
a default partition based on the resources you request.
:::::::::::::::

Whereas the `sinfo` command gives you access to information on a partition
basis, you can also get information about the particular node you are on.
Normally that node will be a login node, but when used in a job script these
commands can give you information on specific nodes.

```bash
lscpu | grep "^CPU(s):"
lscpu | grep "Thread(s) per core:"
```
```output
CPU(s):                               192
Thread(s) per core:                   1
```

If `lscpu` is not available on your machine, you can also use
``` bash
cat /proc/cpuinfo | grep "core id" | wc -l
```
``` output
192
```

::::::::: caution
### lscpu and cpuinfo may report "funny" core counts
The `lscpu` command lists the "Thread(s) per core" as 1. It also lists the
number of CPUs as 192 which is correct. With processors that support
hyperthreading though, you might get that the "Thread(s) per core" is listed
as 2, and you would notice that the number of CPUs gets reported as twice
the number of physical cores.

On such systems `/proc/cpuinfo` would also show twice as many cores as there
are physical cores. In `/proc/cpuinfo` there is no indication that the
processor supports hyperthreading and the number of cores reported is
twice the real number of cores. With `/proc/cpuinfo` you simply have to know
whether the processor you have supports hyperthreading or not.

This means that when you use `lscpu` or `/proc/cpuinfo` you have to be
careful as they might report something else than what you expect. Therefore
it is probably better to stick with `sinfo`. In addition `sinfo` reports
the configuration that the scheduler uses to manage the resources. If you
want to predict how the scheduler will manage the job you are about to
submit then going by the information it uses is better anyway.
:::::::::::::::::

Given the number of cores per node (36) and the number of nodes in the system
(223) you can calculate the number of cores in the cluster. In this case that
comes to about 8028 cores in total, which is substantially higher than the number of
cores in your local machine or any of the login nodes on the cluster.

Another key parameter is the memory in the machine. To see how much memory is
available on the node you are on you can use

```bash
cat /proc/meminfo | grep "MemTotal"
```
```output
MemTotal:       395695636 kB
```

This amount of memory comes to about 396 GB per node, at 223 nodes in the cluster that
means that there is about 88308 GB of memory in aggregate. Again this is a huge amount
of memory compared to what you will have on your desktop.

As you have to share these resources with other users on the machine you might want
to know how big your share is on average. For that you need to know how many users
there are in total on the machine. The `sreport` command can help with this.
For example you might run

```bash
sreport --noheader cluster AccountUtilizationByUser start=1/1/26 end=7/1/26 Format=Cluster,Login | sort -k 2 -u | wc -l
```
```output
98
```

This command uses the scheduler database to extract the usage information of the first half
of 2026 and count the number of users that ran jobs on the cluster during that time.
This information can be used as an estimate for the current number of people who are
using the machine.

Also note that this command might count the usage on multiple clusters. This happens
for example if one scheduler manages the jobs for multiple clusters. In that case
you could select data for a specific cluster either by selecting the cluster as an argument
to `sreport`, alternatively you could add a `| grep <clustername>` command before
the `sort` command.

On some systems `sreport` may be configured for privacy reasons to only give you
information about your own usage. In that case the command won't give you any
useful information about the total number of users. As an alternative approach
you could try counting the number of home directories on the cluster.

```bash
find /home -maxdepth 1 -mindepth 1 -type d | wc -l
```
```output
700
```

:::::: caution

### Home directories may be organised differently on different machines

On some clusters, home directories are not placed directly in `/home`, but are split
up into subdirectories first (e.g., by first letter of the username like `/home/s/someuser`).
In this case, you have to use `-maxdepth 2 -mindepth 2` to count the contents of these
subdirectories. If your cluster does not use `/home` for the users' home directories,
you might have to use a different path (check `dirname "$HOME"` for a clue). Also, this
command only gives an upper limit to the number of real cluster users as there might be
home directories for service users as well.

Finally, some clusters have been setup with an automounter. On such systems the home directories
of a user are only present if the user is logged on to the system, or if the user currently has
a job running on the system. In that case counting the home directories that are present will
give you a poor estimate of the number of users.

::::::::::::::

On some clusters trying to count the number of home directories is not a suitable
approach to getting an idea of the number of users. In that case you might want to check if the
cluster uses the "[hpc-workspace](https://github.com/holgerBerger/hpc-workspace)" tool to
manage project directories. If it does you can locate where those project directories are stored.
Then you can count all users who currently have project directories with

```bash
ls /lustre/scratch | sed -E 's/^([^_-]*).*$/\1/g' | sort -u | wc -l
```
```output
79
```

Note, not every user needs to have a project directory to use the cluster, but if they
don't have one then they are going to be limited by the file quota on their home
directory as to how much data they can store. So serious users should be using workspaces
if they are available.

::::::: challenge

### What is your average share of resources?

For the cluster you are on collect the number of nodes and cores for a partition
of interest. Also collect the amount of memory per node, and estimate the number
of users you have to share the machine with. To get an idea of how many resources
you should be able to use on average, calculate the number of nodes per user,
the number of cores per user, and the amount of memory per user.

:::::::::::::::::

::::::: solution

Based on the information listed above we have collected the following data

| Property | Amount   | Avg. per user |
| -------- | -------- | ------------- |
| Users    | 100      | 1             |
| Nodes    | 223      | 2,2           |
| Cores    | 8028     | 80            |
| Memory   | 88308 GB | 883 GB        |

Note that these numbers are averages. Almost no user will use these resources
sustained over a long period of time. In practice users will run jobs some of
the time that use more resources. Nevertheless, these average resources are
likely substantially higher than what you have on your desktop, and if you
ask for your average share then your job should start relatively quickly.

::::::::::::::::

Above we have established an idea of the resources available to us on
average. In practice, reality can be quite a bit different from average.
So, to target a machine in it's current state we would like to have
a more detailed view of it's actual state. Fortunately `sinfo` can provide
considerably more details then we have looked at sofar. In particular we
can get more information on the state of the machine with

```bash
sinfo -O Partition,CPUsState:40,NodeAIOT:40
```
```output
PARTITION           CPUS(A/I/O/T)                           NODES(A/I/O/T)
STD-l-12h           25408/800/1120/27328                    234/0/10/244
STD-m-48h           25408/800/1120/27328                    234/0/10/244
STD-s-96h*          25408/800/1120/27328                    234/0/10/244
HIM-l-12h           5981/179/0/6160                         55/0/0/55
HIM-m-48h           5981/179/0/6160                         55/0/0/55
HIM-s-96h           5981/179/0/6160                         55/0/0/55
SHM-l-24h           1344/0/112/1456                         12/0/1/13
SHM-s-96h           1344/0/112/1456                         12/0/1/13
GPU-big             1180/612/224/2016                       12/4/2/18
```

::::::::::: spoiler
### Specifying the column width
When running `sinfo` on large clusters the information it provides
might not fit in the default column width. At that point `sinfo` will
just truncate the column contents which may render the data useless.
To avoid this issue you can specify the width of the columns with
the "\<fieldname\>:\<width\>" notation. In the example shown above the
width of the `CPUsState` and `NodeAIOT` columns is set to 40
characters.
:::::::::::::::::::

In the table that `sinfo` produced the states of the CPUs and nodes are
indicated with 4 letters, "A", "I", "O", and "T" meaning:

- A: Allocated - currently running jobs
- I: Idle - free and available to accept jobs
- O: Other - currently unavailable
- T: Total - basically A + I + O

Note that idle nodes are immediately available for jobs submitted to
the appropriate partition. Nevertheless, even if no nodes are idle
there may be free CPUs. This may occur when users run jobs that don't
use all the cores in a node. If the scheduler allows shared node usage
then you may be able to get hold of these idle cores. Note that users
may request exclusive access to a node in their job script as well
(for example they may have calculations that require all the memory
but that cannot use all the cores). So there is no guarantee that
you can get the idle cores, but with small jobs you might be able to.

So far, we have looked at the scale of the cluster we are using and
what resources we should be able to get on average. We have also
looked at what resources are free right now. If we have a job that we
would like to run that can utilize the free resources then this job
should start almost immediately. In practice this is rarely the case.
Nevertheless, we should be able to get an idea of when a job we have
submitted will run.

For this purpose create a jobscript. In its simplest case we can write
something like
```bash
#!/bin/bash
#SBATCH --job-name=basic001
#SBATCH --nodes=1
#SBATCH --tasks-per-node=112
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=<partition>
srun bash -c "sleep 2; hostname"
```
In addition we create a few more:
```bash
#!/bin/bash
#SBATCH --job-name=basic010
#SBATCH --nodes=10
#SBATCH --tasks-per-node=112
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=<partition>
srun bash -c "sleep 2; hostname"
```
and
```bash
#!/bin/bash
#SBATCH --job-name=basic100
#SBATCH --nodes=100
#SBATCH --tasks-per-node=112
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4gb
#SBATCH --partition=<partition>
srun bash -c "sleep 2; hostname"
```
Then we submit these jobs
```bash
$ sbatch basic100.sh; sbatch basic010.sh; sbatch basic001.sh
Submitted batch job 958810
Submitted batch job 958811
Submitted batch job 958812
```
Now we have submitted a bunch of jobs of different sizes, but when will they run?
We can use the `squeue` command to ask the scheduler when it estimates these jobs
will start. To do this we run

```bash
squeue --start -j 958810,958811,958812
```
```output
             JOBID PARTITION     NAME     USER ST          START_TIME  NODES SCHEDNODES           NODELIST(REASON)
            958812 STD-s-96h basic001  userxxx PD 2026-10-06T20:59:44      1 ndshm007             (Priority)
            958811 STD-s-96h basic010  userxxx PD 2026-10-07T06:52:49     10 ndhim[014,016],ndshm (Priority)
            958810 STD-l-12h basic100  userxxx PD 2026-10-10T16:22:44    100 (null)               (Nodes required for job are DOWN, DRAINED or reserved for jobs in higher priority partitions)
```
The `squeue` command was run at approximately 2026-10-06T18:40:00. So we see that dependent on
the size of the job we may have to wait 2 hours, 12 hours, or even 4 days for the job to start,
with the wait getting longer with increasing job size.

:::::::: challenge
### Establish the wait on the cluster you're on
The waiting times shown above were established on a cluster that you probably don't
have access to, at a random time in the past. Can you establish what the current
waiting times are on the cluster you're on? Remember, you just need to get the
estimated starting time for the jobs. They don't need to actually run, so
don't forget to cancel the jobs once you have those estimated times.

For extra credit answer the question why you should cancel the jobs? After all
the jobs won't run more than 2 seconds so how bad can it be to run a 2 second
job on 100 nodes?
::::::::::::::::::
::::::::: solution
The answer to the bonus question is that in order for the cluster to run the
100 node job, there have to be 100 free nodes at the same time. That means
that the scheduler has to hold other jobs back until 100 nodes are free.
So when the last node is still running the 99 other nodes will be waiting
for it to finish what it is doing. This waiting time is going to be orders
of magnitude larger than the cost of running this job.
::::::::::::::::::

The scheduler can fit jobs in dependent on the job size in terms of nodes.
Likewise it will take the length of the job into account. This is reasonable
from the perspective that if you want to run a 10 minute long job then waiting
an hour for the job to start is a long time, whereas if you want to run a job
that lasts 4 days then it doesn't matter so much if it takes an hour before
it starts.

In this light we can perform a similar experiment as before. For example,
we might reserve 2 nodes but for jobs of 10 minutes, 1 hour, 10 hours,
and 96 hours. After submitting these jobs we might ask what the expected
starting time is. To get a reference time we use `date` before the
`squeue` command quering the estimated starting times.
The output that was obtained with this experiment was
```output
Thu Oct 22 06:36:40 PM CEST 2026
             JOBID PARTITION     NAME     USER ST          START_TIME  NODES SCHEDNODES           NODELIST(REASON)
            971369 STD-s-96h basic10m  userxxx PD 2026-10-22T23:18:46      2 ndhim[020,022]       (Priority)
            971370 STD-s-96h  basic1h  userxxx PD 2026-10-22T23:18:46      2 ndhim[023-024]       (Priority)
            971371 STD-s-96h basic10h  userxxx PD 2026-10-22T23:20:47      2 ndstd[168-169]       (Priority)
            971372 STD-s-96h basic96h  userxxx PD 2026-10-22T23:20:47      2 ndstd[170-171]       (Priority)
```
The output shows that the longest two jobs are expected to have to wait an additional
two hours. In this case that doesn't seem to matter much as the expected wait time is 5 hours.
Using the `date` command in the job we can also see when the job
actually ran (because we asked for only 2 nodes the time wasted
waiting for the last node to drain is not too bad). In any case
the conclusion is that providing accurate job time estimates
will help getting your jobs run sooner. Of course, be
careful not to be too tight with you estimates to avoid
having your jobs getting killed because they took a bit
longer than expected. Adding a buffer of about 10%
seems reasonable.

::::::::::::::: challenge
# How does the start time depend on job length on your cluster?

Can you create a few jobs of different lengths and
see how the estimated job start time depends on the
length of the job on the cluster you are currently on?
:::::::::::::::::::::::::
:::::::::::::::: solution
Create a number of jobs with different job lengths.
For example 10 minutes, 1 hour, 10 hours, 100 hours,
similarly to what waa done above. Select a small number
of nodes, 1 or 2 should be fine. Submit all jobs at
the same time and run `squeue --start -j <jobids>`
to get the estimated starting times.
:::::::::::::::::::::::::

The last dimension we can test is the amount of memory our jobs need.
For that we will request a quarter of the cores of a single node, for
a run time of 30 minutes. This means that if a node is partially
occupied with a job our job could share the node if there is enough
memory left. Requesting 1, 2, 4, 8, and 16 GB per core we get:
```output
```

::::::::::::::: challenge
# How does the start time depend on the amount of memory requested on your cluster?

Can you create a few jobs of different memory requests and
see how the estimated job start time depends on the
memory usage of the job on the cluster you are currently on?
:::::::::::::::::::::::::
:::::::::::::::: solution
Create a number of jobs with different memory requests.
For example 1 GB, 2 GB, 4 GB, etc. per core.
Select a small number
of nodes, 1 or 2 should be fine. Submit all jobs at
the same time and run `squeue --start -j <jobids>`
to get the estimated starting times.
:::::::::::::::::::::::::

:::::::::: keypoints
- Your cluster might seem to have an enormous amount of computing resources, but these resources are a shared good.
  - You should only use as much as you need.
  - The larger the share you request the longer your job has to wait before it starts.
- `sinfo` gets you information about how large your cluster is.
- `sreport` can provide information about the number of users actively using the cluster.
- `sbatch` lets you submit jobs.
- `squeue --start` provides estimated start times for your jobs.
::::::::::::::::::::
