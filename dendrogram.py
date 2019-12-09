import matplotlib
matplotlib.use('Agg')
import argparse
import pandas as pd
from seaborn import clustermap
import math
import matplotlib.pyplot as plt

plt.rcParams['svg.fonttype'] = 'none'

parser = argparse.ArgumentParser(description='Generate dendrogram by taxonomy')
parser.add_argument('samples', metavar='N', nargs='+',
                    help='files with taxonomy of samples')
parser.add_argument('-c', dest='count', default = -1, type = int,
                    help='Number of most abundant taxons to use (default: all). Names will be shown if count <= 50')
parser.add_argument('-o', dest='output', default = "dendrogram",
                    help='File to save dendrogram to (default: dendrogam.png)')
args = parser.parse_args()

dat = dict()
dat['total'] = {}

for f in args.samples:
	samp = f[:-4]
	total = 0.
	for line in open(f):
		perc, cnt, uniq, rank, ncbi, name = line.strip().split("\t")
		name = name.strip()
		if int(cnt) == int(uniq) and (rank == 'S' or rank == '-'):
			total += float(uniq)
			if name not in dat:
				dat[name] = {}
			dat[name][samp] = float(uniq)
	dat['total'][samp] = total


df = pd.DataFrame(data=dat, dtype=float)
df = df.fillna(0)
df = df.apply(lambda x: x/x.max(), axis=1)
df = df.drop('total', axis=1)
df.loc['sum'] = df.sum(axis=0)
df = df.sort_values('sum', axis = 1, ascending=False)
df = df.drop('sum', axis=0)

df.to_csv(args.output + ".csv")

if args.count > 0:
	df = df.iloc[:, :args.count]
else:
	args.count = df.shape[1]

sz = min(50, max(args.count, len(args.samples))) // 5
g = clustermap(data=df, metric='braycurtis', col_cluster=False, robust=True, figsize=(sz+5, sz))
if args.count > 50:
	g.ax_heatmap.get_xaxis().set_visible(False)
plt.setp(g.ax_heatmap.xaxis.get_majorticklabels(), fontsize=min(100, 40 * sz // args.count))
plt.setp(g.ax_heatmap.yaxis.get_majorticklabels(), fontsize=min(100, 40 * sz // len(args.samples)))
plt.setp(g.ax_heatmap.yaxis.get_majorticklabels(), rotation=0, va='center')
plt.setp(g.ax_heatmap.xaxis.get_majorticklabels(), rotation=90)
for a in g.ax_row_dendrogram.collections:
	a.set_linewidth(2)
g.savefig(args.output + ".svg")
g.savefig(args.output + ".png")