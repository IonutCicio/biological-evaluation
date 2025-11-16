MATCH (targetPathway:Pathway)
WHERE targetPathway.dbId IN [162582]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node
WITH COLLECT(DISTINCT node) AS reactionsOfInterest
MATCH (physicalEntity:PhysicalEntity)
WHERE
  (toLower(physicalEntity.displayName) CONTAINS 'calcium' OR
    toLower(physicalEntity.displayName) CONTAINS 'estrogen' OR
    toLower(physicalEntity.displayName) CONTAINS 'actin') AND
  EXISTS {
    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
    WHERE reactionLikeEvent IN reactionsOfInterest
  }
RETURN physicalEntity.dbId, physicalEntity.displayName;

MATCH (targetPathway:Pathway)
WHERE targetPathway.dbId IN [162582]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node
WITH COLLECT(DISTINCT node) AS reactionsOfInterest
MATCH (physicalEntity:PhysicalEntity)
WHERE
  physicalEntity.displayName CONTAINS 'EGF' AND
  EXISTS {
    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
    WHERE reactionLikeEvent IN reactionsOfInterest
  }
RETURN physicalEntity.dbId, physicalEntity.displayName;

// ╒═════════════════════╤══════════════════════════════════════════════════════════════════════╕
// │"physicalEntity.dbId"│"physicalEntity.displayName"                                          │
// ╞═════════════════════╪══════════════════════════════════════════════════════════════════════╡
// │1306961              │"EGF:p-EGFR:p-ERBB2:GRB2:GAB1:PI3K [plasma membrane]"                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1306958              │"EGF:p-EGFR:p-ERBB2:GRB2:GAB1 [plasma membrane]"                      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1963587              │"Phosphorylated ERBB2:EGFR heterodimers [plasma membrane]"            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │179863               │"EGF [extracellular region]"                                          │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1306974              │"NRGs/EGFLs:p-ERBB4cyt1:p-ERBB2:PI3K [plasma membrane]"               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1233234              │"HBEGF(63-148) [extracellular region]"                                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │179791               │"EGF-like ligands:p-6Y-EGFR:GRB2:p-5Y-GAB1:PI3K [plasma membrane]"    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180286               │"EGF-like ligands:p-6Y-EGFR:GRB2:p-5Y-GAB1 [plasma membrane]"         │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9624425              │"EGF-like ligands:p-6Y EGFR dimer [plasma membrane]"                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1236393              │"NRGs/EGF-like ligands:ERBB4 [plasma membrane]"                       │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180348               │"EGF-like ligands:p-6Y-EGFR:GRB2:GAB1 [plasma membrane]"              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9624420              │"EGF-like ligands:EGFR dimer [plasma membrane]"                       │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9624419              │"EGFR:EGF-like ligands [plasma membrane]"                             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9674862              │"EGFR:AAMP [plasma membrane]"                                         │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │195376               │"VEGF dimer [extracellular region]"                                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9851427              │"EGFR:FAM83B,(FAM83A, FAM83D) [plasma membrane]"                      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │212703               │"EGF-like ligand:p-6Y-EGFR:p-Y472,771,783,1254-PLCG1 [plasma membrane]│
// │                     │"                                                                     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │212717               │"EGF-like ligands:p-6Y-EGFR:PLCG1 [plasma membrane]"                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1251942              │"EGF:p-EGFR:p-ERBB2:PLCG1 [plasma membrane]"                          │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1306947              │"NRGs/EGFLs:p-ERBB4:p-ERBB2:GRB2:SOS1 [plasma membrane]"              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1250505              │"EGF:p-EGFR:p-ERBB2:GRB2:SOS1 [plasma membrane]"                      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180331               │"EGF-like ligands:p-6Y-EGFR:p-Y349,350-SHC1:GRB2:SOS1 [plasma membrane│
// │                     │]"                                                                    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180337               │"EGF-like ligands:p-6Y-EGFR:p-Y349,350-SHC1 [plasma membrane]"        │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │179820               │"EGF-like ligands:p-6Y-EGFR:GRB2:SOS1 [plasma membrane]"              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │2179409              │"GRB2:SOS1:HB-EGF:p-6Y-EGFR [plasma membrane]"                        │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │2179410              │"HB-EGF:p-6Y-EGFR dimer [plasma membrane]"                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420110              │"VEGFA dimer:p-6Y-VEGFR2 dimer:p-4Y-PLCG1 [plasma membrane]"          │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420101              │"VEGFA dimer:p-6Y-VEGFR2 dimer [plasma membrane]"                     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420203              │"VEGFA dimer:p-6Y-VEGFR2 dimer:PLCG1 [plasma membrane]"               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │195402               │"VEGFA-165 dimer:VEGFR2 [plasma membrane]"                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │215139               │"VEGFR2:VEGFA,C,D [plasma membrane]"                                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9679453              │"VEGFA-165 dimer:VEGFA inhibitors [extracellular region]"             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9624427              │"EGF-like ligands:p-6Y EGFR:SHC1 [plasma membrane]"                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │2179391              │"HBEGF(149-208) [extracellular region]"                               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │2179390              │"HBEGF(20-62) [extracellular region]"                                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218777              │"VEGFA dimer:p-6Y-VEGFR2 dimer:PI3K [plasma membrane]"                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5357453              │"VEGFA:p-6Y-VEGFR2:SH2D2A:p-Y418-SRC-1:p-Y779,Y821-AXL:PI3K [plasma me│
// │                     │mbrane]"                                                              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5357462              │"VEGFA:p-6Y-VEGFR2:SH2D2A:p-Y418-SRC-1:p-Y779,Y821-AXL [plasma membran│
// │                     │e]"                                                                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218788              │"VEGFA:p-6Y-VEGFR2:SH2D2A:p-Y418-SRC-1 [plasma membrane]"             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420137              │"VEGFA dimer:p-6Y-VEGFR2 dimer:SH2D2A [plasma membrane]"              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5357442              │"VEGFA:p-6Y-VEGFR2:SH2D2A:p-Y418-SRC-1:AXL [plasma membrane]"         │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420169              │"VEGFA dimer:p-6Y-VEGFR2 dimer:SH2D2A:SRC-1 [plasma membrane]"        │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │179882               │"EGF:p-6Y-EGFR dimer [plasma membrane]"                               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8857567              │"HBEGF:EGFR:p-Y525-GPNMB:LINC01139:PTK6:LRRK2 [plasma membrane]"      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8857556              │"HBEGF:EGFR:p-Y525-GPNMB [plasma membrane]"                           │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8857574              │"HBEGF:EGFR:p-Y525-GPNMB:LINC01139:p-Y351-PTK6:LRRK2 [plasma membrane]│
// │                     │"                                                                     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8857546              │"HBEGF:EGFR:GPNMB [plasma membrane]"                                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218776              │"CRK:DOCK180:ELMO1,ELMO2:VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90│
// │                     │:p-12Y-BCAR1,VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90:p-Y31,Y118-│
// │                     │PXN [plasma membrane]"                                                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218762              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90:p-12Y-BCAR1 [plasma mem│
// │                     │brane]"                                                               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218757              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-6Y,S732-PTK2:SRC-1:HSP90AA1 [plasma membran│
// │                     │e]"                                                                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420164              │"VEGFA dimer:p-6Y-VEGFR2 dimer:p-S-SHB [plasma membrane]"             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218756              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90:p-Y31,Y118-PXN [plasma │
// │                     │membrane]"                                                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218765              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90:p-12Y-BCAR1/p-Y31,Y118-│
// │                     │PAX:CRK [plasma membrane]"                                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218790              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-6Y,S732-PTK2:SRC-1:HSP90AA1:BCAR1 [plasma m│
// │                     │embrane]"                                                             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218778              │"VEGFA:p-6Y-VEGFR2:Integrin alphaVbeta3:p-Y402-PTK2B [plasma membrane]│
// │                     │"                                                                     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218779              │"VEGFA:p-6Y-VEGFR2:Integrin alphaVbeta3 [plasma membrane]"            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218775              │"VEGFA:p-6Y-VEGFR2:pS-SHB:p-5Y,S732-PTK2:SRC-1:HSP90AA1 [plasma membra│
// │                     │ne]"                                                                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218641              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-Y397-PTK2:SRC-1 [plasma membrane]"         │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218639              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-Y397-PTK2 [plasma membrane]"               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218787              │"VEGFA:p-6Y-VEGFR2:Integrin alphaVbeta3:PTK2B [plasma membrane]"      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420141              │"VEGFA:p-6Y-VEGFR2:p-SHB:PTK2 [plasma membrane]"                      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420196              │"VEGFA dimer:p-6Y-VEGFR2 dimer:SHB [plasma membrane]"                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218637              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-5Y-PTK2:SRC-1:HSP90AA1 [plasma membrane]"  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218636              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-5Y-PTK2:SRC-1 [plasma membrane]"           │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218781              │"VEGFA:p-6Y-VEGFR2:p-SHB:p-7Y-PTK2:SRC-1:HSP90:PXN [plasma membrane]" │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8864106              │"Phosphorylated ERBB2:EGFR heterodimers:PTPN18 [plasma membrane]"     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8864118              │"Phosphorylated ERBB2(dephosphorylated at Y1196,Y1112 and Y1248):EGFR │
// │                     │heterodimers:PTPN18 [plasma membrane]"                                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9625453              │"EGF-like ligands:p-6Y EGFR:PTK2 [plasma membrane]"                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9625464              │"EGF-like ligands:p-6Y EGFR dimer:p-Y397 PTK2 [plasma membrane]"      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180269               │"EGF-like ligands:p-6Y-EGFR:GRB2:p-5Y-GAB1:SHP2 [plasma membrane]"    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180503               │"EGF-like ligands:p-6Y-EGFR:GRB2:p-Y627,659-GAB1:SHP2 [plasma membrane│
// │                     │]"                                                                    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │180326               │"EGF-like ligands:p-5Y-EGFR:GRB2:p-5Y-GAB1:SHP2 [plasma membrane]"    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182960               │"EGF-like ligands:p-6Y-EGFR:CBL [plasma membrane]"                    │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182953               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL [plasma membrane]"             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182961               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:CIN85:Endophilin:Epsin:Eps15L1:│
// │                     │Eps15 [plasma membrane]"                                              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8951489              │"EGF:p-6Y-EGFR:CBL:Beta-Pix:CDC42:GTP:CIN85 [plasma membrane]"        │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182946               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:GRB2:CIN85:Endophilin [plasma m│
// │                     │embrane]"                                                             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182932               │"EGF:p-6Y-EGFR:CBL:Beta-Pix:CDC42:GTP [plasma membrane]"              │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182948               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:GRB2 [plasma membrane]"        │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182928               │"EGF-like ligands:p-6Y-EGFR:CBL:GRB2 [plasma membrane]"               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182936               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:Ub-CIN85:Endophilin:Epsin:Eps15│
// │                     │L1:Eps15 [plasma membrane]"                                           │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8867034              │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:GRB2:CIN85:Endophilin:EPN1:EPS1│
// │                     │5L1:EPS15:HGS:STAM [plasma membrane]"                                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8867035              │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:GRB2:CIN85:Endophilin:EPN1:EPS1│
// │                     │5L1:p-EPS15:HGS:STAM [plasma membrane]"                               │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182930               │"EGF-like ligands:Ub-p-6Y-EGFR:p-Y371-CBL [plasma membrane]"          │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182945               │"EGF-like ligands:Ub-p-6Y-EGFR:p-Y371-CBL:GRB2 [plasma membrane]"     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182939               │"EGF-like ligands:p-6Y-EGFR:CBL:Ub-p-Y53/55-SPRY1/2 [plasma membrane]"│
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │182931               │"EGF-like ligands:p-6Y-EGFR:p-Y371-CBL:CIN85:SPRY1/2:Endophilin:Epsin:│
// │                     │Eps15L1:EPS15 [plasma membrane]"                                      │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │8864028              │"EGF:p-EGFR dimer dephosphorylated at Y1172 (Y1148) [plasma membrane]"│
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │195419               │"NRP1:VEGFR2 dimer [plasma membrane]"                                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │195427               │"NRP2:VEGFR1 dimer [plasma membrane]"                                 │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218793              │"VEGFA:p-6Y-VEGFR2:NCK:p-S21,Y420-FYN:p-3Y-PAK2:CDC42:GTP [plasma memb│
// │                     │rane]"                                                                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218780              │"VEGFA dimer:p-6Y-VEGFR2 dimer:NCK1,NCK2:p-S21,Y420-FYN [plasma membra│
// │                     │ne]"                                                                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218798              │"VEGFA dimer:p-6Y-VEGFR2 dimer:NCK1,NCK2 [plasma membrane]"           │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218792              │"VEGFA:p-6Y-VEGFR2:NCK:p-S21,Y420-FYN:p-2Y-PAK2:CDC42:GTP [plasma memb│
// │                     │rane]"                                                                │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218782              │"VEGFA:p-6Y-VEGFR2:NCK:p-S21,Y420-FYN:PAK2:CDC42:GTP [plasma membrane]│
// │                     │"                                                                     │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218766              │"VEGFA dimer:p-6Y-VEGFR2 dimer:NCK1,NCK2:p-S21,Y420-FYN:PAK2 [plasma m│
// │                     │embrane]"                                                             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218795              │"VEGFA dimer:p-6Y-VEGFR2 dimer:NCK1,NCK2:p-Y420-FYN [plasma membrane]"│
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │5218786              │"VEGFA dimer:p-6Y-VEGFR2 dimer:NCK1,NCK2:FYN [plasma membrane]"       │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │4420171              │"VEGFA:p-6Y-VEGFR2:SHC2 [plasma membrane]"                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │195396               │"VEGFR1 dimer:VEGFA, VEGFB, PGF dimers [plasma membrane]"             │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │215140               │"VEGFR3 dimer:VEGFC, VEGFD dimers [plasma membrane]"                  │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9624270              │"HB-EGF(161-208) [plasma membrane]"                                   │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │9018569              │"EGF:p-6Y-EGFR dimer:NICD3 [plasma membrane]"                         │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │1977956              │"ERBB4:EGFR heterodimer [plasma membrane]"                            │
// ├─────────────────────┼──────────────────────────────────────────────────────────────────────┤
// │444754               │"EGF-7TMs:CHS [plasma membrane]"                                      │
// └─────────────────────┴──────────────────────────────────────────────────────────────────────┘

