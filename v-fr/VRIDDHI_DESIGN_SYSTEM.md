# VRIDDHI (वृद्धि) — OFFICIAL DESIGN SYSTEM SPECIFICATION
> **Single Source of Truth (SSOT) for Visual, Interaction, and Brand Architecture**  
> **Document Version:** 2.0.0 (Production Verified)  
> **Target Platform:** Web Desktop, Tablet, and Mobile (Plain HTML5, Vanilla ES Modules, Tailwind CSS v4.3.3)  
> **Status:** Authoritative Design Specification

---

## 1. PROJECT DESIGN OVERVIEW

### 1.1 Brand Purpose & Communication Goal
**Vriddhi** (वृद्धि = *Sanskrit for growth, ascension, elevation, and progress*) is India's sovereign career and workforce intelligence platform. Visually and architecturally, Vriddhi translates high-velocity Indian engineering market volatility (1.5M+ annual engineering graduates, curriculum obsolescence, distorted salary rumors, notice period complexities) into **empirical, high-conviction clarity**.

Visually, the design achieves three primary communicative feats:
1. **Sovereign Dignity & National Context:** Grounded specifically in the Indian economic and technical landscape—calibrated in ₹ Lakhs Per Annum (LPA), modeled against five distinct Indian tech metros (Bengaluru, Hyderabad, Pune, Delhi-NCR, Mumbai), and addressing indigenous career crossroads such as Service-to-Product MNC transitions.
2. **Editorial Gravitas Meets Technological Precision:** Rather than adopting the hyperactive, neon-saturated aesthetic of consumer SaaS or the drab utilitarianism of enterprise HR portals, Vriddhi draws inspiration from high-end sovereign AI platforms (e.g., Sarvam AI). It balances grand editorial serif typography with razor-sharp JetBrains Mono telemetry and spacious ivory surfaces.
3. **Calm, Intelligent Atmospheric Elevation:** The interface rejects jarring layout shifts and heavy borders. It leverages soft, organic radial diffusions, delicate hairline dividers, floating pill controls, and a pristine white full-screen AI Counselor sanctuary adorned with atmospheric indigo, blush rose, and sage canopies.

### 1.2 Core Aesthetic Pillars
* **Editorial:** High-contrast editorial typography featuring *Instrument Serif* alongside clean geometric grotesk body copy (*Plus Jakarta Sans*).
* **Minimal & Spacious:** Generous negative space (padding from `py-24` to `py-32`), uncluttered single-task layouts, and deliberate content pacing.
* **Warm & Humane:** Soft eggshell surfaces (`#fcfcfc`), warm selection tints (`#fddcce`), and organic sunset gradients that avoid harsh cold blues.
* **Data-Grounded & Technical:** Tabular monospace figures (`font-mono`), Tukey 1.5× IQR outlier indicators, ARIMA time-series charts, and directed acyclic graph (DAG) roadmap nodes.
* **Fluid Motion:** Apple-grade cubic-bezier curves (`cubic-bezier(0.16, 1, 0.3, 1)`), staggered micro-animations, physical DOM translations, and zero-jump page transitions.

---

## 2. BRAND IDENTITY

### 2.1 Master Brand vs. Module Branding Architecture
Vriddhi maintains an explicit brand taxonomy where the **Master Parent Brand** and individual **Functional Modules** hold differentiated visual assets:

```
                            VRIDDHI (वृद्धि)
                    Master Brand Identity (logo.svg)
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       ▼                           ▼                           ▼
MODULE 1 (Career)           MODULE 2 (Skills)           MODULE 3 (Salary)
Outlook & ARIMA             483-Skill DAG               Tukey IQR Calibrator
[model-03.svg / Lavender]   [model-01.svg / Sunset]     [model-07.svg / Sage]
                                   │
                                   ▼
                         VRIDDHI AI COUNSELOR
                 Full-Screen Immersive Intelligence
                [lotus.svg + spark.svg + orbit.svg]
```

### 2.2 Master Vriddhi Wordmark & Logo
* **Wordmark:** Rendered in lowercase lowercase **`vriddhi`** in primary text (`#1f1f1f`).
* **Header Wordmark Typography:** Desktop: `font-bold text-xl sm:text-2xl tracking-tight`. Inside the AI Minimal Header: `font-season text-2xl tracking-tight`.
* **Devanagari Usage Rule:** Per project specification, the Devanagari translation (वृद्धि) is **strictly omitted** from the master navigation headers and primary logos to maintain clean international-standard legibility. Devanagari is reserved exclusively for formal documentation headers (`VRIDDHI (वृद्धि)`).
* **Parent Brand Symbol (`logo.svg`):**
  - **Asset Path:** `/logo.svg` (and duplicated at `/public/assets/logo.svg`).
  - **Geometry:** 45-degree diamond perimeter (`M287,113 L391,217 L287,321 L183,217 Z`) enclosing eight trimmed concentric petal arcs (`A60` and `A89`), centered by a four-point diamond star (`M287,182 Q...`) with a vertical anchor tail (`M285,243 L287,318`).
  - **Color:** Stroke `#000000` (width: 5px, round joins), center star fill `#000000`.
  - **Usage Restriction:** The master `logo.svg` is used **only** where parent Vriddhi branding is represented (Sticky Header, Footer, AI Navigation Back Button). It must **never** be used as a replacement for Vriddhi AI or module icons.
* **Logo Size Rules:**
  - Sticky Platform Header: `w-9 h-9 sm:w-10 sm:h-10` (36px to 40px).
  - AI View Header: `w-8.5 h-8.5 sm:w-9 sm:h-9` (34px to 36px).
  - Platform Footer: `w-10 h-10 sm:w-11 sm:h-11` (40px to 44px).
  - Clear Space: Minimum clearance equal to 50% of logo width on all sides.

---

## 3. TYPOGRAPHY SYSTEM

### 3.1 Font Family Declarations
Vriddhi employs a three-tiered typographical system imported via Google Fonts in `<head>` and mapped through Tailwind CSS v4 `@theme`:

| Token / Variable | Font Family | Import Source | Fallbacks | Available Weights | Primary Purpose |
|---|---|---|---|---|---|
| `--font-serif` (`.font-season`) | **Instrument Serif** | Google Fonts | `"Georgia", serif` | `400 (Normal)`, `400 (Italic)` | Editorial headlines, hero display titles, section titles, AI title |
| `--font-matter` (`font-sans`) | **Plus Jakarta Sans** | Google Fonts | `"Inter", system-ui, sans-serif` | `300, 400, 500, 600, 700` | Platform body copy, buttons, pills, cards, descriptions, navigation |
| `--font-mono` (`font-mono`) | **JetBrains Mono** | Google Fonts | `monospace` | `400, 500, 600` | Salary figures, ₹ LPA metrics, percentiles, chart ticks, code blocks, timestamps |

```css
/* Real Implementation Snippet from src/css/input.css */
@theme {
  --font-serif: "Instrument Serif", "Georgia", serif;
  --font-matter: "Plus Jakarta Sans", "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", monospace;
}

body {
  font-family: var(--font-matter);
  color: var(--color-tx);
  background-color: var(--color-sf);
  line-height: 1.6;
}

.font-season {
  font-family: var(--font-serif);
  font-weight: 400;
  letter-spacing: -0.02em;
  line-height: 1.08;
}
```

