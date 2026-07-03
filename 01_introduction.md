---
title: "Introduction"
teaching: 60
exercises: 60
---

:::::::::::::::::::::::::::::::::::::: questions 

- What exactly is job efficiency in the computing world?
- Why would I care about job efficiency and what are potential pitfalls?
- How can I begin measuring the runtime performance of my programs?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to:

- Use `time` and `date` to measure program runtime.
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

What we're doing here:

- Run workflow example for the first time
- Simple `time` measurement to get started
- Introduce different perspectives on efficiency
- Core-h and correlation to cost in energy/money
- Either set up the first Slurm job here or in the next episode

:::::::::::::::::::::::::::::::::::::

::: instructor

Ask learners: "Why should you care about efficiency?"

After the answers, address the learners with efficient jobs, they can attain/achieve:
- shorter turnaround time
- lower resource consumption
- lower allocation usage
- more scientific iterations
- lower energy consumption

::::::::::::::

<!---the ratio of the useful work performed by a machine or in a process to the total energy expended or heat taken in
-->

## Background

According to Oxford’s English Dictionaries, *efficiency* is "*the ratio of
the useful work performed by a machine [...] to the total energy expended or
heat taken in*".

In a *High-Performance Computing* (*HPC*) context, **the useful work** corresponds
to the scientific computations performed by an application. Efficient execution
therefore means making effective use of allocated computational resources such
as CPU cores, memory, GPUs, storage systems, and interconnect bandwidth, while
also minimizing runtime and energy consumption. Or, phrased more bluntly, we
want to avoid running large HPC systems for *nothing but hot air*.

At first glance, a single inefficient job may seem to have little impact
on overall power consumption of an HPC system, since such systems operate
continuously anyway.
A similar argument could be made about air travel: the airplane will take off
regardless of whether one additional passenger boards the flight.
However, individual behavior still contributes to overall efficiency.
In air travel, passengers can improve fuel efficiency by traveling lightly and
avoiding unnecessary baggage, thereby improving the airplane's ratio
$\frac{useful\;work}{total\;energy\;expended}$.

In HPC systems, users similarly influence overall system efficiency through
the way they configure, execute, and optimize their workloads.
Throughout this lesson, we will examine common inefficiencies in computational
jobs while continuing to use the air-travel analogy to build intuition about
resource utilization and performance optimization.

### Measuring `sleep` with `time`

Let's look at the `sleep` command.

```bash
sleep 2
```

This command pauses execution for a specified duration, here 2 seconds,
before continuing with the next command.
You can verify the pause duration using a stopwatch, here provided by the `time` command:

```bash
time sleep 2
```

which will produce output similar to

```output
real    0m2.002s
user    0m0.001s
sys     0m0.000s
```

The `time` command is often one of the first performance-analysis tools introduced
in HPC.
This command provides a breakdown of elapsed wall-clock time and CPU execution time
consumed by your program.
The `time` command reports three timing measurements: *real*, *user*, and *sys*.

+------+-------------------------------------------------------------------------------+
| Time | Meaning                                                                       |
+------+-------------------------------------------------------------------------------+
| real | Wall-clock time = total runtime as seen on a stopwatch                        | 
+------+-------------------------------------------------------------------------------+
| user | Time spent in *user* mode: application computations such as arithmetic        |
|      | operations, loops, and program logic                                          | 
+------+-------------------------------------------------------------------------------+
| sys  | Time spent in the operating system's *kernel* mode (system calls):            |
|      | I/O = reading/writing files, memory management, and device communication      |
+------+-------------------------------------------------------------------------------+

The `sleep` command performs almost no computations or I/O operations. As a result, the
reported *user* and *sys* times remain close to zero.

:::::::::::::::::::::::::: spoiler

### Shell keyword vs executable: `time` and `/usr/bin/time`

The `time` command exists both as a shell keyword built into the Bash shell and as
a standalone executable, usually residing under `/usr/bin/time`. While they behave similarly,
they are not exactly the same. Shell keywords take precedence during shell command
resolution, including over executables resolved through the user's `PATH`, so preceding
a command with `time` invokes the shell keyword.
Therefore, if you want to explicitly invoke `/usr/bin/time`, you can use

