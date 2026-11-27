"""
Curieosity's industrial chemistry, part 16 (see authored_canon.py): compounds first set aside
because the game lacked a raw material or an intermediate on their route. The intermediates
come first (each with a Wikipedia article of its own), then the compounds they open up, and
one new raw material: colza oil, the high-erucic rapeseed oil grown for industry.
"""

from authored_canon import S, R  # noqa: F401
from authored_content import E3, E4, E5, E6, RAW  # noqa: F401
from gen_authored import (MIX, HEAT, COOL, DISTIL, ELEC, LIGHT, CAT, PRESS, POLY, FLASK, BLAST, SMELT,  # noqa: F401
                          ARC, COLUMN, ECELL, CRACKER, HIGHP, FERM, BIOR)
import authored_content as _C

# --- a new raw material: colza oil, granted with the other oils at the chlorine milestone ----
RAW("ColzaOil", "Colza Oil", "Industrial rapeseed oil: natural rapeseed, not the low-erucic canola bred for "
    "food, whose fat is about half erucic acid. Burned in lamps before kerosene.", "Rapeseed_oil", "#c8b040",
    formula="C69H128O6", state="Liquid")
for _m in _C.MILESTONES:
    if _m.on == "Cl2" and "ColzaOil" not in _m.grant:
        _m.grant = tuple(_m.grant) + ("ColzaOil",)

# --- intermediates -----------------------------------------------------------------------
S(None, "ONCB", "2-Nitrochlorobenzene", "C6H4ClNO2", "Solid", "2-Nitrochlorobenzene",
  "The ortho third of chlorobenzene's nitration: the way into o-phenylenediamine, o-anisidine and the "
  "yellow pigments.", lib=116750)
S(None, "oNitroaniline", "2-Nitroaniline", "C6H6N2O2", "Solid", "2-Nitroaniline",
  "Orange crystals; reduced, it becomes o-phenylenediamine, the parent of the benzimidazoles.", lib=8576)
S(None, "DCB", "3,3'-Dichlorobenzidine", "C12H10Cl2N2", "Solid", "3,3'-Dichlorobenzidine",
  "Doubly diazotised, it couples into the diarylide yellows of printing ink; a carcinogen handled wet.",
  smiles="Nc1ccc(cc1Cl)-c1ccc(N)c(Cl)c1")
S(None, "Hexanol", "1-Hexanol", "C6H14O", "Liquid", "1-Hexanol",
  "A six-carbon alcohol with the smell of cut grass; a building block for flavour esters.", smiles="CCCCCCO")
S(None, "Octanol", "1-Octanol", "C8H18O", "Liquid", "1-Octanol",
  "The eight-carbon fatty alcohol; its partition with water (log P) is chemistry's yardstick for "
  "how fatty a molecule is.", smiles="CCCCCCCCO")
S(None, "Decanol", "1-Decanol", "C10H22O", "Liquid", "1-Decanol",
  "A ten-carbon fatty alcohol from coconut oil, made into surfactants and plasticisers.", smiles="CCCCCCCCCCO")
S(None, "CetylAlcohol", "Cetyl alcohol", "C16H34O", "Solid", "Cetyl_alcohol",
  "Palmityl alcohol, first got from sperm-whale oil (cetus); now from palm oil. Thickens creams.",
  smiles="CCCCCCCCCCCCCCCCO")
S(None, "Sarcosine", "Sarcosine", "C3H7NO2", "Solid", "Sarcosine",
  "N-Methylglycine, an amino acid of the body's own; acylated with fatty acids it makes mild surfactants.",
  smiles="CNCC(=O)O")
S(None, "Adamantane", "Adamantane", "C10H16", "Solid", "Adamantane",
  "Ten carbons locked in the shape of a piece of diamond lattice; it sublimes at room temperature.",
  smiles="C1C2CC3CC1CC(C2)C3")
S(None, "HBA4", "4-Hydroxybenzaldehyde", "C7H6O2", "Solid", "4-Hydroxybenzaldehyde",
  "Phenol with an aldehyde opposite the OH: the start of raspberry ketone and of several drugs.",
  smiles="O=Cc1ccc(O)cc1")
S(None, "Butylamine", "n-Butylamine", "C4H11N", "Liquid", "N-Butylamine",
  "A fishy-smelling amine made from butanol and ammonia; it goes into pesticides, rubber chemicals and drugs.",
  smiles="CCCCN")
S(None, "PSCl3", "Thiophosphoryl chloride", "PSCl3", "Liquid", "Thiophosphoryl_chloride",
  "Phosphorus trichloride with a sulfur atom added: the start of the thiophosphate insecticides.", lib=107743)
S(None, "HeptanoicAcid", "Heptanoic acid", "C7H14O2", "Liquid", "Heptanoic_acid",
  "Enanthic acid, from the heptanal of cracked castor oil; its esters are fruity, its smell rancid.",
  smiles="CCCCCCC(=O)O")
S(None, "Acrylamide", "Acrylamide", "C3H5NO", "Solid", "Acrylamide",
  "Acrylonitrile with water added by an enzyme; polymerised it thickens water for paper-making and gels.",
  smiles="C=CC(N)=O")
S(None, "HMF", "Hydroxymethylfurfural", "C6H6O3", "Solid", "Hydroxymethylfurfural",
  "Fructose that has lost three waters: the furan behind the colour of honey and a hope for green fuels.",
  smiles="O=Cc1ccc(CO)o1")
S(None, "Phthalonitrile", "Phthalonitrile", "C8H4N2", "Solid", "Phthalonitrile",
  "Two nitrile groups side by side on a benzene ring; four of them close into a phthalocyanine.",
  smiles="N#Cc1ccccc1C#N")
S(None, "FuroicAcid", "2-Furoic acid", "C5H4O3", "Solid", "2-Furoic_acid",
  "Furfural's acid, from the Cannizzaro reaction that turns two aldehydes into an acid and an alcohol.",
  smiles="OC(=O)c1ccco1")
S(None, "EtCl", "Chloroethane", "C2H5Cl", "Gas", "Chloroethane",
  "Ethyl chloride: once mostly turned into tetraethyllead; sprayed on skin it numbs by cold.",
  smiles="CCCl")