### 3.2 Typographic Hierarchy & Scale

| Semantic Role | Font Family | Size (Mobile $\rightarrow$ Desktop) | Line Height | Weight | Letter Spacing | Color Token |
|---|---|---|---|---|---|---|
| **Platform Hero Display** | Instrument Serif | `48px` $\rightarrow$ `64px` $\rightarrow$ `76px` | `1.03` | `400` | `-0.02em` (`tracking-tight`) | `#1f1f1f` (`--color-tx`) |
| **AI Landing Hero Title** | Instrument Serif | `60px` $\rightarrow$ `72px` $\rightarrow$ `76px` | `1.0` (`leading-none`) | `400` | `-0.025em` (`tracking-tight`) | `#111111` |
| **Section H2 (Pillars, Lab)** | Instrument Serif | `38px` $\rightarrow$ `54px` | `1.08` – `1.1` | `400` | `-0.02em` | `#1f1f1f` |
| **Dark CTA Display** | Instrument Serif | `36px` $\rightarrow$ `48px` $\rightarrow$ `62px` | `1.08` | `400` | `-0.02em` | `#ffffff` |
| **Pillar / Card Title (H3)** | Plus Jakarta Sans | `1.25rem` (`20px`) | `1.3` | `600` (`font-semibold`) | Normal | `#1f1f1f` |
| **Platform Subtitle** | Plus Jakarta Sans | `1rem` $\rightarrow$ `1.25rem` (`20px`) | `1.75` | `400` | Normal | `#3d3d3d` (`--color-tx-secondary`) |
| **AI Landing Tagline** | Plus Jakarta Sans | `1.125rem` $\rightarrow$ `1.3125rem` (`21px`) | `1.375` (`leading-snug`) | `400` | Normal | `#374151` |
| **Body Standard** | Plus Jakarta Sans | `0.9375rem` (`15px`) | `1.6` – `1.75` | `400` | `-0.01em` | `#242b35` / `#3d3d3d` |
| **Body Small / Captions** | Plus Jakarta Sans | `0.8125rem` – `0.875rem` (`13–14px`) | `1.5` | `400` – `500` | Normal | `#666666` (`--color-tx-tertiary`) |
| **Pill / Button Text** | Plus Jakarta Sans | `0.8125rem` – `0.9375rem` | `1.2` | `500` (`font-medium`) | Normal | `#ffffff` / `#1e2033` |
| **Micro Labels / Metros** | JetBrains Mono | `0.6875rem` (`11px`) | `1.0` | `600` – `700` | `0.06em` (`uppercase`) | `#78716c` / `#a5460f` |
| **Salary Data / LPA Values** | JetBrains Mono | `1rem` – `1.65rem` (`16–26px`) | `1.1` | `700` – `800` | `-0.02em` | `#1c1917` / `#581c87` |
| **Footer Giant Watermark** | Plus Jakarta Sans | `clamp(4rem, 16.5vw, 17rem)` | `0.88` | `800` (`font-extrabold`) | `0.08em` | `#1c1917` (opacity: `0.06`) |

---

## 4. COLOR SYSTEM

### 4.1 Master Brand Palette (Hex, OKLCH & Tokens)

```
[#fcfcfc] Canvas Base       [#1f1f1f] Primary Ink       [#e96c2f] Sovereign Amber
[#f5f5f5] Card Elevated     [#3d3d3d] Secondary Text    [#a5460f] Deep Earth
[#e6e6e6] Hairline Border   [#666666] Tertiary Muted    [#6366f1] Twilight Indigo
```

#### A. Neutrals & Canvas Surfaces
| Token Name | Hex Value | RGB / RGBA | Role & Implementation |
|---|---|---|---|
| `--color-sf` | `#fcfcfc` | `rgb(252, 252, 252)` | Master platform background body canvas |
| `--color-sf-secondary` | `#f5f5f5` | `rgb(245, 245, 245)` | Elevated pill background, select dropdown pill surface |
| `--color-sf-tertiary` | `#f0f0f0` | `rgb(240, 240, 240)` | Card inner section fills, hairline background dividers |
| `--color-st` | `#e6e6e6` | `rgb(230, 230, 230)` | Default card borders, showcase container borders |
| `--color-st-secondary`| `#f0f0f0` | `rgb(240, 240, 240)` | Hairline dividers, subtle horizontal section rules |
| `--color-tx` | `#1f1f1f` | `rgb(31, 31, 31)` | Primary headline and body ink |
| `--color-tx-secondary`| `#3d3d3d` | `rgb(61, 61, 61)` | Secondary subtitle text, navigation links |
| `--color-tx-tertiary` | `#666666` | `rgb(102, 102, 102)` | Muted descriptive paragraphs, card subtitles |
| Surface Pure | `#ffffff` | `rgb(255, 255, 255)` | AI Counselor view canvas, white card surfaces |
| Surface Dark | `#18181b` / `#1e2033` | `rgb(24, 24, 27)` | Dark CTA container, code blocks, dark pill buttons |

#### B. Brand Identity & Sovereign Tints
| Token Name | Hex Value | Purpose & Where Used |
|---|---|---|
| `--color-sr-orange-50` | `#fffbfa` | Announcement ticker top background |
| `--color-sr-orange-100`| `#feede6` | Active showcase role button pill, selection highlight |
| `--color-sr-orange-500`| `#f38858` | Midtone orange chart lines |
| `--color-sr-orange-700`| `#e96c2f` | Active showcase tab underline, ticker diamond motifs |
| `--color-sr-orange-900`| `#a5460f` | Active tab text, announcement badge text, verified pill |
| `--color-sr-indigo-50` | `#fafcff` | Sub-surface tint for technical areas |
| `--color-sr-indigo-100`| `#e8effc` | Module 1 Outlook header card banner |
| `--color-sr-indigo-500`| `#6a88e2` | Hero radial gradient divider line |
| `--color-sr-indigo-900`| `#212191` | Hero sovereign tag text ("India's Sovereign...") |
| `--color-sr-green-50`  | `#f2f8eb` | Module 3 Salary header card banner |
| `--color-sr-green-500` | `#83c040` | Interactive showcase central glowing orb |
| `--color-sr-green-900` | `#263d0e` | High-contrast green text |

#### C. Semantic Feedback Colors
| Semantic State | Fill / BG | Border | Text | Usage |
|---|---|---|---|---|
| **Success** | `#ecfdf5` (`emerald-50`) | `#a7f3d0` (`emerald-200`) | `#047857` (`emerald-700`) | Matched skills (✓), high readiness (>75%), positive delta |
| **Warning / Quick Win** | `#fffbeb` (`amber-50`) | `#fde68a` (`amber-200`) | `#b45309` (`amber-700`) | Adjacent quick-win skills, moderate readiness (60–75%) |
| **Critical / Gap** | `#fff1f2` (`rose-50`) | `#fecdd3` (`rose-200`) | `#be123c` (`rose-700`) | Missing gatekeeper skills (+), critical gaps (<60%) |
| **Informational** | `#eff6ff` (`blue-50`) | `#bfdbfe` (`blue-200`) | `#1d4ed8` (`blue-700`) | Remote work badge, city benchmark pill |

---

## 5. VRIDDHI GRADIENT SYSTEM

