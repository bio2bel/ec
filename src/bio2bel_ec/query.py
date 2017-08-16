import pyuniprot
pyuniprot.update(taxids=[9606, 10090, 10116])

query = pyuniprot.query()