---
title: "Pinning"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions 

- What is "pinning" of job resources?
- How can pinning improve the performance?
- How can I see, if pinning resources would help?
- What requirement hints can I give to the scheduler?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to …

- Define the concept of "pinning" and how it can affect job performance.
- Name Slurms options for memory- and cpu- binding.
- Use hints to tell Slurm how to optimize their job allocation.

::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## Intention: Go deeper in performance and hardware relationship

Narrative:

- We have already seen how to observe resource utilization and identify inefficient use of hardware resources.
- One way to improve resource utilization is to control where processes and threads are placed.
- How does the mapping of work to CPUs and memory regions affect performance?

What we're doing here:

- Introduce pinning and slurm affinity options
- Relate to hardware effects
- A few practical tricks to diagnose and understand poor process placement.

:::::::::::::::::::::::::::::::::::::


## The benchmark code used in this episode
Let us first prepare a so-called benchmark for doing some pinning experiments in this episode.
In a HPC context, a benchmark is a software that implements and runs CPU- and memory-intensive computations
in a well-measurable way. Many different benchmarks exist. Here, we employ the STREAM benchmark, because
it is deliberately designed to mimic computations that are memory-bandwidth limited.

The STREAM benchmark may already be available on your system. Check the `module` environment. If not, it can be installed with:
```bash
# download, it is only a single C-program
wget https://www.cs.virginia.edu/stream/FTP/Code/stream.c
# compile, may need appropriate module to make gcc available, enable OpenMP
gcc -O3 -fopenmp -DSTREAM_ARRAY_SIZE=100000000 -DNTIMES=20 stream.c -o stream
```
This creates the executable `stream`.

### Running `stream`
To get aquainted with the output of `stream`, run it:
```bash
./stream
```
An sample output is:
```output
-------------------------------------------------------------
STREAM version $Revision: 5.10 $
-------------------------------------------------------------
This system uses 8 bytes per array element.
-------------------------------------------------------------
Array size = 100000000 (elements), Offset = 0 (elements)
Memory per array = 762.9 MiB (= 0.7 GiB).
Total memory required = 2288.8 MiB (= 2.2 GiB).
Each kernel will be executed 20 times.
 The *best* time for each kernel (excluding the first iteration)
 will be used to compute the reported bandwidth.
-------------------------------------------------------------
Number of Threads requested = 192
Number of Threads counted = 192
-------------------------------------------------------------
Your clock granularity/precision appears to be 1 microseconds.
Each test below will take on the order of 12271 microseconds.
   (= 12271 clock ticks)
Increase the size of the arrays if this shows that
you are not getting at least 20 clock ticks per test.
-------------------------------------------------------------
WARNING -- The above is only a rough guideline.
For best results, please be sure you know the
precision of your system timer.
-------------------------------------------------------------
Function    Best Rate MB/s  Avg time     Min time     Max time
Copy:          179291.6     0.014355     0.008924     0.019452
Scale:         184755.8     0.013567     0.008660     0.015317
Add:           175990.9     0.015244     0.013637     0.016602
Triad:         172339.1     0.015706     0.013926     0.020396
-------------------------------------------------------------
Solution Validates: avg error less than 1.000000e-13 on all three arrays
-------------------------------------------------------------
```

### Understanding the output
The benchmark reports the achieved memory bandwidth for four simple operations:
```input
Copy:   a[i] = b[i]
Scale:  a[i] = q * b[i]
Add:    a[i] = b[i] + c[i]
Triad:  a[i] = b[i] + q * c[i]
```
These are operations that make up the main work in numerical codes when they loop over large arrays. Improving code efficiency
involves minimizing the overhead associated with accessing the memory of such large arrays during computations. This is where pinning (or binding) will come into play later in this episode.
The reported Best Rate (MB/s) is the highest sustained memory bandwidth achieved for each operation.

The first notable metric is the "Number of Threads" (requested and counted, here 192).
This should appear given that `stream` was compiled with OpenMP (`-fopenmp`). We will treat threads in more detail soon.
The other output of interest is the bandwidth in MB/s reported at the bottom
for the four types of array operations, copy, scale, add and triad. The higher the bandwidth, the faster
these array operations can complete.

## Setting up the HPC kitchen: CPUs, processes, threads, tasks
We first want to agree on some terminology. This is motivated by the fact that in HPC the same words can mean slightly different things depending on
whether you are talking about the operating system, the scheduler (Slurm), or in the context of a parallel programming model (MPI or OpenMP).
While this episode is called "Pinning", you will notice that many pinning-related command options contain the string "bind", also in Slurm. Hence, we will also use the synonym "Binding" in the following.

### What is a CPU in a pinning/binding context?
Let us clarify some potential confusion around the word "CPU", as it is somewhat overloaded.
Hardware vendors often use "CPU" to mean the whole processor chip. That chip contains multiple independent execution units:

