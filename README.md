# Policy Diff
### Version protocol for changes in obligations

A textual diff can show edited words without explaining changed duties. Policy Diff records a semantic change set between an ordered old/new document pair and attaches digests to both.

## Record key
`NORMALIZED_POLICY_ID#SEQUENCE`

Sequence starts at 1. Each proposed record has its own owner, old URL, new URL and predecessor digest. Duplicate keys are rejected.

## Write protocol
`propose_version(policy, sequence, old_url, new_url, previous_digest)`

For sequence 1, pass an empty predecessor digest. Later sequences require a finalized preceding record and the exact stored `newDigest` from that record.

`finalize(policy, sequence)`

Only that version's owner may finalize it, and only from PROPOSED. Read the result with `get_version(policy, sequence)`.

## Result shape
| Field | Representation |
| --- | --- |
| oldDigest / newDigest | SHA-256 of bounded processed bodies |
| added / removed / modified | Sorted, deduplicated strings |
| effectiveDate | Bounded text |
| ambiguities | Bounded strings |

The leader reads up to 18,000 body units per document. Validators refetch the pair, verify digests and independently assess the proposed obligations and effective date. Ambiguities are stored but are not included in the independent proposal check.

## Lineage is narrower than it looks
The supplied predecessor digest is checked at proposal time. Finalization does **not** require the fetched old document's digest to equal that predecessor digest. The protocol therefore records a claimed lineage, not fully verified content continuity.

Ownership is per version, not a permanent policy-owner registry. Different callers may propose successive versions. Consumers must enforce issuer trust and sequence policy themselves.

## Worked pair

### Checking a version pair

The [fixture pair](examples/versions/) and [stored change set](examples/change-trace.json) can be reviewed without submitting a transaction. Preserve the old/new ordering when interpreting their digests.

Run `python -m pip install -r requirements-dev.txt` to install the test tools. `python -m pytest specs/direct -q` exercises the mocked version protocol; `genvm-lint versioning/contract.py` checks the source statically. The tests do not establish legal completeness or cure the lineage limitation described above.

[The network example](tools/smoke.py) proposes sequence 1, checks duplicate rejection and finalizes it. It obtains account 4 from the private `accounts.env` four directories above the repo; a standalone clone must adapt this credential path. Running it creates transactions and replaces the local smoke record.

The [deployment record](deployments/studio.json) names the source and fixture revisions. Do not compare model-generated strings byte-for-byte across separate runs: an obligation change may be represented as replacement or modification.

The synthetic fixture replaces annual incident reporting with quarterly reporting and extends record retention from two to five years. A model may express this as modified obligations or as removed-plus-added obligations. Exact wording is not a stable API.

Inspect the [recorded change set](examples/change-trace.json). Truncated string rows are not a typed legal-obligation schema, and this output is not legal advice.

## Failure behavior
Unknown IDs, repeated proposals, missing predecessors and unauthorized finalization are rejected. Retrieval/model errors can fail finalization. HTTPS structure does not authenticate an issuing authority; documents must be selected and verified by the integrator.

[Interface source](versioning/contract.py) · [Lineage and adversarial tests](specs/direct/test_contract.py)

Deployment and network-run files are generated after execution; use the paths referenced above to inspect the current evidence.