### 5.1 Platform Gradients
* **Top Announcement Ticker:** `linear-gradient(to bottom, #ffffff 0%, #fffbfa 100%)`.
* **Dark CTA Banner:** `linear-gradient(135deg, #2b2e44 0%, #1e2033 50%, #141522 100%)`.
* **Dark Pill Button:** `linear-gradient(to bottom, #3a3f5c 0%, #1e2033 100%)`.
* **Light Pill Button:** `linear-gradient(to bottom, #ffffff 0%, #f0f1f5 100%)`.
* **Module 1 Outlook Banner:** `linear-gradient(to bottom right, #e8effc 0%, #d2dff9 100%)`.
* **Module 2 Skill Gap Banner:** `linear-gradient(to bottom right, #feede6 0%, #fddcce 100%)`.
* **Module 3 Salary Banner:** `linear-gradient(to bottom right, #f2f8eb 0%, #e3f1d8 100%)`.
* **Interactive Central Orb:** `radial-gradient(circle, rgba(131, 192, 64, 0.45) 0%, rgba(200, 228, 176, 0.20) 60%, transparent 80%)`.

### 5.2 The AI Atmospheric Curved Canopy Dome
The AI Counselor interface features an expansive, celestial dome canopy in the top 62vh of the viewport that bathes the lotus centerpiece and branding in an aura of indigo, twilight periwinkle, blush rose, and fresh sage:

```css
/* Exact Implementation from src/css/input.css */
.ai-canopy-container {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 62vh;
  min-height: 560px;
  max-height: 700px;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  background-color: transparent;
  transition: opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

.ai-gradient-canopy {
  position: absolute;
  top: -8%;
  left: 50%;
  transform: translateX(-50%);
  width: 135vw;
  max-width: 1980px;
  height: 130%;
  background:
    /* 1. Luminous Periwinkle / Twilight Indigo Core */
    radial-gradient(ellipse 50% 48% at 50% 6%,
      #6366f1 0%,
      #818cf8 22%,
      rgba(165, 180, 252, 0.75) 44%,
      rgba(199, 210, 254, 0.45) 68%,
      transparent 88%),
    /* 2. Soft Blush Rose Warmth Halo */
    radial-gradient(ellipse 46% 40% at 50% 18%,
      rgba(253, 164, 175, 0.45) 0%,
      rgba(254, 205, 211, 0.30) 40%,
      transparent 75%),
    /* 3. Upper Left Rich Periwinkle Wing */
    radial-gradient(ellipse 55% 55% at 0% 26%,
      #5982ff 0%,
      #769eff 26%,
      rgba(145, 180, 255, 0.95) 50%,
      rgba(185, 210, 255, 0.60) 72%,
      transparent 90%),
    /* 4. Upper Right Rich Periwinkle Wing */
    radial-gradient(ellipse 55% 55% at 100% 26%,
      #5982ff 0%,
      #769eff 26%,
      rgba(145, 180, 255, 0.95) 50%,
      rgba(185, 210, 255, 0.60) 72%,
      transparent 90%),
    /* 5. Mid-Lower Left Blue Flank */
    radial-gradient(ellipse 54% 54% at 4% 60%,
      #628dff 0%,
      #84aaff 28%,
      rgba(155, 192, 255, 0.92) 52%,
      rgba(190, 216, 255, 0.55) 75%,
      transparent 90%),
    /* 6. Mid-Lower Right Blue Flank */
    radial-gradient(ellipse 54% 54% at 96% 60%,
      #628dff 0%,
      #84aaff 28%,
      rgba(155, 192, 255, 0.92) 52%,
      rgba(190, 216, 255, 0.55) 75%,
      transparent 90%),
    /* 7. Subtle Fresh Pale Sage Whisper */
    radial-gradient(ellipse 65% 45% at 50% 45%,
      rgba(187, 247, 208, 0.28) 0%,
      rgba(220, 252, 231, 0.15) 50%,
      transparent 80%);
  /* Curved Dome Arc Fade to Pure White */
  mask-image: radial-gradient(ellipse 85% 82% at 50% 0%,
      black 0%,
      black 58%,
      rgba(0, 0, 0, 0.90) 74%,
      rgba(0, 0, 0, 0.40) 88%,
      transparent 100%);
  -webkit-mask-image: radial-gradient(ellipse 85% 82% at 50% 0%,
      black 0%,
      black 58%,
      rgba(0, 0, 0, 0.90) 74%,
      rgba(0, 0, 0, 0.40) 88%,
      transparent 100%);
  filter: blur(8px);
}
```

### 5.3 Bottom Ambient Conversation Glow
When transitioning into multi-turn dialogue, the top canopy dims (`opacity: 0.15`), and a bottom ambient aura gently illuminates behind the persistent composer:
```css
.ai-bottom-glow {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 100vw;
  max-width: 1100px;
  height: 280px;
  background:
    radial-gradient(ellipse 40% 60% at 30% 100%, rgba(99, 102, 241, 0.22) 0%, transparent 70%),
    radial-gradient(ellipse 40% 60% at 70% 100%, rgba(199, 210, 254, 0.40) 0%, transparent 70%),
    radial-gradient(ellipse 50% 40% at 50% 100%, rgba(255, 255, 255, 0.95) 0%, transparent 80%);
  filter: blur(40px);
  opacity: 0;
  transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.conversation-mode .ai-bottom-glow { opacity: 1; }
```

---

## 6. SHAPE LANGUAGE

Vriddhi adheres to a strict geometric hierarchy of radii to balance editorial sharpness with tactile softness:

```
[9999px] Full Pill   ───>   Buttons, Badges, Search Composer, Category Filters
[32px]   Giant Card  ───>   Showcase Terminal, Dark Hero CTA Banner
[28px]   Master Card ───>   .sarvam-card (Features, Intelligence Units)
[24px]   Pillar Top  ───>   Module Header Banners (Pillars Grid)
[16-20px] Sub-Cards  ───>   AI Structured Callouts, Job Listings, Tooltips
[6px-8px] Minor Pins ───>   Speech bubble anchor notches, code blocks
```

* **Pills (`rounded-full` / `9999px`):** Used without exception for all primary user triggers—`.btn-pill-dark`, `.btn-pill-light`, `.ai-input-pill`, `.ai-category-pill`, `.ai-prompt-chip`, `.ai-followup-chip`, and city select badges.
* **Master Cards (`rounded-[32px]` / `rounded-[28px]`):** Large structural showcase modules and feature cards.
* **Module Banners (`rounded-[24px]`):** Distinct curved banners holding module 3D vector artwork.
* **Callout Units (`rounded-2xl` / `16px–20px`):** Structured AI intelligence cards (Skill Unlocks, Insights, Warnings, Metrics).
* **Asymmetrical Chat Anchors:**
  - Blue & Green Incoming Bubbles: `border-radius: 20px 20px 20px 6px`
  - Peach Outgoing Bubbles: `border-radius: 20px 20px 6px 20px`
  - AI User Message Bubble: `border-radius: 22px 6px 22px 22px`

---

## 7. BORDERS & DIVIDERS

* **Standard Outer Border:** `1px solid #e6e6e6` (`--color-st`).
* **Subtle Internal Dividers:** `1px solid #f0f0f0` (`--color-st-secondary`).
* **Translucent Blur Dividers:** `1px solid rgba(255, 255, 255, 0.60)` on floating controls.
* **Dashed Horizon Lines:** `1px dashed #ea580c` with `stroke-dasharray="4 4"` representing ARIMA forecast horizon lines on SVG charts.
* **Accent Left Borders on Callouts:**
  - Insight Callout: `border-left: 5px solid #0284c7`
  - Recommendation Callout: `border-left: 5px solid #10b981`
  - Critical Gap Callout: `border-left: 5px solid #f43f5e`
