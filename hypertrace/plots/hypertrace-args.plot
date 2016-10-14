set terminal pngcairo  enhanced font "arial,10" fontscale 1.0 size 1000, 800 
set output 'hypertrace-args.png'
set style fill solid 0.25 border -1
set style boxplot outliers pointtype 7
set style data boxplot

set title 'Qemu Hypertrace Overhead Distribution (disabled logging)' font 'Arial,14';
set xtics ('With 1 argument' 1, '3 arguments' 2, '5 arguments' 3, '8 arguments' 4, '9 arguments' 5)
plot for [i=1:6] 'hypertrace-args.dat' using (i):i notitle
