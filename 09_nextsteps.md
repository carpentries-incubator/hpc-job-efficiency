---
title: "Next Steps"
teaching: 10
exercises: 0
---

:::::::::::::::::::::::::::::::::::::: questions 

- What are other patterns of performance bottlenecks?
- How to evaluate an application in more detail?

::::::::::::::::::::::::::::::::::::::::::::::::

::::::::::::::::::::::::::::::::::::: objectives

After completing this episode, participants should be able to …

- Find collection of performance patterns on hpc-wiki.info
- Identify next steps to take with regard to performance optimization.

::::::::::::::::::::::::::::::::::::::::::::::::


:::::::::::::::::::::::::: instructor
## Intention: Provide a roadmap learners could follow

**Most important:** enable users to translate from example workload to their own code! Guide on how to translate learning goals and key points to their situation. Additionally, provide some info on where and how to dig deeper, if there is interest (application profiling, etc.)

All ideas in this episode may need to be reworked, since they were made with the outlook in mind, not so much to help learners transfer insight

Narrative:

- Start with picture of beautiful title slide of the talk with the snowman picture
- Next time we want to tackle the issue way in advance
- Approach our raytracing application more systematically, such that we can get the title slide done much quicker
- What could we do to dive deeper in optimizing the raytracer?
- Where can we go from here?


What we're doing here:

- Learning important programming concepts (parallel programming on many levels)
- Deeper application profiling & tools to use

:::::::::::::::::::::::::::::::::::::


### To be precise: Numerical efficiency

> This has been moved from Introduction as it seems to be an abrupt transistion into
Numerical efficiency.

::: instructor

Ask learners:
- Can a calculation be fast but scientifically useless?
- Can a calculation be extremely accurate but unnecessarily expensive?

Guide the discussion toward the trade-off between numerical accuracy and computational
cost.

Different scientific applications require different levels of numerical precision.
Choosing more precision than necessary may increase runtime, memory usage, and
energy consumption without improving scientific results.

::::::::::::::

Computational inefficiency is not limited to unnecessarily slow implementations.
It can also arise when calculations are performed with a higher numerical precision
than required for the scientific objective.

In scientific computing, numerical precision determines how accurately numbers are
represented and processed by the CPU, for example through single-precision or
double-precision floating-point arithmetic.

Higher numerical precision generally increases computational cost, memory usage,
and data movement. Lower precision, on the other hand, can improve performance and
reduce memory consumption, but may also reduce numerical accuracy and stability.

Choosing an appropriate numerical precision is therefore an important aspect of
computational efficiency and depends strongly on the requirements of a given application.

<!---
The internal accuracy of`bc`is defined by an adjustable parameter`scale`which
defines how some operations use digits after the decimal point. The default value of`scale`is 0.
During each`bc`call within the summation loop of`sum.bash`, the intermediate result is rounded 
according to the current setting of`scale`. An insufficiently low precision setting
leads to an accumulation of rounding errors over many loop iterations,
rendering the final result (like a sum or product) erroneous.--->

::::::::::::: challenge
### Compare numerical results

Our `sum.bash` implementation also demonstrates how numerical methods and implementation
details can affect computational accuracy.

When running the two summation methods from the previous challenge, compare the final
numerical results. Which result appears more accurate, and why?
Is the inaccurate result smaller or larger than the expected value?

:::: hint
Think again about the airplane analogy.
Which scenario is more prone to small losses accumulating over time?
1. Passengers repeatedly handle their own individual baggage items.
2. Baggage is handled collectively in a single coordinated operation.
::::

:::: solution
The external loop implementation `sum.bash` and the internal `bc` one-liner may produce
results similar to

```output
333833499.99999999999667056674 # bc, external loop (sum.bash)
333833500                      # bc, internal loop (one-liner)
```

where the exact floating-point representation may vary slightly between systems.
The implementation in `sum.bash` repeatedly evaluates expressions involving logarithms
and exponentials: 

```bash
e(2 * l($i))
```

These operations introduce small numerical rounding errors during every loop iteration.
Since the result is accumulated repeatedly, the rounding errors also accumulate over time.
The one-liner implementation instead computes the powers directly inside a single `bc`
execution context and therefore avoids much of the repeated conversion and evaluation
overhead.

As a result, the value produced by `sum.bash` is typically slightly smaller than the
mathematically expected result due to accumulated truncation and rounding effects.
Although `bc` supports arbitrary precision arithmetic, the effective numerical precision
still depends on how calculations are performed and how intermediate results are represented.

::::

:::::::::::::

## Next Steps

hpc-wiki.info
- I/O
- CPU Front End
- CPU Back End
- Memory leak
- Oversubscription
- Underutilization

<!-- EPISODE CONTENT HERE -->
## Summary

:::::::::::::::::::::::::: challenge
## Exercise:
::::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::: keypoints
- There are many profilers, some are language-specific, others are vendor-related, ...
- Simple profile with exclusive resources
- Repeated measurements for reliability
::::::::::::::::::::::::::::::::::::::::::::::::
