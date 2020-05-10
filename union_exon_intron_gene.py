import pandas as pd
import re
import csv

all_exons =  pd.read_csv('D:\\MCGDYY\\ont_project\\gtf_files\\sub.gtf', 
	sep = '\t', chunksize = 10000, header= None, comment = '#',
	names = ['chromosome', 'source', 'type', 'start', 'end', 'none1', 'strand', 'none2', 'info'])
all_exons = pd.concat(all_exons, ignore_index = True)

# append a column of gene names
for i in all_exons.index:
	info = all_exons.loc[i, 'info']
	gene_name = re.findall(r"gene_id \"(.*?)\";", info)[0]
	all_exons.loc[i, 'gene'] = gene_name

exon_collector = pd.DataFrame(columns = ['chromosome', 'source', 'type', 'start', 'end', 'none1', 'strand', 'none2', 'info'])
intron_collector = pd.DataFrame(columns = ['chromosome', 'source', 'type', 'start', 'end', 'none1', 'strand', 'none2', 'info'])

gene_list = set(all_exons['gene'])
for i in gene_list:
	gene_table = all_exons[all_exons['gene'] == i]
	# avoid single-exon genes
	if len(gene_table) > 1:
		gene_table.sort_values(by = 'start', inplace = True)
		gene_table.reset_index(drop = True, inplace = True)

		# find union-exons in a gene
		tmp = pd.DataFrame(columns = ['chromosome', 'source', 'type', 'start', 'end', 'none1', 'strand', 'none2', 'info'])
		s0 = gene_table.loc[0, 'start']
		e0 = gene_table.loc[0, 'end']
		for k in gene_table.index:
			s1 = gene_table.loc[k, 'start']
			e1 = gene_table.loc[k, 'end'] 
			
			if s1 < e0 and e1 > e0:
				e0 = e1

			# found a discontinuous exon
			if s1 > e0:
				# firstly append the previous exon into the tmp collector
				cur_len = len(tmp)
				tmp.loc[cur_len, 'chromosome'] = gene_table.loc[0, 'chromosome']
				tmp.loc[cur_len, 'start'] = s0
				tmp.loc[cur_len, 'end'] = e0
				tmp.loc[cur_len, 'strand'] = gene_table.loc[0, 'strand']
				tmp.loc[cur_len, 'info'] = "gene_id \"" + i + "\""
				# secondly define the new discontinuous exon
				s0 = s1
				e0 = e1

			# when we are at the last line of the gene_table, append the last exon and append tmp into exon_collector
			if k + 1 == len(gene_table):
				cur_len = len(tmp)
				tmp.loc[cur_len, 'chromosome'] = gene_table.loc[0, 'chromosome']
				tmp.loc[cur_len, 'start'] = s0
				tmp.loc[cur_len, 'end'] = e0
				tmp.loc[cur_len, 'strand'] = gene_table.loc[0, 'strand']
				tmp.loc[cur_len, 'info'] = "gene_id \"" + i + "\""
				exon_collector = exon_collector.append(tmp)

		# get the intronic regions of this gene based on union-exons in tmp
		for j in tmp.index:
			# avoid the last line
			if j + 1 != len(tmp):
				cur_len = len(intron_collector)
				intron_collector.loc[cur_len, 'chromosome'] = gene_table.loc[0, 'chromosome']
				intron_collector.loc[cur_len, 'start'] = tmp.loc[j, 'end'] + 1
				intron_collector.loc[cur_len, 'end'] = tmp.loc[j + 1, 'start'] - 1
				intron_collector.loc[cur_len, 'strand'] = gene_table.loc[0, 'strand']
				intron_collector.loc[cur_len, 'info'] = "gene_id \"" + i + "\""

exon_collector['source'] = '.'
exon_collector['type'] = 'exon'
exon_collector['none1'] = '.'
exon_collector['none2'] = '.'
intron_collector['source'] = '.'
intron_collector['type'] = 'intron'
intron_collector['none1'] = '.'
intron_collector['none2'] = '.'

exon_collector.to_csv('D:\\MCGDYY\\ont_project\\gtf_files\\anno_gene_union_exons.gtf', 
	header = None, index = False, sep = '\t', quoting = csv.QUOTE_NONE)
intron_collector.to_csv('D:\\MCGDYY\\ont_project\\gtf_files\\anno_gene_union_intron.gtf', 
	header = None, index = False, sep = '\t', quoting = csv.QUOTE_NONE)