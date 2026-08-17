# Biofermentor Virtual SC v3.0 — Scientific Model Note

## Scope

Version 3.0 changes the metabolic structure of the *Saccharomyces cerevisiae*
model. It remains a transparent phenomenological simulator for teaching,
control studies and model-development workflows; it is **not** a validated
digital twin of a particular strain, medium, vessel or industrial plant.

## Scientific motivation

The v2.x formulation linked nearly all glucose uptake and ethanol formation to
the specific growth rate. Consequently, when assimilable nitrogen approached
zero, `mu -> 0`, growth-associated glucose uptake collapsed, and ethanol
formation became almost a maintenance-only residual. This was internally
consistent but too restrictive for nitrogen-limited alcoholic fermentation.

Experimental literature shows that nitrogen deficiency can strongly reduce
biomass formation and glucose-transport/fermentation capacity without implying
that carbon catabolism instantaneously becomes zero. Nitrogen-limited sluggish
fermentation is therefore better represented by separating anabolic growth
from a residual product-forming catabolic capacity.

## v3.0 kinetic structure

Growth remains

```text
mu = mu_max * fS * fN * fP * fT * fpH * oxygen_growth
```

and nitrogen consumption remains growth-associated:

```text
qN = mu / Yxn
```

Growth-associated glucose demand is

```text
qS_growth = mu / Yxs
```

v3.0 adds a non-growth-associated catabolic term:

```text
fS_cat = S / (Ks_cat + S)
fN_cat = N_cat_floor + (1 - N_cat_floor) * N/(Kn_cat + N)
n_uncoupling = (1 - fN)^N_uncouple_exp

qS_ng = qS_ng_max * fS_cat * fP * fT * fpH * fN_cat * n_uncoupling
```

Thus, at high nitrogen availability the extra pathway is weak, while it is
progressively recruited as nitrogen limits growth. At `N -> 0`, the pathway
retains only the bounded fraction `N_cat_floor`; nitrogen starvation therefore
reduces catabolic capacity but does not force it to exactly zero.

Maintenance is kept separate:

```text
qS_maint = ms * S/(Ks_m + S)
```

The active substrate flux is partitioned between fermentation and respiration:

```text
qS_active = qS_growth + qS_ng
qS_ferm = phi * qS_active
qS_resp = (1 - phi) * qS_active + qS_maint
qS = qS_active + qS_maint
qP = Yps * qS_ferm
```

This distinction is visible in the GUI and exported auxiliary variables.

## Nitrogen stress

v3.0 reports

```text
n_stress = Kn_stress/(Kn_stress + N)
```

as a dimensionless diagnostic from 0 to 1. In the reference model it does **not**
directly increase death rate. This is intentional: nitrogen limitation,
quiescence/stress and cell death are not treated as synonymous processes.
A future model may introduce a calibrated dynamic quiescent-state compartment,
but v3.0 does not claim that additional mechanism.

## Reference parameter status

The new parameters `qS_ng_max`, `Ks_cat`, `Kn_cat`, `N_cat_floor`,
`N_uncouple_exp` and `Kn_stress` are **phenomenological reference values**.
They were selected to produce a bounded, auditable reference scenario and are
not asserted to be universal constants for *S. cerevisiae*. Quantitative use
requires parameter identification on strain/medium-specific data followed by
independent validation.

## Default operational recipe

The v3.0 default fed-batch recipe is changed to avoid the previous internally
inconsistent open-loop sugar accumulation:

- initial glucose: 25 g/L;
- initial assimilable N state: 0.45 g/L (model state basis);
- feed strategy: S-stat PID;
- feed start: 3 h;
- substrate set point: 8 g/L;
- feed glucose: 450 g/L;
- feed nitrogen state: 4 g/L;
- nominal maximum working volume: 4.75 L, below the 4.90 L HH trip threshold;
- RK4 step: 0.0025 h for the reference case.

The old exponential-feed option is retained for experiments and control
comparisons, but it is no longer the reference default.

## Literature anchors

These papers motivate the structural decision to avoid the implication that
nitrogen limitation must set fermentative carbon flux to zero. They do **not**
constitute calibration of the v3.0 reference parameters.

1. Varela C, Pizarro F, Agosin E. Biomass content governs fermentation rate in
   nitrogen-deficient wine musts. *Applied and Environmental Microbiology*.
   2004;70(6):3392–3400. DOI: 10.1128/AEM.70.6.3392-3400.2004.
2. Palma M, Madeira SC, Mendes-Ferreira A, Sá-Correia I. Impact of assimilable
   nitrogen availability in glucose uptake kinetics in *Saccharomyces cerevisiae*
   during alcoholic fermentation. *Microbial Cell Factories*. 2012;11:99.
   DOI: 10.1186/1475-2859-11-99.
3. Boender LGM, de Hulster E, van Maris AJA, Daran-Lapujade P, Pronk JT.
   Quantitative physiology of *Saccharomyces cerevisiae* at near-zero specific
   growth rates. *Applied and Environmental Microbiology*. 2009;75(17):5607–5614.
   DOI: 10.1128/AEM.00429-09.
4. Brandberg T, Gustafsson L, Franzén CJ. The impact of severe nitrogen
   limitation and microaerobic conditions on extended continuous cultivations
   of *Saccharomyces cerevisiae* with cell recirculation. *Enzyme and Microbial
   Technology*. 2007;40:585–593.

## Interpretation limits

- `N` is a lumped assimilable-nitrogen state, not a full amino-acid/ammonium model.
- `qS_ng` is a phenomenological capacity, not a mechanistic transporter model.
- the model does not include glycerol, organic acids or storage carbohydrates as
  explicit carbon states; the dynamic carbon audit intentionally exposes any
  residual inconsistency rather than forcing closure;
- the Crabtree/oxygen partition remains phenomenological;
- no default parameter should be presented as strain-independent truth.
