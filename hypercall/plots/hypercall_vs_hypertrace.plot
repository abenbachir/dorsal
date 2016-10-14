set terminal pdf 
set output 'hypercall_vs_hypertrace.pdf'
set style fill solid 0.25 border -1
set style boxplot outliers pointtype 7
set style data boxplot
set logscale y

set title 'Overhead Qemu-Hypertrace VS Hypercall' font 'Arial,14';
set xtics ('Qemu Hypertrace' 1, 'Hypercall' 2)
plot for [i=1:2] 'hypercall_vs_hypertrace.dat' using (i):i notitle
