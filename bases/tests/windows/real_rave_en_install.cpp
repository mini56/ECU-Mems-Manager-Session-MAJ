// Integration test of the actual encrypted English documentary package.
//
// RAVE is 47 original PDF documents; AKM7169ENG is a separate manual.
// All are stored under independent source IDs in one English SQLite.
// This test never writes into user, ECU, French, or live production data.
#include "MemsDocumentaryLocalInstaller.h"
#include "MemsDocumentaryPackCatalog.h"
#include "MemsDocumentaryRepository.h"

#include <QCoreApplication>
#include <QCryptographicHash>
#include <QDir>
#include <QFile>
#include <QFileInfo>
#include <QSettings>
#include <QSqlDatabase>
#include <QSqlError>
#include <QSqlQuery>
#include <QStandardPaths>
#include <QStringList>
#include <QVariant>
#include <cstdio>

namespace {

bool check(bool condition, const char *label)
{
    if (!condition)
        std::fprintf(stderr, "FAIL %s\n", label);
    return condition;
}

bool makeSentinel(const QString &path, const QByteArray &original)
{
    if (!QDir().mkpath(QFileInfo(path).absolutePath()))
        return false;
    QFile file(path);
    return file.open(QIODevice::WriteOnly | QIODevice::Truncate) &&
           file.write(original) == original.size();
}

bool sentinelUnchanged(const QString &path, const QByteArray &original)
{
    QFile file(path);
    return file.open(QIODevice::ReadOnly) && file.readAll() == original;
}

bool inspectInstalled()
{
    const QString path = MemsDocumentaryPackCatalog::installedDatabasePath(
        QStringLiteral("en"));
    if (!check(QFileInfo(path).isFile(), "EN_SQLITE_NOT_INSTALLED"))
        return false;
    bool passed = false;
    const QString connection = QStringLiteral("REAL_RAVE_EN_AUDIT");
    {
        QSqlDatabase db = QSqlDatabase::addDatabase(QStringLiteral("QSQLITE"), connection);
        db.setConnectOptions(QStringLiteral("QSQLITE_OPEN_READONLY"));
        db.setDatabaseName(path);
        if (db.open()) {
            QSqlQuery totals(db);
            passed = totals.exec(QStringLiteral(
                "SELECT (SELECT COUNT(*) FROM documentary_documents),"
                "(SELECT COUNT(*) FROM documentary_pages),"
                "(SELECT COUNT(*) FROM documentary_images),"
                "(SELECT COUNT(*) FROM documentary_entries),"
                "(SELECT COUNT(*) FROM documentary_fts),"
                "(SELECT COUNT(*) FROM procedures),"
                "(SELECT COUNT(*) FROM procedure_steps)")) &&
                totals.next() &&
                totals.value(0).toInt() == 48 &&
                totals.value(1).toInt() == 1841 &&
                totals.value(2).toInt() == 1313 &&
                totals.value(3).toInt() > 0 &&
                totals.value(3).toInt() == totals.value(4).toInt() &&
                totals.value(5).toInt() == 336 &&
                totals.value(6).toInt() == 5055;
            QSqlQuery bySource(db);
            passed = passed && bySource.exec(QStringLiteral(
                "SELECT COUNT(*),SUM(source_pages),"
                "SUM(CASE WHEN document_id='AKM7169ENG' THEN 1 ELSE 0 END),"
                "SUM(CASE WHEN document_id='AKM7169ENG' THEN source_pages ELSE 0 END),"
                "SUM(CASE WHEN document_id='RCL0193ENG' OR "
                "document_id LIKE 'RAVE_%' THEN 1 ELSE 0 END),"
                "SUM(CASE WHEN document_id='RCL0193ENG' OR "
                "document_id LIKE 'RAVE_%' THEN source_pages ELSE 0 END)"
                " FROM documentary_documents WHERE language='en'")) &&
                bySource.next() &&
                bySource.value(0).toInt() == 48 &&
                bySource.value(1).toInt() == 1841 &&
                bySource.value(2).toInt() == 1 &&
                bySource.value(3).toInt() == 482 &&
                bySource.value(4).toInt() == 47 &&
                bySource.value(5).toInt() == 1359;
            QSqlQuery pictures(db);
            passed = passed && pictures.exec(QStringLiteral(
                "SELECT COUNT(*),SUM(CASE WHEN document_id='AKM7169ENG' "
                "THEN 1 ELSE 0 END) FROM documentary_images")) &&
                pictures.next() && pictures.value(0).toInt() == 1313 &&
                pictures.value(1).toInt() == 0;
            QSqlQuery metadata(db);
            passed = passed && metadata.exec(QStringLiteral(
                "SELECT language,publication_status FROM documentary_database "
                "WHERE singleton=1")) && metadata.next() &&
                metadata.value(0).toString() == QStringLiteral("en") &&
                metadata.value(1).toString() == QStringLiteral("source_inventory");
            QSqlQuery integrity(db);
            passed = passed && integrity.exec(QStringLiteral("PRAGMA integrity_check")) &&
                integrity.next() && integrity.value(0).toString() == QStringLiteral("ok");
            db.close();
        }
    }
    QSqlDatabase::removeDatabase(connection);
    return check(passed, "RAVE_47_AKM_SEPARATION_OR_SQLITE_COUNTS_INVALID");
}

bool inspectReader()
{
    MemsDocumentaryRepository repository;
    if (!check(repository.open(), "DOCUMENTARY_REPOSITORY_OPEN_FAILED"))
        return false;
    const QVariantList akm = repository.search(QStringLiteral("AKM7169ENG"), 20);
    const QVariantList rave = repository.search(QStringLiteral("RCL0193ENG"), 20);
    bool akmFound = false;
    bool raveFound = false;
    bool pageImage = false;
    for (const QVariant &row : akm)
        akmFound |= row.toMap().value(QStringLiteral("document_id")).toString() ==
            QStringLiteral("AKM7169ENG");
    for (const QVariant &row : rave) {
        const QVariantMap hit = row.toMap();
        if (hit.value(QStringLiteral("document_id")).toString() !=
            QStringLiteral("RCL0193ENG"))
            continue;
        raveFound = true;
        pageImage |= QFileInfo(
            MemsDocumentaryRepository::imagePathForHit(hit)).isFile();
    }
    return check(akmFound, "AKM_SEARCH_NOT_AVAILABLE") &&
           check(raveFound, "RAVE_SEARCH_NOT_AVAILABLE") &&
           check(pageImage, "RAVE_FACSIMILE_NOT_READABLE");
}

} // namespace

