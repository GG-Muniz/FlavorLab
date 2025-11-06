"""
Utility script to build enriched compound and vitamin/mineral description data
for ingredient analytics.

Run with the backend virtualenv Python:

    cd FlavorLab/backend
    ./venv/Scripts/python.exe analysis/build_nutrient_descriptions.py

It will generate:
    analysis/compound_details.json
    analysis/vitamin_mineral_details.json
"""

from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).parent


COMPOUND_INFO: dict[str, dict[str, object]] = {
    "ALA Omega-3": {
        "summary": "Plant-based alpha-linolenic acid that the body converts to EPA and DHA in limited amounts, helping maintain cardiovascular and cognitive health.",
        "primary_actions": [
            "Supports heart rhythm and healthy cholesterol balance",
            "Provides anti-inflammatory precursors for cell membranes",
        ],
        "evidence_level": "Established",
    },
    "Allicin": {
        "summary": "Sulfur-rich molecule released from crushed garlic with broad antimicrobial, cardiometabolic, and immune benefits.",
        "primary_actions": [
            "Promotes vasodilation and supports healthy blood pressure",
            "Displays antibacterial, antiviral, and antifungal activity",
        ],
        "evidence_level": "Established",
    },
    "Anethole": {
        "summary": "Sweet aromatic compound in fennel and anise that calms smooth muscle and provides antioxidant support.",
        "primary_actions": [
            "Soothes digestive spasms and bloating",
            "Acts as a mild antioxidant supporting liver detox pathways",
        ],
        "evidence_level": "Emerging",
    },
    "Anthocyanins": {
        "summary": "Deeply pigmented flavonoids in berries and purple produce that defend blood vessels and neurons from oxidative stress.",
        "primary_actions": [
            "Improve endothelial function and circulation",
            "Support memory and neuroprotection",
        ],
        "evidence_level": "Established",
    },
    "Antioxidants": {
        "summary": "Broad class of plant compounds and nutrients that neutralize free radicals to limit cellular damage.",
        "primary_actions": [
            "Reduce oxidative stress burden",
            "Protect DNA, lipids, and proteins from peroxidation",
        ],
        "evidence_level": "Established",
    },
    "Apigenin": {
        "summary": "Flavone found in chamomile, celery, and parsley that exerts calming and anti-inflammatory effects.",
        "primary_actions": [
            "Modulates GABA receptors to promote relaxation",
            "Downregulates NF-κB–driven inflammatory pathways",
        ],
        "evidence_level": "Emerging",
    },
    "B vitamins": {
        "summary": "Group of water-soluble cofactors that drive energy metabolism, neurotransmitter synthesis, and cellular repair.",
        "primary_actions": [
            "Support carbohydrate, fat, and protein metabolism",
            "Maintain healthy nervous system and cognitive function",
        ],
        "evidence_level": "Established",
    },
    "B1": {
        "summary": "Thiamine, an essential cofactor for glucose metabolism critical to nerve and cardiac function.",
        "primary_actions": [
            "Drives ATP production via the Krebs cycle",
            "Supports peripheral nerve conduction and heart muscle",
        ],
        "evidence_level": "Established",
    },
    "B12": {
        "summary": "Cobalamin needed for red blood cell formation, myelin maintenance, and methylation.",
        "primary_actions": [
            "Prevents megaloblastic anemia and fatigue",
            "Supports cognitive health through homocysteine regulation",
        ],
        "evidence_level": "Established",
    },
    "B2": {
        "summary": "Riboflavin that powers mitochondrial enzymes and antioxidant recycling.",
        "primary_actions": [
            "Activates flavoproteins for energy metabolism",
            "Regenerates glutathione and other antioxidants",
        ],
        "evidence_level": "Established",
    },
    "B6": {
        "summary": "Pyridoxine involved in amino acid metabolism, neurotransmitter synthesis, and hormone balance.",
        "primary_actions": [
            "Supports serotonin, dopamine, and GABA production",
            "Helps regulate homocysteine and cardiovascular risk",
        ],
        "evidence_level": "Established",
    },
    "BCAAs": {
        "summary": "Leucine, isoleucine, and valine—branched-chain amino acids that fuel muscle tissue and recovery.",
        "primary_actions": [
            "Provide rapid energy substrate during exercise",
            "Stimulate mTOR signaling for muscle protein synthesis",
        ],
        "evidence_level": "Emerging",
    },
    "Beta-carotene": {
        "summary": "Provitamin A carotenoid that the body converts to retinol to support vision and immunity.",
        "primary_actions": [
            "Protects skin and ocular tissues from oxidative light damage",
            "Serves as a vitamin A reserve for immune resilience",
        ],
        "evidence_level": "Established",
    },
    "Beta-glucan": {
        "summary": "Soluble fiber from oats and barley that forms a viscous gel supporting cholesterol balance and satiety.",
        "primary_actions": [
            "Lowers LDL cholesterol by binding bile acids",
            "Feeds beneficial gut microbes to reinforce immunity",
        ],
        "evidence_level": "Established",
    },
    "Beta-glucans": {
        "summary": "Immunomodulatory polysaccharides found in mushrooms and grains that prime innate defense cells.",
        "primary_actions": [
            "Activate macrophages and NK cells for pathogen surveillance",
            "Enhance vaccine and antimicrobial responses",
        ],
        "evidence_level": "Emerging",
    },
    "Betalains": {
        "summary": "Red and yellow pigments in beets acting as potent detox and vascular-protective antioxidants.",
        "primary_actions": [
            "Support nitric oxide availability and blood flow",
            "Neutralize reactive nitrogen and oxygen species",
        ],
        "evidence_level": "Emerging",
    },
    "Bifidobacteria": {
        "summary": "Beneficial probiotic genus that ferments fibers into short-chain fatty acids for gut integrity.",
        "primary_actions": [
            "Crowd out pathogens and reinforce gut barrier function",
            "Produce acetate and lactate that feed other microbiota",
        ],
        "evidence_level": "Established",
    },
    "Bromelain": {
        "summary": "Proteolytic enzyme complex from pineapple stems known for easing inflammation and supporting digestion.",
        "primary_actions": [
            "Reduces exercise-related swelling and soreness",
            "Assists protein digestion in low-acid stomachs",
        ],
        "evidence_level": "Emerging",
    },
    "Caffeine": {
        "summary": "Central nervous system stimulant that blocks adenosine signaling to promote alertness and performance.",
        "primary_actions": [
            "Boosts focus, reaction time, and perceived energy",
            "Enhances endurance by increasing fatty acid mobilization",
        ],
        "evidence_level": "Established",
    },
    "Calcium": {
        "summary": "Major mineral that builds bone matrix and drives muscle contraction and nerve signaling.",
        "primary_actions": [
            "Supports peak bone density and tooth integrity",
            "Regulates heartbeat and neuromuscular transmission",
        ],
        "evidence_level": "Established",
    },
    "Casein protein": {
        "summary": "Slow-digesting dairy protein that provides a steady release of amino acids for muscle repair.",
        "primary_actions": [
            "Enhances overnight muscle protein synthesis",
            "Supports satiety and lean mass maintenance",
        ],
        "evidence_level": "Established",
    },
    "Catechins": {
        "summary": "Green tea flavanols, including EGCG, that confer metabolic and cardioprotective benefits.",
        "primary_actions": [
            "Increase antioxidant enzyme expression",
            "Support thermogenesis and metabolic health",
        ],
        "evidence_level": "Established",
    },
    "Choline": {
        "summary": "Essential methyl donor and phospholipid precursor crucial for brain and liver function.",
        "primary_actions": [
            "Supports acetylcholine production for memory",
            "Promotes liver fat metabolism and methylation",
        ],
        "evidence_level": "Established",
    },
    "Chrysin": {
        "summary": "Flavonoid in passion flower and honeycomb with calming and antioxidant actions.",
        "primary_actions": [
            "Modulates GABAergic signaling for relaxation",
            "Mitigates oxidative stress in vascular tissues",
        ],
        "evidence_level": "Emerging",
    },
    "Collagen": {
        "summary": "Structural protein providing amino acids like glycine and proline that rebuild connective tissue.",
        "primary_actions": [
            "Supports joint cartilage and skin elasticity",
            "Provides building blocks for gut lining repair",
        ],
        "evidence_level": "Established",
    },
    "Complete protein": {
        "summary": "Protein sources supplying all essential amino acids in proportions needed for tissue repair.",
        "primary_actions": [
            "Maintains muscle mass and immune proteins",
            "Supports hormone and enzyme synthesis",
        ],
        "evidence_level": "Established",
    },
    "Complex carbs": {
        "summary": "Slow-digesting starches and fibers that steady energy release and nurture gut microbes.",
        "primary_actions": [
            "Provide sustained glucose for endurance",
            "Feed microbiota for short-chain fatty acid production",
        ],
        "evidence_level": "Established",
    },
    "CoQ10": {
        "summary": "Ubiquinone antioxidant embedded in mitochondria that drives electron transport and protects lipids.",
        "primary_actions": [
            "Supports cellular ATP production and stamina",
            "Shields LDL particles from oxidative damage",
        ],
        "evidence_level": "Established",
    },
    "Curcumin": {
        "summary": "Gold pigment from turmeric with strong anti-inflammatory and antioxidant activity.",
        "primary_actions": [
            "Downregulates COX-2 and inflammatory cytokines",
            "Supports joint comfort and metabolic health",
        ],
        "evidence_level": "Established",
    },
    "Cynarin": {
        "summary": "Artichoke polyphenol that stimulates bile flow and cholesterol metabolism.",
        "primary_actions": [
            "Promotes digestion of fats via increased bile secretion",
            "Supports healthy LDL and triglyceride levels",
        ],
        "evidence_level": "Emerging",
    },
    "DHA": {
        "summary": "Docosahexaenoic acid, a long-chain omega-3 crucial for brain, retina, and anti-inflammatory signaling.",
        "primary_actions": [
            "Maintains neuronal membrane fluidity and vision",
            "Resolves inflammation via specialized mediators",
        ],
        "evidence_level": "Established",
    },
    "EGCG": {
        "summary": "Epigallocatechin gallate, the most studied catechin in green tea with metabolic and anti-cancer effects.",
        "primary_actions": [
            "Activates AMPK to enhance fat oxidation",
            "Protects cells from oxidative DNA damage",
        ],
        "evidence_level": "Established",
    },
    "Ellagic acid": {
        "summary": "Polyphenol in berries and pomegranates that modulates detox enzymes and suppresses tumor growth pathways.",
        "primary_actions": [
            "Induces phase II detoxification enzymes",
            "Inhibits pro-carcinogenic signaling in vitro",
        ],
        "evidence_level": "Emerging",
    },
    "EPA": {
        "summary": "Eicosapentaenoic acid, marine omega-3 that lowers inflammation and supports cardiovascular resilience.",
        "primary_actions": [
            "Generates anti-inflammatory eicosanoids",
            "Reduces triglycerides and supports mood balance",
        ],
        "evidence_level": "Established",
    },
    "Fiber": {
        "summary": "Indigestible carbohydrates that regulate digestion, cholesterol, and blood sugar dynamics.",
        "primary_actions": [
            "Promote satiety and regular bowel movements",
            "Feed gut microbes for short-chain fatty acid production",
        ],
        "evidence_level": "Established",
    },
    "Flavonoids": {
        "summary": "Diverse family of plant polyphenols that modulate inflammation, vascular tone, and detox pathways.",
        "primary_actions": [
            "Enhance endothelial nitric oxide availability",
            "Scavenge reactive oxygen species",
        ],
        "evidence_level": "Established",
    },
    "Folate": {
        "summary": "Vitamin B9 essential for DNA synthesis, red blood cells, and prenatal neural tube development.",
        "primary_actions": [
            "Supports methylation and homocysteine control",
            "Prevents neural tube defects during pregnancy",
        ],
        "evidence_level": "Established",
    },
    "GABA compounds": {
        "summary": "Gamma-aminobutyric acid and related phytochemicals that promote calming neurotransmission.",
        "primary_actions": [
            "Reduce neuronal excitability for stress relief",
            "Support healthy sleep onset",
        ],
        "evidence_level": "Emerging",
    },
    "Gingerol": {
        "summary": "Pungent phenol in ginger responsible for its warming, anti-inflammatory, and antiemetic effects.",
        "primary_actions": [
            "Reduces nausea by modulating serotonin receptors",
            "Inhibits inflammatory prostaglandin synthesis",
        ],
        "evidence_level": "Established",
    },
    "Glucose": {
        "summary": "Primary simple sugar used by cells for rapid energy production.",
        "primary_actions": [
            "Supplies immediate ATP fuel for brain and muscles",
            "Stimulates insulin release to store energy",
        ],
        "evidence_level": "Established",
    },
    "Glutamine": {
        "summary": "Conditionally essential amino acid that fuels rapidly dividing immune and gut cells.",
        "primary_actions": [
            "Supports intestinal barrier integrity",
            "Feeds lymphocytes during immune response",
        ],
        "evidence_level": "Established",
    },
    "Glycine": {
        "summary": "Smallest amino acid with roles in collagen synthesis, neurotransmission, and detoxification.",
        "primary_actions": [
            "Supports joint and connective tissue through collagen",
            "Acts as an inhibitory neurotransmitter promoting restorative sleep",
        ],
        "evidence_level": "Established",
    },
    "Hesperidin": {
        "summary": "Citrus flavanone that strengthens capillaries and modulates inflammation.",
        "primary_actions": [
            "Improves venous tone and reduces leg swelling",
            "Provides antioxidant protection to vascular walls",
        ],
        "evidence_level": "Emerging",
    },
    "Inulin": {
        "summary": "Prebiotic fiber from chicory and plants that selectively feeds bifidobacteria.",
        "primary_actions": [
            "Enhances gut microbiome diversity",
            "Improves mineral absorption, especially calcium",
        ],
        "evidence_level": "Established",
    },
    "Iron": {
        "summary": "Essential trace mineral required to transport oxygen in hemoglobin and support mitochondrial enzymes.",
        "primary_actions": [
            "Prevents anemia-related fatigue",
            "Supports immune enzyme function",
        ],
        "evidence_level": "Established",
    },
    "L-citrulline": {
        "summary": "Amino acid from watermelon that converts to arginine to raise nitric oxide levels.",
        "primary_actions": [
            "Improves blood flow and exercise performance",
            "Supports post-exercise recovery by reducing soreness",
        ],
        "evidence_level": "Emerging",
    },
    "L-Theanine": {
        "summary": "Green tea amino acid that promotes relaxed alertness by increasing alpha brain waves.",
        "primary_actions": [
            "Synergizes with caffeine to improve focus without jitters",
            "Supports stress resilience by modulating neurotransmitters",
        ],
        "evidence_level": "Established",
    },
    "LAB probiotics": {
        "summary": "Lactic acid bacteria such as Lactobacillus that ferment foods and reinforce gut immunity.",
        "primary_actions": [
            "Produce lactic acid to suppress pathogens",
            "Enhance mucosal immune response",
        ],
        "evidence_level": "Established",
    },
    "Lactase": {
        "summary": "Digestive enzyme that splits milk lactose into absorbable sugars.",
        "primary_actions": [
            "Prevents lactose intolerance symptoms",
            "Improves calcium absorption from dairy",
        ],
        "evidence_level": "Established",
    },
    "Lactobacillus": {
        "summary": "Genus of beneficial bacteria common in fermented foods that produce lactic acid and support microbiome balance.",
        "primary_actions": [
            "Maintain acidic gut environment to deter pathogens",
            "Support immune modulation and vitamin synthesis",
        ],
        "evidence_level": "Established",
    },
    "Leucine": {
        "summary": "Key branched-chain amino acid that triggers muscle anabolism via mTOR signaling.",
        "primary_actions": [
            "Stimulates muscle protein synthesis after exercise",
            "Helps preserve lean mass during calorie deficits",
        ],
        "evidence_level": "Established",
    },
    "Lignans": {
        "summary": "Phytoestrogenic fibers in flax and other seeds metabolized into hormone-balancing enterolignans.",
        "primary_actions": [
            "Support estrogen metabolism and menopausal comfort",
            "Provide antioxidant and anti-inflammatory activity",
        ],
        "evidence_level": "Emerging",
    },
    "Limonene": {
        "summary": "Citrus peel terpene with uplifting aroma and gentle detox-supporting properties.",
        "primary_actions": [
            "Enhances mood and reduces perceived stress",
            "Induces hepatic enzymes that aid detoxification",
        ],
        "evidence_level": "Emerging",
    },
    "Lycopene": {
        "summary": "Red carotenoid abundant in tomatoes that concentrates in prostate and cardiovascular tissues.",
        "primary_actions": [
            "Protects LDL cholesterol from oxidation",
            "Supports prostate and skin health against UV damage",
        ],
        "evidence_level": "Established",
    },
    "Magnesium": {
        "summary": "Major mineral cofactor for over 300 enzymes, affecting metabolism, muscle, and nervous system balance.",
        "primary_actions": [
            "Regulates muscle relaxation and heart rhythm",
            "Supports glucose control and energy production",
        ],
        "evidence_level": "Established",
    },
    "Melatonin": {
        "summary": "Sleep hormone and antioxidant produced by the pineal gland and present in some plant foods.",
        "primary_actions": [
            "Synchronizes circadian rhythms and sleep onset",
            "Scavenges free radicals, especially in mitochondria",
        ],
        "evidence_level": "Established",
    },
    "Menthol": {
        "summary": "Mint terpene that activates cold-sensing receptors to create a cooling, soothing sensation.",
        "primary_actions": [
            "Relieves throat irritation and mild congestion",
            "Provides topical analgesic effects",
        ],
        "evidence_level": "Established",
    },
    "Monounsaturated fat": {
        "summary": "Heart-healthy fats dominated by oleic acid that improve lipid profiles and insulin sensitivity.",
        "primary_actions": [
            "Lower LDL while preserving HDL cholesterol",
            "Support anti-inflammatory metabolic signaling",
        ],
        "evidence_level": "Established",
    },
    "Natural sugars": {
        "summary": "Intrinsic fructose, glucose, and sucrose bundled with fiber, water, and micronutrients in whole foods.",
        "primary_actions": [
            "Provide quick energy alongside hydration",
            "Pair with fiber to limit glycemic spikes",
        ],
        "evidence_level": "Established",
    },
    "Nitrates": {
        "summary": "Naturally occurring vegetable nitrates that convert to nitric oxide for vascular support.",
        "primary_actions": [
            "Improve blood flow and exercise endurance",
            "Support healthy blood pressure regulation",
        ],
        "evidence_level": "Established",
    },
    "Oleic acid": {
        "summary": "Main monounsaturated fat in olive oil that supports cardiovascular and metabolic health.",
        "primary_actions": [
            "Reduces LDL oxidation and inflammation",
            "Enhances insulin sensitivity",
        ],
        "evidence_level": "Established",
    },
    "Oleocanthal": {
        "summary": "Peppery phenolic in extra-virgin olive oil with ibuprofen-like COX inhibitory activity.",
        "primary_actions": [
            "Provides anti-inflammatory relief for joints",
            "Offers neuroprotective actions against amyloid aggregation",
        ],
        "evidence_level": "Emerging",
    },
    "Omega-3": {
        "summary": "Family of essential fatty acids including EPA and DHA vital for heart, brain, and immune modulation.",
        "primary_actions": [
            "Resolve inflammation and support cell membrane fluidity",
            "Lower triglycerides and improve mood",
        ],
        "evidence_level": "Established",
    },
    "Papain": {
        "summary": "Papaya-derived protease that aids digestion and softens inflammatory swelling in tissues.",
        "primary_actions": [
            "Assists protein digestion in low-acid stomachs",
            "May reduce inflammatory edema after injury",
        ],
        "evidence_level": "Emerging",
    },
    "Pectin": {
        "summary": "Soluble fiber in apples and citrus that forms gels, moderates digestion, and feeds gut bacteria.",
        "primary_actions": [
            "Helps regulate cholesterol and blood glucose",
            "Supports short-chain fatty acid production for gut lining",
        ],
        "evidence_level": "Established",
    },
    "Polyphenols": {
        "summary": "Large group of plant antioxidants that modulate inflammation, microbiota, and detox enzymes.",
        "primary_actions": [
            "Enhance endothelial nitric oxide and circulation",
            "Influence gut microbiome composition",
        ],
        "evidence_level": "Established",
    },
    "Potassium": {
        "summary": "Primary intracellular electrolyte balancing sodium to manage fluid status and blood pressure.",
        "primary_actions": [
            "Maintains healthy heart rhythm and nerve conduction",
            "Offsets sodium to lower hypertension risk",
        ],
        "evidence_level": "Established",
    },
    "Probiotics": {
        "summary": "Live beneficial microorganisms that confer health benefits when consumed in adequate amounts.",
        "primary_actions": [
            "Improve gut barrier and immune modulation",
            "Enhance digestion of lactose and other nutrients",
        ],
        "evidence_level": "Established",
    },
    "Protein": {
        "summary": "Macronutrient providing essential amino acids for tissue repair, immune molecules, and enzymes.",
        "primary_actions": [
            "Supports muscle maintenance and recovery",
            "Regulates satiety and metabolic rate",
        ],
        "evidence_level": "Established",
    },
    "Punicalagins": {
        "summary": "Ellagitannin antioxidants concentrated in pomegranates that support vascular integrity.",
        "primary_actions": [
            "Improve endothelial function",
            "Exert anti-inflammatory and anti-atherogenic effects",
        ],
        "evidence_level": "Emerging",
    },
    "Quercetin": {
        "summary": "Widely distributed flavonol that stabilizes mast cells and supports cardiovascular resilience.",
        "primary_actions": [
            "Acts as an antihistamine and anti-inflammatory agent",
            "Supports nitric oxide production and blood vessel health",
        ],
        "evidence_level": "Established",
    },
    "Rosmarinic acid": {
        "summary": "Herbal polyphenol in rosemary and mint with antioxidant and anti-allergy effects.",
        "primary_actions": [
            "Neutralizes free radicals in neural tissue",
            "Reduces allergic inflammation and seasonal symptoms",
        ],
        "evidence_level": "Emerging",
    },
    "Selenium": {
        "summary": "Trace mineral incorporated into antioxidant enzymes and thyroid hormone conversion.",
        "primary_actions": [
            "Guards cells from oxidative damage",
            "Supports thyroid hormone activation and immunity",
        ],
        "evidence_level": "Established",
    },
    "Serotonin": {
        "summary": "Neurotransmitter derived from tryptophan that influences mood, digestion, and sleep.",
        "primary_actions": [
            "Regulates gut motility and satiety",
            "Supports positive mood and sleep cycles",
        ],
        "evidence_level": "Established",
    },
    "Shogaol": {
        "summary": "Heat-transformed ginger compound with potent anti-inflammatory and antiemetic actions.",
        "primary_actions": [
            "Relieves nausea and motion sickness",
            "Modulates inflammatory cytokines",
        ],
        "evidence_level": "Emerging",
    },
    "Soluble fiber": {
        "summary": "Fiber fraction that dissolves in water, forming gels that slow digestion and support heart health.",
        "primary_actions": [
            "Stabilizes post-meal blood glucose",
            "Helps reduce LDL cholesterol",
        ],
        "evidence_level": "Established",
    },
    "Sulforaphane": {
        "summary": "Isothiocyanate released from crucifers that activates Nrf2 detox pathways.",
        "primary_actions": [
            "Upregulates cellular antioxidant defenses",
            "Supports detoxification of environmental toxins",
        ],
        "evidence_level": "Established",
    },
    "Sulfur compounds": {
        "summary": "Organosulfur molecules in alliums and crucifers that bolster detoxification and immunity.",
        "primary_actions": [
            "Stimulate glutathione production",
            "Provide antimicrobial support",
        ],
        "evidence_level": "Established",
    },
    "Theobromine": {
        "summary": "Gentle stimulant in cacao that improves mood and circulation without strong caffeine effects.",
        "primary_actions": [
            "Enhances cerebral blood flow and alertness",
            "Acts as a mild bronchodilator for airway support",
        ],
        "evidence_level": "Emerging",
    },
    "Tryptophan": {
        "summary": "Essential amino acid used to synthesize serotonin and melatonin for mood and sleep.",
        "primary_actions": [
            "Supports restorative sleep and relaxation",
            "Helps regulate appetite and mood",
        ],
        "evidence_level": "Established",
    },
    "Tryptophan support": {
        "summary": "Co-factors such as vitamin B6 and magnesium that help convert tryptophan into serotonin.",
        "primary_actions": [
            "Facilitate neurotransmitter synthesis",
            "Enhance mood and sleep quality",
        ],
        "evidence_level": "Emerging",
    },
    "Turmerone": {
        "summary": "Aromatic sesquiterpene in turmeric essential oil with neuroprotective and anti-inflammatory potential.",
        "primary_actions": [
            "Stimulates neural stem cell activity in animal models",
            "Synergizes with curcumin for anti-inflammatory benefits",
        ],
        "evidence_level": "Emerging",
    },
    "Vitamin C": {
        "summary": "Water-soluble antioxidant that supports immunity, collagen synthesis, and iron absorption.",
        "primary_actions": [
            "Neutralizes free radicals and regenerates vitamin E",
            "Improves absorption of non-heme iron",
        ],
        "evidence_level": "Established",
    },
    "Vitamin D": {
        "summary": "Fat-soluble hormone-like nutrient that regulates calcium balance and immune readiness.",
        "primary_actions": [
            "Supports bone mineralization and muscle function",
            "Modulates innate and adaptive immunity",
        ],
        "evidence_level": "Established",
    },
    "Vitamin E": {
        "summary": "Family of tocopherols and tocotrienols that protect cell membranes from oxidative damage.",
        "primary_actions": [
            "Preserves lipid integrity in cardiovascular tissues",
            "Supports immune cell signaling",
        ],
        "evidence_level": "Established",
    },
    "Vitamin K": {
        "summary": "Group of fat-soluble vitamins essential for blood clotting and directing calcium into bones instead of arteries.",
        "primary_actions": [
            "Activates clotting factors for proper wound healing",
            "Supports bone-building osteocalcin activity",
        ],
        "evidence_level": "Established",
    },
    "Zinc": {
        "summary": "Trace mineral required for immune defense, DNA synthesis, and wound healing.",
        "primary_actions": [
            "Supports production of immune cells and antibodies",
            "Facilitates collagen synthesis and skin repair",
        ],
        "evidence_level": "Established",
    },
    "Zingiberene": {
        "summary": "Fragrant sesquiterpene in ginger responsible for its spicy aroma and anti-inflammatory traits.",
        "primary_actions": [
            "Acts as an antioxidant protecting lipids",
            "Contributes to ginger's digestive-soothing effects",
        ],
        "evidence_level": "Emerging",
    },
}