S(None, "DEG", "Diethylene glycol", "C4H10O3", "Liquid", "Diethylene_glycol",
  "Two ethylene glycols joined by an ether oxygen; sweet and poisonous, it killed over a hundred in the "
  "1937 Elixir Sulfanilamide disaster.", smiles="OCCOCCO")
S(None, "SnCl2", "Tin(II) chloride", "SnCl2", "Solid", "Tin(II)_chloride",
  "Stannous chloride, a mild reducing agent: tin dissolved in hydrochloric acid.", smiles="Cl[Sn]Cl")
S(None, "Benzonitrile", "Benzonitrile", "C7H5N", "Liquid", "Benzonitrile",
  "Toluene's methyl group turned into a nitrile by ammonia and air; an almond-smelling solvent.",
  smiles="N#Cc1ccccc1")

# --- the canon substances ------------------------------------------------------------------
S("112-86-7", "ErucicAcid", "Erucic acid", "C22H42O2", "Solid", 302078,
  "A 22-carbon fatty acid making up half of natural rapeseed oil; its amide keeps plastic film from sticking.",
  lib=2731)
S("112-85-6", "BehenicAcid", "Behenic acid", "C22H44O2", "Solid", "Behenic_acid",
  "Docosanoic acid, named after ben oil from moringa seeds; a waxy fat for hair conditioners.", lib=2730)
S("505-52-2", "BrassylicAcid", "Brassylic acid", "C13H24O4", "Solid", 72432625,
  "Tridecanedioic acid, cut from erucic acid by ozone; it makes musks and special nylons.", lib=6088)
S("121-32-4", "Ethylvanillin", "Ethylvanillin", "C9H10O3", "Solid", 19035891,
  "Vanillin with an ethyl group for a methyl: about three times as strong, and never found in vanilla.", lib=2979)
S("95-14-7", "Benzotriazole", "Benzotriazole", "C6H5N3", "Solid", 11363337,
  "A thin film of it stops copper tarnishing; it is in dishwasher tablets and aircraft de-icing fluid.",
  smiles="c1ccc2[nH]nnc2c1")
S("77-98-5", "TEAOH", "Tetraethylammonium hydroxide", "C8H21NO", "Liquid", 63139075,
  "A strong organic base; it templates the pores of some zeolite catalysts.", lib=8075)
S("665-46-3", "TEAF", "Tetraethylammonium fluoride", "C8H20FN", "Solid", 902918,
  "Fluoride as a soluble, organic salt: a reagent for putting fluorine into molecules.", lib=7249)
S("6197-30-4", "Octocrylene", "Octocrylene", "C24H27NO2", "Liquid", 4344583,
  "A sunscreen filter for UVB that also steadies more fragile filters such as avobenzone.", lib=6937)
S("591-22-0", "Lutidine35", "3,5-Lutidine", "C7H9N", "Liquid", 61707641,
  "3,5-Dimethylpyridine, built from aldehydes and ammonia; the start of the ulcer drug omeprazole.", lib=6753)
S("35794-11-7", "DMPip35", "3,5-Dimethylpiperidine", "C7H15N", "Liquid", 40463317,
  "Hydrogenated 3,5-lutidine; a base and a template for zeolites.", lib=5494)
S("90-00-6", "EtPhenol2", "2-Ethylphenol", "C8H10O", "Liquid", 69494491,
  "Phenol with an ethyl group beside the OH; on the way to the dyes and the drug etofenamate.", lib=8622)
S("622-96-8", "pEthyltoluene", "4-Ethyltoluene", "C9H12", "Liquid", 51325456,
  "Made so that its ethyl group can lose hydrogen to give p-methylstyrene, a monomer for clearer plastics.",
  lib=6962)
S("7173-51-5", "DDAC", "Didecyldimethylammonium chloride", "C22H48ClN", "Solid", 12813475,
  "A quaternary ammonium disinfectant for hospital surfaces and swimming pools.", lib=7715)
S("7790-62-7", "K2S2O7", "Potassium pyrosulfate", "K2S2O7", "Solid", 13676264,
  "Molten, it dissolves stubborn oxides in the lab; also a component of sulfuric-acid catalysts.", lib=8161)
S("90-04-0", "oAnisidine", "o-Anisidine", "C7H9NO", "Liquid", 17292148,
  "2-Methoxyaniline, an amine for azo dyes and the drug guaifenesin's cousins.", lib=8623)
S("94317-64-3", "NBPT", "N-(n-Butyl)thiophosphoric triamide", "C4H14N3PS", "Solid", 66226078,
  "Coated on urea fertiliser, it slows the soil enzyme urease so less nitrogen escapes as ammonia.", lib=8804)
S("95-54-5", "OPD", "o-Phenylenediamine", "C6H8N2", "Solid", 3068051,
  "Two amines side by side on a ring: closed up with acids they make benzimidazoles, fungicides and drugs.",
  lib=8822)
S("95-65-8", "Xylenol34", "3,4-Xylenol", "C8H10O", "Solid", 6100539,
  "3,4-Dimethylphenol, once a coal-tar acid; disinfectants and vitamin E start from xylenols.", lib=8825)
S("95-87-4", "Xylenol25", "2,5-Xylenol", "C8H10O", "Liquid", 3399664,
  "2,5-Dimethylphenol, the start of the cholesterol drug gemfibrozil.", lib=8828)
S("104-61-0", "gNonalactone", "gamma-Nonalactone", "C9H16O2", "Liquid", 49408946,
  "'Aldehyde C-18' to perfumers, though it is a lactone: the smell of coconut.", lib=2286)
S("66-25-1", "Hexanal", "Hexanal", "C6H12O", "Liquid", 14571189,
  "The smell of freshly cut grass, and of fats going off.", lib=7221)
S("142-92-7", "HexylAcetate", "Hexyl acetate", "C8H16O2", "Liquid", 28416118,
  "A pear-scented ester for flavours, and a slow-drying lacquer solvent.", lib=3664)