* **Rule on Gradients vs Borders:** Never use double borders. If a gradient fill is applied, border opacity must be lowered to `20%`–`40%` of the primary accent tone.

---

## 8. SHADOWS & DEPTH

* **Master Card Shadow (`.sarvam-card`):**
  - Rest: `box-shadow: 0px 0px 40px 0px rgba(0, 0, 0, 0.04);`
  - Hover: `box-shadow: 0px 8px 40px -4px rgba(0, 0, 0, 0.08); border-color: #d6d3d1;`
* **Dark Pill Inset Highlights (`.btn-pill-dark`):**
  - Rest: `box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.40), inset 0 -2px 0 rgba(0, 0, 0, 0.20);`
  - Hover: `box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.40), 0 4px 16px rgba(30, 32, 51, 0.20); transform: translateY(-1px);`
* **Persistent AI Input Pill (`.ai-input-pill`):**
  - Rest: `box-shadow: 0 4px 24px rgba(58, 63, 92, 0.08), 0 1px 4px rgba(0, 0, 0, 0.04);`
  - Focus: `box-shadow: 0 6px 32px rgba(58, 63, 92, 0.16), 0 0 0 3px rgba(199, 210, 254, 0.55); border-color: rgba(58, 63, 92, 0.65);`
* **AI Send Button (`.ai-send-btn`):** `box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35);`
* **Callout Elevation:** `box-shadow: 0 4px 20px -2px rgba(..., 0.12), 0 1px 3px rgba(0, 0, 0, 0.02);`

---

## 9. ICON SYSTEM

### 9.1 Icon Strategy & Rules
1. **SVG Exclusivity:** All brand, module, and capability symbols **must** be rendered using clean vector SVGs. Emojis (e.g. 🚀, 💡, 💰) are **strictly prohibited** from production UI components, buttons, and titles.
2. **Standard ViewBoxes:**
   - Capability & Action Icons: `viewBox="0 0 24 24"`, `width="24" height="24"`
   - Master Logo: `viewBox="107 37 360 360"`
   - Lotus Centerpiece: `viewBox="0 0 512 512"`
   - Celestial Orbit: `viewBox="0 0 700 200"`
   - Diamond Spark: `viewBox="0 0 28 44"`

### 9.2 Custom Vector Inventory

| Symbol Name | File Path | Dimensions / ViewBox | Primary Colors | Meaning & Usage |
|---|---|---|---|---|
| **Master Vriddhi Logo** | `/logo.svg` | `720x720` (`107 37 360 360`) | `#000000` | Sovereign master parent brand symbol |
| **White Lotus Logo** | `/public/assets/vriddhi/lotus.svg` | `512x512` | `#ffffff` (opacity 0.75–0.98) | Vriddhi AI sacred centerpiece & counselor avatar |
| **Celestial Orbit Curves** | `/public/assets/vriddhi/orbit.svg` | `700x200` | `rgba(255,255,255,0.45-0.75)` | Elliptical planetary curves cradling the lotus |
| **Diamond Spark** | `/public/assets/vriddhi/spark.svg` | `28x44` | `#ffffff` | Pulsing 4-point shimmer on the vertical entrance line |
| **Send Rocket / Arrow** | `/public/assets/vriddhi/send.svg` | `24x24` | `#ffffff` | Floating input pill query submission button |
| **Career Guidance Icon** | `/public/assets/vriddhi/icon-guidance.svg` | `24x24` | Stroke `#2563eb`, Fill `25%` | AI Capability pill: Guidance |
| **Skill Diagnostics Icon** | `/public/assets/vriddhi/icon-skills.svg` | `24x24` | Stroke `#ea580c`, Fill `#ea580c` | AI Capability pill: Skill Gaps |
| **Salary Insights Icon** | `/public/assets/vriddhi/icon-salary.svg` | `24x24` | Stroke `#16a34a` (width 2.2) | AI Capability pill: Salary Percentiles |
| **Courses Icon** | `/public/assets/vriddhi/icon-courses.svg` | `24x24` | Stroke `#db2777` | AI Capability pill: Course Pathways |
| **Market Comparisons Icon** | `/public/assets/vriddhi/icon-market.svg` | `24x24` | Stroke `#f97316` (width 2.5) | AI Capability pill: City Comparisons |
| **Interview Prep Icon** | `/public/assets/vriddhi/icon-interview.svg`| `24x24` | Stroke `#9333ea` | AI Capability pill: Counter-Offer Scripts |
| **Floral Heritage Motif** | `/public/assets/motif.svg` | `228x35` | `#F0F0F0` / Inverted White | Symmetrical Indian cultural divider in Hero & CTA |
| **Hero Sunset Arc** | `/public/assets/hero-gradient.svg` | `3244x1744` | `#F9730C` $\rightarrow$ `#A5BBFC` | Large atmospheric background dome behind Hero |

---

## 10. MODULE SYMBOL SYSTEM

The three functional modules and the intelligence layer share a cohesive geometric visual family featuring multi-petal floral geometries rendered in gradient lighting:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        MODULE SYMBOL FAMILY                            │
├────────────────────┬────────────────────┬──────────────────────────────┤
│ Module 1: Outlook  │ Module 2: Skills   │ Module 3: Salary             │
│ model-03.svg       │ model-01.svg       │ model-07.svg                 │
│ Lavender / Twilight│ Sunset Orange      │ Fresh Crimson & Blue         │
│ 5-Year Horizon     │ 483-Skill DAG      │ Tukey IQR Calibrator         │
└────────────────────┴────────────────────┴──────────────────────────────┘
```

* **Module 1: 5-Year Career Outlook (`public/assets/model-03.svg`):**
  - **Silhouette:** Eight-petal floral medallion with tapered upper leaves and flared lower wings.
  - **Color Palette:** Saturated linear gradient (`#fdaa5f` orange apex down to `#e420ad` magenta base with `#cd3efc` violet radial core).
  - **Container Banner:** `bg-gradient-to-br from-[#e8effc] to-[#d2dff9]`.
* **Module 2: Skill Gap Diagnostics (`public/assets/model-01.svg`):**
  - **Silhouette:** Soft rounded scalloped medallion with a central vertical teardrop spine.
  - **Color Palette:** Rich sunset spectrum (`#6A3DF5` purple base, `#2626FF` royal blue center, `#FF6BDC` warm pink flank, `#FFCDE6` pale base).
  - **Container Banner:** `bg-gradient-to-br from-[#feede6] to-[#fddcce]`.
* **Module 3: Salary Calibrator & Negotiation (`public/assets/model-07.svg`):**
  - **Silhouette:** Pointed heraldic star-crest with inner drop-shadow filter.
  - **Color Palette:** Linear gradient from `#B81514` crimson apex down to `#D2DFF9` periwinkle base.
  - **Container Banner:** `bg-gradient-to-br from-[#f2f8eb] to-[#e3f1d8]`.