```bash
# Explicitly invoking `/usr/bin/time`
$ /usr/bin/time sleep 2
0.00user 0.00system 0:02.00elapsed 0%CPU (0avgtext+0avgdata 2176maxresident)k
0inputs+0outputs (0major+90minor)pagefaults 0swaps

# Compare the output to the Bash built-in:
$ time sleep 2

real    0m2.003s
user    0m0.001s
sys     0m0.003s

# Yet another example output of `time` in zsh, an alternative shell implementation to Bash
$ time sleep 2
sleep 2  0.00s user 0.00s system 0% cpu 2.003 total
```

Notice the different output formatting.
All tools provide similar insight, but the formatting and exact information may differ.
So, if you saw something that looks different from the Bash built-in command, this may be why!

On HPC systems, different login shells or environment configurations may produce slightly
different `time` output formats. This can become important when runtime information is
parsed automatically in benchmarking or profiling workflows.

### Benchmarking and profiling

Runtime measurements are often collected automatically during performance studies.

- **Benchmarking** measures how application performance changes under different execution
conditions, such as varying the number of CPU cores, nodes, threads, problem sizes, or
hardware configurations.
- **Profiling** collects detailed information about how a program uses computational
resources during execution. This may include where execution time is spent, memory usage,
communication overhead, I/O activity, or other performance-related metrics.

Because such workflows often process timing data automatically, differences in the
output format produced by `time` may require special handling.

Benchmarking and profiling are commonly used to identify performance bottlenecks and
evaluate optimization strategies for HPC applications.

It is also worth noting that shell keyword documentation is invoked via `help <KEYWORD>`,
for example `help time`, while most executables have manual pages, e.g., `man time`.
Finally, you can prefix the command with a backslash to force Bash to invoke the external
executable, so `\time sleep 2` will invoke the external `/usr/bin/time` executable.
::::::::::::::::::::::::::

::: callout

Different HPC systems may provide different default login shells or environment configurations.
You can inspect available shells using:

```bash
$ cat /etc/shells
```

```output
/bin/sh
/bin/bash
/usr/bin/sh
/usr/bin/bash
/usr/bin/tmux
/bin/tmux
/bin/csh
/bin/tcsh
/usr/bin/csh
/usr/bin/tcsh
/bin/ksh
/bin/rksh
/usr/bin/ksh
/usr/bin/rksh
```

To determine your currently active shell, you can use:

```bash
$ echo "$SHELL"
```

```output
/bin/bash
```

:::::::::::

### Time for a `date`

The `date` command, as described in its manual page (`man date`), prints or sets the
system date and time.
It can also be used as a lightweight source of high-resolution timestamps:

```bash
date +%s.%N
```
This reports the current point in time as the number of seconds elapsed since a fixed
reference point.

:::: spoiler
### Epoch time

Such a referenced point in time is commonly referred to as *Epoch time*.
According to the `date` manual page, the default reference point is
`1970-01-01 00:00:00 UTC`, commonly known as the Unix epoch.
::::

The format specifier `%s` prints the elapsed time in seconds since the Unix epoch,
while `%N` appends the fractional nanosecond component.

Running the command multiple times will therefore produce large floating-point numbers
with nanosecond-resolution timestamps, although the actual timer precision depends on
the operating system, kernel, and underlying hardware.

::::::::::::: challenge

### An accurate stopwatch using `date`

You can use the construct `date +%s.%N` on the command line or in a Bash script 
to store start and end timestamps in variables:

```bash
start=$(date +%s.%N)

# ... run some command(s) ...

end=$(date +%s.%N)
```

This effectively creates a simple stopwatch:
you record a start timestamp, execute one or more commands, and then record an end
timestamp. The elapsed runtime can then be computed by subtracting the start time
from the end time.
Try this using the `sleep` command between the two timestamps.

:::: hint
Subtracting floating-point numbers can be done using the `bc` calculator tool:

```bash
echo "$end - $start" | bc -l
```

::::

:::: solution

```bash
#!/usr/bin/env bash

start=$(date +%s.%N)
sleep 2
end=$(date +%s.%N)

echo "$end - $start" | bc -l
```

::::

:::::::::::::

## Part 1: An inefficient job example