// In the context of signal transduction pathways, species can refer to various molecules such as proteins, ions, or other signaling molecules. Here are two sets based on their concentration levels:
//
// ▎High Concentration Species
//
// 1. Cyclic AMP (cAMP) - A common second messenger that is often present in relatively high concentrations in cells.
// 2. Calcium ions (Ca²⁺) - These ions are crucial for many signaling processes and can be found at high concentrations within specific compartments of the cell.
//
// ▎Low Concentration Species
//
// 1. Nitric Oxide (NO) - A signaling molecule that is typically present in very low concentrations due to its short half-life.
// 2. Receptor Tyrosine Kinases (RTKs) - While these proteins are critical for signaling, their expression levels can vary widely, and they are often present at lower concentrations compared to other signaling molecules.
//
// These sets illustrate the diversity in concentration levels of different species involved in signal transduction pathways

MATCH (targetPathway:Pathway)
WHERE targetPathway.dbId IN [162582]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node
WITH COLLECT(DISTINCT node) AS reactionsOfInterest
MATCH (physicalEntity:PhysicalEntity)
WHERE
  physicalEntity.displayName CONTAINS 'cAMP' AND
  EXISTS {
    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
    WHERE reactionLikeEvent IN reactionsOfInterest
  }
RETURN physicalEntity.dbId, physicalEntity.displayName;