* **Intelligence Layer: Vriddhi AI (`public/assets/model-11.svg`):**
  - **Silhouette:** Four-point compass star / lotus fusion with inset bevel filter.
  - **Color Palette:** Gradient from `#FCEAF0` blush to `#EA669F` magenta.

---

## 11. AI COUNSELOR VISUAL SYSTEM

### 11.1 Master Structure (100vw × 100vh Full-Screen Overlay)
The Vriddhi AI interface (`#vriddhi-ai-view`) is not a modal or generic popup—it is a full-screen immersive spatial experience.

```
┌────────────────────────────────────────────────────────────────────────┐
│ #ai-header (Floating 56px: Master Logo + Back Button + Metro Selector) │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│ .ai-canopy-container (62vh Layered Atmospheric Dome)                  │
│                                                                        │
│                      Vertical Thread & Diamond Spark                   │
│                                   │                                    │
│                         Vriddhi AI White Lotus                         │
│                         ══════════════════════                         │
│                          Flipped Orbit Curves                          │
│                                                                        │
│                              Vriddhi AI                                │
│          Your AI career counselor, grounded in India's real...         │
│                                                                        │
│                [6 Capability Feature Pills: 2 Rows of 3]               │
│                                                                        │
│                     THE PERSISTENT SEARCH COMPOSER                     │
│                  ✦ [Ask Vriddhi anything...]        [➤]               │
│                                                                        │
│                    "Try asking..." Suggestion Chips                    │
└────────────────────────────────────────────────────────────────────────┘
```

### 11.2 Initial Landing State
1. **Vertical Celestial Centerpiece:**
   - Top vertical hairline dropping from ceiling: `width: 1.2px; height: 80px; bg-gradient-to-b from-transparent via-white/70 to-white/95`.
   - Centered diamond spark: `public/assets/vriddhi/spark.svg` pulsing via `@keyframes spark-shimmer` (3.2s infinite ease-in-out).
   - Bottom vertical hairline fading out cleanly: `height: 48px; bg-gradient-to-b from-white/95 via-white/30 to-transparent`.
   - Pure White Lotus Logo (`public/assets/vriddhi/lotus.svg`): `w-20 h-15 sm:w-22 sm:h-16`, drop shadow `0 2px 16px rgba(255,255,255,0.95)`.
   - Flipped Orbit Curves (`public/assets/vriddhi/orbit.svg`): `max-w-[580px] -mt-13`, inverted vertically with `transform: scaleY(-1)` to cradle the lotus.
2. **Editorial Branding:**
   - Title: `font-season text-6xl sm:text-7xl md:text-[76px] text-[#111111] font-normal tracking-tight`.
   - Subtitle: `font-sans text-lg sm:text-[21px] text-[#374151] max-w-lg leading-snug`.
3. **Capability Feature Pills (2 Rows of 3):**
   - White rounded capsules with colored micro-icons (`w-6 h-6` background circles).
   - Backgrounds: Guidance (`#eff6ff`), Skills (`#f5f3ff`), Salary (`#f0fdf4`), Courses (`#fdf2f8`), Market (`#e0f2fe`), Interview (`#faf5ff`).

### 11.3 Active Conversation State
1. **Physical Hero Collapse:** `#ai-landing-hero` translates upward (`translateY(-30px)`), scales down, and collapses `max-height: 0` with `pointer-events: none` over `700ms cubic-bezier(0.16, 1, 0.3, 1)`.
2. **Persistent Composer Preservation:** The composer does **not** get replaced or re-rendered. It physically translates to the viewport bottom as the conversation thread expands.
3. **Scroll Thread Expansion:** `#ai-conversation-scroll` expands to `height: 100%`, enabling smooth user message and AI card streaming.

---

## 12. AI RESPONSE FORMATTING & CARDS

### 12.1 Core Architectural Principle
> **CRITICAL RULE:** Standard AI conversational prose **must remain normal clean text**.  
> Never wrap the entire response inside one giant card or heavy box.  
> Specialized visual units must only be used selectively when structured data (benchmarks, unlocks, warnings) is present.

### 12.2 Typographic Hierarchy for AI Responses
* **Container:** `.ai-response-body`, `font-size: 0.9375rem (15px)`, `line-height: 1.75`, `color: #242b35`, `letter-spacing: -0.01em`.
* **Paragraphs:** Margin bottom `0.875rem` (`14px`), last paragraph `margin-bottom: 0`.
* **Headings:**
  - H1 / H2: `font-season text-xl sm:text-2xl text-stone-900 font-normal mt-5 mb-2`
  - H3: `font-sans text-sm font-bold uppercase tracking-wider text-stone-800 mt-4 mb-1.5`
* **Bold Semantics:** `<strong class="font-semibold text-stone-900">`
* **Inline Code:** `<code class="px-1.5 py-0.5 rounded bg-slate-100 text-[#3730a3] font-mono text-[13px] border border-slate-200/70">`
* **Inline Growth Badges:** Automatically converted via regex `[+₹2.8L boost]` into `<span class="ai-inline-badge">`:
  - Background: `linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)`
  - Border: `1px solid #93c5fd`
  - Text: `#1d4ed8 font-bold`

### 12.3 Structured Callout Card Inventory

#### 1. Skill Unlock Card (`.ai-card-skill`)
* **Purpose:** Highlights salary boosts and unlocked jobs from mastering a missing skill (e.g. Apache Spark, Kubernetes).
* **Styles:**
  - Background: `linear-gradient(135deg, #edf3fe 0%, #dbe8fe 100%)`
  - Border: `1px solid #bfdbfe`, `border-radius: 20px`, `padding: 1.15rem 1.25rem`
  - Tag: `⚡ SKILL UNLOCK` in `#1d4ed8` font-bold
  - Icon: `w-6 h-6 rounded-lg bg-gradient-to-br from-[#3b82f6] to-[#6366f1] text-white`
  - Pills: White capsule for job openings (`#1e293b`), Light blue capsule for salary uplift (`#1d4ed8`)

#### 2. Market Signal / Insight Card (`.ai-card-insight`)
* **Purpose:** Highlights time-sensitive macro trends, hiring volumes, and ARIMA projections.
* **Styles:**
  - Background: `linear-gradient(135deg, #f0f7ff 0%, #e0f2fe 100%)`
  - Border: `1px solid #bae6fd`, `border-left: 5px solid #0284c7`, `border-radius: 16px`
  - Tag: `MARKET SIGNAL` with SVG spark in `#0369a1`
  - Text: `0.90625rem`, `#0f172a`, `line-height: 1.65`

#### 3. Recommendation Card (`.ai-card-recommendation`)
* **Purpose:** Prescriptive advice on interview prep, resumes, and study timelines.
* **Styles:**
  - Background: `linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)`
  - Border: `1px solid #86efac`, `border-left: 5px solid #10b981`, `border-radius: 16px`
  - Tag: `RECOMMENDATION` with checkmark badge in `#047857`
  - Text: `0.90625rem`, `#064e3b`

#### 4. Critical Gap / Warning Card (`.ai-card-warning`)
* **Purpose:** Alerts candidates to gatekeeper skill gaps or uncalibrated CTC expectations.
* **Styles:**
  - Background: `linear-gradient(135deg, #fff1f2 0%, #ffe4e6 100%)`
  - Border: `1px solid #fecdd3`, `border-left: 5px solid #f43f5e`, `border-radius: 16px`
  - Tag: `CRITICAL GAP` with warning triangle in `#be123c`
  - Text: `0.90625rem`, `#4c0519`

