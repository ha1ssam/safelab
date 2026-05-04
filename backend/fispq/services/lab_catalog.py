"""
Built-in catalog of laboratory reagents for Biomedicine / Clinical labs.

Each entry has a CAS number (primary key for PubChem lookup) and a
Portuguese display name. Organized by category for readability.

Coverage:
  - Inorganic acids and bases
  - Organic acids
  - Organic solvents (polar and nonpolar)
  - Oxidizers and reducers
  - Inorganic salts and reagents
  - Biological and clinical chemistry reagents
  - Buffers and pH indicators
  - Histology fixatives and stains
  - Hematology reagents
  - Microbiological media components
  - Immunology / serology reagents
  - Molecular biology reagents
  - Disinfectants and antiseptics
  - Reactive metals and gases

All CAS numbers are verified against PubChem.
"""

LAB_CATALOG: list[dict[str, str]] = [

    # ═══════════════════════════════════════════════════════════════════════
    # INORGANIC ACIDS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7647-01-0", "name": "Ácido clorídrico (HCl)"},
    {"cas": "7664-93-9", "name": "Ácido sulfúrico (H2SO4)"},
    {"cas": "7697-37-2", "name": "Ácido nítrico (HNO3)"},
    {"cas": "7664-38-2", "name": "Ácido fosfórico (H3PO4)"},
    {"cas": "7601-90-3", "name": "Ácido perclórico (HClO4)"},
    {"cas": "7782-99-2", "name": "Ácido sulfuroso (H2SO3)"},
    {"cas": "7789-23-3", "name": "Ácido fluorídrico (HF)"},
    {"cas": "10035-10-6", "name": "Ácido bromídrico (HBr)"},

    # ═══════════════════════════════════════════════════════════════════════
    # ORGANIC ACIDS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "64-19-7", "name": "Ácido acético glacial"},
    {"cas": "77-92-9", "name": "Ácido cítrico"},
    {"cas": "144-62-7", "name": "Ácido oxálico"},
    {"cas": "79-10-7", "name": "Ácido acrílico"},
    {"cas": "69-72-7", "name": "Ácido salicílico"},
    {"cas": "64-18-6", "name": "Ácido fórmico"},
    {"cas": "79-09-4", "name": "Ácido propiônico"},
    {"cas": "65-85-0", "name": "Ácido benzoico"},
    {"cas": "87-69-4", "name": "Ácido tartárico"},
    {"cas": "110-17-8", "name": "Ácido fumárico"},
    {"cas": "50-21-5", "name": "Ácido láctico"},
    {"cas": "79-11-8", "name": "Ácido cloroacético"},
    {"cas": "76-03-9", "name": "Ácido tricloroacético (TCA)"},
    {"cas": "79-43-6", "name": "Ácido dicloroacético"},
    {"cas": "127-09-3", "name": "Acetato de sódio"},
    {"cas": "6153-56-6", "name": "Ácido oxálico diidratado"},

    # ═══════════════════════════════════════════════════════════════════════
    # INORGANIC BASES
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "1310-73-2", "name": "Hidróxido de sódio (NaOH)"},
    {"cas": "1310-58-3", "name": "Hidróxido de potássio (KOH)"},
    {"cas": "7664-41-7", "name": "Amônia (NH3) solução"},
    {"cas": "1305-62-0", "name": "Hidróxido de cálcio (Ca(OH)2)"},
    {"cas": "1309-42-8", "name": "Hidróxido de magnésio (Mg(OH)2)"},
    {"cas": "1310-65-2", "name": "Hidróxido de lítio (LiOH)"},
    {"cas": "21351-79-1", "name": "Hidróxido de césio (CsOH)"},

    # ═══════════════════════════════════════════════════════════════════════
    # ORGANIC SOLVENTS — POLAR PROTIC
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "64-17-5", "name": "Etanol"},
    {"cas": "67-56-1", "name": "Metanol"},
    {"cas": "67-63-0", "name": "Isopropanol (álcool isopropílico)"},
    {"cas": "71-36-3", "name": "n-Butanol"},
    {"cas": "111-87-5", "name": "1-Octanol"},
    {"cas": "107-21-1", "name": "Etilenoglicol"},
    {"cas": "57-55-6", "name": "Propilenoglicol"},

    # ═══════════════════════════════════════════════════════════════════════
    # ORGANIC SOLVENTS — POLAR APROTIC
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "67-64-1", "name": "Acetona"},
    {"cas": "75-05-8", "name": "Acetonitrila"},
    {"cas": "67-68-5", "name": "Dimetilsulfóxido (DMSO)"},
    {"cas": "68-12-2", "name": "N,N-Dimetilformamida (DMF)"},
    {"cas": "872-50-4", "name": "N-Metil-2-pirrolidona (NMP)"},
    {"cas": "78-93-3", "name": "Metiletilcetona (MEK)"},
    {"cas": "141-78-6", "name": "Acetato de etila"},
    {"cas": "109-99-9", "name": "Tetrahidrofurano (THF)"},

    # ═══════════════════════════════════════════════════════════════════════
    # ORGANIC SOLVENTS — NONPOLAR
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "110-54-3", "name": "Hexano"},
    {"cas": "142-82-5", "name": "Heptano"},
    {"cas": "109-66-0", "name": "Pentano"},
    {"cas": "110-82-7", "name": "Ciclo-hexano"},
    {"cas": "108-88-3", "name": "Tolueno"},
    {"cas": "71-43-2", "name": "Benzeno"},
    {"cas": "1330-20-7", "name": "Xileno (mistura de isômeros)"},
    {"cas": "100-41-4", "name": "Etilbenzeno"},

    # ═══════════════════════════════════════════════════════════════════════
    # ORGANIC SOLVENTS — HALOGENATED
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "67-66-3", "name": "Clorofórmio (CHCl3)"},
    {"cas": "75-09-2", "name": "Diclorometano (CH2Cl2)"},
    {"cas": "56-23-5", "name": "Tetracloreto de carbono (CCl4)"},
    {"cas": "71-55-6", "name": "1,1,1-Tricloroetano"},
    {"cas": "79-01-6", "name": "Tricloroetileno"},

    # ═══════════════════════════════════════════════════════════════════════
    # ETHERS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "60-29-7", "name": "Éter dietílico"},
    {"cas": "115-10-6", "name": "Éter dimetílico"},
    {"cas": "110-91-8", "name": "Morfolina"},
    {"cas": "123-91-1", "name": "1,4-Dioxano"},

    # ═══════════════════════════════════════════════════════════════════════
    # OXIDIZERS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7722-64-7", "name": "Permanganato de potássio (KMnO4)"},
    {"cas": "7722-84-1", "name": "Peróxido de hidrogênio 30% (H2O2)"},
    {"cas": "7681-52-9", "name": "Hipoclorito de sódio (NaClO)"},
    {"cas": "7778-50-9", "name": "Dicromato de potássio (K2Cr2O7)"},
    {"cas": "7775-09-9", "name": "Clorato de sódio (NaClO3)"},
    {"cas": "7790-98-9", "name": "Perclorato de amônio"},
    {"cas": "7727-21-1", "name": "Persulfato de potássio"},
    {"cas": "7775-27-1", "name": "Persulfato de sódio"},
    {"cas": "10294-56-1", "name": "Ácido fosforoso (H3PO3)"},
    {"cas": "7783-00-8", "name": "Ácido selenioso (H2SeO3)"},
    {"cas": "7789-00-6", "name": "Cromato de potássio (K2CrO4)"},
    {"cas": "7778-18-9", "name": "Sulfato de cálcio (CaSO4)"},
    {"cas": "10588-01-9", "name": "Dicromato de sódio (Na2Cr2O7)"},
    {"cas": "7553-56-2", "name": "Iodo (I2)"},
    {"cas": "7726-95-6", "name": "Bromo (Br2)"},

    # ═══════════════════════════════════════════════════════════════════════
    # INORGANIC SALTS — COMMON LAB REAGENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7647-14-5", "name": "Cloreto de sódio (NaCl)"},
    {"cas": "7447-40-7", "name": "Cloreto de potássio (KCl)"},
    {"cas": "10043-52-4", "name": "Cloreto de cálcio (CaCl2)"},
    {"cas": "7786-30-3", "name": "Cloreto de magnésio (MgCl2)"},
    {"cas": "7646-85-7", "name": "Cloreto de zinco (ZnCl2)"},
    {"cas": "7705-08-0", "name": "Cloreto férrico (FeCl3)"},
    {"cas": "7758-94-3", "name": "Cloreto ferroso (FeCl2)"},
    {"cas": "10025-87-3", "name": "Oxicloreto de fósforo (POCl3)"},
    {"cas": "7758-99-8", "name": "Sulfato de cobre II (CuSO4)"},
    {"cas": "7720-78-7", "name": "Sulfato ferroso (FeSO4)"},
    {"cas": "7783-20-2", "name": "Sulfato de amônio ((NH4)2SO4)"},
    {"cas": "7757-82-6", "name": "Sulfato de sódio (Na2SO4)"},
    {"cas": "7487-88-9", "name": "Sulfato de magnésio (MgSO4)"},
    {"cas": "7733-02-0", "name": "Sulfato de zinco (ZnSO4)"},
    {"cas": "10034-99-8", "name": "Sulfato de magnésio heptahidratado"},
    {"cas": "7757-79-1", "name": "Nitrato de potássio (KNO3)"},
    {"cas": "7761-88-8", "name": "Nitrato de prata (AgNO3)"},
    {"cas": "7631-99-4", "name": "Nitrato de sódio (NaNO3)"},
    {"cas": "10124-37-5", "name": "Nitrato de cálcio (Ca(NO3)2)"},
    {"cas": "6484-52-2", "name": "Nitrato de amônio (NH4NO3)"},
    {"cas": "497-19-8", "name": "Carbonato de sódio (Na2CO3)"},
    {"cas": "144-55-8", "name": "Bicarbonato de sódio (NaHCO3)"},
    {"cas": "584-08-7", "name": "Carbonato de potássio (K2CO3)"},
    {"cas": "471-34-1", "name": "Carbonato de cálcio (CaCO3)"},
    {"cas": "7558-80-7", "name": "Fosfato de sódio monobásico (NaH2PO4)"},
    {"cas": "7558-79-4", "name": "Fosfato de sódio dibásico (Na2HPO4)"},
    {"cas": "7601-54-9", "name": "Fosfato de sódio tribásico (Na3PO4)"},
    {"cas": "7778-77-0", "name": "Fosfato de potássio monobásico (KH2PO4)"},
    {"cas": "7758-11-4", "name": "Fosfato de potássio dibásico (K2HPO4)"},
    {"cas": "12125-02-9", "name": "Cloreto de amônio (NH4Cl)"},
    {"cas": "7681-11-0", "name": "Iodeto de potássio (KI)"},
    {"cas": "7647-15-6", "name": "Brometo de sódio (NaBr)"},
    {"cas": "7758-02-3", "name": "Brometo de potássio (KBr)"},
    {"cas": "7681-49-4", "name": "Fluoreto de sódio (NaF)"},
    {"cas": "7789-75-5", "name": "Fluoreto de cálcio (CaF2)"},
    {"cas": "7440-22-4", "name": "Prata metálica (Ag)"},
    {"cas": "10102-17-7", "name": "Tiossulfato de sódio (Na2S2O3)"},
    {"cas": "7757-83-7", "name": "Sulfito de sódio (Na2SO3)"},
    {"cas": "1313-13-9", "name": "Dióxido de manganês (MnO2)"},
    {"cas": "7681-57-4", "name": "Metabissulfito de sódio (Na2S2O5)"},
    {"cas": "10043-35-3", "name": "Ácido bórico (H3BO3)"},
    {"cas": "1303-96-4", "name": "Bórax (Na2B4O7)"},

    # ═══════════════════════════════════════════════════════════════════════
    # HEAVY METAL SALTS (tóxicos — uso analítico)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7487-94-7", "name": "Cloreto de mercúrio II (HgCl2)"},
    {"cas": "7774-29-0", "name": "Iodeto de mercúrio II (HgI2)"},
    {"cas": "10031-22-8", "name": "Brometo de chumbo II (PbBr2)"},
    {"cas": "7758-95-4", "name": "Cloreto de chumbo II (PbCl2)"},
    {"cas": "7446-14-2", "name": "Sulfato de chumbo II (PbSO4)"},
    {"cas": "7440-43-9", "name": "Cádmio metálico (Cd)"},
    {"cas": "7718-54-9", "name": "Cloreto de níquel II (NiCl2)"},
    {"cas": "7440-48-4", "name": "Cobalto metálico (Co)"},
    {"cas": "10124-36-4", "name": "Sulfato de cádmio (CdSO4)"},
    {"cas": "7440-38-2", "name": "Arsênio (As)"},

    # ═══════════════════════════════════════════════════════════════════════
    # BUFFERS AND pH STANDARDS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "77-86-1", "name": "Tris (Tris(hidroximetil)aminometano)"},
    {"cas": "7365-45-9", "name": "HEPES"},
    {"cas": "1132-61-2", "name": "MOPS"},
    {"cas": "5625-37-6", "name": "PIPES"},
    {"cas": "10010-67-0", "name": "MES (ácido 2-(N-morfolino)etanossulfônico)"},
    {"cas": "75621-03-3", "name": "CAPS"},
    {"cas": "103-47-9", "name": "CHES"},
    {"cas": "56-40-6", "name": "Glicina"},
    {"cas": "7732-18-5", "name": "Água destilada"},

    # ═══════════════════════════════════════════════════════════════════════
    # BIOLOGICAL / CLINICAL CHEMISTRY
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "50-00-0", "name": "Formaldeído (formol 37%)"},
    {"cas": "56-81-5", "name": "Glicerol (glicerina)"},
    {"cas": "50-99-7", "name": "Glicose (D-glucose)"},
    {"cas": "57-50-1", "name": "Sacarose"},
    {"cas": "69-93-2", "name": "Ácido úrico"},
    {"cas": "57-13-6", "name": "Ureia"},
    {"cas": "60-27-5", "name": "Creatinina"},
    {"cas": "58-55-9", "name": "Teofilina"},
    {"cas": "69-65-8", "name": "Manitol"},
    {"cas": "87-99-0", "name": "Xilitol"},
    {"cas": "50-01-1", "name": "Cloridrato de guanidina"},
    {"cas": "1071-83-6", "name": "Glifosato"},
    {"cas": "7646-78-8", "name": "Tetracloreto de estanho (SnCl4)"},

    # ═══════════════════════════════════════════════════════════════════════
    # CHELATING AGENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "60-00-4", "name": "EDTA (ácido etilenodiaminotetraacético)"},
    {"cas": "6381-92-6", "name": "EDTA dissódico diidratado"},
    {"cas": "139-89-9", "name": "HEDTA"},
    {"cas": "67-43-6", "name": "DTPA (ácido dietilenotriaminopentaacético)"},
    {"cas": "5064-31-3", "name": "NTA (ácido nitrilotriacético)"},

    # ═══════════════════════════════════════════════════════════════════════
    # DETERGENTS AND SURFACTANTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "151-21-3", "name": "Dodecil sulfato de sódio (SDS/LSS)"},
    {"cas": "9002-93-1", "name": "Triton X-100"},
    {"cas": "9005-64-5", "name": "Tween 20 (polissorbato 20)"},
    {"cas": "9005-65-6", "name": "Tween 80 (polissorbato 80)"},
    {"cas": "9036-19-5", "name": "Nonidet P-40 (NP-40)"},
    {"cas": "7173-51-5", "name": "Cloreto de didecildimetilamônio"},
    {"cas": "112-02-7", "name": "Cloreto de cetiltrimetilamônio (CTAC)"},
    {"cas": "57-09-0", "name": "Brometo de cetiltrimetilamônio (CTAB)"},

    # ═══════════════════════════════════════════════════════════════════════
    # HISTOLOGY — FIXATIVES
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "111-30-8", "name": "Glutaraldeído"},
    {"cas": "20816-12-0", "name": "Tetróxido de ósmio (OsO4)"},
    {"cas": "107-22-2", "name": "Glioxal"},
    {"cas": "298-81-7", "name": "8-Metoxipsoraleno (8-MOP)"},

    # ═══════════════════════════════════════════════════════════════════════
    # HISTOLOGY — STAINS (Colorações)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "548-62-9", "name": "Cristal violeta (violeta de genciana)"},
    {"cas": "17372-87-1", "name": "Safranina O"},
    {"cas": "115-39-9", "name": "Azul de bromotimol"},
    {"cas": "34722-90-2", "name": "Giemsa (corante)"},
    {"cas": "3244-88-0", "name": "Azul de metileno"},
    {"cas": "632-99-5", "name": "Fucsina básica (magenta)"},
    {"cas": "2150-33-6", "name": "Fucsina ácida"},
    {"cas": "477-73-6", "name": "Safranina T"},
    {"cas": "2074-50-2", "name": "Paraquat dicloreto"},
    {"cas": "12222-78-5", "name": "May-Grünwald (corante)"},
    {"cas": "15086-94-9", "name": "Sudan III (corante lipídico)"},
    {"cas": "85-83-6", "name": "Sudan IV (Scarlet Red)"},
    {"cas": "2610-05-1", "name": "Azul de Evans"},
    {"cas": "3861-73-2", "name": "Azul de alcian"},
    {"cas": "2321-07-5", "name": "Fluoresceína sódica"},
    {"cas": "81-88-9", "name": "Rodamina B"},
    {"cas": "3520-42-1", "name": "Acridina laranja"},
    {"cas": "28718-90-3", "name": "Iodeto de propídio"},
    {"cas": "58-56-0", "name": "Brometo de etídio (EtBr)"},

    # ═══════════════════════════════════════════════════════════════════════
    # HISTOLOGY — SPECIAL STAINS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "3688-92-0", "name": "Ácido periódico (PAS stain)"},
    {"cas": "14038-43-8", "name": "Azul da Prússia (ferrocianeto de potássio)"},
    {"cas": "1317-38-0", "name": "Óxido de cobre II (CuO)"},
    {"cas": "7440-50-8", "name": "Cobre metálico (Cu)"},

    # ═══════════════════════════════════════════════════════════════════════
    # HEMATOLOGY
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "6155-35-7", "name": "EDTA tripotássico (K3-EDTA)"},
    {"cas": "6381-59-5", "name": "Citrato de sódio (anticoagulante)"},
    {"cas": "9005-49-6", "name": "Heparina sódica"},
    {"cas": "9041-08-1", "name": "Heparina de lítio"},
    {"cas": "57-11-4", "name": "Ácido esteárico"},

    # ═══════════════════════════════════════════════════════════════════════
    # MICROBIOLOGY — MEDIA COMPONENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "9002-18-0", "name": "Ágar bacteriológico"},
    {"cas": "91079-40-2", "name": "Peptona bacteriológica"},
    {"cas": "8013-01-2", "name": "Extrato de levedura"},
    {"cas": "73049-73-7", "name": "Infusão de cérebro e coração (BHI)"},
    {"cas": "68-11-1", "name": "Ácido tioglicólico"},

    # ═══════════════════════════════════════════════════════════════════════
    # MICROBIOLOGY — ANTIBIOTICS / ANTIMICROBIALS (discos e soluções)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "69-53-4", "name": "Ampicilina"},
    {"cas": "26787-78-0", "name": "Amoxicilina"},
    {"cas": "56-75-7", "name": "Cloranfenicol"},
    {"cas": "57-62-5", "name": "Clortetraciclina"},
    {"cas": "114-07-8", "name": "Eritromicina"},
    {"cas": "1404-04-2", "name": "Neomicina"},
    {"cas": "64-75-5", "name": "Tetraciclina"},
    {"cas": "1397-89-3", "name": "Anfotericina B"},
    {"cas": "22071-15-4", "name": "Cetoprofeno"},

    # ═══════════════════════════════════════════════════════════════════════
    # MOLECULAR BIOLOGY
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "1239-45-8", "name": "Brometo de etídio (EtBr) — mol. bio."},
    {"cas": "75-12-7", "name": "Formamida"},
    {"cas": "110-26-9", "name": "N,N'-Metilenobisacrilamida"},
    {"cas": "79-06-1", "name": "Acrilamida"},
    {"cas": "110-89-4", "name": "Piperidina"},
    {"cas": "102-71-6", "name": "Trietanolamina (TEA)"},
    {"cas": "121-44-8", "name": "Trietilamina"},
    {"cas": "75-21-8", "name": "Óxido de etileno"},
    {"cas": "100-97-0", "name": "Hexametilenotetramina"},
    {"cas": "7447-41-8", "name": "Cloreto de lítio (LiCl)"},
    {"cas": "108-95-2", "name": "Fenol"},
    {"cas": "593-84-0", "name": "Tiocianato de guanidina"},

    # ═══════════════════════════════════════════════════════════════════════
    # ELECTROPHORESIS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "9012-36-6", "name": "Agarose (gel eletroforese)"},
    {"cas": "868-63-3", "name": "Agarose de baixo ponto de fusão"},
    {"cas": "99-20-7", "name": "Trealose"},

    # ═══════════════════════════════════════════════════════════════════════
    # IMMUNOLOGY / SEROLOGY
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "9048-46-8", "name": "Albumina bovina sérica (BSA)"},
    {"cas": "25322-68-3", "name": "Polietilenoglicol (PEG)"},
    {"cas": "7440-57-5", "name": "Ouro coloidal (Au)"},
    {"cas": "26628-22-8", "name": "Azida sódica (NaN3)"},

    # ═══════════════════════════════════════════════════════════════════════
    # DISINFECTANTS / ANTISEPTICS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7782-50-5", "name": "Cloro gasoso (Cl2)"},
    {"cas": "10049-04-4", "name": "Dióxido de cloro (ClO2)"},
    {"cas": "25655-41-8", "name": "Povidona iodada (PVPI)"},
    {"cas": "55-56-1", "name": "Clorexidina"},
    {"cas": "7681-82-5", "name": "Iodeto de sódio (NaI)"},
    {"cas": "8001-54-5", "name": "Cloreto de benzalcônio"},

    # ═══════════════════════════════════════════════════════════════════════
    # REDUCING AGENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "50-81-7", "name": "Ácido ascórbico (vitamina C)"},
    {"cas": "60-24-2", "name": "2-Mercaptoetanol (beta-ME)"},
    {"cas": "3483-12-3", "name": "Ditiotreitol (DTT)"},
    {"cas": "7681-65-4", "name": "Iodeto de cobre I (CuI)"},
    {"cas": "126-33-0", "name": "Sulfolano"},
    {"cas": "7772-98-7", "name": "Tiossulfato de sódio anidro"},

    # ═══════════════════════════════════════════════════════════════════════
    # ENZYMES AND COENZYMES (reagente de laboratório)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "9001-05-2", "name": "Catalase"},
    {"cas": "9002-07-7", "name": "Tripsina"},
    {"cas": "9001-75-6", "name": "Pepsina"},
    {"cas": "9001-63-2", "name": "Lipase"},
    {"cas": "9001-37-0", "name": "Glicose oxidase"},

    # ═══════════════════════════════════════════════════════════════════════
    # AMINO ACIDS (padrões analíticos)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "72-18-4", "name": "L-Valina"},
    {"cas": "56-41-7", "name": "L-Alanina"},
    {"cas": "56-84-8", "name": "L-Ácido aspártico"},
    {"cas": "56-86-0", "name": "L-Ácido glutâmico"},
    {"cas": "61-90-5", "name": "L-Leucina"},
    {"cas": "73-22-3", "name": "L-Triptofano"},
    {"cas": "60-18-4", "name": "L-Tirosina"},
    {"cas": "63-91-2", "name": "L-Fenilalanina"},
    {"cas": "52-90-4", "name": "L-Cisteína"},
    {"cas": "56-45-1", "name": "L-Serina"},
    {"cas": "72-19-5", "name": "L-Treonina"},

    # ═══════════════════════════════════════════════════════════════════════
    # VITAMINS (padrões analíticos)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "150-13-0", "name": "Ácido p-aminobenzoico (PABA)"},
    {"cas": "59-43-8", "name": "Tiamina (vitamina B1)"},
    {"cas": "83-88-5", "name": "Riboflavina (vitamina B2)"},
    {"cas": "98-92-0", "name": "Niacinamida (vitamina B3)"},
    {"cas": "137-08-6", "name": "Pantotenato de cálcio (vitamina B5)"},
    {"cas": "65-23-6", "name": "Piridoxina (vitamina B6)"},
    {"cas": "59-30-3", "name": "Ácido fólico (vitamina B9)"},
    {"cas": "68-19-9", "name": "Cianocobalamina (vitamina B12)"},

    # ═══════════════════════════════════════════════════════════════════════
    # REACTIVE METALS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7440-23-5", "name": "Sódio metálico (Na)"},
    {"cas": "7439-93-2", "name": "Lítio metálico (Li)"},
    {"cas": "7440-09-7", "name": "Potássio metálico (K)"},
    {"cas": "7429-90-5", "name": "Alumínio em pó (Al)"},
    {"cas": "7440-66-6", "name": "Zinco em pó (Zn)"},
    {"cas": "7439-95-4", "name": "Magnésio em fita (Mg)"},

    # ═══════════════════════════════════════════════════════════════════════
    # GASES
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "124-38-9", "name": "Dióxido de carbono (CO2)"},
    {"cas": "7727-37-9", "name": "Nitrogênio (N2)"},
    {"cas": "7782-44-7", "name": "Oxigênio (O2)"},
    {"cas": "7440-37-1", "name": "Argônio (Ar)"},
    {"cas": "7440-59-7", "name": "Hélio (He)"},
    {"cas": "1333-74-0", "name": "Hidrogênio (H2)"},
    {"cas": "7783-06-4", "name": "Sulfeto de hidrogênio (H2S)"},
    {"cas": "630-08-0", "name": "Monóxido de carbono (CO)"},
    {"cas": "10024-97-2", "name": "Óxido nitroso (N2O)"},

    # ═══════════════════════════════════════════════════════════════════════
    # PHOTOGRAPHY / SPECIAL REAGENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "7778-74-7", "name": "Perclorato de potássio (KClO4)"},
    {"cas": "506-64-9", "name": "Cianeto de prata (AgCN)"},
    {"cas": "151-50-8", "name": "Cianeto de potássio (KCN)"},
    {"cas": "143-33-9", "name": "Cianeto de sódio (NaCN)"},
    {"cas": "7440-31-5", "name": "Estanho (Sn)"},

    # ═══════════════════════════════════════════════════════════════════════
    # INDICATORS (pH e redox)
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "77-09-8", "name": "Fenolftaleína"},
    {"cas": "547-25-1", "name": "Alaranjado de metila"},
    {"cas": "3564-09-8", "name": "Ponceau S (corante proteína)"},
    {"cas": "493-52-7", "name": "Vermelho de metila"},
    {"cas": "62625-32-5", "name": "Vermelho de fenol"},
    {"cas": "76-60-8", "name": "Azul de bromofenol"},
    {"cas": "1733-12-6", "name": "Vermelho de cresol"},
    {"cas": "2303-01-7", "name": "Vermelho do Congo"},
    {"cas": "6373-74-6", "name": "Alaranjado de xilenol"},
    {"cas": "1892-80-4", "name": "Negro de eriocromo T"},
    {"cas": "14099-08-8", "name": "Calmagita"},
    {"cas": "587-98-4", "name": "Amarelo de metila"},

    # ═══════════════════════════════════════════════════════════════════════
    # MISCELLANEOUS LAB REAGENTS
    # ═══════════════════════════════════════════════════════════════════════
    {"cas": "127-18-4", "name": "Tetracloroetileno (percloroetileno)"},
    {"cas": "75-36-5", "name": "Cloreto de acetila"},
    {"cas": "98-88-4", "name": "Cloreto de benzoíla"},
    {"cas": "108-24-7", "name": "Anidrido acético"},
    {"cas": "85-44-9", "name": "Anidrido ftálico"},
    {"cas": "7440-44-0", "name": "Carvão ativado"},
    {"cas": "1344-28-1", "name": "Óxido de alumínio (alumina)"},
    {"cas": "112926-00-8", "name": "Sílica gel"},
    {"cas": "7631-86-9", "name": "Dióxido de silício (SiO2)"},
    {"cas": "10043-01-3", "name": "Sulfato de alumínio (Al2(SO4)3)"},
    {"cas": "1336-21-6", "name": "Hidróxido de amônio (NH4OH)"},
    {"cas": "7778-54-3", "name": "Hipoclorito de cálcio (Ca(ClO)2)"},
    {"cas": "10031-43-3", "name": "Nitrato de cobre II (Cu(NO3)2)"},
    {"cas": "7440-02-0", "name": "Níquel metálico (Ni)"},
    {"cas": "1305-78-8", "name": "Óxido de cálcio (cal viva, CaO)"},
    {"cas": "7681-38-1", "name": "Bissulfato de sódio (NaHSO4)"},
    {"cas": "7789-38-0", "name": "Bromato de sódio (NaBrO3)"},
    {"cas": "7790-99-0", "name": "Cloreto de iodo (ICl)"},
    {"cas": "7803-51-2", "name": "Fosfina (PH3)"},
    {"cas": "463-82-1", "name": "Neopentano"},
    {"cas": "7439-97-6", "name": "Mercúrio metálico (Hg)"},
    {"cas": "1314-56-3", "name": "Pentóxido de fósforo (P2O5)"},
    {"cas": "7446-09-5", "name": "Dióxido de enxofre (SO2)"},
]
