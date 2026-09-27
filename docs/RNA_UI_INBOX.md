# RNA UI inbox routing

Issue #9 receives DNA-to-RNA delta reports. Routing is based on record shape,
not on whether a directory or status group is new.

| Record shape | Existing surface |
|---|---|
| Typed node | Catalog and Graph |
| Typed STOP node | Catalog and STOP correction desk |
| Typed bridge | Graph and Catalog |
| External-source manifest | Provenance/index documentation |
| Unknown shape | needs-surface; human review |

This resolves the reviewed runic and SUNET rows without inventing a new UI.
The classifier does not deploy or inspect grok.me.

verification_type: software_test
