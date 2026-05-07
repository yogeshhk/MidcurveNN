# Pending Tasks — Intro GeoMod Comprehensive Deck

## 1. Recover PPT files (optional)
Check git history to see if PPTs were committed:
```
git log --oneline --all -- "publications/IntroToGeoMod/Intro_SolidModeling.ppt"
```
If found, restore:
```
git checkout <hash> -- "publications/IntroToGeoMod/Intro_SolidModeling.ppt"
git checkout <hash> -- "publications/IntroToGeoMod/Introduction To 3D Modeling_yhk.ppt"
git checkout <hash> -- "publications/IntroToGeoMod/Intro_3DModeling.ppt"
```
Alternatively try Windows **Previous Versions** on the folder, or **Recuva** for file recovery.

## 2. Export slide images
Export **pages 21–106** of `Intro_SolidModeling.pdf` (or the recovered PPT) as PNG files
into the `images/` folder using this naming convention:

| PDF page | Filename        |
|----------|-----------------|
| 21       | solidmod_01.png |
| 22       | solidmod_02.png |
| …        | …               |
| 106      | solidmod_86.png |

Formula: `NN = page_number − 20`, zero-padded to 2 digits.

The 86 grey placeholder PNGs currently in `images/` will be overwritten by the real exports.

## 3. Recompile
```
cd publications\IntroToGeoMod
texify -cp Main_Intro_GeoMod_Comprehensive.tex
```
or simply run `make.bat` from that folder.

## 4. Review and tidy frame titles
Open the compiled `Main_Intro_GeoMod_Comprehensive.pdf` and compare it against the slides.
Update any blank-title image frames in `intro_geomod_comprehensive_content.tex` where
a proper slide title is visible.