S("112-02-7", "CTAC", "Cetrimonium chloride", "C19H42ClN", "Liquid", 5349042,
  "A cationic surfactant that clings to hair and smooths it: the active part of most conditioners.", lib=2701)
S("122-18-9", "BKC16", "Cetalkonium chloride", "C25H46ClN", "Solid", 22561086,
  "A benzalkonium antiseptic with a sixteen-carbon tail, in mouth gels and eye drops.", lib=3019)
S("540-10-3", "CetylPalmitate", "Cetyl palmitate", "C32H64O2", "Solid", 25399724,
  "The main wax of spermaceti, now made from palm oil, for cosmetics and candles.", lib=6370)
S("123-96-6", "Octanol2", "2-Octanol", "C8H18O", "Liquid", 45660291,
  "The other half of castor oil's caustic fusion, beside sebacic acid; a frother in ore flotation.", lib=3092)
S("137-16-6", "SLSarc", "Sodium lauroyl sarcosinate", "C15H28NNaO3", "Liquid", 14754966,
  "A mild foaming surfactant from coconut fat and sarcosine, in toothpastes and baby shampoos.", lib=3511)
S("110-25-8", "Oleoylsarcosine", "Oleoyl sarcosine", "C21H39NO3", "Solid", 52344511,
  "An oily corrosion inhibitor for lubricants and fuels.", lib=2590)
S("919-30-2", "APTES", "(3-Aminopropyl)triethoxysilane", "C9H23NO3Si", "Liquid",
  "(3-Aminopropyl)triethoxysilane",
  "Silanes like this glue glass to plastics: the ethoxy end bonds to the glass, the amine to the resin.", lib=8707)
S("40372-72-3", "Si69", "Bis(triethoxysilylpropyl) tetrasulfide", "C18H42O6S4Si2", "Liquid", 45532908,
  "Bonds silica filler into tyre rubber for 'green' tyres that roll more easily.", lib=5723)
S("5333-42-6", "Octyldodecanol", "2-Octyldodecanol", "C20H42O", "Liquid", 19887814,
  "A Guerbet alcohol: branched, so it stays liquid; an emollient in creams and lipsticks.", lib=6311)
S("6358-85-6", "PY12", "Pigment Yellow 12", "C32H26Cl2N6O4", "Solid", 55053258,
  "Diarylide yellow, the yellow of most printing ink, including the Y in CMYK.", lib=7056)
S("694-83-7", "DACH", "1,2-Diaminocyclohexane", "C6H14N2", "Solid", 63644909,
  "Its mirror-image forms hold platinum in the cancer drug oxaliplatin.", lib=7623)
S("78-08-0", "VTEO", "Vinyltriethoxysilane", "C8H18O3Si", "Liquid", 52363271,
  "Grafted onto polyethylene, it lets the plastic cross-link in water for cable insulation.", lib=8171)
S("89-00-9", "QuinolinicAcid", "Quinolinic acid", "C7H5NO4", "Solid", 15648814,
  "Pyridine-2,3-dicarboxylic acid; also made in the brain, where too much of it harms neurons.", lib=8593)
S("665-66-7", "AmantadineHCl", "Amantadine hydrochloride", "C10H18ClN", "Solid", 1128227,
  "An adamantane with an amine: an old flu drug, now used for Parkinson's disease.", lib=7250)
S("115-27-5", "ChlorendicAnhydride", "Chlorendic anhydride", "C9H2Cl6O3", "Solid", 3156026,
  "Six chlorines carried into polyesters to make them fire-retardant.", lib=2782)
S("24650-42-8", "DMPAP", "2,2-Dimethoxy-2-phenylacetophenone", "C16H16O3", "Solid", 28276736,
  "A photoinitiator: ultraviolet light splits it into radicals that set inks and dental fillings.", lib=4671)
S("5471-51-2", "RaspberryKetone", "Raspberry ketone", "C10H12O2", "Solid", 12102450,
  "The scent of raspberries; the fruit holds so little that it is made from other chemicals.", lib=6433)
S("103-95-7", "CyclamenAldehyde", "Cyclamen aldehyde", "C13H18O", "Liquid", 44750710,
  "A fresh floral note for soaps, named after the cyclamen flower though not found in it.", lib=2243)
S("106-30-9", "EthylHeptanoate", "Ethyl heptanoate", "C9H18O2", "Liquid", 3292511,
  "A grape and brandy note for flavours.", lib=2381)
S("1072-63-5", "Vinylimidazole", "1-Vinylimidazole", "C5H6N2", "Liquid", 53794817,
  "A monomer whose polymers grab dyes and metals.", lib=2479)
S("109-46-6", "DBTU", "N,N'-Dibutylthiourea", "C9H20N2S", "Liquid", 45259842,
  "A corrosion inhibitor and rubber accelerator.", lib=2556)
S("110-26-9", "MBA", "Methylenebisacrylamide", "C7H10N2O2", "Solid", 19797219,
  "The cross-linker in polyacrylamide gels, the jelly that sorts DNA and proteins by size.", lib=2591)
S("1116-76-3", "TOA", "Trioctylamine", "C24H51N", "Liquid", 58977127,
  "Pulls metals and acids out of water into kerosene in solvent extraction.", lib=2688)
S("1119-94-4", "DTAB", "Dodecyltrimethylammonium bromide", "C15H34BrN", "Solid", 3479946,
  "A cationic detergent used to study micelles.", lib=2696)
S("119-75-5", "NitroDPA2", "2-Nitrodiphenylamine", "C12H10N2O2", "Solid", 5047795,
  "A stabiliser in smokeless powder, mopping up the nitrogen oxides it slowly gives off.", lib=2868)
S("121-47-1", "Metanilic", "Metanilic acid", "C6H7NO3S", "Solid", 51479192,
  "3-Aminobenzenesulfonic acid, a water-solubilising part of azo dyes.", lib=2985)
S("13560-89-9", "DechloranePlus", "Dechlorane Plus", "C18H12Cl12", "Solid", 20870743,
  "A chlorinated flame retardant for cable coatings, now restricted as a persistent pollutant.", lib=3469)