#### 5. Benchmark Metric Card (`.ai-card-metric`)
* **Purpose:** Standalone numeric callouts (e.g. P50 Median: ₹18.0L LPA).
* **Styles:**
  - Background: `linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)`
  - Border: `1px solid #d8b4fe`, `border-radius: 18px`, `padding: 1.1rem 1.35rem`
  - Label: `font-mono text-xs text-[#7e22ce] uppercase font-bold`
  - Value: `font-mono text-2xl sm:text-[1.65rem] font-extrabold text-[#581c87]`
  - Subtext: `text-xs font-semibold text-[#047857]`

---

## 13. AI STREAMING & INTERACTION ENGINE

### 13.1 Progressive Block-Aware Streaming
Rather than dumping markdown or recalculating innerHTML across the entire response on each token, Vriddhi utilizes an AST-based block parser:
1. `markdownToBlocks()` separates raw streaming text into blocks: `prose`, `heading`, `list`, `table`, `code`, and `callout`.
2. `streamBlocks()` renders blocks sequentially:
   - Prose tokens stream word-by-word with an active blinking cursor (`.ai-stream-cursor`).
   - Words stream at `18ms` intervals for a fluid, natural reading pace.
   - Finished blocks are locked in the DOM; their state is never re-evaluated or re-painted.
   - Structured cards reveal instantaneously with an upward glide (`callout-entrance` 320ms).
3. **Smart Scroll Retention:** The viewport only auto-scrolls down (`scrollContainer.scrollTop = scrollContainer.scrollHeight`) if the user is already within `80px` of the bottom. If the user scrolls up to review earlier guidance, auto-scroll gracefully pauses.

### 13.2 Loading & Thinking Animation
* **Avatar:** Official White Lotus logo enclosed in a 40px gradient circle: `linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%)`.
* **Lottie Player:** Renders `loading.json` (`width: 40px; height: 40px;`) without text labels or enclosing containers.
* **CSS Fallback:** If Lottie Web script is delayed, three animated bouncing dots (`bg-[#6366f1]`) display seamlessly with staggered delays (`0s`, `0.2s`, `0.4s`).

---

## 14. MOTION & TRANSITION SYSTEM

### 14.1 Easing Curves & Timing Standards
Vriddhi standardizes all movement on the Apple decelerate cubic curve:
* **Primary Fluid Easing:** `cubic-bezier(0.16, 1, 0.3, 1)`
* **Micro-interaction Hover:** `0.20s – 0.25s ease`
* **Page & View Switch Duration:** `0.42s – 0.45s`
* **Atmospheric Canopy Transitions:** `0.70s – 0.80s`

### 14.2 Platform $\leftrightarrow$ AI View Page Transition
Switching between the main website and Vriddhi AI uses a coordinated, cinematic dual-view choreography:

| Step | Target Element | Action & CSS Applied |
|---|---|---|
| **1. Capture Scroll** | `window` | `savedScrollY = window.scrollY` recorded to avoid jumping to top on return |
| **2. Dim Platform** | `#platform-view` | Add `.platform-dimmed`: `scale(0.972) translateY(-10px) blur(5px) opacity(0)` |
| **3. Elevate AI** | `#vriddhi-ai-view` | Remove `.hidden`, add `.ai-active`: `scale(1) translateY(0) opacity(1)` |
| **4. Stagger Header** | `#ai-header` | `.ai-header-anim`: `translateY(0) opacity(1)` (80ms delay) |
| **5. Stagger Canopy** | `#ai-canopy-container` | `.ai-canopy-anim`: `scale(1) opacity(1)` (50ms delay) |
| **6. Stagger Centerpiece** | `.ai-centerpiece-anim` | `translateY(0) scale(1) opacity(1)` (120ms delay) |
| **7. Stagger Title** | `.ai-title-anim` | `translateY(0) opacity(1)` (180ms delay) |
| **8. Stagger Pills** | `.ai-pills-anim` | `translateY(0) opacity(1)` (240ms delay) |
| **9. Stagger Composer**| `#ai-composer-wrapper` | `translateY(0) scale(1) opacity(1)` (280ms delay) |
| **10. Return Flow** | `#vriddhi-ai-view` | Add `.ai-closing`: `scale(0.985) translateY(14px) opacity(0)`, scroll restored |

---

## 15. SPACING SYSTEM

### 15.1 Platform Gutters & Containers
* **Master Layout Max-Widths:**
  - Header & Global Bar: `max-w-[1340px]`
  - Standard Sections (Pillars, Lab, Features): `max-w-[1280px]`
  - Text & Subtitle Enclosures: `max-w-4xl` (`56rem` / 896px) or `max-w-2xl` (`42rem` / 672px)
  - AI Center Conversation Column: `max-w-3xl` (`48rem` / 768px)
  - AI Persistent Composer Width: `max-w-[640px]`
* **Horizontal Page Padding:**
  - Mobile: `px-6` (24px)
  - Desktop: `px-10` (40px)
* **Vertical Section Spacing:**
  - Standard Section Spacing: `py-24 md:py-32` (96px mobile, 128px desktop)
  - Dark Hero CTA Section: `py-16 md:py-24` (64px mobile, 96px desktop)
  - Hero Section: `pt-24 pb-20 md:pt-32 md:pb-28`

### 15.2 Component Padding & Margins
* **Pill Buttons:** `py-3 px-7` (`0.75rem 1.75rem`)
* **AI Category Pills:** `py-2 px-4.5` (`0.52rem 1.15rem`)
* **AI Prompt Chips:** `py-1.5 px-4` (`0.45rem 1.05rem`)
* **AI Input Pill:** `px-5 py-2.5` (`1.25rem 0.625rem`)
* **AI Callout Cards:** `padding: 1rem 1.25rem`
* **Card Margins in Conversation:** `my-3.5` (14px)

---

## 16. LAYOUT SYSTEM

### 16.1 Section Composition & Stacking Order
1. **Top Announcement Ticker:** `z-50`, fixed height `h-8` (32px), subtle border bottom.
2. **Sticky Navigation Header:** `z-40`, height `h-16` (64px), backdrop blur with `bg-white/90`.
3. **Hero Stage:** Symmetrical center alignment, layered SVG arc background, radial divider lines.
4. **Partner Ecosystem Ribbon:** Symmetrical horizontal flex wrap with `gap-8 md:gap-12`, `opacity-50 grayscale hover:grayscale-0`.
5. **3-Module Pillars Grid:** 3-column desktop layout (`grid-cols-1 md:grid-cols-3 gap-8`), matching top gradient banners.
6. **Showcase Terminal:** Large rounded card (`rounded-[32px]`) featuring 12-column asymmetric split (3-col selector, 5-col orb stage, 4-col live intelligence output).
7. **2×2 Intelligence Feature Grid:** 4 cards in `grid-cols-1 md:grid-cols-2 gap-6`.
8. **Dark Hero CTA Section:** Centered 32px rounded enclosure with white button.
9. **Editorial Footer:** 6-column desktop navigation with flush watermark.

---

## 17. RESPONSIVE SYSTEM

