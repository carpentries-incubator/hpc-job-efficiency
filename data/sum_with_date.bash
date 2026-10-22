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