::: instructor

Ask learners to run the script with `time` and estimate what it might be doing
before revealing the source code of `sum.bash`.

Guide learners toward identifying where time is spent:
the mathematical calculations themselves or the repeated creation of external processes.

::::::::::::::

After warming up with some basic timing methods, let's analyze the efficiency of
a small script that performs a slightly more demanding workload than the `sleep`
command. Have a look at the following short Bash script.

```bash
#!/usr/bin/env bash

sum=0

for i in $(seq 1 1000)
do
  val=$(echo "e(2 * l(${i}))" | bc -l)
  sum=$(echo "$sum + $val" | bc -l)
done

echo Sum=$sum
```

Copy this into a file called `sum.bash`, or download it directly:

```bash
curl -L -o sum.bash https://raw.githubusercontent.com/carpentries-incubator/hpc-job-efficiency/main/learners/data/sum.bash
```

Then make it executable:

```bash
chmod u+x sum.bash
```

The main part of this shell script is a `for` loop that computes the sum of all
squares $i^2$ over 1000 iterations; note that `seq 1 1000` generates the sequence
$i = 1, 2, 3, \ldots, 1000$. Inside the `for` loop, the `bc` calculator tool is used
to evaluate the mathematical expressions. The first statement inside the loop
(`val=...`) evaluates the expression `e(2 * l(${i}))`, which corresponds to the
mathematical identity $i^2 = e^{2 \cdot \ln(i)}$.
For example, $e^{2 \cdot \ln(3)} = 3^2$, where $\ln$ denotes the natural logarithm.
The second statement inside the loop (`sum=...`) accumulates the computed values
$i^2$ into the variable `sum`, so the final `echo` statement prints the total sum
$\sum_{i=1}^{1000}i^2$.

::::::::::::: challenge

### Identify the inefficient pieces

In the above Bash script, the `for` loop invokes the `bc` calculator twice during
every loop iteration. Compared to more efficient approaches shown later, this
method is relatively slow. Why might that be the case?

:::: hint
Each statement of the form `echo ... | bc -l` launches a new `bc` process through a
pipe and subshell.
::::

:::: solution
The construct `echo ... | bc -l` launches a new `bc` process for every invocation.
In this script, each loop iteration creates two separate `bc` processes.

Process creation, shell expansion, pipe setup, and inter-process communication all
introduce overhead. Since the mathematical computation itself is very small, most
of the total runtime of `sum.bash` is spent managing repeatedly spawned processes
rather than performing useful calculations.
::::

:::::::::::::

The overhead in this shell script is dominated by repeatedly launching external `bc`
processes. Each invocation requires process creation, shell expansion, pipe setup,
and inter-process communication, while the actual mathematical work performed by
`bc` is comparatively small.

Going back to our air-travel analogy, the summation of 1000 numbers is equivalent 
to boarding 1000 passengers onto a large airplane. If minimizing total boarding time
matters, an inefficient boarding procedure would involve every passenger bringing
multiple oversized carry-on bags. Many travelers have experienced how loading
excessive baggage into overhead compartments slows movement throughout the aircraft
cabin.

Similarly, the repeated creation of 2000 `bc` subprocesses (two during each loop
iteration) introduces substantial process-management overhead that slows the overall
execution of the script far more than the mathematical calculations themselves.

::::::::::::: challenge

### Let's pull out our stopwatches

We can use either the `time` command or `date`-based timestamps.
Can you measure the runtime of `sum.bash`?

:::: hint
You can prepend almost any command with `time`. If you want to use `date`,
remember that `now=$(date +%s.%N)` stores the current timestamp in a variable,
while `&&` allows multiple commands to be chained together.
::::

:::: solution
A straightforward approach is

```bash
time ./sum.bash
```

Alternatively, `date` and `&&` can be combined into a wrapper command that measures
the runtime of `sum.bash` externally:

```bash
start=$(date +%s.%N) && ./sum.bash && end=$(date +%s.%N) && echo "$end - $start" | bc -l
```

Another option is to place the timestamp measurements directly inside the `sum.bash`
script, or download it directly:

```bash
curl -L -o sum_with_date.bash https://raw.githubusercontent.com/carpentries-incubator/hpc-job-efficiency/main/learners/data/sum_with_date.bash
```

