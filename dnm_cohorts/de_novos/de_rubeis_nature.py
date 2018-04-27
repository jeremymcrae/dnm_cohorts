
import pandas

url = "http://www.nature.com/nature/journal/v515/n7526/extref/nature13772-s4.xlsx"

def de_rubeis_de_novos():
    """ get de novo data from the 2014 De Rubeis et al. autism exome study in Nature
    
    De novo mutation data sourced from Supplementary table 3:
    De Rubeis et al. (2013) Nature 515:209-215
    doi: 10.1038/nature13772
    
    Returns:
        data frame of de novos, including gene symbol, functional consequence
         (VEP format), chromosome, nucleotide position
    """
    
    data = pandas.read_excel(url, sheet_name="De Novo", skip_footer=1)
    
    # rename columns to match the other de novo datasets
    data = data.rename(columns={'Chr': 'chrom', 'Pos': 'pos',
        'Child_ID': 'person_id', 'Ref': 'ref', 'Alt': 'alt'})
    
    # strip whitespace and ensure columns are string
    for col in ['person_id', 'chrom', 'ref', 'alt']:
        data[col] = data[col].astype(str).str.replace(' |\t', '')
    
    data['study'] = "derubeis_nature_2014"
    
    return data[["person_id", "chrom", "pos", "ref", "alt", "study"]]