// ╒═════════════════════╤═════════════════════════════════════════════╕
// │"physicalEntity.dbId"│"physicalEntity.displayName"                 │
// ╞═════════════════════╪═════════════════════════════════════════════╡
// │8951729              │"PKA tetramer:4xcAMP [cytosol]"              │
// ├─────────────────────┼─────────────────────────────────────────────┤
// │30389                │"cAMP [cytosol]"                             │
// ├─────────────────────┼─────────────────────────────────────────────┤
// │111923               │"cAMP:PKA regulatory subunit [cytosol]"      │
// ├─────────────────────┼─────────────────────────────────────────────┤
// │5610566              │"PKA regulatory subunits:cAMP [ciliary base]"│
// └─────────────────────┴─────────────────────────────────────────────┘

MATCH (targetPathway:Pathway)
WHERE targetPathway.dbId IN [162582]
CALL
  apoc.path.subgraphNodes(
    targetPathway,
    {relationshipFilter: "hasEvent>", labelFilter: ">ReactionLikeEvent"}
  )
  YIELD node
WITH COLLECT(DISTINCT node) AS reactionsOfInterest
MATCH (physicalEntity:PhysicalEntity)
WHERE
  physicalEntity.displayName CONTAINS 'NO ' AND
  EXISTS {
    MATCH (physicalEntity)<-[:output]-(reactionLikeEvent:ReactionLikeEvent)
    WHERE reactionLikeEvent IN reactionsOfInterest
  }