```bash
#!/usr/bin/env bash

start=$(date +%s.%N) # store start timestamp

sum=0

for i in $(seq 1 1000)
do
  val=$(echo "e(2 * l(${i}))" | bc -l)
  sum=$(echo "$sum + $val" | bc -l)
done

end=$(date +%s.%N) # store end timestamp

echo Sum=$sum runtime=$(echo "$end - $start" | bc -l)s
```

::::
:::::::::::::

### Speeding things up

A remedy for the inefficiencies inside the `for` loop of `sum.bash` is to avoid
repeatedly spawning external `bc` processes.
Ideally, we would like to perform all computations within a single `bc` invocation
instead of launching thousands of separate subprocesses.

Let us now revisit the airplane analogy: we want passengers to consolidate their
carry-on baggage into a single large container that can be loaded onto the airplane
in one coordinated operation, rather than having every passenger individually block
the aisle while handling multiple bags.

This reduction in process-management overhead can be achieved by replacing the external
shell loop with a loop executed internally by `bc`:

```bash
echo "s=0; for(i=1; i<=1000; i++) s+=i^2; s" | bc -l
```

In this approach, which we will call the *one-liner*, the loop, arithmetic, and 
accumulation are executed inside a single `bc` process. This avoids the repeated process
creation and communication overhead present in the original implementation.

This example illustrates a common performance-engineering principle in HPC:
substantial speedups can often be achieved by replacing inefficient implementations with
numerically optimized software libraries or by reducing runtime-management overhead.

::::::::::::: challenge

### Evaluate the runtime improvement

Compare the runtimes of the summation script `sum.bash` and the one-liner.

:::: hint
The Bash keyword `time` is sufficient to observe the runtime difference.
::::

:::: solution
You can use `time` for both summation methods:

```bash
time ./sum.bash
time echo "s=0; for(i=1; i<=1000; i++) s+=i^2; s" | bc -l
```

::::
:::::::::::::

While the exact numbers depend on the underlying hardware and software
environment, you will typically observe that the one-liner executes dramatically
faster than `sum.bash`.

Of course, one could tolerate such inefficiency if the script is only executed
occasionally and its runtime is only a few seconds. However, consider a large-scale
computational job running on a supercomputer where compute time is limited, shared,
or billed per usage hour.

In such environments, even seemingly small inefficiencies can become expensive.
A slowdown by only a factor of two may double both the runtime and associated
resource consumption, increasing cost, queue occupancy, and energy usage.

:::: spoiler
### CPU-bound versus memory-bound

The runtime comparisons above primarily measure computational performance.
When the execution speed of a program is mainly limited by the processor's ability
to perform computations, the workload is called *CPU-bound* or *compute-bound*.

In contrast, a *memory-bound* workload is limited primarily by memory-access
performance rather than computational throughput. This occurs when the CPU spends
a significant fraction of time waiting for data to be fetched from main memory,
cache, or other memory hierarchies instead of performing computations.

Optimizing memory-bound applications therefore focuses on improving data locality,
memory-access patterns, cache utilization, and data movement efficiency rather
than increasing raw computational performance.

Finally, if performance is dominated by reading or writing data to storage devices
or transferring data across a network, the workload becomes *I/O-bound*. In such cases,
storage throughput, latency, or network bandwidth become the primary performance
bottlenecks.
::::

So far we have focused on efficiency from the perspective of runtime.
In HPC environments, however, efficiency also affects
resource consumption and energy usage. We now broaden the discussion from
individual programs to the computing systems that execute them.

## Part 2: About HPC power consumption

Modern HPC systems achieve high performance by distributing computations across many
CPU cores, GPUs, and compute nodes that operate in parallel.

To make effective use of these resources, parallel programs divide a workload into
smaller tasks that can execute concurrently.

As a result, many HPC efficiency considerations revolve around keeping computational
resources utilized effectively while minimizing idle time, synchronization overhead,
and unnecessary communication.

We will revisit several of these performance and efficiency aspects in later episodes.

::: instructor

Ask learners:
- How do HPC centers measure resource usage?
- How do users know how much of their allocation they have consumed?