- A **core** is the *physical* execution unit on the chip — the actual hardware that runs instructions.
- A **thread** is the *logical* execution unit exposed by a core. If simultaneous multithreading (SMT) is off, one core provides exactly one thread, so the two are the same thing. If SMT is on, one physical core provides two (or more) threads, each independently schedulable.

This physical-vs-logical distinction matters because the number of logical execution units (threads) can be larger than the number of physical cores actually present.

In Linux and Slurm, CPU refers to a thread - logical execution unit - not the physical processor chip. And:

- We will use quite a few Slurm commands below. Slurm command options often contain "cpu", for example `--cpus-per-task`.
This is because a CPU in Slurm is: 1 logical execution unit = 1 *Slurm-CPU*.
- A Slurm-CPU is a schedulable execution unit visible to the operating system.
- In general: 1 Slurm-CPU = 1 physical CPU core, but not always, sometimes with SMT enabled: 2 or more Slurm-CPUs constitute 1 physical CPU core.
- The Slurm option `--cpus-per-task` determines how many threads Slurm allocates.

:::::::::::::::::::::::::: spoiler
Historically, CPU refers to the *physical processor chip*. For example, a compute
node might have two *CPU sockets* (two processor chips). If each socket hosts 32 physical cores, we have:  
```
2 physical CPUs (sockets) = 2 x 32 cores = 64 cores = 64 Slurm-CPUs
```
However, the physical CPU hardware can pretend to have more cores than physically present. This is called *Simultaneous Multithreading* (SMT), or
*Hyperthreading* for Intel processors. Then,
```
2 physical CPUs (sockets) = 2 x 32 cores x 2 SMT threads = 128 logical CPUs = 128 Slurm-CPUs
```
Therefore, on systems without SMT, a Slurm CPU corresponds to a physical core.
On systems with SMT enabled, multiple logical execution units map onto a physical core. People then also talk about *hardware threads*,
A hardware thread is a feature of the processor that allows a core to execute more than one software thread at a time. With SMT,  
`1 Slurm CPU = 1 hardware thread`, and  
`2 Slurm CPUs = 2 hardware threads = 1 physical core`.  
Be aware that "thread" is another expression being a bit overused.
From now on, we will refer to thread as something only on the software layer. This will be explained below.
::::::::::::::::::::::::::

### Processes
Time to run our `stream` program in an "HPC-way".
We are now on a HPC compute node. You may be on the login node, the landing point when you `ssh`-ed from your own machine.
In case, you cannot run jobs on the login node, you will need to allocate some resources first:
```bash
salloc --ntasks=2 --cpus-per-task=24 --nodes=1 --mem=5G
```
Now we use Slurm's tool `srun` for running parallel jobs. Launch the following two runs:
```bash
# if you did not do the `salloc`: add the option `--mem=4G` after each `srun`.
srun --ntasks=1 ./stream
srun --ntasks=2 ./stream
```
In the first run, the operating system creates one *process* which will be associated with `stream`.
This process is an isolated entity as it does not directly share the following things with other processes:

- virtual memory,
- process ID (PID),
- file descriptors.

Think of a process resembling a large kitchen. This kitchen has its own ingredients, utensils, recipes and storage space.
Other kitchens do not have direct access to it.

When running the second job with `--ntasks=2`, Slurm commissioned two such kitchens. Again, they work independently. Therefore you
see the `stream` output twice.

::::::::::::: challenge
### Multiple tasks
When running `srun --ntasks=2 ./stream`, you may have noticed differing outputs for the two bandwidth summaries
(copy, scale, add ,triad). Why are these not identical?

:::: hint
As in the kitchen analogy, the two tasks (kitchens) run independently, that is, they do not even know about each other.
::::

:::: solution
The two `stream` tasks denote two independent processes that may also occupy different (Slurm-)CPU resources.
Hence, with multiple CPUs, their runtimes and bandwidth outcomes will never be exactly identical. 
::::
:::::::::::::

### Tasks
In the above `srun` commands, Slurm uses the options `--ntasks`, and not something like `--nprocesses`. 
A *task* is Slurm's term for an independent unit of work that the scheduler starts, places on resources and manages. In most cases: **1 task = 1 process**.

