#!/usr/bin/python3

# example for GPU vs CPU comparison:
# python3 test.py -g -s seaborn-v0_8-bright -t "HeCBench, GPU vs CPU speedup" -c hecbench_GPU.csv -b hecbench_CPU.csv

#### CONFIG USED BY CHIPSTAR PAPER:


# python3 plot.py -v -r --color '#b7cce9' -m 0.8 -s seaborn-v0_8-pastel -t "HeCBench, Intel Arc750, HIP vs SYCL speedup" -c test_20_strict_hip_oclBE_arc_after.csv -b test_20_strict_sycl_oclBE_arc_after.csv -o hecbench_intel_arc750_hip_vs_sycl.pdf

# python3 plot.py -v -r --color '#b7cce9' -s seaborn-v0_8-pastel -t "PowerVR BXE-4-32 GPU vs StarFive JH7110 CPU" -b CPU_3_x_with_abort_strictmath.csv -c GPU_3_x_with_abort_strictmath.csv -o hecbench_visionfive2_gpu_vs_cpu.pdf


from optparse import OptionParser
import matplotlib.pyplot as plt
import csv

import math

def geomean(xs):
        return math.exp(math.fsum(math.log(x) for x in xs) / len(xs))

parser = OptionParser(description="Takes an input two CSV files produced by HeCBench's runner script (autohecbench.py), and produces a matplotlib chart with data from one CSV normalized to other CSV.")
parser.add_option("-b", "--input-file-baseline", dest="input_base",
                  help="CSV file with baseline data", metavar="BASE_PATH")
parser.add_option("-c", "--input-file-compared", dest="input_comp",
                  help="CSV file with compared data", metavar="COMP_PATH")
parser.add_option("-o", "--output-file", dest="output", default=None,
                  help="if specified, write output to this file (SVG,PDF,..) otherwise show chart on screen", metavar="OUTPUT_PATH")

parser.add_option("-e", "--errorbars", dest="errbars", default=False, action="store_true",
                  help="draw error bars, default = don't draw")

parser.add_option("-g", "--geomean", dest="geomean", default=False, action="store_true",
                  help="draw geometric mean, default = don't draw")

parser.add_option("--color", dest="color", default=None,
                  help="Adjust chart bar color (optional, default = None)", metavar="STRING")

parser.add_option("--ecolor", dest="ecolor", default=None,
                  help="Adjust chart bar error color (optional, default = None)", metavar="STRING")


parser.add_option("-m", "--bottom", dest="bottom", default=0.0,  type="float",
                  help="Adjust chart bottom (optional, default = 0.0)", metavar="FLOAT")

parser.add_option("-r", "--refline", dest="refline", default=False, action="store_true",
                  help="draw dotted line @ y=1.0, default = don't draw")

parser.add_option("-s", "--style", dest="style", default='default',
                  help="chart style (optional, default = default)", metavar="STYLE-NAME")

parser.add_option("-t", "--title", dest="title", default=None,
                  help="chart title (optional)", metavar="TITLE")

parser.add_option("-x", "--xlabel", dest="xlabel", default=None,
                  help="X axis label (optional)", metavar="XLABEL")
parser.add_option("-y", "--ylabel", dest="ylabel", default=None,
                  help="Y axis label (optional)", metavar="YLABEL")
parser.add_option("-z", "--zlabel", dest="zlabel", default=None,
                  help="Label embedded into chart (optional)", metavar="ZLABEL")

parser.add_option("-v", "--bar-values", dest="bar_values", default=True, action="store_false",
                  help="do not draw values of each bar, default = draw")

(options, args) = parser.parse_args()
if (not options.input_comp) or (not options.input_base):
	parser.error("both input files must be specified")

Baseline = {}
Compared = {}

# baseline and compared are switched here, because we want the
# graph of speedup (3x faster) which is inverse of time (0.33 time),
# and the data in CSV are recorded times
f = open(options.input_comp,'r')
reader = csv.reader(f, delimiter = ',')
for row in reader:
	K = row[0]
	if K.endswith('-hip'):
		K = K[:-4]
	if K.endswith('-cuda'):
		K = K[:-5]
	if K.endswith('-sycl'):
		K = K[:-5]
	Baseline[K] = {
	'min': float(row[1]),
	'mean': float(row[2]),
	'stddev': float(row[3]),
	'var': float(row[4]) }
f.close()

f = open(options.input_base,'r')
reader = csv.reader(f, delimiter = ',')
for row in reader:
	K = row[0]
	if K.endswith('-hip'):
		K = K[:-4]
	if K.endswith('-cuda'):
		K = K[:-5]
	if K.endswith('-sycl'):
		K = K[:-5]
	Compared[K] = {
	'min': float(row[1]),
	'mean': float(row[2]),
	'stddev': float(row[3]),
	'var': float(row[4]) }
f.close()

bench_names = []
mins = []
means = []
stddevs = []
#vars = []

for K in Baseline.keys():
	if not K in Compared.keys():
		print("skipping bench: ", K)
		continue
	Comp = Compared[K]['min'] / Baseline[K]['min']
	if Comp > 10:
		print("Bench too large:", K, " compared: ", Compared[K]['min'], " baseline: ", Baseline[K]['min'], " compared/base: ", Comp)
		continue
	if Comp < 0.1:
		print("Bench too small:", K, " compared: ", Compared[K]['min'], " baseline: ", Baseline[K]['min'], " compared/base: ", Comp)
		continue
	bench_names.append(K)
	mins.append(Compared[K]['min'] / Baseline[K]['min'])
	means.append(Compared[K]['mean'] / Baseline[K]['mean'])
	stddevs.append(Compared[K]['stddev'] / Baseline[K]['mean'])

zipped_data = zip(bench_names, means, stddevs)
sorted_data = sorted(zipped_data, key = lambda x: x[1])
sorted_bench_names, sorted_means, sorted_stddevs = zip(*sorted_data)

bar_width = 0.68

plt.style.use(options.style)

errs = sorted_stddevs
if not options.errbars:
	errs = None

bar1 = plt.bar(sorted_bench_names, [x-float(options.bottom) for x in sorted_means], bar_width, align='center',
               yerr=errs, color=options.color, ecolor=options.ecolor,
               label=options.zlabel, bottom=float(options.bottom) )

if options.xlabel:
	plt.xlabel(options.xlabel)
if options.ylabel:
	plt.ylabel(options.ylabel)
if options.title:
	plt.title(options.title)

plt.xticks(rotation='vertical')
if options.refline:
	plt.axhline(1.0, ls='dotted')
if options.geomean:
	g = geomean(sorted_means)
	s = "Geomean = %.2f" % g
	plt.axhline(g, ls='dashed', label=s)
if options.bar_values:
	plt.bar_label(bar1, fmt='%.2f', label_type='edge', rotation='vertical', fontsize='small')

# plt.legend()
plt.tight_layout()

if options.output:
	plt.savefig(options.output)
else:
	plt.show()