Use the upcoming challenge to introduce common HPC accounting concepts such as
core-hours, allocations, queues, and resource limits.

::::::::::::::

### The more the merrier: Parallel resources

Many parallel computing applications use multiple CPU cores, or even multiple CPUs,
simultaneously.
A CPU core is an independent processing unit capable of executing program instructions.
Modern processors typically contain multiple cores. As of 2026, consumer CPUs commonly
provide quad-core (4 cores), octa-core (8 cores), and higher core-count configurations.
High-end desktop and gaming CPUs often feature 16 or more cores, while HPC compute
nodes frequently provide multiple CPUs with dozens of cores each, typically 64 or more
cores per node.

Nowadays, most HPC centers are also equipped with *GPUs* (*Graphics Processing Units*).
GPUs are particularly well suited for workloads that benefit from executing very large
numbers of lightweight operations in parallel. The number of GPU cores varies greatly
depending on the hardware model, ranging from a few hundred cores in low-end devices to
many thousands in modern accelerator hardware.

### Measuring parallel runtime: core hours

Because HPC applications often execute in parallel, resource usage is commonly measured
using units that account for both runtime and the number of utilized processing cores.

The unit **core hour** (**core-h**) represents the usage of one CPU core for one hour.
Resource consumption therefore scales approximately linearly with the number of allocated
cores and the runtime of the application.
For example, assume you have a monthly allocation of $500$ core-h, with additional usage
incurring extra cost. In that case, you could run:
- a parallel job using $500$ CPU cores for $1$ hour, or
- a single-core job for $500$ hours.

Of course, the latter may require some patience before the computation finishes.
Some HPC systems additionally account for GPU usage through units such as **GPU-hours**.

:::::::::::::::::::::::::: spoiler
### Other HPC resource types

So far, the focus has been on CPU/GPU core counts and runtime as primary HPC resource
allocations. However, HPC workloads also depend heavily on other hardware resources:

- **Memory:** Some applications require very large amounts of memory (RAM), regardless
  of whether they execute in parallel or serially. For example, certain numerical methods
  for solving large systems of equations require large shared-memory regions that cannot
  easily be partitioned across independent processes. HPC centers therefore often provide
  dedicated large-memory nodes for memory-intensive applications.
- **Storage:** Other applications process massive amounts of data. Fields such as
  genomics, climate modeling, and large-scale simulations may involve terabytes or even
  petabytes of data that must be stored, transferred, and analyzed efficiently.
- **GPU-hours:** Some HPC centers account for GPU usage separately using
  **GPU-hours** (**GPU-h**). A GPU-hour represents the use of one GPU for one hour,
  analogous to a CPU core-hour. For example, running a job for one hour on a node
  with four allocated GPUs consumes **4 GPU-h**. GPU-hours are typically
  accounted for independently of CPU core-hours, although individual HPC centers
  may combine both resources in their allocation or billing policies.

For example, a job allocated one compute node with 48 CPU cores and 4 allocated GPUs
for one hour consumes:
- 1 node-hour,
- 48 core-hours, and
- 4 GPU-hours.

::::::::::::::::::::::::::

### A typical HPC computing job
Like many high-performance systems, HPC infrastructures require substantial electrical
power to operate. Large-scale scientific computations therefore also translate into
significant energy consumption.
Consider a typical parallel scientific-computing workload running on an HPC center.
Assume the problem is too large for a single CPU and therefore executes across multiple
compute nodes in parallel.
Power consumption is measured in watts (W), the SI unit of power, which describes the
rate at which electrical energy is consumed.
Modern HPC compute nodes equipped with 64-core CPUs may consume roughly:
- about 250–300 W while idle, and
- about 850–900 W under heavy computational load,
depending on factors such as processor generation and cooling technology.

For comparison, a household coffee machine typically consumes between 800 W and 1500 W
while operating.

Assume our example HPC job uses the following resources:
- 12 compute nodes running in parallel,
- 64 CPU cores per node (e.g., Intel® Xeon® 6774P or AMD® EPYC® 9534),
- 12 hours of sustained high utilization (realistic for many scientific simulations),
- approximate power per node:
  - idle: $\sim 300$ W,
  - full load: $\sim 900$ W,
  - additional power draw under load: $\sim 600$ W.

