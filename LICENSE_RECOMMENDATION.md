# License Decision

## Current License

The public repository now uses Apache License 2.0 in `LICENSE`.

## Approved License For The Public Portion

Apache License 2.0 was approved for the public source-code and documentation portion only. It is permissive and includes an explicit patent license and patent termination clause.

## Advantages Of Apache License 2.0

- Permissive commercial and non-commercial use.
- Explicit patent grant from contributors.
- Patent termination clause if a licensee initiates certain patent claims.
- Clear notice and modification requirements.
- Familiar license for open-source fund, cloud, and enterprise reviewers.

## Disadvantages Of Apache License 2.0

- Longer and more complex than MIT.
- Still allows others to use, modify, distribute, and sell the public code.
- Does not keep public source-code improvements exclusive unless contribution policy is controlled.
- Does not protect trademarks, hosted services, datasets, or model weights unless those are separately licensed.

## Commercial Use By Others

Apache 2.0 would generally allow third parties to use the public code commercially, including in proprietary products, as long as they follow the license terms. It would not automatically grant rights to private data, model weights, hosted services, trademarks, logos, or separately licensed components.

## Scope Clarification

Apache 2.0 applies only to files present in the public repository. The following remain outside that license unless separately released:

- training data
- private reference texts
- final OCR model weights
- LoRA/QLoRA adapters
- checkpoints
- private training recipes and final hyperparameters
- proprietary data-collection tools
- production credentials and deployment configuration
- customer data
- trademarks, logos, and brand assets

## README Scope Text

```text
Unless otherwise stated, the source code and documentation in this repository are licensed under Apache License 2.0. This license applies only to files included in this public repository. Training datasets, model weights, adapters, checkpoints, hosted services, production configurations, trademarks, logos, and commercial components are not included and may be licensed separately.
```

## Future Data And Weight Licensing

Use separate licenses or agreements for datasets and model artifacts. Options may include a data-use agreement, research-only license, commercial license, model license, or a public dataset license if redistribution rights are clear.

## Irrevocability Warning

Once a version is published under an open-source license, recipients can usually continue using that version under those terms. Future versions can change license only if the project has the legal right to relicense all included contributions.

## Contributor Impact

External contributions can make future relicensing harder unless contributions are covered by a Developer Certificate of Origin, contributor license agreement, or another documented contribution policy. This should be decided before accepting substantial third-party contributions.
