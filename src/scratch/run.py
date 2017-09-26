from bio2bel_ec.tree import write_expasy_tree, standard_ec_id
from bio2bel_ec.enrich import get_parent
import pybel
from pybel.constants import PROTEIN

import pyuniprot
pyuniprot.set_mysql_connection()

#with open('/home/agrigoryan/expasy_enzyme.bel', 'w+') as f:
#    write_expasy_tree(f)

ec = standard_ec_id('1.14.99.1')
ec_p = standard_ec_id('1.14.99.-')
ec_pp = standard_ec_id('1.14. -.-')
ec_ppp = standard_ec_id('1. -. -.-')

cyclooxygenase = PROTEIN, 'HGNC', 'PTGS2'
cyclooxygenase_ec = PROTEIN, 'EC', ec
cyclooxygenase_ec_p = PROTEIN, 'EC', ec_p
cyclooxygenase_ec_pp = PROTEIN, 'EC', ec_pp
cyclooxygenase_ec_ppp = PROTEIN, 'EC', ec_ppp

#bgraph = pybel.BELGraph()
#bgraph = pybel.from_path('/home/agrigoryan/belscript.bel', no_identifier_validation=True)
#f = open('/home/agrigoryan/dd.txt', 'w+')

#bgraph.add_simple_node(*cyclooxygenase_ec)
#bgraph.add_simple_node(PROTEIN, 'EC',get_parent(cyclooxygenase_ec[-1]))
#bgraph.add_edge(cyclooxygenase_ec, cyclooxygenase_ec_p)
#for edge in bgraph.edges():
#    print(edge)
#print(bgraph.node[cyclooxygenase_ec]['function'])
#pybel.to_csv(bgraph, file=f)
#print(bgraph)

###

#query = pyuniprot.query()
#print(query.entry(as_df=True))

from bio2bel_ec.enzyme import expasy_parser
db = expasy_parser()
for entry in db:
    if entry['DELETED'] == True:
        print(entry['ID'])

