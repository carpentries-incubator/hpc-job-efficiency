---
title: Setup
---

## Learning Objectives
After attending this training, participants will be able to:

- Explain efficiency in the context of *High Performance Computing* (*HPC*) systems
- Use batch system tools and third party tools to measure job efficiency
- Discern between worse and better performing jobs
- Describe common concepts and terms related to performance on HPC systems
- Identify hardware components involved in performance considerations
- Achieve first results in performance optimization of their application
- Recall next steps to take towards learning performance optimization

::: callout

# Additional Note

In this course, job efficiency refers to how effectively an application utilizes allocated computational resources, such as CPU cores, memory, GPUs, runtime, interconnect bandwidth, and energy consumption.

:::::::::::

## Prerequisites
::: prereq

- Access to an HPC system
- Access to an example workload setup
- Basic understanding of HPC systems including batch schedulers, parallel file systems, and environment modules
- Ability to submit basic jobs and understand typical HPC execution workflows
- Knowledge of tools and workflows used in HPC environments:
    - Bash shell scripting
    - Secure remote access and file transfer using SSH and SCP
    - Basic Slurm job scripts and workload management commands (`srun`, `sbatch`, `squeue`, `scancel`)
    - Version control systems: Git, GitHub, and GitLab

::::::::::


::: instructor
## ToDo: Improve prerequisites
Link to external resources in prerequisites:

- HPC Intro
- HPC Shell
- HPC.NRW
- Maybe Python for plotting performance data?
- Amount of knowledge about MPI, OpenMPI, CUDA, etc.?
  - Don't require in-depth MPI knowledge, but some basic understanding might be necessary?

Maybe make sure required definitions / concepts are available in the hpc-wiki and link to those? But this course should be somewhat self-contained.
"Jargon buster" similar to HPC intro?