RETURN physicalEntity.dbId, physicalEntity.displayName;

// ╒═════════════════════╤════════════════════════════╕
// │"physicalEntity.dbId"│"physicalEntity.displayName"│
// ╞═════════════════════╪════════════════════════════╡
// │202124               │"NO [cytosol]"              │
// └─────────────────────┴────────────────────────────┘

MATCH (n)
WHERE
  n.dbId IN [
    164358,
    202124,
    29968,
    5610577,
    5610579,
    70106,
    29468,
    170655,
    163622,
    1497830,
    170665,
    29356,
    396910,
    29368,
    392049,
    29364,
    30389,
    29366,
    74294,
    113592,
    111865,
    111294,
    5693375,
    392129,
    392129,
    111930,
    111930,
    111930,
    202127,
    202127,
    5610727,
    5610727,
    5610727,
    5610727,
    170676,
    170676
  ]
RETURN n;

MATCH (n {dbId: 202124}), (m {dbId: 30389})
CALL apoc.algo.dijkstra(n, m, "input|output", "", 1) YIELD path, weight
RETURN path;
// OPTIONAL MATCH
//   (n)-[:catalystActivity]->
// (c:CatalystActivity)-[:physicalEntity]->
// (m:PhysicalEntity)

;//
WITH [
  392129, 5610727, 202127, 170676, 111930, 164358, 202124, 29968, 5610577, 5610579,
  70106, 29468, 170655, 163622, 1497830, 170665, 29356, 396910, 29368, 392049, 29364,
  30389, 29366, 74294, 113592, 111865, 111294, 5693375
] AS network
WITH network
MATCH (node)
WHERE node.dbId IN network
RETURN node
  UNION
