# Source verification and conservative content policy

Reviewed 12 November 2026. Numeric source values below are historical/local
references, not current Telangana/AP prescriptions. The app retains a small
verified numeric subset and refers other crops to an agriculture officer.
Synthetic query generation adds language examples, never agronomic evidence.

| Content | Source and scope |
|---|---|
| Paddy NPK | [TNAU rice nutrient management](https://agritech.tnau.ac.in/agriculture/agri_main_feild_%20InOrganic_biofertilizers_Rice.html), 120:40:40 to 150:50:50 kg/ha for specified conventional situations; four N/K splits |
| Cotton NPK | [TNAU cotton](https://agritech.tnau.ac.in/agriculture/agri_cotton_Inorganic_manures%20.html), 32:16:16 to 48:24:24 **kg/acre**; existing approximate hectare conversion corrected |
| Chilli NPK | [TNAU chilli manuring](https://agritech.tnau.ac.in/horticulture/horti_vegetables_chilli_Manuring.html), conventional season 60:60:30 kg/ha; avoid applying hybrid fertigation as conventional schedule |
| Tomato NPK | [TNAU tomato hybrid fertigation](https://agritech.tnau.ac.in/horticulture/horti_vegetables_tomato_fertigation.html), 200:250:250 kg/ha. The earlier irrigation URL has inconsistent crop headings, so it is not used for nutrient attribution |
| Brinjal NPK | [TNAU brinjal](https://agritech.tnau.ac.in/horticulture/horti_vegetables_brinjal_manuring.html), season 100:50:30 to 200:150:100 kg/ha |
| Groundnut NPK | [TNAU groundnut](https://agritech.tnau.ac.in/agriculture/crop_prot_crop_grounnut_nutrient%20mgmt.html), 25:50:75 kg/ha; emphasizes soil testing |
| Maize NPK | [TNAU irrigated maize](https://agritech.tnau.ac.in/agriculture/agri_maize_irrigated_maize.html), 250:75:75 kg/ha, quarter/half/quarter N |
| Turmeric NPK | [TNAU turmeric](https://agritech.tnau.ac.in/horticulture/horti_spice_turmeric_manuring.html), conventional basal plus repeated topdress totals 150:60:108 kg/ha |
| Chickpea NPK | [TNAU Bengalgram](https://agritech.tnau.ac.in/agriculture/agri_nutrientmgt_bengalgram.html), rainfed/irrigated 12.5:25:12.5 to 25:50:25 kg/ha |
| General fertilizer guidance | [ICAR-CRIDA balanced nutrients](https://www.icar.gov.in/en/icar-crida-hyderabad-organises-awareness-programme-soil-health-management-and-balanced-fertilizer-0), soil-test-based decisions; no extrapolated crop dose |
| General water planning | [ICAR soil-moisture indicator](https://icar.gov.in/en/crop-science/other-technologies-farmers-prosperity) and [TNAU soil science, irrigation scheduling](https://agritech.tnau.ac.in/agriculture/pdf/ISSS.pdf); fixed intervals are not universal |
| Brinjal irrigation | [TNAU brinjal irrigation](https://agritech.tnau.ac.in/horticulture/horti_vegetables_brinjal_irrigation.html): weekly after establishment; local adjustment required; no guessed depth |
| Crop symptom inspection | [TNAU Agritech](https://agritech.tnau.ac.in/); original nine common-crop cards retained as educational possible causes. All other entries are explicitly unconfirmed inspection cues with officer referral; no species-specific disease, chemical or dose is invented |
| Historical MSP | [PIB, 5 August 2025](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2152556): 22 mandated commodities, 2025-26 marketing references; coconut shown as milling **copra**, not raw coconut. Jowar hybrid, cotton medium staple and paddy common are specified |
| Districts | [Telangana official district portal](https://www.telangana.gov.in/about/districts/) (33); [Government online directory, AP](https://igod.gov.in/sg/AP/E042/organizations) (28), including [Markapuram](https://markapuram.ap.gov.in/about-district/) and [Polavaram directory](https://igod.gov.in/district/11599/sub_districts). Names are search candidates; the API may require a nearby town |
| Weather | [Open-Meteo forecast docs](https://open-meteo.com/en/docs), [geocoding](https://open-meteo.com/en/docs/geocoding-api), [IMD warnings](https://mausam.imd.gov.in/) |

Product conversion assumes urea 46% N, DAP 18% N/46% P2O5 and MOP 60% K2O.
These are nutrient-equivalent arithmetic examples; product choice must follow the
local recommendation. An officer-provided plan can be entered for every crop.
Broad three-row allocations do not claim to reproduce each source's detailed
calendar. Organics quantities and unsupported water-depth/soil multipliers from
the previous site were removed rather than attributed to unrelated sources.
Net water conversion is a unit identity: 1 acre = 4046.8564224 m²; 1 mm over
1 m² = 1 L. The default 10 mm is clearly an example user input.

Original scheme cards link to the responsible departments. Eligibility is an
enquiry aid; current orders, procurement, deadlines, premium terms and benefits
must be checked with those departments. No live market rate is claimed.


## Upgrade sources and limits

Optional mandi integration: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi ; configured resource https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070 . No real API key was available; authentication and current upstream filter compatibility require a manual keyed check. The adapter was tested with labelled synthetic fixtures only. No fixture is included as an observed live price.

Colab checkpoint references: https://huggingface.co/ai4bharat/indic-bert and https://huggingface.co/google/muril-base-cased . Trainer API reference: https://huggingface.co/docs/transformers/v4.46.3/en/main_classes/trainer . The notebook is unexecuted here; no neural scores are claimed. Existing crop-care guidance is reused with uncertainty and officer referral, rather than new unsourced treatments.
