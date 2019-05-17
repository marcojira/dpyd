# DPYD Loss of Function Analysis
Analysis of DPYD variants with loss of function characteristics and their frequency across different populations.

## Purpose
Use the **gnomAD** (genome and exome) and **ClinVar** VCF files to identify variants with potential loss of function. The VCFs are parsed in python using [cyvcf2](https://github.com/brentp/cyvcf2) (very fast parsing of VCF with region-queries) to find all variants which belong to the gene DPYD. These variants are then filtered to only include those with no filter and that either exhibit one of the three following characteristics:
 - One of the INESSS variants
 - Low or high confidence LOF
 - Likely pathogenic or pathogenic according to ClinVar

Once filtered, we compare the allele frequency of these variants as well as the relative frequency of the INESSS variants (compared to all the variants) for each population provided in gnomAD.

## Required Packages

 - numpy
 - pandas
 - cyvcf2
 - matplotlib
 - seaborn (for prettier graphs)

## Structure
```bash
│───analysis
│   ├───.tsv files are generated here
├───data
│   ├───Put data files here
│───scripts
│   ├───Python scripts are here
```


## Required Data

 - [gnomAD exome VCF (chromosome 1)](https://storage.googleapis.com/gnomad-public/release/2.1.1/vcf/exomes/gnomad.exomes.r2.1.1.sites.1.vcf.bgz)
	 - [Tabix](https://storage.googleapis.com/gnomad-public/release/2.1.1/vcf/exomes/gnomad.exomes.r2.1.1.sites.1.vcf.bgz.tbi)
 - [gnomAD genome VCF (chromosome 1)](https://storage.googleapis.com/gnomad-public/release/2.1.1/vcf/genomes/gnomad.genomes.r2.1.1.sites.1.vcf.bgz)
	 - [Tabix](https://storage.googleapis.com/gnomad-public/release/2.1.1/vcf/genomes/gnomad.genomes.r2.1.1.sites.1.vcf.bgz.tbi)
 - [ClinVar VCF (all chromosomes)](ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/clinvar_20190513.vcf.gz)
	 - [Tabix](ftp://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh37/clinvar_20190513.vcf.gz.tbi)
## Use

 1. Navigate in your command line to directory where you want to put project.
 2. Run `git clone https://github.com/MarcoJiralerspong/dpyd.git`
 3. `cd dpyd` and create folders called `data` and `analysis` respectively.
 4. Download all data files into `data` folder, for example with `wget url` (see structure above).
 5. Navigate to the `scripts` folder and run `python create_tsvs.py` to create .tsv files and then run `python create_graphs.py` to create the graph.
 6. All results will be placed in the `analysis` folder.

## Generated files
 - `clean_gnomad.tsv`: All DPYD variants with their associated ID, clinical signature, allele count, etc.
 - `filtered_variants`.tsv: Same fields as above but only filtered variants that meet the requirements described above.
