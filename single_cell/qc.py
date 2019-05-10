'''
Created on Feb 19, 2018

@author: dgrewal
'''
import os
import pypeliner
import pypeliner.managed as mgd
from workflows import align,alignment_metrics, hmmcopy, qc_annotation
from single_cell.utils import helpers
import copy


def qc_workflow(args):

    config = helpers.load_config(args)

    align_config = config['alignment']

    sampleinfo = helpers.get_sample_info(args['input_yaml'])
    cellids = helpers.get_samples(args['input_yaml'])
    bam_files, _ = helpers.get_bams(args['input_yaml'])

    lib = args["library_id"]

    outdir = os.path.join(args["out_dir"], "results", "alignment")

    alignment_metrics_csv = os.path.join(outdir, '{}_alignment_metrics.csv.gz'.format(lib))
    gc_metrics_csv = os.path.join(outdir, '{}_gc_metrics.csv.gz'.format(lib))
    plots_dir = os.path.join(outdir,  'plots')
    plot_metrics_output = os.path.join(plots_dir, '{}_plot_metrics.pdf'.format(lib))

    ctx={'docker_image': align_config['docker']['single_cell_pipeline']}
    workflow = pypeliner.workflow.Workflow(ctx=ctx)

    if args['alignment']:

        if not args["metrics_only"]:
            fastq1_files, fastq2_files = helpers.get_fastqs(args['input_yaml'])
            triminfo = helpers.get_trim_info(args['input_yaml'])
            centerinfo = helpers.get_center_info(args['input_yaml'])

            workflow.setobj(
                obj=mgd.OutputChunks('cell_id', 'lane'),
                value=list(fastq1_files.keys()),
            )

            workflow.subworkflow(
                name='alignment_workflow',
                func=align.create_alignment_workflow,
                args=(
                    mgd.InputFile('fastq_1', 'cell_id', 'lane', fnames=fastq1_files, axes_origin=[]),
                    mgd.InputFile('fastq_2', 'cell_id', 'lane', fnames=fastq2_files, axes_origin=[]),
                    mgd.OutputFile('bam_markdups', 'cell_id', fnames=bam_files, axes_origin=[], extensions=['.bai']),
                    align_config['ref_genome'],
                    align_config,
                    args,
                    triminfo,
                    centerinfo,
                    sampleinfo,
                    cellids,
                ),
            )
        else:
            workflow.setobj(
                obj=mgd.OutputChunks('cell_id'),
                value=cellids,
            )

        workflow.subworkflow(
            name='metrics_workflow',
            func=alignment_metrics.create_alignment_metrics_workflow,
            args=(
                mgd.InputFile('bam_markdups', 'cell_id', fnames = bam_files, axes_origin=[], extensions=['.bai']),
                mgd.OutputFile(alignment_metrics_csv),
                mgd.OutputFile(gc_metrics_csv),
                mgd.OutputFile(plot_metrics_output),
                align_config['ref_genome'],
                align_config,
                args,
                sampleinfo,
                cellids,
            ),
        )

    if args['hmmcopy']:
        for params_tag, params in config['hmmcopy'].iteritems():
            params_tag = "hmmcopy_" + params_tag

            multipliers = copy.deepcopy(params["multipliers"])
            multipliers = [0] + multipliers
            workflow.setobj(
                obj=mgd.OutputChunks('multiplier'),
                value=multipliers,
            )

            results_dir = os.path.join(args['out_dir'], 'results', params_tag)

            reads_csvs = os.path.join(
                results_dir, '{0}_multiplier{1}_reads.csv.gz'.format(lib, '{multiplier}'))
            segs_csvs = os.path.join(
                results_dir, '{0}_multiplier{1}_segments.csv.gz'.format(lib, '{multiplier}'))
            params_csvs = os.path.join(
                results_dir, '{0}_multiplier{1}_params.csv.gz'.format(lib, '{multiplier}'))
            metrics_csvs = os.path.join(
                results_dir, '{0}_multiplier{1}_metrics.csv.gz'.format(lib, '{multiplier}'))
            igv_csvs = os.path.join(
                results_dir, '{0}_multiplier{1}_igv_segments.seg'.format(lib, '{multiplier}'))

            plots_dir = os.path.join(results_dir, "plots")
            segs_pdf = os.path.join(
                plots_dir, "segments", '{}_segs.tar.gz'.format(lib))
            bias_pdf = os.path.join(plots_dir, "bias", '{}_bias.tar.gz'.format(lib))

            heatmap_filt_pdf = os.path.join(
                plots_dir, '{}_heatmap_by_ec_filtered.pdf'.format(lib))
            heatmap_pdf = os.path.join(
                plots_dir, '{}_heatmap_by_ec.pdf'.format(lib))
            metrics_pdf = os.path.join(
                plots_dir, '{}_metrics.pdf'.format(lib))
            kernel_density_pdf = os.path.join(
                plots_dir, '{}_kernel_density.pdf'.format(lib))

            workflow.subworkflow(
                name='hmmcopy_workflow_' + params_tag,
                func=hmmcopy.create_hmmcopy_workflow,
                args=(
                    mgd.InputFile('bam_markdups', 'cell_id', fnames=bam_files, extensions=['.bai']),
                    mgd.OutputFile("reads.csv.gz", 'multiplier', template=reads_csvs, axes_origin=[]),
                    mgd.OutputFile("segs.csv.gz", 'multiplier', template=segs_csvs, axes_origin=[]),
                    mgd.OutputFile("metrics.csv.gz", 'multiplier', template=metrics_csvs, axes_origin=[]),
                    mgd.OutputFile("params.csv.gz", 'multiplier', template=params_csvs, axes_origin=[]),
                    mgd.OutputFile("igv.seg", 'multiplier', template=igv_csvs, axes_origin=[]),
                    mgd.OutputFile(segs_pdf),
                    mgd.OutputFile(bias_pdf),
                    mgd.OutputFile(heatmap_pdf),
                    mgd.OutputFile(heatmap_filt_pdf),
                    mgd.OutputFile(metrics_pdf),
                    mgd.OutputFile(kernel_density_pdf),
                    cellids,
                    params,
                ),
            )

    if args['annotation']:
        workflow.subworkflow(
            name='annotation_workflow',
            func=qc_annotation.create_qc_annotation_workflow,
            args=(
            ),
        )


    return workflow