VITAMIN_INFO: dict[str, dict[str, object]] = {
    "Calcium": {
        "summary": "Macro mineral essential for bone structure, nerve transmission, and smooth muscle contraction.",
        "primary_actions": [
            "Builds and maintains dense bones and teeth",
            "Supports normal heart rhythm and neuromuscular signaling",
        ],
        "amount_reference": "DV 1,300 mg",
        "evidence_level": "Established",
    },
    "Iron": {
        "summary": "Trace mineral that enables oxygen transport in hemoglobin and powers mitochondrial enzymes.",
        "primary_actions": [
            "Prevents anemia-related fatigue and brain fog",
            "Supports immune enzyme activity",
        ],
        "amount_reference": "DV 18 mg",
        "evidence_level": "Established",
    },
    "Magnesium": {
        "summary": "Cofactor for hundreds of enzymes influencing metabolism, blood sugar control, and muscle relaxation.",
        "primary_actions": [
            "Reduces muscle cramping and supports calm sleep",
            "Helps regulate insulin sensitivity and blood pressure",
        ],
        "amount_reference": "DV 420 mg",
        "evidence_level": "Established",
    },
    "Potassium": {
        "summary": "Primary intracellular electrolyte balancing sodium to manage fluid status and blood pressure.",
        "primary_actions": [
            "Maintains healthy heart rhythm and nerve conduction",
            "Offsets sodium to lower hypertension risk",
        ],
        "amount_reference": "Adequate Intake 4,700 mg",
        "evidence_level": "Established",
    },
    "Selenium": {
        "summary": "Trace mineral incorporated into antioxidant enzymes and thyroid hormone conversion.",
        "primary_actions": [
            "Guards cells from oxidative damage",
            "Supports thyroid hormone activation and immunity",
        ],
        "amount_reference": "DV 55 mcg",
        "evidence_level": "Established",
    },
    "Vitamin B1 (Thiamine)": {
        "summary": "Coenzyme that enables carbohydrate metabolism and nerve impulse conduction.",
        "primary_actions": [
            "Supports steady energy production",
            "Promotes cardiovascular and nervous system health",
        ],
        "amount_reference": "DV 1.2 mg",
        "evidence_level": "Established",
    },
    "Vitamin B2 (Riboflavin)": {
        "summary": "Flavin cofactor for mitochondrial energy enzymes and antioxidant recycling.",
        "primary_actions": [
            "Supports ATP generation and fatty acid oxidation",
            "Regenerates glutathione and other antioxidants",
        ],
        "amount_reference": "DV 1.3 mg",
        "evidence_level": "Established",
    },
    "Vitamin B6 (Pyridoxine)": {
        "summary": "Coenzyme in amino acid metabolism and neurotransmitter synthesis including serotonin and GABA.",
        "primary_actions": [
            "Assists in mood regulation and cognitive function",
            "Helps manage homocysteine to protect the heart",
        ],
        "amount_reference": "DV 1.7 mg",
        "evidence_level": "Established",
    },
    "Vitamin C": {
        "summary": "Water-soluble antioxidant essential for collagen formation, immunity, and iron absorption.",
        "primary_actions": [
            "Shields immune cells from oxidative stress",
            "Improves uptake of non-heme iron",
        ],
        "amount_reference": "DV 90 mg",
        "evidence_level": "Established",
    },
    "Zinc": {
        "summary": "Trace mineral required for immune defense, DNA synthesis, and wound healing.",
        "primary_actions": [
            "Supports production of immune cells and antibodies",
            "Facilitates collagen synthesis and skin repair",
        ],
        "amount_reference": "DV 11 mg",
        "evidence_level": "Established",
    },
}


