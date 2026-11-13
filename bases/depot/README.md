# Dossier de dépôt des bases documentaires chiffrées

**Dossier :** `bases/depot/`

Ce dossier existe pour recevoir les versions des bases documentaires de
MEMS Manager SESSION, notamment les fichiers `.encrypted` FR et EN, puis
les prochains snapshots par langue.

**ATTENTION : le dépôt GitHub ECU-Mems-Manager-Session-MAJ est PUBLIC.**
Ne pas transférer ici de fichier contenant des documents ou illustrations
constructeur dont la redistribution n'est pas autorisée. Le chiffrement
ne remplace pas l'autorisation. Dans ce cas, préparer les packs localement
et les conserver dans un dépôt réellement privé.

## Tailles / dépôt

Le pack FR initial pèse environ 28,1 Mo, au-dessus de la limite de 25 Mio
pour un fichier envoyé depuis le navigateur GitHub. Utiliser **GitHub Desktop
et Git LFS** pour déposer ce pack dans ce dossier. Le fichier EN plus petit
peut aussi suivre ce circuit pour garder la même méthode.

La règle Git LFS est enregistrée dans `.gitattributes`.

## IMPORTANT — état technique

Ce dossier n'est PAS encore une interface d'importation automatique des
packs dans le manifeste MAJ. Placer deux fichiers ici ne déclenche pas à
lui seul leur activation, ni leur installation par SESSION.

Le programme télécharge actuellement les packs référencés par
`manifest.json` depuis les Releases vérifiées. Avant d'activer
une nouvelle version, contrôler AES-GCM, mot de passe propriétaire,
langue, SQLite, provenance et droits de distribution ; conserver les
anciens manuels lors de la mise à jour.
