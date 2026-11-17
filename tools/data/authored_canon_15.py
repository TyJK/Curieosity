"""
Curieosity's industrial chemistry, part 15 (see authored_canon.py): the compounds first set
aside because their route's vessel and reactants were already taken, each given another
real route.
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E4, E5  # noqa: F401
from gen_authored import (CAT, FLASK, HEAT, HIGHP, FERM)  # noqa: F401


# --- the canon substances ------------------------------------------------------------------
S("2004-70-8", "Piperylene", "Piperylene", "C5H8", "Liquid", 12234794,
  "1,3-Pentadiene, the five-carbon diene from steam cracking: a monomer for the hydrocarbon "
  "resins in adhesives.", lib=6085, smiles="C=CC=CC")
S("513-85-9", "BDO23", "2,3-Butanediol", "C4H10O2", "Liquid", 13948661,
  "A small diol that bacteria make from sugar; dehydrated, it gives methyl ethyl ketone.",
  lib=6164, smiles="OC(C)C(O)C")
S("10016-20-3", "AlphaCD", "alpha-Cyclodextrin", "C36H60O30", "Solid", 20213052,
  "Six glucoses in a ring, the smallest cyclodextrin: its narrow cavity holds small molecules.",
  lib=2035, smiles="OCC1OC2OC3C(O)C(O)C(OC3CO)OC4C(O)C(O)C(OC4CO)OC5C(O)C(O)C(OC5CO)OC6C(O)C(O)"
                   "C(OC6CO)OC7C(O)C(O)C(OC7CO)OC1C(O)C2O")
S("112-49-2", "Triglyme", "Triglyme", "C8H18O4", "Liquid", 36267103,
  "Triethylene glycol dimethyl ether: a high-boiling reaction solvent, and a component of "
  "brake fluids and paint strippers.", lib=2717, smiles="O(C)CCOCCOCCOC")
S("124-02-7", "Diallylamine", "Diallylamine", "C6H11N", "Liquid", 70206705,
  "A secondary amine with two allyl arms; it becomes the herbicide safener dichlormid and the "
  "monomer DADMAC.", lib=3101, smiles="C=CCNCC=C")
S("5657-17-0", "EDDA", "Ethylenediaminediacetic acid", "C6H12N2O4", "Solid", 56137857,
  "Two glycines joined at their nitrogens by an ethylene bridge: a smaller cousin of EDTA that "
  "also grips metal ions.", lib=6566, smiles="O=C(O)CNCCNCC(=O)O")


# --- the reactions -------------------------------------------------------------------------
E4.reactions += [
    R("Piperylene from the C5 Cut", "Hexane -> Piperylene + Methane + H2", HEAT,
      "Light naphtha cracked hot with steam; piperylene is distilled from the five-carbon cut "
      "that comes off with the ethylene.", wiki="Piperylene", T=850),
    R("Butanediol Fermentation", "Sucrose + O2 -> 2 BDO23 + 4 CO2 + H2O", FERM,
      "Klebsiella ferments molasses sugar with the air held back: the scarcer the oxygen, the "
      "more of the sugar ends as butanediol.", wiki="Butanediol_fermentation", T=37),
]
E5.reactions += [
    R("Alpha-Cyclodextrin", "Starch -> AlphaCD", FLASK,
      "Starch paste stirred warm with the enzyme cyclodextrin glucanotransferase; a guest "
      "molecule added to the tank steers it towards the six-sugar ring.", wiki=20213052, T=50,
      exact=False),
    R("Triglyme", "Diglyme + EO -> Triglyme", CAT,
      "Boron trifluoride opens one more ethylene oxide into diglyme's chain, the same insertion "
      "that builds glymes from dimethyl ether.", wiki=36267103, cat="BF3", T=50),
    R("Diallylamine", "2 Acrylonitrile + 4 H2 -> Diallylamine + NH3", HIGHP,
      "Acrylonitrile hydrogenated only part way: two half-reduced molecules couple, and ammonia "
      "leaves.", wiki="Diallylamine", T=100),
    R("Ethylenediaminediacetic Acid", "EDA + 2 ClAcOH + 2 NaOH -> EDDA + 2 NaCl + 2 H2O", FLASK,
      "Ethylenediamine alkylated once at each end by chloroacetic acid, with caustic soda taking "
      "up the hydrogen chloride.", wiki=56137857, T=80),
]

import authored_canon_16  # noqa: E402,F401
