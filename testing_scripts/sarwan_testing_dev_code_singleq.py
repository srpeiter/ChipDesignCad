import numpy as np
from source_dev.chip import Base_Chip
import source_dev.transmon as transmon


dict_pads = {'width': 700,
             'height': 350,
             'lead_width': 20,
             'lead_height': 30,
             'rounded_edges': True,
             'layer': 1}

dict_pads2 = {'width': 700,
             'height': 350,
             'lead_width': 10,
             'lead_height': 40,
             'rounded_edges': True,
             'layer': 1}


# adding 0.1 at the end of the equation makes sure that we have some extra room

# Note that overlap cannot be negative!!!!!
w_dolan_bridge = 0.2
appr_overlap = (2 * (320 - 40) * np.tan(35 * np.pi / 180) -
                w_dolan_bridge * 1e3) / 1e3 + 0.1

print appr_overlap
dict_junctions = {'bjunction_width': 2,
                  'bjunction_height':20,
                  'junction_width': 0.1,
                  'junction_height': 1,
                  'w_dolan_bridge': w_dolan_bridge,
                  'appr_overlap': appr_overlap,
                  'overl_junc_lead': 2.1,
                  'layer': 3}

dict_junctions2 = {'bjunction_width': 2,
                  'bjunction_height':10,
                  'junction_width': 0.1,
                  'junction_height': 1,
                  'w_dolan_bridge': w_dolan_bridge,
                  'appr_overlap': appr_overlap,
                  'overl_junc_lead': 2.1,
                  'layer': 3}


first_qubit = transmon.Singlejunction_transmon('test', dict_pads,
                                              dict_junctions, short=False)
first_qubit.gen_pattern()

dict_squidloop = {'squid_thickness': 8,
                  'squid_width': 10,
                  'squid_height': 10}

second_qubit = transmon.Squidjunction_transmon('test2', dict_pads2, dict_squidloop,
                                              dict_junctions2)
second_qubit.gen_pattern()
chip = Base_Chip('test_single junction transmon_chip', 9000, 9000)
for i in range(3):

  chip.add_component(first_qubit.cell, (-2000 +i*2000, -2000 ))

for i in range(2):
  for j in range(3):
    chip.add_component(second_qubit.cell, (-2000 +j*2000, 0 +i*2000))

# chip.add_component(first_qubit.cell, (0, 0))
# chip.add_component(second_qubit.cell, (1000, 0))
chip.save_to_gds(save=True,show=True)
