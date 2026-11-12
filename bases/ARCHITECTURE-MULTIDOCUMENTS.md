# Architecture documentaire multi-sources — ECU MEMS Manager SESSION

## Règle structurante

**Une base par langue ; plusieurs documents par base.** RAVE n'est que le premier manuel.
Les prochaines sources peuvent être d'autres manuels constructeur, bulletins techniques,
fiches de maintenance, schémas, notices ou documents autorisés à l'utilisation.

La base française `mems_documentary_fr.sqlite` peut contenir simultanément
`AKM7169FRE`, d'autres éditions françaises de RAVE et des documents sans lien
avec RAVE. Il n'est pas nécessaire de créer une nouvelle base pour chaque PDF.

## Identité et traçabilité

Chaque document possède :
- un `document_id` **stable**, indépendant de sa langue et de son titre ;
- une `source_revision` (une nouvelle édition reste identifiable) ;
- son éditeur, sa référence d'édition, son langage, son SHA-256 et sa licence ;
- son domaine d'applicabilité (véhicule, moteur, famille ECU et année si indiqués) ;
- ses sections, ses étapes, ses pages et leurs références constructeur.

**Une référence de procédure peut exister dans plusieurs manuels.** Elle ne
constitue pas une clé globale. Les identifiants des lignes sont toujours
liés à `document_id + source_revision + section_id / entry_id`.

## Mise à jour sans perdre les documents

Une nouvelle documentation est d'abord préparée séparément puis vérifiée.
Elle peut être **ajoutée** à la base de la langue correspondante.
Une autre édition du même manuel doit avoir une révision différente ;
on conserve la provenance de l'ancienne version.

La mise à jour installée chez l'utilisateur est une **nouvelle version complète
de la base de sa langue** (snapshot versionné) : l'application télécharge le
pack dans un emplacement temporaire, vérifie SHA-256, langue, schéma,
intégrité et provenance, exige le mot de passe, sauvegarde l'ancienne base,
puis remplace le fichier de façon atomique. Un échec conserve l'ancienne version.
Un import hors ligne suit exactement les mêmes contrôles.

Ce mécanisme n'est pas encore intégré au logiciel : le présent dépôt fixe le
contrat et fournit un premier schéma de référence à tester.

## Publication et qualité

- Chaque **document inclus** doit être complet et contrôlé ; une base peut
  accueillir **de nouveaux documents ultérieurement** sans être considérée
  comme éternellement incomplète.
- En français, aucune procédure anglaise n'est insérée pour combler un manque.
  Si l'édition française d'un nouveau document manque, ce document reste
  **absent** de la base française jusqu'à réception d'une source française.
- Pour une langue sans pack disponible, le repli anglais reste un choix de
  langue de la documentation, clairement indiqué à l'utilisateur ; il ne
  mélange jamais des passages anglais dans une fiche française.
- IA MEMS et écran Base de données interrogent le **même lecteur** de la base
  documentaire sélectionnée. Les réponses incluent document, révision et page.
- La recherche ne doit jamais déduire qu'une procédure concerne un ECU
  connecté sans compatibilité confirmée avec le véhicule, le moteur et le calculateur.
- Le diagnostic ECU, le moteur expert, les références des MEMS 1.2/1.3/1.6/1.9
  et les bases utilisateur restent **séparés**. Une mise à jour documentaire
  ne peut ni écraser ni supprimer ces données.
- Aucun PDF ni corpus dérivé de tiers ne doit être publié dans le dépôt public
  sans vérification des droits de redistribution. Un mot de passe/chiffrement
  ne remplace pas l'autorisation de distribution.

## Socle technique

Le fichier `schema_multidoc_v1.sql` formalise le catalogue et les contenus
multi-documents par langue. Le test `tests/test_schema_multidoc.py` vérifie
l'ajout de plusieurs sources, les révisions, l'isolation linguistique,
l'absence de collision des références et le rejet transactionnel des
mises à jour invalides.

**Ce nouveau schéma n'est pas celui du lecteur Rover 482 actuel.**
Son adoption dans le programme demandera une migration testée des données
existantes et une adaptation propre des lecteurs C++, sans patch ni remplacement
des bases de diagnostic. Aucune base publiée n'est prétendue compatible
tant que cette intégration n'a pas été vérifiée.

Dernière mise à jour : 12 novembre 2026.
