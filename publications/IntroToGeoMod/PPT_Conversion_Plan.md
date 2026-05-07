# PPT to LaTeX Beamer Conversion Plan
## Folder: publications/IntroToGeoMod

**Goal**: Convert 3 PowerPoint decks to LaTeX Beamer presentations following the
same structure as `Main_IntroductionToCAD_Presentation.tex`, using the existing
`template_presentation.tex` (Warsaw/whale theme). Then compile all decks via `make.bat`.

**Success criterion**: All three `Main_*.tex` drivers compile without errors via
`make.bat` and produce PDF slide decks whose content faithfully reproduces each PPT.

---

## 0. File Naming

| PPT Source | LaTeX Driver | Content File |
|---|---|---|
| `Intro_3DModeling.ppt` | `Main_Intro_3DModeling.tex` | `intro_3dmodeling_content.tex` |
| `Intro_SolidModeling.ppt` | `Main_Intro_SolidModeling.tex` | `intro_solidmodeling_content.tex` |
| `Introduction To 3D Modeling_yhk.ppt` | `Main_Introduction_To_3D_Modeling_yhk.tex` | `intro_3dmodeling_yhk_content.tex` |

> Note: spaces replaced with underscores in all filenames — `texify` and LaTeX
> cannot handle spaces in filenames reliably.

---

## 1. Driver File Structure

All three drivers follow exactly the same pattern as the existing presentation:

```latex
\documentclass[t,pdf]{beamer}
\graphicspath{{images/}}
\input{template_presentation}

\title[<Short Title> \hspace{4cm} \insertframenumber/\inserttotalframenumber]{<Full Title>}
\subtitle[]{}
\date[]{\today}

\begin{document}

\begin{frame}
\titlepage
\end{frame}

\input{<content_file>}

\begin{frame}[c]{}
Thanks \ldots \\
\vspace{5mm}
yogeshkulkarni@yahoo.com
\end{frame}

\end{document}
```

Specific values per deck:

| Driver | `\title` short | `\title` full |
|---|---|---|
| `Main_Intro_3DModeling.tex` | `3D Modeling` | `3D Modeling` |
| `Main_Intro_SolidModeling.tex` | `Solid Modeling` | `Introduction to Solid Modeling` |
| `Main_Introduction_To_3D_Modeling_yhk.tex` | `3D Modeling` | `Introduction to 3D Modeling` |

---

## 2. Pre-Execution: User Actions Required (do BEFORE the session)

### A. Export missing PDFs
Open in PowerPoint → **File → Export → Create PDF/XPS**

| PPT | Save as |
|---|---|
| `Intro_SolidModeling.ppt` | `Intro_SolidModeling.pdf` (same folder) |
| `Introduction To 3D Modeling_yhk.ppt` | `Intro_3DModeling_yhk.pdf` (same folder) |

### B. Export images from `Intro_3DModeling.ppt`

Images already present in `images/` (reuse directly):

| PPT Slide | Description | Existing file |
|---|---|---|
| 5 | Evolution of CAD Technology | `geomod1.png` |
| 7 | Manual drafting 4-view drawings | `geomod2.png` |
| 10, 11 | Wire frame part geometry | `geomod4.png` |
| 12 | Wire frame ambiguity problem | `geomod5.png` |
| 14 | 3D Surface model NURBS | `geomod7.png` |
| 15 | Alias StudioTools inline skate | `geomod8.jpg` |
| 16 | Rhino Ducati motorcycle | `geomod9.jpg` |
| 18 | 2D Applications composite | `geomod10.png` |
| 19 | 3D Applications composite | `geomod11.png` |
| 20 | FEA mesh image | `geomod12.png` |

Images that need to be exported from the PPT (right-click image → Save as Picture → PNG):

