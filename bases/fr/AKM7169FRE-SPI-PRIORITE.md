# AKM7169FRE — MEMS injection monopoint SPi (20 pages françaises)

## État du chapitre : relecture documentaire terminée le 13 novembre 2026

Source originale **Rover Group, 1993 — AKM7169FRE**, extrait SPi de **20 pages**, SHA-256 du fac-similé original :

`37cd0434347fe4009963d075e4b91b0b21ebc905bae5657519a8080c3026d4f5`

Ce résultat couvre le **chapitre SPi disponible**, pas le manuel Rover complet. Il ne reprend aucune traduction de l'édition anglaise.

| Élément contrôlé | Résultat |
| --- | ---: |
| Pages originales et images conservées | 20 sur 20 |
| Opérations de réglage/réparation | 20 |
| Étapes numérotées liées à la page exacte | 267 |
| Sections descriptives transcrites | 19 |
| Valeurs techniques identifiées avec leurs conditions | 22 |
| Consignes constructeur particulières | 4 |
| Entrées documentaires du chapitre dans la nouvelle SQLite | 429 |
| Entrées de ce chapitre avec le statut `review_required` | **0** |

**Corrections importantes :** le premier index ne contenait que 9 valeurs. La relecture a également retrouvé notamment les couples de serrage du corps de papillon (10 N.m) et du boîtier d'injecteur (5 N.m) à la page PDF 18, les conditions de purge à la page 10 et l'angle représenté dans le schéma d'allumeur 19M0157 à la page 20.

**Renvoi interne du constructeur conservé :** à la page PDF 12, étape 9 de l'essai de pression, le manuscrit renvoie aux étapes « 3 et 4 », tandis que les pressions 1,0 bar et 0,7 bar sont imprimées aux étapes 7 et 8. La transcription préserve mot pour mot le renvoi imprimé ; une table éditoriale distincte indique les emplacements des valeurs, sans faire passer cette interprétation pour un erratum officiel.

## Nouvelle SQLite française réunie (prépublication privée)

- Sources : **RCL0193FRE (371 pages)** et **AKM7169FRE SPi (20 pages)**.
- Total : **391 pages, 6 387 entrées, 345 illustrations**.
- Les **5 958 entrées d'origine RCL0193FRE** n'ont subi aucune modification.
- Index FTS5 : 6 387 entrées ; contrôles SQLite et clés étrangères réussis.
- Empreintes SHA-256 des 345 images vérifiées.
- Aucun enregistrement avec le statut `review_required` dans la nouvelle SQLite.
- SHA-256 SQLite réunie : `b314a275fec750fb4a073b2fa3a1d14e09b03e63f993226908da8041accefb19`.
- ZIP privé contenant uniquement la SQLite et ses images : SHA-256 `fc1ca6c19a2b5b4e4bb93c49546f0a2278de07de6e6b65c5c8e21f52a8d9d372`.

Le ZIP complet et l'archive spécifique du chapitre sont conservés dans les livrables du propriétaire, pas sur ce dépôt public.

## Compatibilité MAJ

Le format du futur pack chiffré est **MEMSDOC1 / AES-256-GCM** avec le mot de passe défini par l'administrateur. La branche de développement du programme accepte désormais le contrôle des deux éditions françaises par leurs empreintes constructeur exactes et teste le format à l'aide de **données synthétiques**.

[Inventaire de prépublication](../prepublication/2026-11-13/akm7169fre-spi-final-candidate.json).

**La publication n'est pas réalisée :** ce dépôt MAJ reste public et les droits de redistribution de la transcription et des illustrations Rover ne sont pas établis. `manifest.json` doit donc rester à `available: false`. Le mot de passe ne constitue pas à lui seul une autorisation de diffusion.

La relecture documentaire garantit la fidélité du relevé au **chapitre d'origine** ; les valeurs et procédures ne constituent pas une approbation universelle d'une intervention pour tous les véhicules et millésimes.