int main(int argc, char **argv)
{
    QCoreApplication app(argc, argv);
    QCoreApplication::setOrganizationName(QStringLiteral("MEMS_TEST"));
    QCoreApplication::setApplicationName(QStringLiteral("REAL_RAVE_EN_47_TEST"));
    QStandardPaths::setTestModeEnabled(true);
    if (app.arguments().size() != 2)
        return check(false, "EXPECTED_ONE_ENCRYPTED_PACK") ? 0 : 1;
    const QString password = qEnvironmentVariable("MEMS_DOCUMENTARY_PUBLISH_PASSWORD");
    if (password.size() < 12)
        return check(false, "PUBLISHER_PASSWORD_MISSING") ? 0 : 1;
    QSettings settings(QSettings::IniFormat, QSettings::UserScope,
                       QStringLiteral("ECU_Mems_Manager"));
    settings.setValue(QStringLiteral("Settings/Language"), QStringLiteral("en"));
    settings.sync();
    if (!check(settings.status() == QSettings::NoError, "LOCALE_SETTING_FAILED"))
        return 1;

    const QString root = QStandardPaths::writableLocation(
        QStandardPaths::AppLocalDataLocation);
    const QString french = QDir(root).filePath(
        QStringLiteral("documentary/bases/fr/mems_documentary_fr.sqlite"));
    const QString ecu = QDir(root).filePath(
        QStringLiteral("ecu/never-touch-existing-ecu.dat"));
    const QByteArray sentinel("PRESERVE_EXISTING_DOCUMENTARY_FR_AND_ECU");
    if (!check(makeSentinel(french, sentinel) &&
               makeSentinel(ecu, sentinel), "SENTINEL_PREPARATION_FAILED"))
        return 1;

    const QString failure = MemsDocumentaryLocalInstaller::installEncrypted(
        app.arguments().at(1), QStringLiteral("en"), password);
    if (!check(failure.isEmpty(), "REAL_RAVE_EN_DECRYPT_AND_INSTALL_FAILED")) {
        std::fprintf(stderr, "DETAIL %s\n", qPrintable(failure));
        return 1;
    }
    if (!inspectInstalled() || !inspectReader() ||
        !check(sentinelUnchanged(french, sentinel) &&
               sentinelUnchanged(ecu, sentinel), "FR_OR_ECU_SENTINEL_MODIFIED"))
        return 1;

    std::puts("PASS_47_ORIGINAL_RAVE_DOCUMENTS_1359_PAGES");
    std::puts("PASS_AKM7169ENG_SEPARATE_SOURCE_482_PAGES");
    std::puts("PASS_ONE_ENGLISH_SQLITE_48_DOCUMENTS_1841_PAGES");
    std::puts("PASS_1313_RAVE_FACSIMILES");
    std::puts("PASS_REAL_AES_GCM_WINDOWS_INSTALL_AND_REPOSITORY_SEARCH");
    std::puts("PASS_FR_AND_ECU_ISOLATION_NO_PUBLIC_RELEASE");
    return 0;
}