S("142-22-3", "ADC", "Allyl diglycol carbonate", "C12H18O7", "Liquid", 3059400,
  "Polymerised in moulds it gives CR-39, the light plastic of most spectacle lenses.", lib=3647)
S("16874-33-2", "THFoic", "Tetrahydro-2-furoic acid", "C5H8O3", "Liquid", 41170521,
  "A building block for the blood-pressure drug alfuzosin.", lib=4076)
S("17920-88-6", "DFP", "2,2-Di-2-furylpropane", "C11H12O2", "Liquid", "2,2-Di-2-furylpropane",
  "Two furans tied by an acetone; hydrogenated, it is a catalyst ligand for polymerising butadiene.", lib=4186)
S("37764-25-3", "Dichlormid", "Dichlormid", "C8H11Cl2NO", "Liquid", 75668939,
  "A herbicide safener: mixed into maize weedkillers, it lets the crop shrug off the herbicide.", lib=5615)
S("4418-61-5", "Aminotetrazole", "5-Aminotetrazole", "CH3N5", "Solid", 49238352,
  "A ring of four nitrogens and a carbon; it fills airbags with nitrogen when it burns.", lib=5858)
S("574-93-6", "H2Pc", "Phthalocyanine", "C32H18N8", "Solid", 1156511,
  "Four isoindoles in a ring around a hole, the parent of the blue and green pigments.", lib=6621)
S("598-30-1", "sBuLi", "sec-Butyllithium", "C4H9Li", "Liquid", 6847430,
  "A stronger base than butyllithium for pulling protons off reluctant carbons.", lib=6802)
S("625-86-5", "DMF25", "2,5-Dimethylfuran", "C6H8O", "Liquid", 11878024,
  "A biofuel candidate from sugar, with more energy per litre than ethanol.", lib=6980)
S("66-71-7", "Phenanthroline", "1,10-Phenanthroline", "C12H8N2", "Solid", 1584707,
  "Grips iron(II) as a blood-red complex: the ferroin indicator of titrations.", lib=7222)
S("76-84-6", "Triphenylmethanol", "Triphenylmethanol", "C19H16O", "Solid", 3930613,
  "The classic Grignard product of student labs; its cation is the heart of triarylmethane dyes.", lib=7981)
S("7790-76-3", "Ca2P2O7", "Calcium pyrophosphate", "Ca2P2O7", "Solid", 2699300,
  "A mild abrasive in toothpaste; its crystals in joints cause the gout-like disease pseudogout.", lib=8163)
S("814-94-8", "SnC2O4", "Tin(II) oxalate", "SnC2O4", "Solid", 68408392,
  "A catalyst for making polyesters.", lib=8342)
S("301-10-0", "SnOctoate", "Tin(II) 2-ethylhexanoate", "C16H30O4Sn", "Liquid", 31821360,
  "Stannous octoate, the catalyst that ring-opens lactide into polylactic acid and cures silicones.", lib=5163)
S("90-93-7", "EthylMichler", "4,4'-Bis(diethylamino)benzophenone", "C21H28N2O", "Solid", 17330400,
  "Ethyl Michler's ketone, a photosensitiser for printing plates and photoresists.", lib=8633)
S("95-64-7", "DMA34", "3,4-Dimethylaniline", "C8H11N", "Solid", 8328185,
  "3,4-Xylidine, the ring on which riboflavin (vitamin B2) is built.", lib=8824)
S("512-42-5", "NaMeSO4", "Sodium methyl sulfate", "CH3NaO4S", "Solid", 13574236,
  "What is left of dimethyl sulfate after it has methylated something.", lib=6154)
S("91-76-9", "Benzoguanamine", "Benzoguanamine", "C9H9N5", "Solid", 56431724,
  "Melamine with a benzene ring for one amine: its resins are tougher and glossier.", lib=8679)
S("131-57-7", "Oxybenzone", "Oxybenzone", "C14H12O3", "Solid", 287585,
  "Benzophenone-3, a sunscreen filter for UVB and short UVA.", lib=3297)
S("143-24-8", "Tetraglyme", "Tetraglyme", "C10H22O5", "Liquid", 33744207,
  "A high-boiling glyme that wraps around lithium ions; tried as a battery electrolyte solvent.", lib=3685)
S("6362-80-7", "AMSDimer", "2,4-Diphenyl-4-methyl-1-pentene", "C18H20", "Liquid", 30440484,
  "alpha-Methylstyrene dimer, a chain-transfer agent that keeps polymer chains short.", lib=7062)
S("6674-22-2", "DBU", "DBU", "C9H16N2", "Liquid", 1782065,
  "1,8-Diazabicyclo[5.4.0]undec-7-ene, a strong base that pulls off protons without attacking carbon.",
  lib=7263)
S("97-74-5", "TMTM", "Tetramethylthiuram monosulfide", "C6H12N2S3", "Solid", 13747746,
  "Thiram with one sulfur fewer: a rubber accelerator that does not release sulfur.", lib=8893)
S("7789-80-2", "CaIodate", "Calcium iodate", "CaI2O6", "Solid", 14345569,
  "The iodine in cattle feed and in some iodised salt.", lib=8158)
S("10124-56-8", "SHMP", "Sodium hexametaphosphate", "Na6P6O18", "Solid", 629218,
  "A ring of six phosphates that softens water by holding calcium; Calgon.", lib=2147)
S("1068-55-9", "iPrMgCl", "Isopropylmagnesium chloride", "C3H7ClMg", "Liquid", 60094874,
  "A Grignard reagent sold in solution, for swapping halogens and adding isopropyl groups.", lib=2428)
S("91-95-2", "DAB", "3,3'-Diaminobenzidine", "C12H14N4", "Solid", 1872657,
  "Stains tissue brown where an enzyme-tagged antibody has bound: the classic dye of immunohistochemistry.",
  lib=8683)
S("26040-51-7", "TBPH", "Bis(2-ethylhexyl) tetrabromophthalate", "C24H34Br4O4", "Liquid", 73318950,
  "A brominated plasticiser and flame retardant for PVC and foam.", lib=4838)


