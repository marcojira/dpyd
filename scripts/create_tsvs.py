import pandas as pd
from cyvcf2 import VCF


def get_gene_clin(variant):
    """
    :param variant: cyvcf2 variant object from ClinVar
    :return: Gene corresponding to variant, False if not found
    """
    if variant.INFO.get('GENEINFO') is None:
        return False

    return variant.INFO.get('GENEINFO').split(':')[0]


def get_gene_gnomad(variant):
    """
    :param variant: cyvcf2 variant object from gnomAD
    :return: Gene corresponding to variant
    """
    return variant.INFO.get('vep').split('|')[3]


def create_var_dict(var_list):
    """
    :param var_list: List of variants
    :return: Dictionary with following key/value pair: <CHROM>-<POS>-<REF>-<ALT>: variant
    """
    dict = {}

    for variant in var_list:
        var_id = str(variant.CHROM) + "-" + str(variant.POS) + "-" + variant.REF + "-" + ''.join(variant.ALT)

        dict[var_id] = variant

    return dict


def create_row_dict(gnomad_dict, clinvar_dict, output_dict):
    """
    Function to construct a row of the final .tsv
    :param gnomad_dict: A dictionary of var_id -> variant from gnomad
    :param clinvar_dict: A dictionary of var_id -> variant from clinvar
    :return: Dictionary with aggregated counts between what was already in output dict
    """

    for id, variant in gnomad_dict.items():

        # When variant only found in either exome or genome, construct entry from scratch
        if id not in output_dict.keys():

            # Basic fields
            output_dict[id] = {
                'VAR_ID': id,
                'CHR': variant.POS,
                'REF': variant.REF,
                'ALT': ''.join(variant.ALT),  # Formatted as list for some reason
                'QUAL': variant.QUAL,
                'FILTER': 'None' if variant.FILTER == None else variant.FILTER,
                'AC': variant.INFO.get('AC'),
                'AN': variant.INFO.get('AN'),
                'LOF': variant.INFO.get('vep').split('|')[64],  # LOF in vep field
                'INESSS': 'True' if id in inesss_var_id else 'False'
            }

            # If there is a Clin_SIG from ClinVar, use that one, else use provided one (always none so far)
            if id in clinvar_dict.keys():
                output_dict[id]['CLIN_SIG'] = clinvar_dict[id].INFO.get('CLNSIG')
            else:
                output_dict[id]['CLIN_SIG'] = variant.INFO.get('vep').split('|')[56]

            # Add AC, AN for each population
            for population in populations:
                output_dict[id]['AC' + '_' + population] = variant.INFO.get('AC' + '_' + population)
                output_dict[id]['AN' + '_' + population] = variant.INFO.get('AN' + '_' + population)

        # When it is in both genome and exome, add AC/AN of both
        else:


            # Add AC, AN for each population to get total AC/AN over genome and exome
            output_dict[id]['AC'] += variant.INFO.get('AC')
            output_dict[id]['AN'] += variant.INFO.get('AN')

            for population in populations:
                if variant.INFO.get('AC' + '_' + population) == None:
                    output_dict[id]['AC' + '_' + population] += 0
                else:
                    output_dict[id]['AC' + '_' + population] += variant.INFO.get('AC' + '_' + population)

                if variant.INFO.get('AN' + '_' + population) == None:
                    output_dict[id]['AN' + '_' + population] += 0
                else:
                    output_dict[id]['AN' + '_' + population] += variant.INFO.get('AN' + '_' + population)

    return output_dict


""" GET DPYD VARIANTS """

# Create lists of dpyd variants from ClinVar and gnomAD vcfs
clin_vcf = VCF('../data/clinvar_20190513.vcf.gz')
gnomad_exome_vcf = VCF('../data/gnomad.exomes.r2.1.1.sites.1.vcf.bgz')
gnomad_genome_vcf = VCF('../data/gnomad.genomes.r2.1.1.sites.1.vcf.bgz')

clin_dpyd_variants = []
for variant in clin_vcf('1:97443300-98486606'):
    if get_gene_clin(variant) == 'DPYD':
        clin_dpyd_variants.append(variant)

gnomad_exome_dpyd_variants = []
for variant in gnomad_exome_vcf('1:97443300-98486606'):
    if get_gene_gnomad(variant) == 'DPYD':
        gnomad_exome_dpyd_variants.append(variant)

gnomad_genome_dpyd_variants = []
for variant in gnomad_genome_vcf('1:97443300-98486606'):
    if get_gene_gnomad(variant) == 'DPYD':
        gnomad_genome_dpyd_variants.append(variant)

# Create dictionaries from list using var_id as key
clin_dict = create_var_dict(clin_dpyd_variants)
gnomad_exome_dict = create_var_dict(gnomad_exome_dpyd_variants)
gnomad_genome_dict = create_var_dict(gnomad_genome_dpyd_variants)


""" FORMAT DICTIONARIES """
inesss_var_id = ['1-97915614-C-T',
             '1-97547947-T-A',
             '1-97981343-A-C',
             '1-98039419-C-T'] # Variants recommended for testing by INESSS

populations = ["eas", "afr", "amr", "asj", "sas", "nfe", "fin"] # Populations available in gnomAD


# Create dictionary with relevant fields for each variant found in gnomad
clean_dict = {}
clean_dict = create_row_dict(gnomad_exome_dict, clin_dict, clean_dict) # Update entries from exome
clean_dict = create_row_dict(gnomad_genome_dict, clin_dict, clean_dict) # Update entries using genome

pre_filter_variants = pd.DataFrame.from_dict(clean_dict, orient='index')

# Export pre_filter version to .tsv
export_tsv = pre_filter_variants.to_csv (r'../data/clean_gnomad.tsv', index = None, header=True, sep='\t')


""" FILTER DATA """
LOFs = ["HC", "LC"]
CLIN_SIGs = ["pathogenic", "likely_pathogenic"]

# Get variants with no filter and that are either in INESSS, have a LOF or a CLIN_SIG
filtered_variants = pre_filter_variants.loc[
    (pre_filter_variants['FILTER'] == 'None') &
    (
        (pre_filter_variants['INESSS'] == 'True') |
        pre_filter_variants['LOF'].isin(LOFs) |
        pre_filter_variants['CLIN_SIG'].isin(CLIN_SIGs)
     )
]

# Export post_filter version to .tsv
export_tsv = filtered_variants.to_csv (r'../data/filtered_variants.tsv', index = None, header=True, sep='\t')

