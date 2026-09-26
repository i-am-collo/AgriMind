"""
AgriMind — Agronomic Knowledge Base
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A curated corpus of verified agronomic facts used as the retrieval
source for the RAG (Retrieval-Augmented Generation) engine.

Each document in the corpus is a self-contained chunk describing:
- A specific disease / pest / deficiency / healthy state
- Its category (Crops | Poultry | Livestock)
- Visual symptoms, diagnosis criteria
- Exact treatment protocols with dosages
- Preventive and biosecurity measures
- FAO / extension guide references

These chunks are embedded and retrieved at query time to provide
Gemini with verified, domain-specific context before it generates
the structured DiagnosticResult.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Corpus
# Each entry: {id, category, topic, text}
# Keep text chunks under ~400 tokens for efficient embedding.
# ---------------------------------------------------------------------------

CORPUS: list[dict] = [

    # =========================================================
    # CROPS — Healthy
    # =========================================================
    {
        "id": "crop_healthy",
        "category": "Crops",
        "topic": "Healthy Crop Specimen",
        "text": (
            "A healthy maize or cereal crop presents vibrant, uniform green pigmentation "
            "across all leaf surfaces. The leaf architecture shows no lesions, pustules, "
            "or necrotic spots. Vascular tissue is intact with no wilting. Canopy surface "
            "is clean — no insect frass, webbing, or discoloration. Stem internodes are "
            "firm and upright. Root system anchoring is strong with no rot smell. "
            "No chemical intervention is required. Maintain NPK fertilization schedule "
            "appropriate to the crop growth stage and continue standard irrigation cycles. "
            "Perform weekly visual scouting for early pest or disease detection."
        ),
    },

    # =========================================================
    # CROPS — Nitrogen Deficiency
    # =========================================================
    {
        "id": "crop_nitrogen_deficiency",
        "category": "Crops",
        "topic": "Nitrogen Deficiency — Interveinal Chlorosis",
        "text": (
            "Nitrogen (N) deficiency causes V-shaped yellowing starting at the tips of "
            "lower, older leaves, progressing upward. The yellowing is uniform — no "
            "distinct spots or lesions. Upper canopy leaves appear pale green. "
            "Vegetative growth is stunted and stem elongation is reduced. "
            "Diagnosis: pale lower leaves with V-tip chlorosis in nitrogen-demanding crops. "
            "Optimal soil pH for N uptake: 6.0–6.8. "
            "Treatment: Apply Calcium Ammonium Nitrate (CAN 27% N) or Urea (46% N) "
            "at 5 kg/ha as a foliar spray, or top-dress at 50 kg/ha. "
            "Supplement with humic acid at 2 L/ha to improve N uptake efficiency. "
            "Correct soil pH with agricultural lime if below 6.0. "
            "Prevention: split nitrogen application across vegetative growth stages (V4, V8, VT). "
            "Practice leguminous cover crop rotation (soybean, cowpea) to fix atmospheric N. "
            "Source: FAO Fertilizer and Plant Nutrition Bulletin No. 16."
        ),
    },

    # =========================================================
    # CROPS — Fall Armyworm
    # =========================================================
    {
        "id": "crop_fall_armyworm",
        "category": "Crops",
        "topic": "Fall Armyworm — Spodoptera frugiperda",
        "text": (
            "Fall Armyworm (FAW) is the most economically destructive maize pest in "
            "sub-Saharan Africa. Larvae feed inside the plant whorl, creating a "
            "characteristic 'ragged window-pane' defoliation pattern. "
            "Visual signs: moist frass (greenish-black pellets) accumulated inside "
            "whorls; irregular holes on young leaves; larvae (caterpillars) 1–4 cm "
            "with an inverted Y marking on the head capsule. "
            "Larval instars 1–3 are most vulnerable to treatment. "
            "Biological control: Bacillus thuringiensis (Bt) var. kurstaki at 1 kg/ha "
            "applied directly into the whorl — effective on early instars. "
            "Chemical control: Emamectin Benzoate 5% SG at 200 g/ha, or "
            "Chlorantraniliprole 20% SC at 150 mL/ha. Apply in the early morning or "
            "late afternoon to protect beneficial insects. "
            "Install 4–6 pheromone FAW trapping stations per hectare for monitoring. "
            "Push-pull companion planting: Desmodium (push) + Napier grass (pull) "
            "reduces FAW pressure by 80% (FAO/CABI field trial data). "
            "Prevention: early planting before peak moth flight; destroy crop residue "
            "post-harvest to break the life cycle."
        ),
    },

    # =========================================================
    # CROPS — Northern Corn Leaf Blight (NCLB)
    # =========================================================
    {
        "id": "crop_nclb",
        "category": "Crops",
        "topic": "Northern Corn Leaf Blight — Exserohilum turcicum",
        "text": (
            "Northern Corn Leaf Blight (NCLB) is a fungal disease caused by "
            "Exserohilum turcicum. Lesions are distinctive: elongated, tan/grey, "
            "cigar-shaped, 5–15 cm long with wavy margins. "
            "Dark olive-green sporulation (conidia) is visible on the lesion surface "
            "under humid conditions. A chlorotic (yellow) halo surrounds necrotic tissue. "
            "The disease spreads from lower to upper canopy leaves under high humidity "
            "and temperatures of 18–27°C. "
            "Fungicide treatment: Azoxystrobin (250 g/L) + Propiconazole (250 g/L) "
            "at 0.5 L/ha applied at VT–R1 (silking) growth stage. "
            "Alternative: Pyraclostrobin + Metconazole at 0.4 L/ha. "
            "Supplement with foliar micronutrients (Zinc 0.5% + Manganese 0.3%) "
            "to strengthen leaf tissue. "
            "Cultural practices: switch to drip irrigation; avoid evening overhead "
            "watering to reduce leaf wetness period. "
            "Prevention: plant certified NCLB-resistant hybrid varieties; "
            "rotate with non-host legume crops (soybean, bean) for 1–2 seasons. "
            "Source: CIMMYT Maize Disease Manual."
        ),
    },

    # =========================================================
    # CROPS — Gray Leaf Spot
    # =========================================================
    {
        "id": "crop_gray_leaf_spot",
        "category": "Crops",
        "topic": "Gray Leaf Spot — Cercospora zeae-maydis",
        "text": (
            "Gray Leaf Spot (GLS) is a fungal disease that produces rectangular, "
            "tan-to-grey lesions bounded by leaf veins — giving them a brick-like "
            "appearance. Lesions are 1–4 cm long and 2–4 mm wide. "
            "The disease thrives in humid, warm conditions (25–30°C) with prolonged "
            "dew periods. GLS severely reduces photosynthetic area and grain fill. "
            "Fungicide: Propiconazole 25% EC at 0.5 L/ha at tasseling (VT stage). "
            "Strobilurin fungicides (Azoxystrobin) improve plant health and green "
            "leaf area retention. "
            "Reduce irrigation frequency; improve field drainage and air circulation. "
            "Plant resistant hybrid varieties selected for GLS tolerance. "
            "Minimum 2-year rotation away from maize."
        ),
    },

    # =========================================================
    # CROPS — Maize Streak Virus
    # =========================================================
    {
        "id": "crop_maize_streak_virus",
        "category": "Crops",
        "topic": "Maize Streak Virus — MSV (Leafhopper-transmitted)",
        "text": (
            "Maize Streak Virus (MSV) causes yellow/cream broken streaks running "
            "parallel to the midrib on young leaves. Severe infection produces "
            "a mosaic pattern with severely stunted plant height. "
            "Transmitted by the leafhopper Cicadulina mbila. "
            "There is NO curative chemical treatment for viral infections. "
            "Management: apply systemic insecticide (Imidacloprid 70% WS seed "
            "treatment at 5 mL/kg seed) to control leafhopper vector at planting. "
            "Foliar spray: Thiamethoxam 25% WG at 100 g/ha at 2–3 weeks post-emergence. "
            "Rogue (remove and destroy) heavily infected plants immediately to prevent spread. "
            "Plant MSV-tolerant/resistant hybrid varieties (e.g., WEMA, CIMMYT-MSV lines). "
            "Early planting at the onset of rains reduces vector pressure."
        ),
    },

    # =========================================================
    # POULTRY — Healthy Flock
    # =========================================================
    {
        "id": "poultry_healthy",
        "category": "Poultry",
        "topic": "Healthy Poultry Flock",
        "text": (
            "A healthy poultry flock displays: bright red, firm combs and wattles; "
            "smooth, clean, fully aligned plumage; clear, bright eyes with no discharge; "
            "active foraging and alert responses to stimuli; firm, well-formed droppings "
            "(caecal droppings are normal brown/green, not bloody). "
            "Feed intake and water consumption are consistent with age and bodyweight targets. "
            "No mortality above the normal baseline (broilers: <5% cumulative). "
            "Management: maintain litter moisture below 20%, ensure adequate ventilation "
            "(0.3–0.5 m/s air speed), and enforce foot-bath biosecurity at coop entry. "
            "Routine prophylaxis: multivitamin + electrolyte supplement in water once weekly. "
            "Vaccination schedule per OIE/national guidelines (Newcastle, IBD, Marek's)."
        ),
    },

    # =========================================================
    # POULTRY — Coccidiosis
    # =========================================================
    {
        "id": "poultry_coccidiosis",
        "category": "Poultry",
        "topic": "Coccidiosis — Eimeria tenella Cecal Infection",
        "text": (
            "Coccidiosis is caused by Eimeria species (most severe: E. tenella — cecal; "
            "E. necatrix — small intestine). "
            "Clinical signs: bloody or dark-red mucoid droppings (hallmark sign); "
            "ruffled feathers, lethargy, huddling; pale comb and wattles due to "
            "intestinal hemorrhaging; sudden rise in flock mortality (2–10 days old to 6 weeks). "
            "Diagnosis is confirmed by post-mortem lesion scoring of the intestinal segments. "
            "Treatment: Amprolium (9.6% solution) at 28 mL per 4 litres of drinking water "
            "for 5–7 consecutive days. Do NOT use during sulphonamide treatment. "
            "Supplement with Vitamin K3 (menadione) at 2 mg/L water to control hemorrhage. "
            "Vitamin A supplementation supports intestinal mucosa recovery. "
            "Biosecurity: keep litter moisture below 22%; replace wet litter around "
            "waterers immediately. Use anticoccidial shuttle program in starter feed "
            "(Salinomycin → Narasin rotation). "
            "Vaccinate day-old chicks with live Eimeria oocyst vaccine (Paracox) in "
            "endemic high-risk operations. "
            "Source: Merck Veterinary Manual — Coccidiosis in Poultry."
        ),
    },

    # =========================================================
    # POULTRY — Infectious Bronchitis
    # =========================================================
    {
        "id": "poultry_infectious_bronchitis",
        "category": "Poultry",
        "topic": "Avian Infectious Bronchitis — IBV Respiratory Strain",
        "text": (
            "Infectious Bronchitis Virus (IBV) is a highly contagious coronavirus "
            "affecting the respiratory and urogenital tracts of chickens. "
            "Respiratory signs: tracheal rales (rattling breath sounds), open-beak "
            "gasping, persistent coughing, sneezing; serous to mucopurulent nasal discharge; "
            "swelling of the infraorbital sinuses. "
            "Flock-level signs: sudden 10–50% drop in feed intake; birds huddling near "
            "heat sources; egg production drops sharply with misshapen or soft-shelled eggs. "
            "There is no specific antiviral. Supportive treatment: "
            "Tylosin tartrate (water-soluble, 500 mg/L for 5 days) OR "
            "Oxytetracycline (200 mg/L for 5 days) to prevent secondary Mycoplasma/E. coli infection. "
            "Provide multivitamin + electrolyte solution. Increase coop temperature by 2–3°C. "
            "Biosecurity: immediate quarantine of affected section; disinfect air with "
            "formaldehyde aerosol fumigation (40 mL formalin/m³) with birds removed. "
            "Vaccination: IB H120 live vaccine (intranasal or drinking water) at day 1 and 14; "
            "booster with IB 4/91 or local variant strain at 4–6 weeks. "
            "Source: OIE Terrestrial Manual — Infectious Bronchitis."
        ),
    },

    # =========================================================
    # POULTRY — Newcastle Disease
    # =========================================================
    {
        "id": "poultry_newcastle",
        "category": "Poultry",
        "topic": "Newcastle Disease — Velogenic NDV",
        "text": (
            "Newcastle Disease (ND) caused by Avian Paramyxovirus type-1 (APMV-1) "
            "is a notifiable OIE-listed disease with extremely high mortality (up to 100%). "
            "Clinical signs — Velogenic (viscerotropic) strain: "
            "sudden death; greenish watery diarrhoea; haemorrhagic lesions in proventriculus; "
            "petechiae on intestinal mucosa; nervous signs (torticollis, tremors, paralysis "
            "of legs/wings); severe respiratory distress. "
            "THERE IS NO TREATMENT. Action upon suspicion: "
            "1. IMMEDIATE farm-level quarantine; notify veterinary authorities. "
            "2. Cull all infected and in-contact birds humanely. "
            "3. Dispose of carcasses by deep burial (1 m) with quicklime or incineration. "
            "4. Disinfect premises with 2% NaOH or phenolic disinfectant. "
            "Prevention: Vaccinate with La Sota live vaccine (intranasal at day 7 and 21) "
            "plus Clone 30 or Hitchner B1 as initial priming. "
            "Killed inactivated ND oil-emulsion vaccine booster at 8 weeks."
        ),
    },

    # =========================================================
    # POULTRY — Fowl Typhoid / Salmonellosis
    # =========================================================
    {
        "id": "poultry_salmonella",
        "category": "Poultry",
        "topic": "Fowl Typhoid / Pullorum Disease — Salmonella gallinarum",
        "text": (
            "Fowl Typhoid (FT) is caused by Salmonella gallinarum. "
            "Signs: sudden onset high mortality; pale/cyanotic wattles; yellowish-green "
            "diarrhoea; enlarged, copper-bronze coloured liver; splenomegaly; pericarditis. "
            "In layers: sharp drop in egg production; poor hatchability. "
            "Diagnosis: bacteriological culture from liver/spleen. Serology: rapid plate "
            "agglutination test (RPA) for flock screening. "
            "Treatment: Enrofloxacin 10% solution at 10 mg/kg bodyweight for 5 days "
            "(in drinking water: 1 mL per 10 L). "
            "Alternative: Trimethoprim-Sulfamethoxazole at 30 mg/kg for 7 days. "
            "Note: respect antimicrobial withdrawal periods before slaughter. "
            "Prevention: source day-old chicks only from Salmonella-tested parent flocks; "
            "implement all-in/all-out flock management; disinfect houses between flocks "
            "with formaldehyde fumigation."
        ),
    },

    # =========================================================
    # LIVESTOCK — Healthy
    # =========================================================
    {
        "id": "livestock_healthy",
        "category": "Livestock",
        "topic": "Healthy Cattle / Livestock Specimen",
        "text": (
            "A healthy dairy or beef cow presents: Body Condition Score (BCS) 3.0–3.5 "
            "on a 5-point scale; bright eyes with no ocular discharge; "
            "moist, clean nostrils; pink/salmon oral mucous membranes; normal rumen motility "
            "(2–3 contractions per 2 minutes via flank auscultation); "
            "firm, pelleted feces (beef) or soft-formed (dairy); rectal temperature 38–39.5°C. "
            "Milk: uniform white, no clots or blood; CMT (California Mastitis Test) negative. "
            "Management: minimum 50 L of fresh drinking water per adult cow per day; "
            "standard TMR (Total Mixed Ration) appropriate to production stage; "
            "mineral lick blocks (containing Calcium, Phosphorus, Magnesium, Zinc, Selenium); "
            "routine deworming every 3 months with Albendazole 10% at 7.5 mg/kg body weight; "
            "quarterly foot trimming; FMD + Anthrax + Brucellosis vaccination per national schedule."
        ),
    },

    # =========================================================
    # LIVESTOCK — Bovine Mastitis
    # =========================================================
    {
        "id": "livestock_mastitis",
        "category": "Livestock",
        "topic": "Bovine Mastitis — Acute Bacterial Infection",
        "text": (
            "Bovine Mastitis is inflammation of the udder mammary gland, caused by bacteria "
            "(Staphylococcus aureus, Streptococcus agalactiae, E. coli). "
            "Clinical signs: one or more udder quarters swollen, hot, red, painful; "
            "watery, clotted, or blood-tinged milk (confirmed by California Mastitis Test — CMT); "
            "reduced milk yield; cow showing pain response to palpation; "
            "mild to severe systemic signs (fever 39.5–41°C, anorexia, dehydration in peracute E. coli mastitis). "
            "Treatment: "
            "Intramammary: infuse Cephapirin sodium 200 mg (or Amoxicillin-cloxacillin) "
            "into affected quarters post-milking for 3–5 days. "
            "Systemic (peracute): Penicillin G at 22,000 IU/kg IM or IV twice daily; "
            "NSAID (Flunixin meglumine 2.2 mg/kg IV) for pain and inflammation. "
            "Supportive: IV fluids (NaCl 0.9%, 20–40 L) in toxic/dehydrated cases. "
            "Strip affected quarters frequently (4×/day) to remove toxins. "
            "Prevention: pre- and post-milking teat dipping in 1% iodine solution; "
            "dry cow therapy with intramammary antibiotic at drying-off; "
            "dry, clean bedding (kiln-dried wood shavings); milking machine vacuum pressure "
            "maintenance below 38 kPa. "
            "Source: IDF Mastitis Control Guide."
        ),
    },

    # =========================================================
    # LIVESTOCK — Foot and Mouth Disease
    # =========================================================
    {
        "id": "livestock_fmd",
        "category": "Livestock",
        "topic": "Foot and Mouth Disease — FMD (FMDV)",
        "text": (
            "Foot and Mouth Disease (FMD) is caused by an Aphthovirus and is a "
            "highly contagious OIE-listed transboundary disease. "
            "Signs: fever (40–41°C); vesicles (fluid-filled blisters) on tongue, gums, "
            "dental pad, lips, coronary band of feet, and teats; "
            "excessive salivation (ropy drooling); severe lameness; anorexia; "
            "sharp drop in milk production. "
            "FMD has no specific curative treatment. "
            "Management: "
            "1. IMMEDIATE notification to veterinary authority — legally notifiable. "
            "2. Quarantine affected animals; restrict farm movement. "
            "3. Oral lesion antiseptic wash: 1% citric acid or 2% acetic acid solution. "
            "4. Foot baths with 4% sodium carbonate or 2% formaldehyde solution. "
            "5. Soft, palatable feed; analgesics (Flunixin meglumine) for pain management. "
            "Prevention: FMD polyvalent inactivated vaccine — biannual vaccination; "
            "match vaccine serotype to circulating strain (O, A, SAT 1/2/3). "
            "Do NOT move animals or equipment off-farm during an outbreak."
        ),
    },

    # =========================================================
    # LIVESTOCK — East Coast Fever (ECF)
    # =========================================================
    {
        "id": "livestock_ecf",
        "category": "Livestock",
        "topic": "East Coast Fever — Theileria parva (Tick-borne)",
        "text": (
            "East Coast Fever (ECF) is caused by the protozoan parasite Theileria parva, "
            "transmitted by the brown ear tick (Rhipicephalus appendiculatus). "
            "Signs: high fever (41–42°C); enlarged superficial lymph nodes (especially "
            "parotid lymph node — hallmark sign); lacrimation (watery eyes); "
            "respiratory distress (pulmonary oedema); nasal discharge; anorexia; "
            "milk production drops sharply; death within 18–28 days if untreated. "
            "Treatment: Buparvaquone (Butalex) at 2.5 mg/kg IM — single injection; "
            "or Parvaquone at 20 mg/kg IM. "
            "Supplement: antipyretic (Dipyrone/Metamizole 50 mg/kg IM); "
            "supportive fluids; vitamins B complex IM. "
            "Prevention: Tick control — Amitraz 12.5% cattle dip at 1 mL/L water "
            "every 7–14 days (strategic dipping calendar); "
            "Infection-and-treatment (ITM) immunization with live T. parva sporozoites + "
            "long-acting oxytetracycline cover (most effective and recommended approach). "
            "Source: FAO Animal Production and Health Paper No. 170."
        ),
    },

    # =========================================================
    # LIVESTOCK — Lumpy Skin Disease
    # =========================================================
    {
        "id": "livestock_lsd",
        "category": "Livestock",
        "topic": "Lumpy Skin Disease — LSD (Capripoxvirus)",
        "text": (
            "Lumpy Skin Disease (LSD) is caused by Capripoxvirus, transmitted by "
            "biting insects (mosquitoes, flies, ticks). "
            "Signs: fever (41°C); firm, circumscribed skin nodules (2–5 cm) over the "
            "entire body — especially on head, neck, limbs, and perineum; "
            "enlarged lymph nodes; profuse nasal and ocular discharge; "
            "reduced milk production; lameness due to swollen legs and feet. "
            "There is no specific antiviral. Treatment is supportive: "
            "Antibiotic cover (Oxytetracycline LA 20% at 20 mg/kg IM every 72 hours) "
            "to prevent secondary bacterial infections on skin nodules. "
            "NSAID analgesics for pain and fever reduction. "
            "Wound care: clean ulcerated nodules with 1% povidone-iodine solution. "
            "Prevention: Neethling strain live attenuated vaccine — annual vaccination "
            "before insect season; vector control with pyrethroid pour-ons and insecticide "
            "spray around farm. "
            "Source: OIE Terrestrial Manual — Lumpy Skin Disease."
        ),
    },
]


def get_corpus() -> list[dict]:
    """Return the full agronomic knowledge corpus."""
    return CORPUS


def get_corpus_by_category(category: str) -> list[dict]:
    """Return corpus chunks relevant to a specific category."""
    cat_lower = category.lower()
    return [
        doc for doc in CORPUS
        if cat_lower in doc["category"].lower()
        or doc["category"].lower() == "all"
    ]