# --- the reactions -------------------------------------------------------------------------
E3.reactions += [
    R("2-Nitrochlorobenzene", "Chlorobenzene + HNO3 -> ONCB + H2O", FLASK,
      "Nitrating chlorobenzene gives about a third ortho isomer, separated from the para by crystallising.",
      wiki="2-Nitrochlorobenzene", T=50),
    R("Tin(II) Chloride", "Sn + 2 HCl -> SnCl2 + H2", MIX,
      "Tin dissolves slowly in hydrochloric acid, giving off hydrogen.", wiki="Tin(II)_chloride"),
    R("Fat Splitting of Colza Oil", "ColzaOil + 3 H2O -> 3 ErucicAcid + Glycerol", HEAT,
      "Rapeseed oil split by steam under pressure: half the acid that comes out is erucic.",
      wiki="Erucic_acid", T=250),
]
E4.reactions += [
    R("2-Nitroaniline", "ONCB + 2 NH3 -> oNitroaniline + NH4Cl", PRESS,
      "Ammonia under pressure swaps the chlorine for an amine.", wiki="2-Nitroaniline", T=170),
    R("o-Phenylenediamine", "oNitroaniline + 3 H2 -> OPD + 2 H2O", CAT,
      "The nitro group hydrogenated to a second amine beside the first.", wiki=3068051, cat="Ni", T=100),
    R("3,3'-Dichlorobenzidine", "2 ONCB + 5 Zn + H2O -> DCB + 5 ZnO", FLASK,
      "Zinc in caustic soda reduces two molecules to a hydrazobenzene; acid then rearranges it into the "
      "benzidine.", wiki="3,3'-Dichlorobenzidine", T=60),
    R("Pigment Yellow 12", "DCB + 2 NaNO2 + 2 HCl + 2 Acetoacetanilide -> PY12 + 2 NaCl + 4 H2O", COOL,
      "Both amines diazotised in the cold, then each coupled with acetoacetanilide.", wiki=55053258, T=5),
    R("3,3'-Diaminobenzidine", "DCB + 4 NH3 -> DAB + 2 NH4Cl", HIGHP,
      "Ammonia replaces both chlorines over copper.", wiki=1872657, cat="Cu", T=200),
    R("o-Anisidine", "ONCB + NaOH + Methanol + 3 H2 -> oAnisidine + NaCl + 3 H2O", HIGHP,
      "Sodium methoxide swaps the chlorine for a methoxy group; the nitro group is then hydrogenated.",
      wiki=17292148, cat="Ni", T=100),
    R("2-Nitrodiphenylamine", "ONCB + Aniline -> NitroDPA2 + HCl", HEAT,
      "Aniline displaces the chlorine.", wiki=5047795, T=200),
    R("Benzotriazole", "OPD + NaNO2 + AcOH -> Benzotriazole + NaC2H3O2 + 2 H2O", FLASK,
      "Nitrous acid diazotises one amine, which closes onto the other.", wiki=11363337, T=10),
    R("1,10-Phenanthroline", "OPD + 2 Glycerol + O2 + H2SO4 -> Phenanthroline + 8 H2O + H2SO4", FLASK,
      "Two Skraup reactions on one ring: sulfuric acid turns glycerol into acrolein, which closes a "
      "pyridine onto each amine.", wiki=1584707, T=150),
    R("1,2-Diaminocyclohexane", "OPD + 3 H2 -> DACH", HIGHP,
      "The benzene ring hydrogenated.", wiki=63644909, cat="Ni", T=180),
    R("Brassylic Acid", "2 ErucicAcid + 2 O3 + O2 -> 2 BrassylicAcid + 2 NonanoicAcid", FLASK,
      "Ozone cuts erucic acid at its double bond into a thirteen-carbon diacid and nonanoic acid.",
      wiki="Erucic_acid", T=20),
    R("Behenic Acid", "ErucicAcid + H2 -> BehenicAcid", CAT,
      "The double bond of erucic acid hydrogenated.", wiki="Behenic_acid", cat="Ni", T=180),
    R("Chloroethane", "Ethylene + HCl -> EtCl", CAT,
      "Hydrogen chloride added across ethylene over aluminium chloride.", wiki="Chloroethane", cat="AlCl3",
      T=40),
    R("Ethylvanillin", "2 Catechol + 2 EtCl + 2 GlyoxylicAcid + O2 -> 2 Ethylvanillin + 2 HCl + 2 CO2 + 2 H2O",
      FLASK, "Catechol ethylated to guaethol, condensed with glyoxylic acid, then oxidised and decarboxylated.",
      wiki=19035891, T=80),
    R("Thiophosphoryl Chloride", "PCl3 + S -> PSCl3", HEAT,
      "Phosphorus trichloride heated with sulfur at 180 C.", wiki="Thiophosphoryl_chloride", T=180),
    R("n-Butylamine", "Butanol + NH3 -> Butylamine + H2O", HIGHP,
      "Butanol and ammonia over alumina.", wiki="N-Butylamine", cat="Alumina", T=350),
    R("Heptanoic Acid", "2 Heptanal + O2 -> 2 HeptanoicAcid", MIX,
      "Heptanal from cracked castor oil oxidised by air.", wiki="Heptanoic_acid"),
    R("Ethyl Heptanoate", "HeptanoicAcid + Ethanol -> EthylHeptanoate + H2O", CAT,
      "Heptanoic acid esterified with ethanol.", wiki=3292511, cat="H2SO4", T=80),
    R("Diethylene Glycol", "EG + EO -> DEG", PRESS,
      "Ethylene oxide meets ethylene glycol already made, adding a second unit.", wiki="Diethylene_glycol",
      T=150),
    R("2-Furoic Acid", "2 Furfural + H2O -> FuroicAcid + FurfurylAlcohol", FLASK,
      "The Cannizzaro reaction in caustic soda: one furfural is oxidised, the other reduced.",
      wiki="2-Furoic_acid", T=20),
    R("Xylenol by Caustic Fusion", "oXylene + H2SO4 + 2 NaOH -> Xylenol34 + Na2SO3 + 2 H2O", HEAT,
      "o-Xylene sulfonated, then the sulfonate fused with caustic soda.", wiki=6100539, T=320),
    R("2,5-Xylenol by Caustic Fusion", "pXylene + H2SO4 + 2 NaOH -> Xylenol25 + Na2SO3 + 2 H2O", HEAT,
      "p-Xylene sulfonated, then the sulfonate fused with caustic soda.", wiki=3399664, T=320),
    R("Metanilic Acid", "Nitrobenzene + SO3 + 3 H2 -> Metanilic + 2 H2O", HIGHP,
      "Nitrobenzene sulfonated in the meta position, then the nitro group reduced.", wiki=51479192,
      cat="Ni", T=100),
    R("Potassium Pyrosulfate", "K2SO4 + SO3 -> K2S2O7", HEAT,
      "Potassium sulfate takes up sulfur trioxide.", wiki=13676264, T=300),
    R("Calcium Pyrophosphate", "2 CaCO3 + 2 H3PO4 -> Ca2P2O7 + 2 CO2 + 3 H2O", HEAT,
      "Chalk and phosphoric acid, then calcined so two phosphates join.", wiki=2699300, T=900),
    R("Calgon", "6 H3PO4 + 3 SodaAsh -> SHMP + 3 CO2 + 9 H2O", SMELT,
      "Sodium phosphate melted until the phosphates link into rings, then quenched to a glass.",
      wiki=629218, T=700),
    R("Calcium Iodate", "CaCl2 + 2 KIO3 -> CaIodate + 2 KCl", MIX,
      "Calcium iodate is the less soluble salt and settles out.", wiki=14345569),
    R("Triphenylmethanol", "2 Benzophenone + 2 PhMgBr + 2 HCl -> 2 Triphenylmethanol + MgCl2 + MgBr2", FLASK,
      "Phenylmagnesium bromide adds to benzophenone; dilute acid frees the alcohol.", wiki=3930613,
      T=35),
    R("Tin(II) Oxalate", "SnCl2 + Oxalic -> SnC2O4 + 2 HCl", MIX,
      "Stannous chloride and oxalic acid; the oxalate is insoluble.", wiki=68408392),
    R("Sodium Methyl Sulfate", "DimethylSulfate + NaOH -> NaMeSO4 + Methanol", MIX,
      "Caustic soda takes one methyl group off dimethyl sulfate.", wiki=13574236),
]
E5.reactions += [
    R("Benzonitrile", "2 Toluene + 2 NH3 + 3 O2 -> 2 Benzonitrile + 6 H2O", CAT,
      "Ammoxidation: toluene, ammonia and air over an oxide catalyst at 420 C.", wiki="Benzonitrile",
      cat="V2O5", T=420),
    R("Benzoguanamine", "Benzonitrile + DCD -> Benzoguanamine", FLASK,
      "Benzonitrile adds to dicyandiamide in hot caustic.", wiki=56431724, T=150),
    R("Phthalonitrile", "oXylene + 2 NH3 + 3 O2 -> Phthalonitrile + 6 H2O", CAT,
      "o-Xylene ammoxidised in one continuous step at 480 C.", wiki="Phthalonitrile", cat="V2O5", T=480),
    R("Phthalocyanine", "4 Phthalonitrile + H2 -> H2Pc", HEAT,
      "Four phthalonitriles close into one ring around a metal ion; acid takes the metal out and leaves "
      "two hydrogens in the middle.", wiki=1156511, T=200),
    R("Hexanal by Hydroformylation", "Pentene + CO + H2 -> Hexanal", HIGHP,
      "1-Pentene and syngas over a cobalt catalyst: the oxo process.", wiki=14571189, cat="Co", T=150),
    R("1-Hexanol", "Hexanal + H2 -> Hexanol", CAT,
      "Hexanal hydrogenated.", wiki="1-Hexanol", cat="Ni", T=120),
    R("gamma-Nonalactone", "Hexanol + AcrylicAcid -> gNonalactone + H2O", FLASK,
      "A radical from hexanol adds to acrylic acid, and the chain closes into a lactone.",
      wiki=49408946, T=150),
    R("Hexyl Acetate", "Hexanol + AcOH -> HexylAcetate + H2O", CAT,
      "1-Hexanol esterified with acetic acid.", wiki=28416118, cat="H2SO4", T=110),
    R("1-Decanol", "Decanoic + 2 H2 -> Decanol + H2O", CAT,
      "Coconut decanoic acid hydrogenated to the fatty alcohol.", wiki="1-Decanol", cat="Cu", T=250),
    R("1-Octanol", "Octanoic + 2 H2 -> Octanol + H2O", CAT,
      "Octanoic acid hydrogenated to the fatty alcohol.", wiki="1-Octanol", cat="Cu", T=250),
    R("Cetyl Alcohol", "PalmiticAcid + 2 H2 -> CetylAlcohol + H2O", CAT,
      "Palmitic acid (as its ester) reduced to the fatty alcohol.", wiki="Cetyl_alcohol", cat="Cu", T=250),
    R("Didecyldimethylammonium Chloride", "2 Decanol + Methylamine + CH3Cl -> DDAC + 2 H2O", PRESS,
      "Methylamine takes two decyl chains; methyl chloride then quaternises the amine.", wiki=12813475,
      T=150),
    R("Trioctylamine", "3 Octanol + NH3 -> TOA + 3 H2O", CAT,
      "Ammonia alkylated three times by octanol.", wiki=58977127, cat="Ni", T=200),
    R("2-Octyldodecanol", "2 Decanol -> Octyldodecanol + H2O", CAT,
      "The Guerbet reaction: two alcohols join at the carbon next to the OH.", wiki=19887814,
      cat="KOH", T=230),
    R("Cetrimonium Chloride", "CetylAlcohol + Me2NH + CH3Cl -> CTAC + H2O", PRESS,
      "Cetyl alcohol aminated with dimethylamine, then quaternised with methyl chloride.", wiki=5349042, T=150),
    R("Cetalkonium Chloride", "CetylAlcohol + Me2NH + BenzylChloride -> BKC16 + H2O", FLASK,
      "Cetyl dimethylamine quaternised with benzyl chloride.", wiki=22561086, T=80),
    R("Cetyl Palmitate", "CetylAlcohol + PalmiticAcid -> CetylPalmitate + H2O", CAT,
      "Cetyl alcohol esterified with palmitic acid.", wiki=25399724, cat="H2SO4", T=150),
    R("Dodecyltrimethylammonium Bromide", "Dodecanol + Me2NH + MeBr -> DTAB + H2O", PRESS,
      "Lauryl alcohol aminated with dimethylamine, then quaternised with methyl bromide.", wiki=3479946, T=100),
    R("Sarcosine", "EtClAc + Methylamine + NaOH -> Sarcosine + NaCl + Ethanol", FLASK,
      "Methylamine displaces the chlorine of ethyl chloroacetate; the ester is hydrolysed.",
      wiki="Sarcosine", T=40),
    R("Sodium Lauroyl Sarcosinate", "Sarcosine + LauroylCl + 2 NaOH -> SLSarc + NaCl + 2 H2O", FLASK,
      "A Schotten-Baumann acylation of sarcosine with lauroyl chloride.", wiki=14754966, T=30),
    R("Oleoyl Sarcosine", "Sarcosine + OleicAcid -> Oleoylsarcosine + H2O", HEAT,
      "Sarcosine and oleic acid condensed hot to the amide.", wiki=52344511, T=170),
    R("Aminopropyltriethoxysilane", "Allylamine + TEOS_H -> APTES", CAT,
      "Triethoxysilane adds across allylamine's double bond over platinum.",
      wiki="(3-Aminopropyl)triethoxysilane", cat="Pt", T=100),
    R("Si-69", "2 AllylChloride + 2 HSiCl3 + 6 Ethanol + Na2S4 -> Si69 + 2 NaCl + 6 HCl", HIGHP,
      "Trichlorosilane adds to allyl chloride over platinum, ethanol swaps the chlorines on silicon, and "
      "sodium tetrasulfide joins two silanes.", wiki=45532908, cat="Pt", T=100),
    R("Vinyltriethoxysilane", "HSiCl3 + Acetylene + 3 Ethanol -> VTEO + 3 HCl", CAT,
      "Trichlorosilane adds to acetylene; ethanol then replaces the chlorines.", wiki=52363271, cat="Pt", T=120),
    R("Tetraethylammonium Hydroxide", "Et3N + EtCl + KOH -> TEAOH + KCl", FLASK,
      "Triethylamine quaternised with ethyl chloride; potash swaps chloride for hydroxide.", wiki=63139075,
      T=60),
    R("Tetraethylammonium Fluoride", "TEAOH + HF -> TEAF + H2O", MIX,
      "The hydroxide neutralised with hydrofluoric acid.", wiki=902918),
    R("Octocrylene", "Benzophenone + EthylCyanoacetate + 2EH -> Octocrylene + H2O + Ethanol", FLASK,
      "Cyanoacetate transesterified with 2-ethylhexanol, then a Knoevenagel condensation with "
      "benzophenone.", wiki=4344583, T=140),
    R("3,5-Lutidine", "2 Propanal + CH2O + NH3 -> Lutidine35 + 3 H2O + H2", CAT,
      "Aldehydes, formaldehyde and ammonia condensed over a catalyst into a pyridine ring.",
      wiki=61707641, cat="Alumina", T=400),
    R("3,5-Dimethylpiperidine", "Lutidine35 + 3 H2 -> DMPip35", HIGHP,
      "The pyridine ring hydrogenated.", wiki=40463317, cat="Ni", T=180),
    R("2-Ethylphenol", "Phenol + Ethylene -> EtPhenol2", HIGHP,
      "Aluminium phenoxide steers the ethyl group to the ring position beside the OH.", wiki=69494491,
      cat="Al", T=300),
    R("4-Ethyltoluene", "Toluene + Ethylene -> pEthyltoluene", CRACKER,
      "Toluene ethylated in a shape-selective zeolite whose pores let only the para isomer out.",
      wiki=51325456, cat="ZSM5", T=400),
    R("NBPT", "PSCl3 + Butylamine + 5 NH3 -> NBPT + 3 NH4Cl", FLASK,
      "Butylamine takes one chlorine of thiophosphoryl chloride, ammonia the other two.", wiki=66226078, T=0),
    R("N,N'-Dibutylthiourea", "2 Butylamine + CS2 -> DBTU + H2S", FLASK,
      "Two butylamines on carbon disulfide, with hydrogen sulfide given off.", wiki=45259842, T=60),
    R("Acrylamide", "Acrylonitrile + H2O -> Acrylamide", BIOR,
      "Bacterial cells hydrate acrylonitrile to acrylamide, cleaner than the old copper catalyst.",
      wiki="Acrylamide", T=10),
    R("Methylenebisacrylamide", "2 Acrylamide + CH2O -> MBA + H2O", FLASK,
      "Two acrylamides bridged by formaldehyde.", wiki=19797219, T=60),
    R("1-Vinylimidazole", "Imidazole + Acetylene -> Vinylimidazole", PRESS,
      "Reppe vinylation: imidazole adds to acetylene under pressure with potash.", wiki=53794817,
      T=130),
    R("Quinolinic Acid", "2 Quinoline + 9 O2 -> 2 QuinolinicAcid + 4 CO2 + 2 H2O", CAT,
      "Quinoline oxidised: the benzene ring burns away and leaves two acid groups on the pyridine.",
      wiki=15648814, T=200),
    R("Adamantane", "DCPD + 2 H2 -> Adamantane", CAT,
      "Schleyer's route (1957): dicyclopentadiene hydrogenated, then aluminium chloride shuffles the "
      "cage into adamantane.", wiki="Adamantane", cat="AlCl3", T=150),
    R("Amantadine", "Adamantane + Br2 + Acetonitrile + 2 H2O + HCl -> AmantadineHCl + AcOH + 2 HBr", FLASK,
      "Adamantane brominated; a Ritter reaction with acetonitrile puts on an amide, which is hydrolysed "
      "to the amine.", wiki=1128227, T=80),
    R("Chlorendic Anhydride", "HCCP + MaleicAnhydride -> ChlorendicAnhydride", HEAT,
      "A Diels-Alder addition of maleic anhydride to hexachlorocyclopentadiene.",
      wiki=3156026, T=150),
    R("Dechlorane Plus", "2 HCCP + COD -> DechloranePlus", PRESS,
      "Two Diels-Alder additions onto cyclooctadiene.", wiki=20870743, T=140),
    R("2,2-Dimethoxy-2-phenylacetophenone", "Benzil + 2 Methanol -> DMPAP + H2O", CAT,
      "One ketone of benzil turned into a dimethyl ketal.", wiki=28276736, cat="H2SO4", T=60),
    R("4-Hydroxybenzaldehyde", "pCresol + O2 -> HBA4 + H2O", CAT,
      "p-Cresol's methyl group oxidised by air over a cobalt catalyst in alkaline methanol.",
      wiki="4-Hydroxybenzaldehyde", cat="Co", T=60),
    R("Raspberry Ketone", "HBA4 + Acetone + H2 -> RaspberryKetone + H2O", CAT,
      "An aldol condensation with acetone, then the double bond hydrogenated.", wiki=12102450,
      cat="Pd", T=80),
    R("Cyclamen Aldehyde", "Cuminaldehyde + Propanal + H2 -> CyclamenAldehyde + H2O", CAT,
      "Cuminaldehyde condensed with propanal, then hydrogenated.", wiki=44750710, cat="Pd", T=80),
    R("Allyl Diglycol Carbonate", "DEG + 2 COCl2 + 2 AllylAlcohol -> ADC + 4 HCl", FLASK,
      "Diethylene glycol made into its bis(chloroformate) with phosgene, then capped with allyl alcohol.",
      wiki=3059400, T=10),
    R("Tetrahydro-2-furoic Acid", "FuroicAcid + 2 H2 -> THFoic", CAT,
      "The furan ring hydrogenated.", wiki=41170521, cat="Pd", T=80),
    R("2,2-Di-2-furylpropane", "2 Furan + Acetone + HCl -> DFP + H2O + HCl", FLASK,
      "Two furans condensed with acetone in hydrochloric acid.", wiki="2,2-Di-2-furylpropane", T=20),
    R("Dichlormid", "Diallylamine + DCAC -> Dichlormid + HCl", FLASK,
      "Diallylamine acylated with dichloroacetyl chloride.", wiki=75668939, T=10),
    R("5-Aminotetrazole", "AGB + NaNO2 + HCl -> Aminotetrazole + CO2 + NaCl + 3 H2O", FLASK,
      "Aminoguanidine diazotised; the diazo group closes onto the ring.", wiki=49238352, T=10),
    R("sec-Butyllithium", "2-Butene + HCl + 2 Li -> sBuLi + LiCl", FLASK,
      "2-Butene takes hydrogen chloride to 2-chlorobutane, which lithium metal turns into the reagent.",
      wiki=6847430, T=30),
    R("Hydroxymethylfurfural", "Fructose -> HMF + 3 H2O", FLASK,
      "Fructose dehydrated by acid, losing three waters.", wiki="Hydroxymethylfurfural", T=120),
    R("2,5-Dimethylfuran", "HMF + 3 H2 -> DMF25 + 2 H2O", CAT,
      "Both oxygen groups of HMF hydrogenated off.", wiki=11878024, cat="Cu", T=220),
    R("Tin(II) 2-Ethylhexanoate", "SnCl2 + 2 EHAcid + 2 NaOH -> SnOctoate + 2 NaCl + 2 H2O", FLASK,
      "Stannous chloride and sodium 2-ethylhexanoate swap partners.", wiki=31821360, T=60),
    R("Ethyl Michler's Ketone", "2 DiethylAniline + COCl2 -> EthylMichler + 2 HCl", FLASK,
      "Phosgene acylates two diethylanilines at the para position.", wiki=17330400, T=50),
    R("3,4-Dimethylaniline", "oXylene + HNO3 + 3 H2 -> DMA34 + 3 H2O", HIGHP,
      "o-Xylene nitrated, then the nitro group hydrogenated.", wiki=8328185, cat="Ni", T=100),
    R("Oxybenzone", "Resorcinol + BenzoicAcid + DimethylSulfate + NaOH -> Oxybenzone + NaMeSO4 + 2 H2O",
      FLASK, "Resorcinol benzoylated to 2,4-dihydroxybenzophenone; one OH is then methylated.",
      wiki=287585, T=150),
    R("Tetraglyme", "Triglyme + EO -> Tetraglyme", CAT,
      "One more ethylene oxide opened into the glyme chain by boron trifluoride.", wiki=33744207,
      cat="BF3", T=50),
    R("alpha-Methylstyrene Dimer", "2 AMS -> AMSDimer", FLASK,
      "alpha-Methylstyrene dimerised by acid.", wiki=30440484, T=60),
    R("DBU", "Caprolactam + Acrylonitrile + 2 H2 -> DBU + H2O", HIGHP,
      "Caprolactam cyanoethylated, the nitrile hydrogenated, and the second ring closed.", wiki=1782065,
      cat="Ni", T=150),
    R("Tetramethylthiuram Monosulfide", "Thiram + NaCN -> TMTM + NaSCN", FLASK,
      "Cyanide plucks one sulfur out of thiram's disulfide bridge.", wiki=13747746, T=30),
    R("Isopropylmagnesium Chloride", "Propylene + HCl + Mg -> iPrMgCl", FLASK,
      "Propylene takes hydrogen chloride to isopropyl chloride, which magnesium turns into a Grignard "
      "reagent in ether.", wiki=60094874, T=35),
    R("Tetrabromophthalate Ester", "PhthalicAnhydride + 4 Br2 + 2 2EH -> TBPH + 4 HBr + H2O", FLASK,
      "Phthalic anhydride brominated in oleum, then esterified with 2-ethylhexanol.", wiki=73318950, T=150),
]

import authored_canon_17  # noqa: E402,F401