Back to the kitchen analogy. Imagine the `stream` computing job would be a catering order.
Then, Slurm would be the event manager. It manages the resources you requested, which may be one (`--ntasks=1)` or two (`--ntasks=2`) kitchens.

:::::::::::::::::::::::::: spoiler
Slurm uses the term "task" because it is a scheduler concept rather than an operating-system concept.
While in most HPC applications, one task corresponds to one process, Slurm is more general by treating a task as something overarching a process,
some kind of workload to be scheduled onto (Slurm-)CPUs.
In other words, the Slurm scheduler doesn't manage kitchens directly. Instead, it acts as the event manager making sure the workload runs
on the available resources requested via `--ntasks`, and other options.
::::::::::::::::::::::::::

Now, what about the cooks working in a kitchen? One kitchen can employ one or multiple cooks, in other words, a process can have one or more threads.  

### Threads
Threads live inside a process and

- share the same memory (kitchen storage space),
- can access the same variables (ingredients and utensils),
- execute concurrently (multiple cooks working simultaneously).

A thread is also referred to as an *execution stream* within a process that shares memory with other threads in the same process.
So the threads are like the cooks being busy in the same kitchen. They can

- share the ingredients,
- share the utensils,
- can cooperate.

Threads may sometimes get in each other's way, unless they are told not to move around the kitchen by "pinning" them to their work area.
We will get to that.

So let's assign four CPUs to one task:
```bash
srun --ntasks=1 --cpus-per-task=4 ./stream
```
where now the output for "Number of Threads" will most likely show the number 4.
The `stream` runtime is programmed such that it detects four available CPUs and therefore creates four threads by default.

## Multiple cooks: OpenMP

In case you want to try again, put `time` in front of every `srun` and check the parallel against the sum of the sequential runtimes.

The `stream` program is an OpenMP-parallel program. The large loops of array operations are distributed over OpenMP-threads.
The thread number can be set via the environment variable `OMP_NUM_THREADS`:
```bash
export OMP_NUM_THREADS=4
srun --ntasks=1 ./stream
```

:::::::::::::::::::::::::: spoiler
The Slurm option `--cpus-per-task` determines how many CPUs Slurm allocates, while `OMP_NUM_THREADS` determines how many
OpenMP threads the application creates.
Slurm does not automatically force OpenMP to obey `--cpus-per-task`. Therefore, users should normally set
```bash
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
```
after setting CPUs/task via Slurm directives.
This sets `number of OpenMP threads = number of CPUs`. Otherwise, ending up with `number of OpenMP threads > number of CPUs`
would involve an oversubscription of the allocated CPUs.
::::::::::::::::::::::::::

::::::::::::: challenge
### Understanding `OMP_NUM_THREADS`
When you do
```bash
export OMP_NUM_THREADS=4
srun --ntasks=1 --cpus-per-task=3 ./stream
```
what is the actual count `stream` reports under "Number of Threads".

:::: hint
Remember that `stream` is an OpenMP-parallel program.
::::

:::: solution
The count is likely reported as `Number of Threads counted = 4`.
Since `stream` is an OpenMP-parallel program, setting `OMP_NUM_THREADS=4` will be evaluated inside the program.
However, Slurm only allocated 3 CPUs via `--cpus-per-task=3`, which is fine but will oversubscribe the CPU resources.
::::
:::::::::::::

::::::::::::: challenge
### Understanding `OMP_NUM_THREADS` more
In case you did the previous challenge, now run this:
```bash
srun --ntasks=1 --cpus-per-task=3 ./stream
```
What is the actual count reported under "Number of Threads"?

:::: hint
In the previous challenge you set `OMP_NUM_THREADS`. What happened to it?
::::

:::: solution
Your earlier setting `export OMP_NUM_THREADS=4` is still active, unless you have changed the terminal.
Hence, the count is still reported as `Number of Threads counted = 4`.
If you do
```bash
unset OMP_NUM_THREADS
srun --ntasks=1 --cpus-per-task=3 ./stream
```
this will indeed produce `Number of Threads counted = 3`.
::::
:::::::::::::

## Multiple kitchens: MPI
Before, we assigned multiple threads to one process, that is, we put four cooks into one kitchen.
Now suppose, the catering job is so large that one 4-cook kitchen is not enough. This leads to the MPI programming model.
Assume the workload requires running two independent kitchens. In fact, we have already done this:
```bash
unset OMP_NUM_THREADS # reset in order to undo earlier settings
srun --ntasks=2 ./stream

```
where each task is a separate MPI process. MPI-parallel programs involve data exchange between processes (or Slurm tasks).
Note that `stream` it is not programmed to have this feature. However, like every program,
it can be run as multiple independent process instances.

## Multiple cooks + kitchens: OpenMP + MPI
Parallel programs can also combine the OpenMP and MPI models, sometimes referred to as a hybrid model.
So let's now run such a hybrid "2-kitchens, 4-cooks-per-kitchen" job:
```bash
srun --ntasks=2 --cpus-per-task=4 ./stream
```
This will involve a total of 8 CPUs.

::::::::::::: challenge
### Requesting resources for a hybrid parallel program
You want to request resources for a hybrid OpenMP - MPI parallel program.
The estimated workload consists of two processes where each process itself involves three threads.
What are the two options submitting an `srun` command for this?

:::: hint
Remember that a process is almost always equivalent to a Slurm task. Also, OpenMP uses the environment
variable `OMP_NUM_THREADS` to set the thread count. 
::::

:::: solution
```bash
# Option 1)
srun --ntasks=2 --cpus-per-task=3 ./stream
# Option 2)
export OMP_NUM_THREADS=3
srun --ntasks=2 ./stream
```
::::
:::::::::::::


<<<<<<< HEAD
## Managing the kitchen: The Linux scheduler
By now, we have gained some decent understanding about tasks and threads and how they make up a parallel run.
So we are almost ready to see how to control CPU alignment in parallel runs via pinning.
There is one more thing useful to know about. 

In our kitchen analogy, we referred to Slurm as the event manager, who takes care of the whole catering job without
getting involved with the cooks (CPUs) inside the kitchen(s). However, on the lower kitchen level,
there is actually another manager. This is
the Linux scheduler. Similar to rotating cooks around the kitchen's different workstations, where a workstation equates a (Slurm-)CPU,
the Linux scheduler may migrate threads between CPUs during execution. 

Thread migration happens by default because Linux is designed to optimize overall system responsiveness and throughput,
not necessarily the performance of a single process.

:::::::::::::::::::::::::: spoiler
How can we observe thread migration?
Let's first create another version of our benchmark. This is a version that will run a bit longer:
```bash
gcc -O3 -fopenmp -DSTREAM_ARRAY_SIZE=100000000 -DNTIMES=100 stream.c -o stream_long
```
Now open a second terminal on the same compute node where you have been running `stream` and type
```bash
srun --pty --overlap --jobid=<id> /bin/bash
watch -n 0.5 'ps -eLo pid,tid,psr,comm | grep stream_long
```
The `watch` command keeps an eye on repeated calls to `ps` which then greps for running `stream` processes.
Back in the original terminal, employ 12 CPUs by running the new version, `stream_long`:
```bash
srun --pty --overlap --jobid=<id> /bin/bash
export OMP_NUM_THREADS=12
./stream_long
```
Now, observe the 12 processes showing up in the second terminal. The numbers in the third column are likely to
change occasionally. The manpage of `ps` refers to that number as the "processor that process is currently assigned to",
which in our context is the CPU number. Threads are being moved around when it changes.
::::::::::::::::::::::::::

To optimize a selected process entails removing the overhead due to its moving threads.
This requires extra directives to keep the cooks at their workstations, so they don't bump into each other, that is, to pin or bind them.

## Binding 1: CPU affinity
Pinning, or binding, is the assignment of processes or threads to specific CPU resources so that the operating system does not freely move them between CPUs.
This is also called CPU affinity. In the run
```bash
unset OMP_NUM_THREADS # reset in order to undo earlier settings
srun --ntasks=1 --cpus-per-task=3 --cpu-bind=cores ./stream
```
the option `--cpu-bind=cores` binds a task and its threads to the Slurm CPUs allocated to it.
On systems without SMT/Hyperthreading, these CPUs correspond to physical cores.
For example, suppose the above run allocated CPUs 48-50.
Then Slurm will create an *affinity mask* like: `Allowed CPUs = {48,49,50}` for that task.
=======
## Motivation
:::::::::::::::::::::::::: challenge
## Exercise 
Case 1: 1 thread per rank
`mpirun -n 8 ./raytracer -width=512 -height=512 -spp=128 -threads=1 -alloc_mode=3 -png=snowman.png`

Case 2: 2 thread per rank
`mpirun -n 8 ./raytracer -width=512 -height=512 -spp=128 -threads=2 -alloc_mode=3 -png=snowman.png`

Questions:
- Do you notice any difference in runtime between the two cases?
- Is the increase in threads providing a speedup as expected?

::::: solution
- Observation: The computation times are almost the same.
- Expected behavior: Increasing threads should ideally reduce runtime.
- Hypothesis: Additional threads do not contribute.
::::::::::::::
::::::::::::::::::::::::::::::::::::

## How to investigate?

You can verify the actual core usage in two ways:
1. Use `--report-bindings` with `mpirun`
2. Use `htop`command on the compute node

:::::::::::::::::::::::::: instructor
## Note: Login to the compute job

This is cluster specific. It can possibly be  done in two ways:
1. `srun --pty --overlap --jobid=<jobid> /bin/bash`
2. Check on which node job runs and login to the node via SSH
:::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::: challenge
### Can be removed
## Exercise
Follow any one of the option above and run for 2 threads per rank
`mpirun -n 8 ./raytracer -width=512 -height=512 -spp=128 -threads=2 -alloc_mode=3 -png=snowman.png`

Questions:
- Did you find any justification for the hypothesis we made?

::::: solution
Only 8 cores are active instead of 16
::::::::::::::
::::::::::::::::::::::::::::::::::::

Explanation:

- Eventhough we requested 2 threads per MPI rank, both threads are pinned to the same core.
- The second thread waits for the first thread to finish, so no actual thread-level parallelization is achieved.

:::::::::::::::::::::::::: instructor
## TODO: Show an animation
- current behavior with overlapping threads on the same core.
- Expected behavior when threads are pinned to separate cores.
:::::::::::::::::::::::::::::::::::::

## How to achieve?
## Exercise: Understanding Process and Thread Binding

Pinning (or binding) means locking a process or thread to a specific hardware resource such as a CPU core, socket, or NUMA region. Without pinning, the operating system may move tasks between cores, which can reduce cache reuse and increase memory latency, directly diminishes performance.

In this exercise we will explore how MPI process and thread binding works. We will try binding to **core**, **socket**, and **numa**, and observe timings and bindings.

:::::::::::::::::::::::::: instructor
## Note
- This exercise assumes the following hardware setup:  
  - Dual-socket system (2 sockets, 48 cores per socket, 8 NUMA regions, 96 cores total).  
  - Each MPI process can use multiple threads (`-threads`) for parallel execution.
- The idea is to **demonstrate oversubscription** by giving more MPI processes than available sockets or NUMA regions, or by over-allocating threads per domain.  
- You are free to adjust `-n` and `-threads` based on your cluster.
:::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::: challenge
### Can be removed
## Exercise
Case 1: `--bind-to numa`
`mpirun -n 8 --bind-to numa ./raytracer -width=512 -height=512 -spp=128 -threads=12 -alloc_mode=3 -png=snowman.png`

Case 2: `--bind-to socket`
`mpirun -n 4 --bind-to socket /raytracer -width=512 -height=512 -spp=128 -threads=48 -alloc_mode=3 -png=snowman.png`

Questions:
- What is difference between Case 1 and Case 2. Any difference in performance? How many workers?
- How could you adjust process/thread counts to better utilize the hardware in Case 2?

::::: solution
- MPI and thread pinning is hardware-aware.
- If the number of processes matches the number of domains (socket or NUMA), then the number of threads should equal the cores per domain to fully utilize the node.
- No speedup in Case 2: Oversubscription occurs because we requested 4 processes on a system with only 2 sockets.
- Threads compete for the same cores → OpenMPI queues threads and waits until other processes finish.
::::::::::::::
::::::::::::::::::::::::::::::::::::

## Best Practices for MPI Process and Thread Pinning

### Difference between Binding and Mapping

**Mapping** is about distributing MPI ranks across hardware hierarchy which tells where your processes will be placed.

**Binding* is locking your MPI processes/threads to a specific resource which prevents from moving it around from one to another.

## Mapping vs. Binding Analogy

Think of running MPI processes and threads like booking seats for a group of friends:

- **Mapping** is like planning where your group will sit in the theatre or on a flight.  
  - Example: You decide some friends sit in Economy, some in Premium Economy, and some in Business.  
  - Similarly, `--map-by` distributes MPI ranks across nodes, sockets, or NUMA regions.

- **Binding** is like reserving the exact seats for each friend in the planned area.  
  - Example: Once the seating area is chosen, you assign specific seat numbers to each friend.  
  - Similarly, `--bind-to` pins each MPI process or thread to a specific core or hardware unit to avoid movement.

This analogy helps illustrate why **mapping defines placement** and **binding enforces it**.

We will use `--bind-to core` (the smallest hardware unit) and `--map-by` to distribute MPI processes across sockets or NUMA or node regions efficiently.

### Choosing the Smallest Hardware Unit

Binding processes to the smallest unit (core) is recommended because:

1. **Exclusive use of resources**  
   Each process or thread is pinned to its own core, preventing multiple threads or processes from competing for the same CPU.

2. **Predictable performance**  
   When processes share cores, execution times can fluctuate due to scheduling conflicts. Binding to cores ensures consistent timing across runs.


- Best practice: Always bind processes to the smallest unit (core) and spread processes evenly across the available hardware using `--map-by`.
- Example options:
  - `--bind-to core` → binds each process to a dedicated core (avoids oversubscription).  
  - `--map-by socket:PE=<threads>` → spreads given number of threads as a processing element across the socket
  - `--map-by numa:PE=<threads>` → spreads processes across NUMA domains, assigning `<threads>` cores per process.
  - similarly `--map-by numa:PE=<threads>`
  - `--cpus-per-rank <n>`→ Assigns `<n>` cores (hardware threads) to each MPI rank - ensuring that all threads within a rank occupy separate cores.

:::::::::::::::::::::::::: challenge
## Exercise
Use the given best practices above for case 1: `-n 8`, `-threads=1` and case 2: `-n 8`, `-threads=4` and answer following questions

Questions:
- How many cores does the both jobs use?
- Did you get more workers than you requested?
- Did you see the scaling when running with 4 threads?

::::: solution
- 8 and 32
- No.
- Yes
::::::::::::::
::::::::::::::::::::::::::::::::::::  
>>>>>>> origin/pinning


::::::::::::: challenge
### Displaying information about the CPU architecture: `lscpu`
The command `lscpu` gathers CPU architecture information. Give it a try and see how many CPUs are reported.
The end of the output will show something about "NUMA".
Can you figure out the number of NUMA nodes on your system? Any idea what this is?

<<<<<<< HEAD
:::: hint
`lscpu` will first report the CPU architecture, then number of CPUs.
You will see that CPUs are grouped into "NUMA nodes".
::::

:::: solution
An example output of `lscpu` is as follows (some output truncated):
```output
Architecture:                x86_64
  CPU op-mode(s):            32-bit, 64-bit
  Address sizes:             46 bits physical, 57 bits virtual
  Byte Order:                Little Endian
CPU(s):                      192
  On-line CPU(s) list:       0-191
Vendor ID:                   AuthenticAMD
  Model name:                AMD EPYC 9654 96-Core Processor
    CPU family:              25
    Model:                   17
    Thread(s) per core:      1
    Core(s) per socket:      96
    Socket(s):               2
[ ... text truncated ... ]
NUMA:                        
  NUMA node(s):              8
  NUMA node0 CPU(s):         0-23
  NUMA node1 CPU(s):         24-47
[ ... text truncated ... ]
  NUMA node7 CPU(s):         168-191
```
Here, the CPU architecture consists of two sockets with 96 physical cores per socket, totaling 192 CPUs.
We further see 8 NUMA nodes, each listing CPU ranges. NUMA nodes appear to be some regions dividing the CPUs into groups with 24 consecutive CPU numbers.
So these NUMA regions seem to resemble something like "areas of jurisdiction" over the CPU entirety.
::::
:::::::::::::

## Non-Uniform Memory Access (NUMA)
*Non-Uniform Memory Access* (NUMA) is a computer memory design used in multiprocessor systems. Memory access time depends on where the memory is located relative to the accessing processor.
In a NUMA system, the architecture is divided into multiple regions called *NUMA nodes*.
A single compute node can contain several NUMA nodes.
Each NUMA node contains one or more cores  along with the portion of the system's memory that is *local* to it - meaning that CPU can access it faster than memory attached to a different NUMA node. 
Memory isn't exclusive to a NUMA node, though: a core  can still access another NUMA node's memory, just at higher latency and/or lower bandwidth, which is precisely what makes access "non-uniform" rather than a fixed cost regardless of location.

Your personal laptop may have only one node, while a HPC system is likely to have more.

## Binding 2: Memory affinity
On NUMA systems, memory attached to nearby CPUs can be accessed faster than memory from distant CPUs.
Moreoever, when a thread repeatedly runs on the same CPU, data already stored in the CPU's cache can be reused.
On the other hand, if the operating system moves the thread to another CPU, some of that advantage due to *data locality* may be lost.
Therefore, CPU affinity goes hand in hand with *memory affinity* to keep computation and data close together.
The run
```bash
srun --ntasks=1 --cpus-per-task=3 --mem-bind=local ./stream
```
tries to allocate memory close to the CPUs running the task, that is, within the NUMA node of those CPUs.
In such a context, people also talk about minimizing memory access *latency*.

:::::::::::::::::::::::::: spoiler
Latency in computing refers to the time delay between the initiation of an action and the resulting output or response.
Therefore, it represents a "wait time", rather than the speed of a data transfer (bandwidth).
Latency is measured in milliseconds or microseconds, while bandwidth is measured in bits per second.

+--------------------+------------------------------+-----------------+
| Performance metric | Meaning                      | Measured in     |
+--------------------+------------------------------+-----------------+
| latency            | wait time                    | ms, $\mu$s      |
+--------------------+------------------------------+-----------------+
| bandwidth          | maximum rate of data transer | bps, Mbps, Gbps |
+--------------------+------------------------------+-----------------+
::::::::::::::::::::::::::

## Before pinning, understand Slurm's configuration
The CPU/memory-binding behaviour is not the same across different HPC systems.
For example, the `srun` documentation cautions that the `--mem-bind` option is "used only when the task/affinity plugin is enabled
and the NUMA memory functions are available." Further it says, "Note that the resolution of CPU and memory binding may differ on some architectures."
It is thus recommended to determine the specific configuration of your system via a self-reporting run:
```bash
srun --ntasks=2 --cpus-per-task=4 --cpu-bind=verbose,none --mem-bind=verbose,none ./stream
```
where Slurm's output (omitting the `stream` output) may be:
```output
cpu-bind=MASK - computenode14032, task  0  0 [447219]: mask 0x3fffc0000000000 set
cpu-bind=MASK - computenode14032, task  1  1 [447220]: mask 0x3fffc0000000000 set
mem-bind=NONE - computenode14032, task  0  0 [447219]: mask 0xff
mem-bind=NONE - computenode14032, task  1  1 [447220]: mask 0xff
```
In this output, the first two lines correspond to the CPU masks. The mask essentially shows which CPUs a task is allowed to use.
No need to decrypt the hexadecimal output after "mask" for now.
The fact that these masks are identical for both tasks, here `0x3fffc0000000000`, indicates that
both tasks were allowed to **run on the same set of CPUs**.
 
The memory binding information in the last two lines shows which NUMA nodes are available for memory allocation.
Here, the output `mem-bind=NONE` shows that memory allocation was unrestricted across all NUMA nodes.

Now try with CPU-binding enabled:
```bash
srun --ntasks=2 --cpus-per-task=4 --cpu-bind=verbose,cores ./stream
```
telling Slurm to try to give **each task its own set of cores**.
Most likely, you will then see different mask codes, like in our example:
```output
cpu-bind=MASK - computenode14032, task  0  0 [460428]: mask 0x3c0000000000 set
cpu-bind=MASK - computenode14032, task  1  1 [460429]: mask 0x3c00000000000 set
```
which is what we wanted.

Finally, let's make this cryptical mask output human-readable:
```bash
srun --ntasks=2 --cpus-per-task=8 --cpu-bind=verbose,cores \
     bash -c 'grep Cpus_allowed_list /proc/self/status'
```
Voilà
```output
cpu-bind=MASK - computenode14032, task  0  0 [459142]: mask 0x3fc0000000000 set
cpu-bind=MASK - computenode14032, task  1  1 [459143]: mask 0x3fc000000000000 set
Cpus_allowed_list:	42-49
Cpus_allowed_list:	50-57
```
Now we can see how the different masks correspond to non-overlapping CPU sets.

Probing Slurm's default behaviour will help understand what to expect when enforcing CPU/memory binding.

## Giving Slurm a hint
You can advise Slurm to bind tasks according to application hints. Let's look at two hint types that are closely
related to CPU- and memory-binding:

```bash
srun --ntasks=1 --cpus-per-task=4 --hint=compute_bound ./stream
```
The option `--hint=compute_bound` tells Slurm that the application is expected to spend most of its time performing computations.

```bash
srun --ntasks=1 --cpus-per-task=4 --hint=memory_bound ./stream
```
The option `--hint=memory_bound` tells Slurm that the application is expected to spend much of its time moving data between memory and CPUs.

Again, the exact behavior of `--hint` will be site-dependent.
Some clusters may ignore certain hints, while others use them to influence CPU placement and affinity settings.

Moreover, while hints provide guidance to the scheduler, they do not guarantee a particular placement.
On some systems, the default placement may already be well suited to the application, resulting in no observable performance difference.

Investigate your system by cross-comparing the above two runs against a third one without hints:
```bash
srun --ntasks=1 --cpus-per-task=4 ./stream
```

:::::::::::::::::::::::::: spoiler
On most HPC systems, the default Slurm configuration already keeps tasks reasonably close to their memory.
Therefore, there may be only little performance difference between the default execution and runs
that use CPU/memory binding explicitly or via hints.
::::::::::::::::::::::::::


## Controlling NUMA: `numactl`
NUMA nodes are interconnected, allowing CPUs to access both their own memory and that from other nodes. The tool `numactl` can alter the
default memory-access behavior of the Linux scheduler. This can be useful for studying the potential benefit of binding before
launching production runs.

You can get an overview over the NUMA nodes of the machine where you run:
```bash
numactl --hardware
```
This shows the whole node inventory, adding some details to the earlier `lscpu` output. On an 8-node architecture, it could look like this:
```output
available: 8 nodes (0-7)
node 0 cpus: 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
node 0 size: 192453 MB
node 0 free: 176208 MB
node 1 cpus: 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47
node 1 size: 193529 MB
node 1 free: 186718 MB
[ ... text truncated ... ]
node 7 cpus: 168 169 170 171 172 173 174 175 176 177 178 179 180 181 182 183 184 185 186 187 188 189 190 191
node 7 size: 193421 MB
node 7 free: 173933 MB
node distances:
node     0    1    2    3    4    5    6    7 
   0:   10   12   12   12   32   32   32   32 
   1:   12   10   12   12   32   32   32   32 
   2:   12   12   10   12   32   32   32   32 
   3:   12   12   12   10   32   32   32   32 
   4:   32   32   32   32   10   12   12   12 
   5:   32   32   32   32   12   10   12   12 
   6:   32   32   32   32   12   12   10   12 
   7:   32   32   32   32   12   12   12   10 
```
One can see the assignment of the total of 192 CPUs to 8 nodes, in addition to each node's memory available.
The trailing output "node distances" shows a matrix with memory access latency between node pairs.

::::::::::::: spoiler
When you run `numactl --hardware`, the node distance matrix 
lets you select two nodes given by a row-column pair, and find the associated node distance.
Node distance is related to the memory access latency when CPUs of different nodes exchange data.
Staying on the same node has the lowest latency (10 in the above example), which you find on the diagonal of the matrix.
Further, the matrix is symmetric, indicating that on node A, fetching data from node B has the same latency as the reverse way.
:::::::::::::


## Investigating binding via `numactl`
Before executing production runs, it may be useful to investigate potential latencies on your NUMA system.
The tool `numactl` allows for a more fine-grained control because one can
deliberately place computation and memory on different NUMA nodes.

So let's put `stream` to work once more. Placing both CPU and memory on node 0 is done as follows:
```bash
numactl --cpunodebind=0 --membind=0 ./stream
```
The two options `--cpunodebind` and `--membind` are to some degree the counterparts of the
`srun` options `--cpu-bind` and `--mem-bind`.
To be more accurate:

- `--cpunodebind` restricts execution to CPUs belonging to a NUMA node.
- `--membind` allocates memory from a specific NUMA node.

Compare the above run with one where we put the CPUs on a different node:
```bash
numactl --cpunodebind=N --membind=0 ./stream
```
By setting *N*>0, CPUs are placed on nodes away from 0, while memory stays on 0.
Can you see a correlation between increasing *N* and bandwidth?

::::::::::::: challenge
### Observing thread count on NUMA nodes
First and foremost `unset OMP_NUM_THREADS`  
Compare the output for "Number of Threads" between the run
`numactl ./stream` and a corresponding run with CPU-binding to node 0.
You may see a different "Number of Threads". If that is the case, which one is smaller and why?

:::: hint
CPU-binding to node 0 is done using the option `--cpunodebind=0`.
::::

:::: solution
CPU-binding to node 0, without worrying about memory-binding, is done via
```bash
numactl --cpunodebind=0 ./stream
```
Generally, the thread count is the number of (logical) CPUs available to the process.  

- First run, without binding, `numactl ./stream`: This will involve all CPUs available to the process, which may encompass multiple nodes.
- Second run, with binding, `numactl --cpunodebind=0 ./stream`: This will restrict to the CPUs of node 0.  

In most cases, when your system has multiple (NUMA) nodes, the binding call will report a smaller
count because fewer CPUs are accessible.
::::
:::::::::::::


::::::::::::: challenge
### Test different memory placement
Figure out the NUMA node number *N* which is farthest away from node 0 and perform two `numactl` runs
with different memory placement. 
Let each run use 4 threads. Also, measure the runtime of the two runs.
What do you observe in terms of performance and how would you explain differences?

:::: hint
The most distant node *N* probably corresponds to the maximum node number. 
Either `lscpu` or `numactl --hardware` report node numbers.
::::

:::: solution
Assuming that *N*=7, launch one run on node 0 and the second on node 7.
```bash
export OMP_NUM_THREADS=4
time numactl --cpunodebind=0 --membind=0 ./stream
time numactl --cpunodebind=7 --membind=0 ./stream
```
The most likely outcome is that the second run will exhibit a smaller bandwidth as well as
a longer runtime. The reason is memory access lateny, which increaes when computation and data storage happen on
different nodes. 
::::
:::::::::::::

We have gained some overview over Slurm's binding options as well as the kinds of lateny studies that can be
performed using `numactl`. Note that many more parameters exist for controlling binding behaviour. 
The optimal parameter set depends on your application and the employed HPC system.

:::::::::::::::::::::::::::::::::::::: keypoints
- A Slurm-CPU is a schedulable execution unit visible to the operating system.
- A process usually equates a Slurm task and involves $\ge 1$ (Slurm-)CPUs.
- OpenMP threads are software threads created by an application.
  - It is common to run one OpenMP-thread per CPU.
- Pinning, or binding, is to keep computation and data close together in order to improve performance through minimized latencies.
  - The CPU- and memory-binding options of `srun` control resource allocation and placement of Slurm jobs.
  - `srun --cpu-bind ...` controls where Slurm runs tasks, i.e., where computation runs.
  - `srun --mem-bind ...` controls where Slurm allocates memory, i.e., where data is allocated.
- The benefit of CPU and memory placement strongly depends on the application, cluster configuration and hardware.
- On NUMA systems, CPU- and memory often go together to keep computation and data close to one another.
- Hints provide guidance to Slurm about the expected characteristics of an application.
  - `srun --hint=compute_bound ...` may be beneficial for applications that require many CPU resources.
  - `srun --hint=memory_bound ...` may be beneficial for applications that are limited by memory bandwidth.
- Memory-intensive applications are often more sensitive to NUMA locality than compute-intensive applications. The `stream` program is such a case.
- `numactl` provides fine-grained control over CPU and memory placement.
::::::::::::::::::::::::::::::::::::::::::::::::