WITH [
  392129, 5610727, 202127, 170676, 111930, 164358, 202124, 29968, 5610577, 5610579,
  70106, 29468, 170655, 163622, 1497830, 170665, 29356, 396910, 29368, 392049, 29364,
  30389, 29366, 74294, 113592, 111865, 111294, 5693375
] AS network
MATCH
  (reaction:ReactionLikeEvent)-[:catalystActivity]->
  (c:CatalystActivity)-[:physicalEntity]->
  (node:PhysicalEntity)
WHERE reaction.dbId IN network AND node.dbId IN network
RETURN c AS node
UNION
WITH [
  392129, 5610727, 202127, 170676, 111930, 164358, 202124, 29968, 5610577, 5610579,
  70106, 29468, 170655, 163622, 1497830, 170665, 29356, 396910, 29368, 392049, 29364,
  30389, 29366, 74294, 113592, 111865, 111294, 5693375
] AS network
MATCH (reaction:ReactionLikeEvent)-[:regulatedBy]->(regulation)-[:regulator]->(regulator:PhysicalEntity)
WHERE reaction.dbId IN network AND regulator.dbId IN network
RETURN regulation AS node



// input species
MATCH (n)
WHERE n.dbId IN [29364, 113592, 29368, 70106, 29468]
RETURN n

// output species
MATCH (n)
WHERE n.dbId IN [29356, 202124, 29968, 30389, 29366, 111294]
RETURN n

// experiment
MATCH (n:PhysicalEntity)
WITH n LIMIT 10
CALL {
    WITH n
    MATCH (n)--(r:ReactionLikeEvent)
    RETURN COLLECT({rId: r.dbId}) AS react
}
WITH COLLECT({react: react}) AS nodes
UNWIND nodes AS A
UNWIND A.react AS B
RETURN apoc.convert.toSet(apoc.coll.flatten(COLLECT(B.rId)));

// input species
MATCH (n)
WHERE n.dbId IN [164358, 1497830, 163622, 170665, 29356, 202124, 396910, 29968, 392049, 5610577, 5610579, 170655, 30389, 74294, 29366, 111865, 111294, 5693375]
RETURN n;

// output species
MATCH (n)
WHERE n.dbId IN [164358, 1497830, 163622, 170665, 396910, 170655, 392049, 5610577, 5610579, 29364, 74294, 113592, 29368, 111865, 70106, 29468, 5693375]
RETURN n;