The additional energy consumption caused by the workload is therefore approximately

\[
12 \text{ nodes} \times 600 \text{ W} \times 12 \text{ h}
= 86{,}400 \text{ Wh}
= 86.4 \text{ kWh}
\]

::::::::::::: challenge
### How many core hours does this job involve?

HPC centers often provide different job *queues* for different classes of workloads.
For example, a queue named *big-jobs* may be reserved for jobs exceeding a certain
number of *parallel tasks* (often implemented as *processes*) (e.g., 1024).
Another queue, such as *big-mem*, may provide access to nodes with very large
memory capacities (e.g., 512 GB, 1 TB, or more RAM per compute node).

Assume the following queues are available, all with identical memory configurations:

- `small-jobs`: total task count up to 511.
- `medium-jobs`: total task count 512–1023.
- `big-jobs`: total task count 1024 or more.

When submitting the example HPC workload from the previous section:
1. Into which queue would the job be placed?
2. If the allocation cost is 1 cent per core-h, what would be the total cost in euros
   (€1 = 100 cents)?

:::: hint
For this example, assume one task is assigned to each CPU core.
The total number of tasks is therefore approximately:
\[
\text{cores per node}  \times \text{number of nodes}
\]

Total core hours are then computed as:
\[
\text{task count} \times \text{runtime in hours}
\]

::::

:::: solution
The total number of tasks is 
\[
\text{cores per node} \times \text{number of nodes} = 64 \times 12 = 768
\]
which places the job into the `medium-jobs` queue.

The total number of core hours is
\[
64 \times 12 \times 12 = 9216 \text{ core-h}
\]

At a billing rate of 1 cent per core-h, the total cost becomes
\[
9216 \times 0.01\,€ = 92.16\,€
\]

::::

:::::::::::::

### What are watt-hours?

The unit Wh (watt-hour) measures energy. For example, 86,400 Wh corresponds to the
amount of energy consumed by an 86.4 kW machine operating continuously for one hour.

Returning to our coffee analogy, brewing a single cup of coffee typically requires
roughly 50–100 Wh of energy, depending on the preparation method and brewing time.
Running our 12-node HPC job for 12 hours therefore consumes energy comparable to
brewing approximately 864–1728 cups of coffee.

For a more physics-inspired comparison, suppose — unrealistically — that all energy
consumed by the compute job could be converted perfectly into mechanical work.
Using gravitational potential energy,

\[
\text{Energy} = \text{mass} \times \text{gravitational acceleration} \times \text{height}
\]

we could lift an average African elephant (approximately 6000 kg) vertically by roughly

\[
h \approx \frac{86.4 \times 3.6 \times 10^6}{6000 \times 9.81} \approx 5285 \text{ m}
\]

which is nearly the elevation of Mount Kilimanjaro (5895 m).

:::: spoiler
### Power-consuming hardware pieces

Note that the focus so far has been on **additional** power consumption caused by computational
load beyond a system's idle state. Attributing this increase only to CPU usage would
underestimate the true energy footprint of an HPC workload.

In practice, the additional power draw between idle and full utilization also depends
on many other hardware components involved in executing a computational job. Therefore,
it is useful to briefly examine which parts of an HPC system become active after
submitting a large-scale computational workload.

- **CPUs** consume power through two primary mechanisms:

  1. **Dynamic power consumption:**
     caused by transistor switching activity during computations. It depends strongly
     on clock frequency and operating voltage.
  2. **Static power consumption:**
     caused by leakage currents that persist even when transistors are not actively
     switching (i.e., even when the CPU is idle). This component depends on transistor
     count and semiconductor manufacturing characteristics.

  Both mechanisms ultimately dissipate electrical energy as heat, which is why CPU
  cooling is essential.

- **Memory (DRAM)** consumes power primarily because stored electrical charge leaks
  over time and must therefore be refreshed periodically. These refresh cycles compensate
  for charge leakage in the memory cells. Periodic refreshing is necessary to maintain
  data integrity, which is one reason why DRAM consumes power even while idle.
  Additional power is consumed by memory-controller circuitry and by active
  read/write operations.

