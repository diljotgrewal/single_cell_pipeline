'''
Created on Jul 24, 2017

@author: dgrewal
'''
import pandas as pd
from scripts import SummaryMetrics
from scripts import PlotKernelDensity
from scripts import PlotHeatmap
from scripts import PlotMetrics
from scripts import PlotPcolor
from single_cell.utils import csvutils
from single_cell.utils import pdfutils
from single_cell.utils import helpers
from scripts import GenHmmPlots

def merge_tables(infile, output, sep,
                 merge_type, key_cols, nan_val):
    csvutils.merge_csv(infile, output, merge_type, key_cols)


def concatenate_csv(in_filenames, out_filename, nan_val='NA'):
    csvutils.concatenate_csv(in_filenames, out_filename)

def get_summary_metrics(infile, output):
    summ = SummaryMetrics(infile, output)
    summ.main()


def plot_kernel_density(infile, output, sep, colname, plot_title):
    plot = PlotKernelDensity(infile, output, sep, colname, plot_title)
    plot.main()

def plot_metrics(metrics, output, plot_title, gcbias_matrix, gc_content):
    plot = PlotMetrics(metrics, output, plot_title, gcbias_matrix, gc_content)
    plot.main()


def plot_heatmap(infile, metrics, order_data, output, plot_title=None,
                 column_name=None, plot_by_col=None, numreads_threshold=None,
                 mad_threshold=None, chromosomes=None, max_cn=None):

    plot = PlotHeatmap(infile, metrics, order_data, output, plot_title=plot_title,
                       column_name=column_name, plot_by_col=plot_by_col,
                       numreads_threshold=numreads_threshold,
                       mad_threshold=mad_threshold, chromosomes=chromosomes,
                       max_cn = max_cn)
    plot.main()

def plot_pcolor(infile, metrics, order_data, output, plot_title=None,
                 column_name=None, plot_by_col=None, numreads_threshold=None,
                 mad_threshold=None, chromosomes=None, max_cn=None):

    plot = PlotPcolor(infile, metrics, order_data, output, plot_title=plot_title,
                       column_name=column_name, plot_by_col=plot_by_col,
                       numreads_threshold=numreads_threshold,
                       mad_threshold=mad_threshold, chromosomes=chromosomes,
                       max_cn = max_cn)
    plot.main()


def plot_hmmcopy(reads, segments, params, metrics, sample_info, ref_genome, reads_out, segs_out,
                 bias_out, params_out, sample_id, num_states=7, plot_title=None,
                 mad_threshold=None, annotation_cols=None):
    plot = GenHmmPlots(reads, segments, params, metrics, sample_info, ref_genome, reads_out, segs_out,
                       bias_out, params_out, sample_id, num_states=num_states, plot_title=plot_title,
                       mad_threshold=mad_threshold, annotation_cols=annotation_cols)
    plot.main()


def filtersamps(samp, metrics, mad_threshold):
    mad = metrics[metrics['cell_id'] == samp]['mad_neutral_state'].iloc[0]
    if mad>mad_threshold:
        return True
    return False
    

def merge_pdf(in_filenames, out_filename, metrics, mad_threshold):

    metrics = pd.read_csv(metrics, sep=',')
    expconds = metrics["experimental_condition"].unique()

    cells = []
    for expcond in expconds:
        cells += sorted(metrics[metrics["experimental_condition"]==expcond]["cell_id"])

    for infiles, out_file in zip(in_filenames, out_filename):

        helpers.makedirs(out_file, isfile=True)

        infiles = [infiles[samp] for samp in cells\
                   if filtersamps(samp, metrics, mad_threshold)]

        pdfutils.merge_pdfs(infiles, out_file)