| Slide | Description | Save as |
|---|---|---|
| 6 | Drafting board photo | `images/3dmod_drafting_board.png` |
| 7 | 4-view drawings (Multiview/Axonometric/Oblique/Perspective) | `images/3dmod_manual_drafting_views.png` |
| 8 top-right | 2D profile with hole (small pentagon-like shape) | `images/3dmod_2d_profile.png` |
| 8 mid | Multiple wireframe boxes | `images/3dmod_wireframe_boxes.png` |
| 8 mid | Car body surface mesh (black bg) | `images/3dmod_car_surface.png` |
| 8 bot | Blue solid mechanical part | `images/3dmod_solid_part.png` |
| 9 | Circle-in-square 2D CAD diagram | `images/3dmod_2d_diagram.png` |
| 12 | Wire frame + 2 solid interpretations | `images/3dmod_wireframe_ambiguity.png` |
| 13 | Two yellow surface model views | `images/3dmod_surface_models.png` |
| 18 | 2D Applications (circuit + floor plan) | `images/3dmod_2d_apps.png` |
| 19 | 3D Applications (FEA + PCB + assembly) | `images/3dmod_3d_apps.png` |
| 20 | FEA: CAD model → mesh → stress result | `images/3dmod_fea_sequence.png` |

### C. Export images from `Intro_SolidModeling.ppt` and `Intro_3DModeling_yhk.ppt`
Image tables for these two decks will be built in-session after reading their PDFs.
Naming convention: `solidmod_NN.png` and `3dmodyhk_NN.png`.

---

## 3. Slide Content Map — `Intro_3DModeling.ppt` (slides 1–20 confirmed from PDF)

| # | Frame Title | Layout | Image(s) | Key text |
|---|---|---|---|---|
| 1 | *(Title slide)* | `\titlepage` | — | Title: "3D Modeling" |
| 2 | *(Section divider)* | `{\Large Introduction}` centred | — | bare section label |
| 3 | Introduction | Bullets | — | Design/Comm/Analysis/Mfg/CAx |
| 4 | History | Bullets | — | GM 1960s; Sutherland 1963; post-1970 |
| 5 | Evolution of CAD Technology | Full image | `geomod1.png` | Drawing→Wire→Surface→Solid |
| 6 | *(caption slide)* | Image + caption | `3dmod_drafting_board.png` | "Manual drafting. Since 1970s: electronic drafting board." |
| 7 | Manual Drafting | Bullets + right image | `3dmod_manual_drafting_views.png` | 2D reps, standards, difficult to visualise |
| 8 | CAD -- Types | Bullets + inline images | `3dmod_2d_profile.png`, `3dmod_wireframe_boxes.png`, `3dmod_car_surface.png`, `3dmod_solid_part.png` | 2D model; 3D: Wireframe, Surface, Solid; alertblock "Advantages and Disadvantages?" |
| 9 | 2D CAD | Bullets + right image | `3dmod_2d_diagram.png` | Replaces drawing; AutoCAD |
| 10 | *(caption slide)* | Image + caption | `geomod4.png` | "Early 1980s: wire frame geometry" |
| 11 | 3D Wire frame Modeling | Bullets + right image | `geomod4.png` | Lines/curves; ambiguous; easy to store |
| 12 | What is this? | Title + left image + right images | `3dmod_wireframe_ambiguity.png` | "Problems with wire frame models" |
| 13 | *(caption slide)* | Image + caption | `3dmod_surface_models.png` | "Late 1980s: Surface Modeling" |
| 14 | 3D Surface Modeling | Bullets + right image | `geomod7.png` | Points defined; no volume; open surfaces |
| 15 | Surface Model — Alias StudioTools | Title + centre image | `geomod8.jpg` | Inline skate render |
| 16 | Surface Model — Rhino | Title + centre image | `geomod9.jpg` | Ducati motorcycle render |
| 17 | Why draw 3D Models? | Bullets only | — | Interpret / cheaper / FEA / CNC |
| 18 | 2D Applications | Bullets + bottom images | `3dmod_2d_apps.png` | Drafting, Art, Electronics |
| 19 | 3D Applications | Bullets + bottom images | `3dmod_3d_apps.png` | CAD/CAM/CAE/CG |
| 20 | Basics of FEA | Bullets + bottom images | `3dmod_fea_sequence.png` | Complex → smaller problems; FEA for design |
| 21+ | **Unknown** | — | — | Read pages 21+ of PDF at session start |

---

## 4. LaTeX Frame Patterns