- **Network interface cards (NICs)** consume power while transmitting and receiving
  data across the network fabric. Power consumption generally increases with
  network throughput, link speed, physical media, and interconnect technology.

- **Storage systems** also contribute significantly to power consumption:

  - **Hard disk drives (HDDs)** require continuous power for spinning disks and
    moving mechanical components.
  - **Solid-state drives (SSDs)** store data electronically and are typically more
    power-efficient, especially during idle operation. Under heavy I/O workloads,
    however, SSD power consumption can still become substantial, although they
    typically complete data transfers faster than HDDs and return to idle
    operation sooner.

- **Cooling systems** are among the largest contributors to total datacenter energy use:

   - **Idle:** During low utilization, cooling may account for roughly 10–20% of total
     system power.
   - **Maximum load:** Under sustained heavy computational load, cooling infrastructure can
     consume a substantially larger fraction of overall datacenter power consumption,
     sometimes approaching 50–70% depending on cooling technology and datacenter design.

   Cooling is essential because all electrical components generate heat during operation.
   Under heavy workloads, insufficient cooling may cause CPUs and GPUs to exceed safe
   operating temperatures, potentially reducing performance through thermal throttling or
   damaging hardware.

::::

These considerations highlight why identifying efficiency bottlenecks before submitting
large HPC workloads is essential. Efficient job design reduces unnecessary energy
consumption, improves overall system utilization, and allows HPC systems to execute
workloads more efficiently and sustainably.

Returning to the airplane analogy, if passengers minimize unnecessary baggage, the total
aircraft load decreases. This either allows more passengers to travel simultaneously or
reduces the fuel required for the journey. Similarly, efficient HPC workloads reduce
unnecessary resource consumption and allow HPC systems to execute computational workloads
more efficiently.

<!---
 Use timing commands provided by `time`and`date`.
- Understand the benefits of efficient jobs in terms of runtime and numerical accuracy.
- Have developed some awareness about the overall high energy consumption of HPC.
--->

:::::::::::::::::::::::::::::::::::::: keypoints
- Runtime can be measured using tools such as `time` and `date`.
- Repeated process creation can dominate runtime.
- HPC resource usage is commonly measured in core-hours.
- Computational workloads may be compute-bound, memory-bound, or I/O bound.
- Efficient jobs reduce both resource consumption and energy use.
- Implementation choices can affect both runtime and numerical accuracy.

::::::::::::::::::::::::::::::::::::::

## So what's next?

The following episodes will put a number of these introductory thoughts 
into concrete action by looking at efficiency aspects around 
a computationally demanding graphical program.
While it is not directly an action-loaded video game, it does contain essential
pieces thereof, because it uses the technique of ray tracing.

Ray tracing is a technique that simulates how light travels in a 3D scene to create 
realistic images. It simulates the behavior of light in terms of optical effects like
reflection, refraction, shadows, absorption, etc. 
The underlying calculations involve real-world physics, 
which makes them computationally expensive - an ideal HPC use case.

::: instructor

Encourage learners to estimate the ratio between `user` and `real` before discussing
the meaning of the `-np 4` option. Do not explain the result immediately.

The explanation of accumulated CPU time across multiple MPI processes will be
introduced in the following episodes.

:::

::::::: challenge

### Submit your first raytracer job with Slurm

```bash
#!/usr/bin/env bash
#SBATCH --job-name=first-script-Snowman
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --tasks-per-node=4

# Put in the same "module load ..." command when building the raytracer program

time mpirun -np 4 raytracer -width=800 -height=800 -spp=128
```

::: hint
Compare the `real` and `user` times reported at the end of the job's output file
(named something like `slurm-<NUMBER>.out`).

How do they differ?

:::

::: solution

Notice that the reported *user* time is substantially larger than the elapsed
*real* time.

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
Performance (rays/sec):     2.699e+06
----------------------------------------------
Max Local Computation Time (s):              30.357
Min Local Computation Time (s):              30.106
Avg Local Computation Time (s):              30.172
==============================================

real    0m38.484s
user    2m1.221s
sys     0m3.969s
```

:::

:::::::

::: discussion
What is the ratio between the reported `user` and `real` times?

Which command-line argument in `mpirun -np 4` might explain this ratio?

::::::::::::::