Maybe add some form of self test, e.g. like [PC2 HPC and Linux self test?](https://pc2.uni-paderborn.de/teaching-old/trainings/hpc-user-trainings/selftests/selftest-hpc)
Or as an exercise in the setup / prerequisites sections?

Selftest should help to answer "Is the course for me?", i.e. prerequisites should be mostly green, course material should be mostly red

::::::::::::::


### HPC Access
::: instructor
## Tell learners how to get access to an HPC System

- Do they need to apply somewhere?
- Are they eligible to request access to another system?
- Are they expected to already have an account?
- Could they try to log in in advance?
- Is there maybe some test cluster in the cloud?

::::::::::::::

You will need access to an HPC cluster to run the examples in this lesson.
Discuss how to find out where to apply for access as a researcher (in general, in EU, in Germany, in NRW?).
To learn how to access and use a compute cluster, refer to the [HPC Introduction](https://carpentries-incubator.github.io/hpc-intro/) lessons.

- Executive summary of typical HPC workflow? Or refer to other HPCC courses that cover this
- "HPC etiquette"
   - E.g. don't run benchmarks and other computationally heavy workloads on login node. Emphasise their purpose
   - Don't disturb jobs on shared nodes (<-- this phrasing is hard to grasp for newcomers and should be avoided. It will block them from trying things if they are afraid to break anything. Maybe this is more the responsibility of admins and users should just be aware that they may affect other users?)
- Setup of the example workflow below (next section)


::: discussion 

### Common Software on HPC Systems
Working on an HPC system commonly involves:

- a *batch system* used to schedule and manage *jobs* (e.g. Slurm, PBS Pro, HTCondor, ...)
- a *module system* to load and manage centrally provided software packages and software versions
- a secure method to connect to a *login node* of the cluster, typically using SSH

::::::::::::::

To login via `ssh`, you can use on (remove this since it's discussed in HPC introduction?)

::: spoiler

### Windows

- PuTTY
- `ssh` in PowerShell

:::::::::::


::: spoiler

### MacOS

- `ssh` in Terminal.app

:::::::::::


::: spoiler

### Linux

- `ssh` in Terminal

:::::::::::


### Example Workload: Snowman Raytracer
<!--
FIXME: place any data you want learners to use in `episodes/data` and then use
       a relative link ( [data zip file](data/lesson-data.zip) ) to provide a
       link to it, replacing the example.com link.

Download the [data zip file](https://example.com/FIXME) and unzip it to your Desktop
-->

::: instructor

## TODO: Episodes are tied together with a narrative around the example job

- Needs a specific example job.
- Gradual improvement throughout the course
- Introduce only topics that are directly observed/experienced with the example
- Point to additional information/overview in hpc-wiki where useful
- Maybe close every episode with the same metric? (snowman pictures / hour at a given energy?)
  - Could start with "?" when we didn't learn yet how to do it in the first episodes
  - Motivates the discovery of certain metrics, tools, etc.

::::::::::::::

Throughout the course, we will use an example application to learn workflows and tools for evaluating job performance.
The example is a ray tracer used to render a predefined scene.
It supports multiple parallelization models, including distributed-memory parallelism using MPI, shared-memory multithreading, and GPU acceleration using CUDA. MPI and multithreading can also be combined.
The GPU-accelerated version uses MPI processes primarily for process management and coordination, while all computational work is performed on one or more GPUs.

We do not have to study and understand the example code in detail.
After compilation, all necessary options are exposed as separate binaries or through command-line arguments.

We do, however, need to prepare a build environment with all required libraries and build the code with `CMake`. This is a common occurrence in scientific software as well.
Researchers often depend on existing software, and their first interaction with a new project frequently occurs in a situation like this, where they have to build and prepare unfamiliar code.
Their first question is typically: "Is this project useful for my research?"

The example application should be prepared in a central location, such as the parallel file system of your cluster, to ensure that it is accessible from multiple worker nodes during distributed job execution.

Let's get started by cloning the repository:

```bash
# Log in to your cluster via ssh first
mkdir jobefficiencyguide && cd jobefficiencyguide
git clone --recursive https://codeberg.org/HPC-NRW/SnowmanRaytracer.git
cd SnowmanRaytracer
```

::: callout

# Do not forget `--recursive`

Our example project depends on another project, implementing the basic ray tracing methods.
This dependency is introduced as a `git submodule`, so recursive cloning is necessary, otherwise we cannot build the project.

:::::::::::


#### CPU Build
The example application can perform computations on CPUs using shared-memory multithreading and distributed-memory parallelism across multiple nodes via MPI communication.
To prepare the out-of-source build:

```bash
# Assuming you are still in the SnowmanRaytracer source directory
cd ..
mkdir build && cd build
```

##### Dependencies
To build the example, you need to provide the following dependencies:

- Compiler, e.g. GCC
- MPI, e.g. OpenMPI
- CMake
- Boost
- libpng

::: instructor

Show learners how to prepare their environment on your particular HPC system.
This also serves as a reminder on how to work with software modules in general.

::::::::::::::


In HPC systems, this often happens through loading software modules, centrally provided by your administrators.
The exact module names and required software stacks can vary significantly depending on the configuration of the cluster.
In one particular environment, the setup may look like this:

```bash
# Only one example, consult your cluster documentation or ask the instructor or your HPC support
module load 2025 GCC/13.2.0 OpenMPI/4.1.6 Boost/1.83.0 CMake/3.27.6 libpng/1.6.40 buildenv/default
```

::: callout

# Software management differs widely on HPC systems
The details of how different compiler and library versions are loaded depend strongly on the configuration of your particular HPC system.
Follow the instructor's guidance or consult your site's documentation or support staff if you have questions.

:::::::::::


##### Building the Software

::: instructor

# Show the preferred build process for your cluster
Do you recommend building the software on your login nodes, since they have enough resources and share the same hardware architecture with the worker nodes?
Or do you recommend building on the target architecture directly?

::::::::::::::

::: instructor

# TODO: Is the description here compatible / identical to the repo readme?

Also discuss output of the application & `scp` to copy the output png

::::::::::::::


Typically, it is recommended to build software on the same hardware architecture on which it will later be executed.
For HPC systems, you should consider whether the login nodes provide sufficient resources for software compilation and whether they use the same hardware architecture as the worker nodes.
Check your cluster documentation for any recommendations!

Here, we will build and test the software in a first Slurm job script, `build_snowman.sbatch`:

```bash
#!/usr/bin/env bash
#SBATCH --job-name=build-and-test-Snowman
#SBATCH --nodes=1
#SBATCH --ntasks=4

# Prepare your environment with the dependencies
# This will likely look different in your case!
module load 2025 GCC/13.2.0 OpenMPI/4.1.6 Boost/1.83.0 CMake/3.27.6 libpng/1.6.40 buildenv/default

# Assuming you are submitting from the "build" directory
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=OFF ../SnowmanRaytracer

# Building the software in parallel
cmake --build . --parallel

# First test run with 4 MPI processes
mpirun -n 4 ./raytracer -width=800 -height=800 -spp=128 -threads=1 -png=snowman.png
```

::: instructor

# TODO: Is the script general, useful, correct?

How about `srun cmake`, vs. multiple processes vs. multiple cpus per process?

::::::::::::::

##### Running the Ray Tracer
The `mpirun` command from our first test run above:

- starts the `raytracer` binary with the prepared scene,
- computes the ray-traced image with $N = 4$ MPI processes, each using a single thread (`-threads=1`),
- computes $128 / N = 32$ samples per pixel (`-spp=128`) in each MPI process,
- sets the `height` and `width` of the resulting image to $800$ pixels, and finally
- stores the generated image as `snowman.png`.

A ray tracer computes the interaction of straight "light rays" with objects placed in a 3D scene.
Each object can have different material properties, resulting in different optical effects, such as matte or partially translucent surfaces.
Light rays that reach the "camera" contribute to rendering the image by accumulating their effects across all pixels.

Computationally, ray tracing primarily consists of many independent geometric and vector operations, including matrix-vector and matrix-matrix calculations.
These operations can therefore be evaluated in parallel across large numbers of rays and pixels.
This enables different parallelization strategies.
You could divide the pixels of the final image into regions, where each parallel process computes one region.
Another strategy, which is applied here, is dividing the number of *samples per pixel* (`spp`) across all parallel processes.
For each pixel, `spp` samples contribute to the final pixel.
For example, with `-spp=128` and $4$ MPI processes, each MPI process computes $\frac{128}{4}=32$ samples contributing to all pixels of the final image.

In addition to MPI-based parallelization, the application also supports shared-memory parallelism through $T$ threads using the `-threads=T` parameter.
Threads share the same address space and therefore may require less memory overhead than multiple processes.


#### CUDA Build
The example application can also utilize NVIDIA GPUs via CUDA.
In this case, the ray-tracing computations are performed on GPUs, which provide an ideal environment for this type of workload, provided that the problem size and rendering complexity are sufficiently large to benefit from massive parallelism.

CUDA support requires a separate build, which we will execute in a separate Slurm job.
In this case, it may be especially important to build on the target hardware, since your login nodes may not contain the accelerators intended for execution.

Let us prepare the build directory again on our login node:
```bash
# Assuming you are still in the SnowmanRaytracer source directory or inside the CPU build directory
cd ..
mkdir build_gpu && cd build_gpu
```

In addition to the dependencies listed above, this build relies on CUDA and you may have to load the corresponding modules for your HPC system.
The application still uses MPI for process management and coordination, for example, to assign one MPI process per GPU when multiple GPUs are used.

Our build script (`build_gpu_snowman_cuda.sbatch`) may look like this:
```bash
#!/usr/bin/env bash
#SBATCH --job-name=build-gpu-and-test-Snowman
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --partition=gpu
#SBATCH --gpus=2

# Prepare your environment with the dependencies
# This will likely look different in your case!
module load 2025 GCC/13.2.0 OpenMPI/4.1.6 Boost/1.83.0 CMake/3.27.6 libpng/1.6.40 buildenv/default CUDA/12.6.0

# Assuming you are submitting from the "build_gpu" directory
cmake -DCMAKE_BUILD_TYPE=Release -DENABLE_CUDA=ON ../SnowmanRaytracer

# Building the software in parallel
cmake --build . --parallel

# First test run with 2 MPI processes
export CUDA_VISIBLE_DEVICES=0,1 # Some HPC systems configure GPU visibility automatically
mpirun -n 2 ./raytracer -width=800 -height=800 -spp=128 -threads=1 -png=snowman_gpu.png
```

::: instructor

# TODO: CUDA Modules missing or needed different versions on your HPC cluster?

Some HPC systems automatically manage `CUDA_VISIBLE_DEVICES`.
Manual configuration may not be necessary and can interfere with scheduler resource isolation.

::::::::::::::

## We are all set to learn about job efficiency!
With the example application in place, we are now ready to explore the many factors that affect job performance.
We will repeatedly use this application in different configurations throughout the course, so make sure to keep it in a central location that remains accessible during the entire course.

## Acknowledgements

Course created in context of [HPC.NRW](https://hpc.dh.nrw/).