### Caption-only slide (PPT slides 6, 10, 13)
```latex
\begin{frame}[fragile]{}
\begin{center}
\includegraphics[width=0.75\linewidth,keepaspectratio]{3dmod_drafting_board}
\end{center}
\vspace{2mm}
\small Manual drafting. Since 1970s: electronic drafting board.
\end{frame}
```

### Bullets + right image
```latex
\begin{frame}[fragile]\frametitle{3D Wire frame Modeling}
\begin{columns}
  \begin{column}{0.55\linewidth}
  \begin{itemize}
  \item Geometric entities are lines and curves in 3D
  \item Volume or surfaces of object not defined
  \item Easy to store and display
  \item Hard to interpret --- ambiguous
  \end{itemize}
  \end{column}
  \begin{column}{0.45\linewidth}
  \begin{center}
  \includegraphics[width=0.9\linewidth,keepaspectratio]{geomod4}
  \end{center}
  \end{column}
\end{columns}
\end{frame}
```

### Alertblock callout (PPT slide 8 "Advantages and Disadvantages of each?")
```latex
\begin{alertblock}{}
Advantages and Disadvantages of each?
\end{alertblock}
```

### Full-image slide
```latex
\begin{frame}[fragile]\frametitle{Evolution of CAD Technology}
\begin{center}
\includegraphics[width=0.9\linewidth,keepaspectratio]{geomod1}
\end{center}
\end{frame}
```

---

## 5. Final Step — Compile with make.bat

After all three `Main_*.tex` drivers are created, run:
```
make.bat
```

`make.bat` executes:
```bat
for /r %%i in (Main*.tex) do texify -cp %%i
```

This compiles every `Main_*.tex` in the folder (including the 3 new ones and the
existing ones) using `texify` with `-cp` (clean + pdf mode). Output PDFs land
beside each `.tex` file.

---

## 6. Execution Steps (next session — in order)

| # | Step | Who |
|---|---|---|
| 0a | Export `Intro_SolidModeling.ppt` → PDF | **User (before session)** |
| 0b | Export `Introduction To 3D Modeling_yhk.ppt` → PDF | **User (before session)** |
| 0c | Export images listed in Section 2B to `images/` | **User (before session)** |
| 1 | Read pages 21+ of `Intro_3DModeling.pdf`; complete slide map | Claude |
| 2 | Create `Main_Intro_3DModeling.tex` (driver) | Claude |
| 3 | Create `intro_3dmodeling_content.tex` (all frames) | Claude |
| 4 | Read `Intro_SolidModeling.pdf`; build slide + image map | Claude |
| 5 | User exports SolidModeling images → `images/solidmod_*.png` | **User (during session)** |
| 6 | Create `Main_Intro_SolidModeling.tex` + `intro_solidmodeling_content.tex` | Claude |
| 7 | Read `Intro_3DModeling_yhk.pdf`; compare with step 3 to find overlap | Claude |
| 8 | User exports YHK-specific images → `images/3dmodyhk_*.png` | **User (during session)** |
| 9 | Create `Main_Introduction_To_3D_Modeling_yhk.tex` + `intro_3dmodeling_yhk_content.tex` | Claude |
| 10 | Run `make.bat`; fix any compilation errors | Claude + User |

---

## 7. Risks and Notes

1. **Slides 21+ unknown**: The full slide count of `Intro_3DModeling.pdf` is not yet
   determined. Session starts by reading remaining pages before writing any `.tex`.

2. **YHK variant overlap**: `Introduction To 3D Modeling_yhk.ppt` likely shares
   most content with `Intro_3DModeling.ppt`. After viewing its PDF, shared frames
   may be pulled in via `\input{}` rather than duplicated.

3. **Autodesk © images** (slides 18–19): Marked "© 2013 Autodesk". Fine for
   personal/educational use. Noted in content file comments.

4. **Image sizing for multi-image slides**: PPT slide 8 has 4 separate images
   arranged freely. In Beamer this needs a two-column layout or a minipage grid.
   The execution session will handle this per slide.

5. **`texify` availability**: `make.bat` uses `texify` (MiKTeX). If not installed or
   not on PATH, the compilation step fails. Verify MiKTeX is installed before running.
