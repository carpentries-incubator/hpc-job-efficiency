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

- We get the feeling, that hardware has a lot to offer, but the rabbit hole is deep!
- What are the "dimensions" in which we can optimize the throughput of snowman pictures per hour?
- Can we improve how the work maps to certain CPUs / Memory regions?


What we're doing here:

- Introduce pinning and slurm hint options
- Relate to hardware effects
- Use third party performance tools to observe effects!

:::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## ToDo: Extract episode about pinning

Stick to simple options here.
Put more complex options for pinning / hints, etc. into its own episode somewhere later in the course

Pinning is an important part of job optimization, but requires some knowledge, e.g. about the hardware hierarchies in a cluster, NUMA, etc.
So it should be done after we've introduced different performance reports and their perspective on hardware

Maybe point to [JSC pinning simulator](https://apps.fz-juelich.de/jsc/llview/pinning) and have similar diagrams as an independent "offline" version in this course

:::::::::::::::::::::::::::::::::::::

## Setting up the HPC kitchen: CPUs, processes, threads, tasks
In this episode, we will first agree on some terminology. This is motivated by the fact that in HPC the same words can mean slightly different things depending on
whether you are talking about the operating system, the scheduler (Slurm), or in the context of a parallel programming model (MPI or OpenMP).

### CPUs
First, let us clarify some potential confusion around the word "CPU", as it is somewhat overloaded.
Hardware vendors often use it to mean a processor chip, while Linux and Slurm usually use it to mean a logical execution unit.
To emphasize this distinction, this logical execution unit is also called *Slurm-CPU*.

A Slurm-CPU is a schedulable execution unit. In general, one such unit corresponds to one physical CPU core, the latter being an independent execution engine on the processor chip.

Note that in Slurm documentation, a CPU usually means Slurm-CPU. Slurm-CPU is also referred to as a logical CPU visible to the operating system.
The distinction between logical and physical comes into play because the number of logical CPUs does not always match the number of given physical CPU cores. 

For now, remember whenever you see "cpus" in Slurm directives, for example `#SBATCH --cpus-per-task=4`, Slurm-CPUs are meant.
Also throughout this episode, CPU will refer to Slurm-CPU.

:::::::::::::::::::::::::: spoiler
Historically, CPU refers to the *physical processor chip*. For example, a compute
node might have two *CPU sockets* (two processor chips). If each socket hosts 32 physical cores, we have:  
```
2 physical CPUs (sockets) = 2 x 32 cores = 64 cores = 64 Slurm-CPUs
```
However, the physical CPU hardware can pretend to have more cores than physically present. This is called *Simultaneous Multithreading* (SMT), or
*Hyperthreading* for Intel CPUs. Then,
```
2 physical CPUs (sockets) = 2 x 32 cores x 2 SMT threads = 128 logical CPUs = 128 Slurm-CPUs
```
To summarize, on systems without SMT, a Slurm CPU corresponds to a physical core.
On systems with SMT enabled, more than one logical CPUs map onto a physical core. In the SMT context, the expression *hardware thread* is also used.
A hardware thread is a feature of the processor that allows a core to execute more than one software thread at a time. With SMT,  
`1 Slurm CPU = 1 hardware thread`, and  
`2 Slurm CPUs = 2 hardware threads = 1 physical core`.  
Note that "thread" is yet another expression being a bit overused.
Hence, be advised that the upcoming subchapter "Threads" below refers to threading only on the software layer.

<!--
Node
├── CPU (socket)
│   ├── Core
│   │   ├── Hardware thread
│   │   └── Hardware thread
│   ├── Core
│   └── ...
└── CPU (socket)
-->
::::::::::::::::::::::::::

### Processes
Suppose you just happily programmed `myapp.py` and want to run it with `python myapp.py`.
Upon execution, the operating system creates one process which will be associated with `myapp.py`.
This process is an isolated entity as it does not directly share the following three things with other processes:

- virtual memory,
- process ID (PID),
- file descriptors.

Think of a process resembling a large kitchen. This kitchen has its own ingredients, utensils, recipes and storage space.
Other kitchens do not have direct access to it.
Now, what about the cooks working in that kitchen? Our kitchen can employ one or multiple cooks, in other words, a process can have one ore more threads.  

### Threads
Threads live inside a process and

- share the same memory (kitchen storage space),
- can access the same variables (ingredients and utensils),
- execute concurrently (multiple cooks working simultaneously).

A thread is also referred to as an execution stream within a process that shares memory with other threads in the same process.
So the threads are like the cooks being busy in the same kitchen. They can

- share the ingredients,
- share the utensils,
- can cooperate.

Important to note, the cooks may sometimes get in each other's way, unless they are told not to move around the kitchen. We will talk about this below
when introducing the pinning concept.

### Tasks
We use the work "task" in the context of the job scheduler, here Slurm. Note that the term can have different meanings in different software packages.
A task is Slurm's term for a unit of work that the scheduler starts and manages. In practice, one task usually corresponds to one process.

In Slurm, starting for example three processes is done via `#SBATCH --ntasks=3`. Back to the analogy, the whole computing job would be a big catering order.
Slurm would be the event manager. It manages the resources you requested, consisting of three kitchens.

:::::::::::::::::::::::::: spoiler
You might wonder why the Slurm option `--ntasks` is not called something like "--nprocesses".
Slurm uses the term "task" because it is a scheduler concept rather than an operating-system concept. A task refers to a unit of work that Slurm launches and manages.
While in most HPC applications, one task corresponds to one process, Slurm is more general by treating a task as something to be scheduled onto (Slurm-)CPUs,
which usually entails a process. In other words, the Slurm scheduler doesn't manage kitchens directly; instead, it acts as the event manager making sure the workload runs
on the available resources requested through `--ntasks`.
::::::::::::::::::::::::::

## Multiple cooks and kitchens: OpenMP and MPI
Setting
```bash
export OMP_NUM_THREADS=4
```
before running a parallel OpenMP program, assigns four threads to one process, that is, we put four cooks into one kitchen.
Now suppose the catering job is so large that one 4-cook kitchen is not enough. This leads to the MPI programming model.
Assume the workload requires three independent kitchens. In Slurm, this translates to
```bash
#SBATCH --ntasks=3
```
where each separate kitchen is a separate MPI process.


Parallel programs can also combine the OpenMP and MPI models. In Slurm, we would set up a multi-kitchen, multi-cook environment like this
```bash
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=4
export OMP_NUM_THREADS=4
```
so four cooks (`--cpus-per-task=4`) work in one kitchen, totaling 12 over all three (`--ntasks=3`) kitchens.
Keep in mind that analogies are imperfect. The main takeaway to remember is:

- A process is an independently running program.
- A thread is an execution stream within a process.
- A task is Slurm's unit of scheduled work, almost always the same as process.

::::::::::::: challenge
### Requesting resources for a parallel program
Assume you want to request resources for a hybrid OpenMP - MPI parallel program.
Your estimated workload consists of 8 processes where each process itself involves 6 threads.
What are the Slurm directives (`#SBATCH ...`) and other environment variable settings to be set?

:::: hint
Remember that a process is almost always equivalent to a Slurm task. Also, OpenMP uses the environment
variable `OMP_NUM_THREADS` to define the thread count. 
::::

:::: solution
```bash
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=6
export OMP_NUM_THREADS=6
```
::::
:::::::::::::

::::::::::::: challenge
### Selecting an optimal process and thread count
You have a job where one wants to render 128 snowmen of the same pixel size. The employed parallel rendering framework
is able to spawn independent instances of the raytracer program. Given the pixel size, the recommendation is
to use 8 execution streams for each raytacer instance.
What are the Slurm directives (`#SBATCH ...`) and other environment variable settings to be set?

:::: hint
Each raytracer instance can be treated as a Slurm task. The number of execution streams within a task is the thread count.
::::

:::: solution
```bash
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=8
export OMP_NUM_THREADS=8
```
::::
:::::::::::::


## Managing the kitchen: The Linux scheduler
In our kitchen analogy, we referred to Slurm as the event manager, who takes care of the whole catering job without
getting involved with any of the cooks inside the kitchen(s). However, there is actually something like a kitchen manager. This is
the Linux scheduler. Similar to rotating cooks around the kitchen's different workstations, where a workstation equates a (Slurm-)CPU,
the Linux scheduler may migrate threads between CPUs during execution. 

Thread migration happens by default because Linux is designed to optimize overall system responsiveness and throughput,
not necessarily the performance of a single HPC application. To optimize a single job then entails removing the overhead due to its moving threads.
This requires extra directives to keep the cooks at their workstations, so they don't bump into others, that is, to pin them.

## Pinning / Binding of CPU resources
Pinning is the assignment of processes or threads to specific CPU resources so that the operating system does not freely move them between CPUs.
When a thread repeatedly runs on the same CPU, data already stored in the CPU's cache can be reused.
If the operating system moves the thread to another CPU, some of that advantage due to *data locality* may be lost.

*... up to here, to be continued ...*



Binding / pinning:

- `--mem-bind=[{quiet|verbose},]<type>`
- `-m, --distribution={*|block|cyclic|arbitrary|plane=<size>}[:{*|block|cyclic|fcyclic}[:{*|block|cyclic|fcyclic}]][,{Pack|NoPack}]`
- `--hint=`: Hints for CPU- (`compute_bound`) and memory-bound (`memory_bound`), but also `multithread`, `nomultithread`
- `--cpu-bind=[{quiet|verbose},]<type>` (`srun`)
- Mapping of application <-> job resources


## Why what how?
B
<!-- EPISODE CONTENT HERE -->


## Summary

:::::::::::::::::::::::::: challenge
## Exercise:
::::::::::::::::::::::::::::::::::::

Leading question: Pinning is very specific, but was it really limiting the performance of out application? How can I identify the biggest issue?

:::::::::::::::::::::::::::::::::::::: keypoints
- C
::::::::::::::::::::::::::::::::::::::::::::::::