def build() -> None:
    compound_template_path = BASE_DIR / "compound_details_template.json"
    vitamin_template_path = BASE_DIR / "vitamin_mineral_details_template.json"

    compounds_template = json.loads(compound_template_path.read_text(encoding="utf-8"))
    vitamins_template = json.loads(vitamin_template_path.read_text(encoding="utf-8"))

    filled_compounds: list[dict[str, object]] = []
    for entry in compounds_template:
        name = entry["name"]
        if name not in COMPOUND_INFO:
            raise KeyError(f"Missing compound info for {name}")
        filled_compounds.append({"name": name, **COMPOUND_INFO[name]})

    filled_vitamins: list[dict[str, object]] = []
    for entry in vitamins_template:
        name = entry["name"]
        if name not in VITAMIN_INFO:
            raise KeyError(f"Missing vitamin/mineral info for {name}")
        filled_vitamins.append({"name": name, **VITAMIN_INFO[name]})

    (BASE_DIR / "compound_details.json").write_text(
        json.dumps(filled_compounds, indent=2),
        encoding="utf-8",
    )
    (BASE_DIR / "vitamin_mineral_details.json").write_text(
        json.dumps(filled_vitamins, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {len(filled_compounds)} compound entries and {len(filled_vitamins)} vitamin/mineral entries.")


if __name__ == "__main__":
    build()