Vriddhi uses standard Tailwind breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`):

| Viewport | Header | Hero Headline | Pillars & Grids | AI Composer & Pills |
|---|---|---|---|---|
| **Mobile (<640px)** | Hamburger / CTAs only | `48px` | Single column vertical stack (`grid-cols-1`) | Single column stacked pills, full width composer |
| **Tablet (640px–767px)** | Logo + CTAs + Metro | `64px` | Single or 2-column | 2 rows of 3 wrapped pills, centered composer |
| **Laptop (768px–1023px)**| Full Navigation Links | `76px` | 3-column pillars, 2-column feature cards | 2 rows of 3 pills, max 640px composer |
| **Desktop ($\ge$1024px)**| Full Sticky Nav | `76px` | 12-column split showcase, 3-column pillars | Full spatial canopy and staggers |

---

## 18. COMPONENT VISUAL LANGUAGE

### 18.1 Button Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VRIDDHI BUTTON MATRIX                           │
├─────────────────────┬───────────────────────────┬──────────────────────┤
│ Variant             │ Visual Specification      │ Hover State          │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ .btn-pill-dark      │ linear-gradient(#3a3f5c,  │ translateY(-1px),    │
│                     │  #1e2033), white text     │ shadow: 0 4px 16px   │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ .btn-pill-light     │ linear-gradient(#ffffff,  │ translateY(-1px),    │
│                     │  #f0f1f5), dark text      │ border: rgba(30..)   │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ .ai-send-btn        │ linear-gradient(#4f46e5,  │ scale(1.05),         │
│                     │  #7c3aed, #2563eb)        │ shadow: 0 6px 22px   │
├─────────────────────┼───────────────────────────┼──────────────────────┤
│ .ai-category-pill   │ #ffffff, border: #e5e7eb, │ translateY(-1px),    │
│                     │ color: #374151            │ border: #818cf8      │
└─────────────────────┴───────────────────────────┴──────────────────────┘
```

* **Dark Pill (`.btn-pill-dark`):**
  - Background: `linear-gradient(to bottom, #3a3f5c 0%, #1e2033 100%)`
  - Text: `#ffffff font-medium text-[15px]`
  - Shadow: `inset 0 1px 0 rgba(255, 255, 255, 0.4), inset 0 -2px 0 rgba(0, 0, 0, 0.2)`
* **Light Pill (`.btn-pill-light`):**
  - Background: `linear-gradient(to bottom, #ffffff 0%, #f0f1f5 100%)`
  - Text: `#1e2033 font-medium text-[15px]`
  - Border: `1px solid rgba(30, 32, 51, 0.14)`
* **AI Send Button (`.ai-send-btn`):**
  - Dimensions: `40px × 40px` circular button
  - Background: `linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%)`

---

## 19. DATA VISUALIZATION STYLE

All charts and telemetry visualizers are implemented in pure SVG with zero external charting library bloat:

### 19.1 10-Year Trend Visualizer (2020–2030)
* **Historical Data (2020–2024):** Solid stroke `#1c1917` (stroke-width: 2.5px), under-curve area fill `linear-gradient(to bottom, rgba(28,25,23,0.08) 0%, transparent 100%)`.
* **ARIMA Projected Forecast (2025–2030):** Dashed stroke `#f97316` (stroke-dasharray: `5 4`, stroke-width: 2.5px).
* **Divider Horizon:** Vertical dashed separator `#ea580c` with label `TODAY / FORECAST HORIZON`.
* **Data Ticks:** Monospace text in `#78716c` with horizontal hairline guidelines (`#e7e5e4`, dashed `3 3`).

### 19.2 Readiness Score Gauge
* **Structure:** Circular SVG gauge (`viewBox="0 0 120 120"`), stroke-width 9px.
* **Track:** Inactive ring `#f5f5f4`, animated active stroke with `stroke-dasharray` and `stroke-dashoffset`.
* **Threshold Colors:**
  - $\ge 75\%$: Green (`#16a34a`)
  - $60\% - 74\%$: Amber (`#d97706`)
  - $< 60\%$: Red (`#dc2626`)
* **Center Metric:** Large monospace percentage display (`font-mono text-3xl font-bold text-stone-900`).

### 19.3 Compensation Band Visualizer
* **Baseline Track:** Height 12px (`h-3 bg-stone-100 rounded-full`).
* **Market P25 to P75 Range:** Muted bar `#e7e5e4`.
* **Candidate Worth:** Active bar with gradient `from-orange-400 to-orange-500`.

---

## 20. PAGE COMPOSITION RULES

1. **Whitespace Generosity:** Sections must maintain minimum `py-24` padding. Crowded layouts dilute editorial authority.
2. **Selective Card Usage:** Do not turn everything into a card. Cards are reserved for self-contained actionable modules or structured data units.
3. **No Admin Panel Aesthetic:** Avoid dense tables, gray borders around raw text, or cluttered dashboards.
4. **Color Discipline:** 90% of the visual field remains ivory, pure white, and charcoal ink. Vivid gradients are strictly confined to top module banners, the celestial canopy dome, and actionable status badges.

---

## 21. ASSET RULES

1. **Preferred Asset Directory Structure:**
   - Master Logos: Project root (`/logo.svg`)
   - Reusable Module Icons: `/public/assets/` (`model-01.svg`, `model-03.svg`, `model-07.svg`, `model-11.svg`)
   - AI Counselor Assets: `/public/assets/vriddhi/` (`lotus.svg`, `spark.svg`, `orbit.svg`, `send.svg`, `icon-*.svg`)
   - Partner Logos: `/public/assets/` (`aadhaar.svg`, `cred.svg`, `infosys.svg`, etc.)
2. **When to use SVG vs. CSS:**
   - Use **SVG** for logos, brand glyphs, DAG illustrations, charts, and icons.
   - Use **CSS** for gradients, atmospheric glow, shadows, and transitions.

---

## 22. DESIGN TOKENS (CSS & TAILWIND v4)

```css
:root {
  /* Surfaces */
  --color-sf: #fcfcfc;
  --color-sf-secondary: #f5f5f5;
  --color-sf-tertiary: #f0f0f0;

  /* Borders */
  --color-st: #e6e6e6;
  --color-st-secondary: #f0f0f0;

  /* Typography */
  --color-tx: #1f1f1f;
  --color-tx-secondary: #3d3d3d;
  --color-tx-tertiary: #666666;

  /* Sovereign Orange */
  --color-sr-orange-50: #fffbfa;
  --color-sr-orange-100: #feede6;
  --color-sr-orange-500: #f38858;
  --color-sr-orange-700: #e96c2f;
  --color-sr-orange-900: #a5460f;

  /* Sovereign Indigo */
  --color-sr-indigo-50: #fafcff;
  --color-sr-indigo-100: #e8effc;
  --color-sr-indigo-500: #6a88e2;
  --color-sr-indigo-900: #212191;

  /* Sovereign Sage */
  --color-sr-green-50: #f2f8eb;
  --color-sr-green-500: #83c040;
  --color-sr-green-900: #263d0e;

  /* Geometry */
  --radius-4xl: 32px;
  --radius-3xl: 24px;
}
```

---

## 23. DESIGN DO'S

