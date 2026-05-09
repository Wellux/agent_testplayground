# seed/ — first-day vault content

`scripts/install.sh` copies this directory tree into `$VAULT/` on first
install (`cp -n` semantics — never overwrites existing files). It exists
so that on day 1 the chain has skills to amend, prompts to A/B, and a
profile to evolve, instead of waiting for organic accumulation.

## What lands where

| Source                              | Vault path                           |
| ----------------------------------- | ------------------------------------ |
| `seed/CLAUDE.md`                    | `$VAULT/CLAUDE.md`                   |
| `seed/40-Skills/recall.md`          | `$VAULT/40-Skills/recall.md`         |
| `seed/40-Skills/pr-from-branch.md`  | `$VAULT/40-Skills/pr-from-branch.md` |
| `seed/50-Prompts/code-review.md`    | `$VAULT/50-Prompts/code-review.md`   |
| `seed/50-Prompts/daily-summary.md`  | `$VAULT/50-Prompts/daily-summary.md` |
| `seed/60-Interactions/user-profile.md` | `$VAULT/60-Interactions/user-profile.md` |

## Curriculum (Voyager)

```
recall  ──prerequisite_of──►  pr-from-branch
```

`recall` has zero prerequisites and is the foundation; `pr-from-branch`
depends on `recall` (it reads the user-profile + matching daily notes
before composing the PR body). Future skills should keep extending this
chain rather than re-deriving foundations.

## A/B fixtures

The two seed prompts have matching promptfoo-shaped fixtures already
shipped at `harness/fixtures/code-review.yml` and
`harness/fixtures/daily-summary.yml`. The interaction pass (#3) will A/B
them once the user has pushed candidate variants.
