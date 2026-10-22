#!/usr/bin/env bash

sum=0

for i in $(seq 1 1000)
do
    val=$(echo "e(2 * l(${i}))" | bc -l)
    sum=$(echo "$sum + $val" | bc -l)
done

echo Sum=$sum