* **DO** use the lowercase editorial wordmark `vriddhi` in headlines and navigation.
* **DO** use *Instrument Serif* (`.font-season`) for primary display titles and *Plus Jakarta Sans* for UI.
* **DO** format all currency and compensation in **₹ LPA** with Tukey IQR calibration labels.
* **DO** keep normal AI dialogue as unboxed, beautifully spaced editorial prose.
* **DO** use selective structured cards for Skill Unlocks, Insights, Warnings, and Metrics.
* **DO** use the official pure white lotus logo (`public/assets/vriddhi/lotus.svg`) for AI branding.
* **DO** preserve scroll position (`savedScrollY`) when switching to and from the AI Counselor view.

---

## 24. DESIGN DON'TS

* **DON'T** use random emojis (🚀, 💡, 💰, 🔥) in production components; use dedicated SVGs.
* **DON'T** wrap an entire AI conversation response inside one giant card.
* **DON'T** destroy and recreate the search input pill; it must physically translate.
* **DON'T** add the Hindi Devanagari translation (वृद्धि) to the primary navigation headers.
* **DON'T** use harsh blue neon shadows or generic Bootstrap-style buttons.
* **DON'T** introduce third-party chart libraries (Chart.js, Recharts); use lightweight native SVGs.
* **DON'T** use square corners on action buttons; all buttons must be pills (`rounded-full`).

---

## 25. MASTER FILE & ASSET INDEX

| Asset / File | File System Path | Format | Role & Purpose |
|---|---|---|---|
| **Master Vriddhi Logo** | `logo.svg` | SVG | Primary brand identity logo |
| **Vriddhi AI Lotus** | `public/assets/vriddhi/lotus.svg` | SVG | Official pure white lotus centerpiece & AI avatar |
| **Diamond Spark** | `public/assets/vriddhi/spark.svg` | SVG | Pulsing diamond spark on celestial hairline |
| **Celestial Orbit** | `public/assets/vriddhi/orbit.svg` | SVG | Planetary orbit curves cradling lotus |
| **Send Rocket Arrow** | `public/assets/vriddhi/send.svg` | SVG | Query submit action button icon |
| **AI Guidance Icon** | `public/assets/vriddhi/icon-guidance.svg` | SVG | Feature capability pill icon: Guidance |
| **AI Skills Icon** | `public/assets/vriddhi/icon-skills.svg` | SVG | Feature capability pill icon: Skills |
| **AI Salary Icon** | `public/assets/vriddhi/icon-salary.svg` | SVG | Feature capability pill icon: Salary |
| **AI Courses Icon** | `public/assets/vriddhi/icon-courses.svg` | SVG | Feature capability pill icon: Courses |
| **AI Market Icon** | `public/assets/vriddhi/icon-market.svg` | SVG | Feature capability pill icon: Market |
| **AI Interview Icon**| `public/assets/vriddhi/icon-interview.svg`| SVG | Feature capability pill icon: Interview |
| **Floral Heritage Motif** | `public/assets/motif.svg` | SVG | Cultural decorative divider in Hero & CTA |
| **Hero Arc Gradient** | `public/assets/hero-gradient.svg` | SVG | Large background atmospheric gradient arc |
| **Module 1 Symbol** | `public/assets/model-03.svg` | SVG | Career Outlook Module artwork (Lavender) |
| **Module 2 Symbol** | `public/assets/model-01.svg` | SVG | Skill Diagnostics Module artwork (Sunset) |
| **Module 3 Symbol** | `public/assets/model-07.svg` | SVG | Salary Calibrator Module artwork (Crimson) |
| **AI Layer Symbol** | `public/assets/model-11.svg` | SVG | Vriddhi AI Counselor Module artwork (Pink) |
| **Lottie Loading Data**| `loading.json` / `loadingAnimationData.js` | JSON/JS | Vriddhi thinking indicator animation |
| **Master Stylesheet**| `src/css/input.css` | CSS | Source Tailwind CSS v4 design tokens & utilities |
| **Compiled CSS** | `dist/css/styles.css` | CSS | Minified production CSS bundle |
| **Master Web Shell** | `index.html` | HTML | Complete single-page application shell |
| **AI Counselor Engine**| `src/js/aiCounselor.js` | JS | Full-screen counselor controller & animations |
| **Response Renderer**| `src/js/aiResponseRenderer.js` | JS | Markdown parser & callout rendering engine |
| **UI Visual Widgets**| `src/js/components.js` | JS | Native SVG charts, gauges, range bars, cards |
| **State Store** | `src/js/state.js` | JS | Centralized reactive application store |
| **Mock Data Layer** | `src/data/mockData.js` | JS | 72k postings, 5 metros, compensation schemas |

---

## 26. IMPLEMENTATION REFERENCES

Before implementing any new page, module, or component in the Vriddhi repository, developers and AI agents must review:
1. `src/css/input.css`: Check predefined `@theme` tokens, `.sarvam-card`, `.btn-pill-dark`, and `.ai-card-*` classes before writing custom styles.
2. `index.html`: Review existing semantic HTML structure, accessibility tags, and modal layouts.
3. `src/js/components.js`: Reuse existing chart, gauge, and card generators rather than introducing new dependencies.
4. `src/js/aiResponseRenderer.js`: Review markdown parsing rules and callout element builders.

---

## 27. VRIDDHI DESIGN AT A GLANCE

```
┌────────────────────────────────────────────────────────────────────────┐
│                      VRIDDHI DESIGN QUICK REFERENCE                    │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Primary Typography  │ Instrument Serif (Display) + Plus Jakarta Sans   │
│ Monospace Font      │ JetBrains Mono (Numbers, LPA, Charts, Badges)    │
│ Base Background     │ #fcfcfc (Canvas) / #ffffff (AI Sanctuary)        │
│ Primary Ink         │ #1f1f1f (Body) / #3d3d3d (Muted) / #111111 (AI)  │
│ Accent Colors       │ Sovereign Amber (#e96c2f), Twilight Indigo       │
│                     │ (#6366f1), Sage Green (#10b981), Rose (#f43f5e)   │
│ Button Geometry     │ Strictly Pill-Shaped (border-radius: 9999px)     │
│ Card Geometry       │ rounded-[28px] or rounded-[32px]                 │
│ Callout Geometry    │ rounded-2xl (16px to 20px)                       │
│ Master Brand Logo   │ /logo.svg (Diamond with inner petal arcs & star) │
│ AI Counselor Logo   │ /public/assets/vriddhi/lotus.svg (White Lotus)   │
│ Motion Curve        │ cubic-bezier(0.16, 1, 0.3, 1) (Apple Decelerate) │
│ Primary Currency    │ ₹ Lakhs Per Annum (LPA)                          │
│ AI Response Rule    │ Clean unboxed text; cards only for special data  │
└─────────────────────┴──────────────────────────────────────────────────┘
```

---

## 28. SOURCE OF TRUTH RULE

> **MANDATORY NOTICE FOR ALL DEVELOPERS AND AI CODING AGENTS:**  
> This file is the **absolute visual and design system source of truth** for future Vriddhi frontend work.  
> 
> Before creating any new page, section, component, icon, SVG, gradient, or animation:  
> 1. Read this document thoroughly.  
> 2. Reuse the existing design tokens and CSS utility classes.  
> 3. Reuse the existing SVG vector assets.  
> 4. Preserve typographical rules (Instrument Serif + Plus Jakarta Sans + JetBrains Mono).  
> 5. Maintain the module symbol family (`model-01`, `model-03`, `model-07`, `model-11`).  
> 6. Only introduce new design primitives when they are strictly required and adhere to this design philosophy.
