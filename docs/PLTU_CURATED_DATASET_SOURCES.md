# Curated PLTU Target Dataset Sources

This document records the public sources used by `python -m app.import_target_pltu`.
The importer replaces the broad historical screening dataset with the 26 target PLTU sites requested by the user.

Important interpretation:

- `capacity_mw` and `latitude`/`longitude` are the best public-source values found for screening.
- `confidence_level=high` means the coordinate is from a named plant page or exact map object.
- `confidence_level=medium` means the coordinate is public but requires reconciliation with alternate capacity/status references.
- `confidence_level=low` means only a public locality/address was found, not a fence-line plant coordinate.
- Stack pollutant fields use the Indonesian regulatory emission limit benchmark for existing coal PLTU under Permen LHK P.15/2019, not measured stack-test results.
- The CO2 stack geometry is a deterministic screening benchmark calibrated from site capacity, not CEMS or DCS data.

## Baku Mutu Baseline

For existing coal-fired PLTU, Permen LHK P.15/MENLHK/SETJEN/KUM.1/4/2019 Lampiran I lists:

| Parameter | Existing coal PLTU baseline |
|---|---:|
| SO2 | 550 mg/Nm3 |
| NOx | 550 mg/Nm3 |
| Particulate / PM | 100 mg/Nm3 |
| Hg | 0.03 mg/Nm3 |

The same regulation also lists stricter post-regulation PLTU values: SO2 200, NOx 200, PM 50, Hg 0.03 mg/Nm3.
The current importer uses the existing-coal baseline so it does not overstate compliance for older operating units.

Source: https://ppkl.menlhk.go.id/website/filebox/767/190930180734PERMENLHK%20NOMOR%2015%20TAHUN%202019.pdf

## Site Source Table

| No | Site | Capacity MW | Latitude | Longitude | Confidence | Public source |
|---:|---|---:|---:|---:|---|---|
| 1 | UP Tenayan | 220 | 0.564370 | 101.523450 | high | https://www.gem.wiki/Pekanbaru_Tenayan_power_station |
| 2 | UP Indramayu | 990 | -6.274738 | 107.970430 | high | https://www.gem.wiki/Indramayu_power_station |
| 3 | UP Rembang | 630 | -6.636000 | 111.474900 | high | https://www.gem.wiki/Rembang_power_station |
| 4 | UP Tanjung Awar-Awar | 700 | -6.810524 | 111.995503 | high | https://www.gem.wiki/Tanjung_Awar-Awar_power_station |
| 5 | UP Pacitan | 630 | -8.257818 | 111.373558 | high | https://www.gem.wiki/Pacitan_power_station |
| 6 | UP Paiton | 1460 | -7.713041 | 113.578536 | medium | https://www.gem.wiki/PLN_Paiton_power_station and https://www.gem.wiki/PLN_Paiton_Baru_power_station |
| 7 | UP Kaltim Teluk / Teluk Balikpapan | 220 | -1.170360 | 116.788720 | high | https://www.gem.wiki/Kaltim_Teluk_Balikpapan_power_station |
| 8 | UP Pulang Pisau | 120 | -2.822646 | 114.208831 | high | https://www.gem.wiki/Kalteng-1_Pulang_Pisau_power_station |
| 9 | UP Nagan Raya | 220 | 4.107550 | 96.198891 | high | https://www.gem.wiki/Nagan_Raya_power_station |
| 10 | UP Bukit Asam | 260 | -3.732130 | 103.797527 | high | https://www.gem.wiki/Bukit_Asam_Muara_Enim_power_station |
| 11 | UP Sebalang | 200 | -5.585940 | 105.387190 | medium | https://www.gem.wiki/Lampung_Sebalang_power_station |
| 12 | UP Tarahan | 200 | -5.521207 | 105.353477 | high | https://www.gem.wiki/Tarahan_power_station |
| 13 | UP Punagaya | 220 | -5.623635 | 119.550822 | medium | https://www.gem.wiki/Takalar_power_station and https://uppunagaya.com/pembangkit |
| 14 | PLTU Tembilahan | 14 | -0.298972 | 103.204805 | high | https://www.openstreetmap.org/search?query=PLTU%20Tembilahan |
| 15 | PLTU Ketapang | 20 | -1.780572 | 109.942072 | medium | https://lhketapang.wixsite.com/lhketapang/post/2017/11/17/izin-penyimpanan-sementara-limbah-b3-pltu-ketapang |
| 16 | PLTU Kendari 1-2 / Nii Tanasa | 24 | -3.895295 | 122.537864 | medium | https://www.openstreetmap.org/way/943189957 and https://web.pln.co.id/cms/media/siaran-pers/2011/04/pltu-kendari-mulai-beroperasi/ |
| 17 | PLTU Amurang | 50 | 1.182502 | 124.480564 | medium | https://www.gem.wiki/Amurang_power_station |
| 18 | PLTU Anggrek | 55 | 0.850288 | 122.796453 | medium | https://bukutelepon.cybo.com/ID-biz/pltu-anggrek |
| 19 | PLTU Ampana | 7 | -1.098500 | 121.811400 | low | https://kodepos.co.id/kodepos/sulawesi-tengah/kabupaten-tojo-una-una/ampana-tete/sabo and https://mediasulut.co/berita-5654-performance-test-pltu-ampana.html |
| 20 | PLTU Bolok | 33 | -10.240166 | 123.491350 | high | https://www.openstreetmap.org/way/611789533 |
| 21 | PLTU Ropa | 14 | -8.509167 | 121.700556 | medium | https://wikimapia.org/25361683/id/Pembangkit-Listrik-Tenaga-Uap-Ropa |
| 22 | PLTU Tidore | 14 | 0.739852 | 127.387721 | high | https://www.openstreetmap.org/search?query=PLTU%20Tidore |
| 23 | PLTU Kendari #3 | 9.8 | -3.895295 | 122.537864 | medium | https://www.openstreetmap.org/way/943189957 and https://www.pln-npservices.com/dari-kendari-untuk-indonesia/ |
| 24 | PLTU Bangka / Air Anyir | 60 | -2.079245 | 106.149617 | high | https://www.gem.wiki/Bangka_Baru_power_station |
| 25 | PLTU Belitung / Suge | 33 | -2.893259 | 107.563881 | high | https://www.pln-npservices.com/bio-diversity/pltu-belitung/ |
| 26 | PLTU Sambelia | 100 | -8.422199 | 116.711002 | medium | https://www.openstreetmap.org/search?query=PLTU%20Sambelia and https://www.plnnusantarapower.co.id/business-product/om |

## Known Reconciliation Notes

- Paiton is seeded as one site aggregate for PLN Paiton 1-2 plus Paiton 9. The coordinate is a capacity-weighted centroid because public sources expose the two project points separately.
- Sebalang is seeded at 200 MW because the user requested the 2 x 100 MW PLTU basis; some public sources mention a higher combined value.
- Punagaya is seeded at 220 MW following the user's target list and UP Punagaya gross-capacity framing; GEM's Takalar page lists 200 MW net-style capacity.
- Ketapang source text appears to type longitude as 119E, which is outside West Kalimantan. The importer corrects the obvious digit error to 109E.
- Kendari 1-2 and Kendari #3 share the Nii Tanasa site coordinate; public sources variously describe the site as 2 x 10 MW, 1 x 10 MW unit 3, or 3 x 10 MW.
- Ampana has public source confirmation for Desa Sabo, Kecamatan Ampana Tete and 2 x 3 MW/related operating references, but no public fence-line coordinate found. It is intentionally marked `low`.
- Sambelia's latest O&M/ownership status should be checked internally before investment use.
