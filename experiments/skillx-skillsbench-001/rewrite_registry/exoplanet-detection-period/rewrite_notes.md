# Rewrite Notes — exoplanet-detection-period

## Why this task is in scope
- cleanest current zero-zero case: both original conditions completed without exceptions but both failed
- good test of whether SkillX can improve a skill bundle that currently does not lift performance at all
- the task is narrow enough that bundle ordering and role separation should matter

## Rewrite strategy
- preserve the five-skill bundle
- make the task hierarchy explicit:
  - `exoplanet-workflows` = overall pipeline and method choice
  - `light-curve-preprocessing` = quality filtering and detrending
  - `transit-least-squares` = primary transit search
  - `box-least-squares` = backup transit check
  - `lomb-scargle-periodogram` = exploratory periodicity check, mainly for variability understanding
- strongly bias the bundle toward writing one final scalar period to `/root/period.txt`

## Main SkillX additions
- explicit primary-vs-secondary search method boundaries
- stronger focus on the output contract instead of library walkthroughs
- warnings against over-detrending and destroying the transit signal
- bundle-level derived layer around period validation, aliases, and final file formatting

## Expected value of the rewrite
- clearer algorithm selection and less method-shopping
- less risk of spending time on generic astronomy exploration without producing the required period output
- better chance of converging on a transit-specific result instead of a stellar-variability period

